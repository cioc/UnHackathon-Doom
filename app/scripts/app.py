from flask import Flask, render_template, request
import Image
import leargist
import base64
import gc
import struct
import numpy
import cStringIO as StringIO

app = Flask(__name__)

runs = { }

def add_file(start, filename, type):
  fp = open(filename, 'r')
  runs[start] = [ ]
  
  for i in xrange(0, 2000):
    read = fp.read(960 * 4)
    if len(read) == 0:
      break
    runs[start].append(( read, type))
  
  fp.close()

add_file(12724438, "/mnt/ti-12724438.gists", "cat")
add_file(21177641, "/mnt/ti-21177641.gists", "dog")
add_file(34413854, "/mnt/ti-34413854.gists", "house")
add_file(43291924, "/mnt/ti-43291924.gists", "map")
add_file(72581998, "/mnt/ti-72581998.gists", "toy")

@app.route("/")
def hello():
  return render_template('index.html')

@app.route("/search", methods = ["POST"])
def search():
  image = Image.open(request.files["image"].stream)
  
  gist = leargist.color_gist(image)
  html = [ ]
  html.append("""
  <style type="text/css">
  *{margin:0;padding:0;}
  h1{font:bold 3em/2em Helvetica,sans-serif;}
  h1 a{font:11px sans-serif;color:#39c;}
  html{background-color:#f8f8f8;}
  body{width:1000px;margin:0 auto;}
  .bar{position:relative}
  b{height:70px;float:left;width:1px;display:block;position:relative;}
  i{background-color:#000;display:block;width:1px;position:absolute;bottom:0;}
  .bar{width:960px;height:70px;border:1px solid #eee;background-color:#fff;margin-left:70px;}
  .bar{margin-bottom:5px;}
  img{position:absolute;width:70px;left:-5.5em;}
  .breakdown div{float:left;display:block;height:50px;border-left:1px solid #999;margin-left:-1px;text-align:center;}
  .breakdown{height:50px;margin-bottom:10px;font:0.9em/50px sans-serif;color:#333;}
  strong{position:absolute;top:0.5em;left:0.5em;font:0.9em sans-serif;color:#999;}
  </style>
  """)
  
  output = StringIO.StringIO()
  image.save(output, format="PNG")
  
  html.append('<h1>Image Search <a href="/">reset search</a></h1>')
  html.append('<div class="bar"><img src="data:image/png;base64,%s"/>' % base64.b64encode(output.getvalue()))
  for i in xrange(960):
    html.append('<b><i style="height:%f%%"></i></b>' % (gist[i] * 100))
  html.append('</div>')
  html.append('<br style="height:5em;display:block;"/>')
  
  (results, types) = process(image)
  
  html.append('<div class="breakdown">')
  for (weight, key) in types[::-1]:
    html.append('<div style="width:%0.2f%%">%s (%0.1f%%)</div>' % (weight * 100, key, weight * 100))
  html.append('</div>')
  
  for image, g, type in results:
    output = StringIO.StringIO()
    image.save(output, format="PNG")
    
    html.append('<div class="bar"><img src="data:image/png;base64,%s"/>' % base64.b64encode(output.getvalue()))
    for i in xrange(960):
      html.append('<b><i style="height:%f%%"></i></b>' % (g[i] * 100))
    html.append('<strong>%s</strong></div>' % type)
  
  return ''.join(html)

def numeric(filename, i, goal):
    image = Image.open(filename)
    result = leargist.color_gist(image)
    return (distance(result, goal), filename)

def distance(a, b):
    sum = 0
    for i in xrange(960):
      sum += (a[i] - b[i]) * (a[i] - b[i])
    return sum

def process(test_image):
    index = [ ]
    
    tests = 500
    result = leargist.color_gist(test_image)
    
    for (start, items) in runs.items():
      for (i, (buffer, type)) in enumerate(items):
        gist = numpy.array(struct.unpack("f" * 960, buffer), dtype=float)
        index.append( ( numpy.linalg.norm(gist - result), i, type, start ) )
    
    index.sort()
    
    types = { }
    
    for fn in index[:100]:
      if not fn[2] in types:
        types[fn[2]] = 0
      types[fn[2]] += 1 / (1 + fn[0])
    
    total = sum(types.values())
    
    for type in types.keys():
      types[type] /= total
    
    result = [ ]
    for fn in index[:10]:
      filename = "/tiny/tinyimages/subset/%s/%s.png" % (fn[2], fn[1] + fn[3])
      image = Image.open(filename)
      buffer = runs[fn[3]][fn[1]][0]
      gist = struct.unpack("f" * 960, buffer)
      result.append((image, gist, fn[2]))
    
    return (result, sorted([ (b, a) for (a, b) in types.items() ]))

if __name__ == "__main__":
  app.run(debug = True, host = '0.0.0.0')
