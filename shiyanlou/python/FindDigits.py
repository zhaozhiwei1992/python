#/usr/bin/env python3
import re
f = open("/home/shiyanlou/Code/String.txt")
try:
	allText = f.read()
finally:
	f.close()
m = re.findall(r'[0-9]', allText)

print("".join(list(m)))
