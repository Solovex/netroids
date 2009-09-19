import os, glob, py_compile

def make(filename):
	print "Compiling file: %s..." % filename
	out = filename + "c"
	if os.path.exists(out):
		print " *** File %s exists. Overwriting..." % out
	r = py_compile.compile(filename)
	return r == None

def main():
	print("netroids module compiler 1.0 by Drajwer & asdf")
	dirs = ['', 'client/', 'server/']
	l = []	
	map(lambda x: l.extend(x), map(lambda d: glob.glob("%s*.py" % d),dirs))
	if l == []:
		print "Files not found"
		return False
	fail = False
	for fn in l:
		if not make(fn):
			fail = True
			break
	if fail:
		print "Module compiling failed."

if __name__ == '__main__': main()
