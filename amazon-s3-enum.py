#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import queue
import threading
import argparse

class amazonBucketClass():

	def __init__(self,domain,wordlist):
		self.q = queue.Queue()
		self.Searchdomain = domain
                self.wordlist = wordlist
                self.amazonBase = ".s3.amazonaws.com"
                self.httpStart = "http://"
		self.buckets = []
                self.bucketContent = []
		self.bucketDumpDone = 0
		self.bucketCheckDone = 0


	def worker(self):
		while 1:
			domain = self.q.get()
			#test url make sure no errors
			try:
				requests.get(domain,timeout=5)
				self.checkS3Bucket(domain)
			except:
				pass
			self.q.task_done()

	def run(self):
		with open(self.wordlist) as fp:
			for word in fp:
				word = word.strip()
				self.q.put(self.httpStart + word + "." + self.Searchdomain + self.amazonBase)
				self.q.put(self.httpStart + word + "-" + self.Searchdomain + self.amazonBase)
				#q.put(httpStart + domain + "." + word + amazonBase)
				#q.put(httpStart + domain + "-" + word + amazonBase)


	def checkS3Bucket(self,domain):
		self.bucketCheckDone = 0

		r = requests.get(domain,timeout=5)
		soup = BeautifulSoup(r.content, 'xml')
		message = soup.find('Message')
		#print(domain)
		if message:
			if 'Access Denied' in message.get_text():
				self.buckets.append({'domain':domain,'access':message.get_text()})
			elif message:
				pass
		else:
			self.buckets.append({'domain':domain,'access':'Access Granted'})

	def s3BucketDump(self,domain):
		self.bucketContent = []
		self.bucketDumpDone = 0

		r = requests.get(domain,timeout=5)
                soup = BeautifulSoup(r.content, 'xml')
		isTruncated = soup.find("IsTruncated").get_text()
		while 1:
			contents = soup.find_all('Contents')
			for content in contents:
				key = content.find("Key").get_text()
				lastModified = content.find("LastModified").get_text()
				size = content.find("Size").get_text()

				self.bucketContent.append({'key':key,'modified':lastModified,'size':size})
				#print {'key':key,'modified':lastModified,'size':size}
			if isTruncated == 'false':
				break

			r = requests.get(domain + "/?marker="+self.bucketContent[-1]['key'] )
			soup = BeautifulSoup(r.content, 'xml')
			isTruncated = soup.find("IsTruncated").get_text()
		self.bucketDumpDone = 1

	def startThreads(self,i):
		#Spin up workers
		for i in range(i):
			t = threading.Thread(target=self.worker)
			t.daemon = True
			t.start()


'''
	Use tool to find s3 buckets belonging to a domain. Uses simple brute force.
	Once bucket is found we can grab a list of all files in the bucket.

	Example:
		Find S3Buckets	 - 	script.py -d test -w wordlist.txt
		Dump Bucket	-	script.py -d http://dev-test.s3.amazon.com -e 1
'''

parser = argparse.ArgumentParser()
parser.add_argument("-d","--domain", help="Domain Name; EX: test.com")
parser.add_argument("-w","--wordlist", help="Wordlist; EX: test.txt")
parser.add_argument("-e","--extract", help="Etract Bucket Contents; EX: -d test.s3.amazon.com -e 1")
args = parser.parse_args()

if args.extract:
	s3Buck = amazonBucketClass(None,None)
	s3Buck.s3BucketDump(args.domain)
	print("%-30s %-20s %-40s\n" % ("Last Modified","Size","Key"))
	for bucket in s3Buck.bucketContent:
		print("%-30s %-20s %-40s\n" % (bucket['modified'],bucket['size'],bucket['key']))
else:
	print("Brute forcing s3 buckets......\nThis could take awhile.......")
	s3Buck = amazonBucketClass(args.domain,args.wordlist)
	s3Buck.startThreads(20)
	s3Buck.run()
	s3Buck.q.join()
	s3Buck.bucketCheckDone = 1

	print("%-25s %-40s" % ("Access","S3 Bucket"))
	for bucket in s3Buck.buckets:
		print("%-25s %-40s" % (bucket['access'],bucket['domain']))

print("\n\nDone!")
