#!/usr/bin/python

import sys
from secretsharing import SecretSharer

minimum = 25
total = 700

for share in SecretSharer.split_secret(sys.argv[1], minimum, total):
	print(share)
