import struct

def swizzle(byte_fields, resolution = 20):
  """
  This function takes a series of IEEE encoded floats,
  discretizes them, and repacks them into a string,
  allowing them to be used in our massive sort
  operation.
  """
  
  floats = struct.unpack('f' * 384, byte_fields)
  discretized = [ int(x * (1 << resolution)) for x in floats ]
  result = 0
  for i in resolution:
    for value in discretized:
      result <<= 1
      result |= (value >> (resolution - i)) & 1
  total_bytes = ceil(resolution * len(floats) / 8)
  output = [ ]
  for i in total_bytes:
    output.append(struct.pack('B', result >> ((total_bytes - i - 1) * 8) % 255))
  return ''.join(output)
