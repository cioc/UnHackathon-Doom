import sys
sys.path.append("/home/charles/PyTinyImage")
import tinyimage as tinyimage
import leargist
import scipy
import struct

start = int(sys.argv[1])
stop = int(sys.argv[2])

f = open('/mnt/ti-%i.gists' % start, "w+")

tinyimage.openTinyImage()

for i in xrange(start, stop):
	s = tinyimage.sliceToBin(i)
	image = scipy.misc.toimage(s.reshape(32,32,3, order="F").copy())
	gist = leargist.color_gist(image)	
	print len(gist)
	f.write(struct.pack('f' * 960, *gist))
	print "Remaining: %i" % (stop - i)

tinyimage.closeTinyImage()
f.close()
