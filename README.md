# s3brute
s3 brute force tool

# Usage
```
python amazon-s3-enum.py -w BucketNames.txt -d example.com
```
#If you face Error Like

  File "amazon-s3-enum.py", line 13
    self.wordlist =wordlist
                          ^
TabError: inconsistent use of tabs and spaces in indentation|


Then Type This Command And Run Again 

1) sudo apt-get install python3-autopep8

2) autopep8 -i amazon-s3-enum.py 

3) python3 amazon-s3-enum.py -w BucketNames.txt -d example.com
