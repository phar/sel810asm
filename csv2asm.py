import csv, sys

filename = sys.argv[1]

with open(filename) as f:
	reader = csv.reader(f)
	for row in reader:
#		print(row)
		if len(sys.argv) > 2:
			print(row[2].strip().ljust(10),row[3].strip().ljust(4),row[4].strip().ljust(4),row[5].strip().ljust(25),row[6].strip())
		else:
			print(row[3].strip().ljust(4),row[4].strip().ljust(4),row[5].strip().ljust(25),row[6].strip())
			
