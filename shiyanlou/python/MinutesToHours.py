#!/usr/bin/env python3
import sys

def Hours():
	num = int(sys.argv[1])
	try:
		if(num < 0):
			raise ValueError("ddd")
		else:
			hour, mini = divmod(num, 60)
			print(str(hour) + " H, " + str(mini) + " M")

	except ValueError:
		print("ValueError: Input number cannot be negative")

if __name__ == "__main__":
	Hours()
