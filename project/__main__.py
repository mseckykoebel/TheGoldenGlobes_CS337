import sys
import helpers

if __name__ == '__main__':

	if len(sys.argv) != 2:
		print("Wrong number of arguments, make sure to include your data file. ie. python3 project ./yourdata.json")
		sys.exit(2)

	path = sys.argv[1]

	helpers.comment_extract_file(path)
	print("Opening file " + path)



