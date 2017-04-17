# me - this DAT
# 
# dat - the DAT that received a message
# rowIndex - the row number the message was placed into
# message - an ascii representation of the data
#           Unprintable characters and unicode characters will
#           not be preserved. Use the 'bytes' parameter to get
#           the raw bytes that were sent.
# bytes - a byte array of the message.
# timeStamp - the arrival time component the OSC message
# address - the address component of the OSC message
# args - a list of values contained within the OSC message
# peer - a Peer object describing the originating message
#   peer.close()    #close the connection
#   peer.owner  #the operator to whom the peer belongs
#   peer.address    #network address associated with the peer
#   peer.port       #network port associated with the peer
#

classes = {
  'movieFileIn' : (moviefileinTOP, 'moviefilein', 'TOP'),
  'displace' : (displaceTOP, 'displace', 'TOP'),
  'noiseCHOP' : (noiseCHOP, 'noise', 'CHOP'),
  'chopToTop' : (choptoTOP, 'chopto', 'TOP')
}

def receiveOSC(dat, rowIndex, message, bytes, timeStamp, address, args, peer):
  global classes

  addr = "/project1" + address
  if args[0] == "create":
    clazz = classes.get(args[1], 'none')
    if clazz == "none":
      return

    if op(addr) != None:
      if op(addr).type == clazz[1] and op(addr).family == clazz[2]:
        return
      else:
        op(addr).destroy()

    name = addr[(addr.rfind('/') + 1):]
    par = addr[:(addr.rfind('/'))]
    op(par).create(clazz[0], name)

  elif args[0] == "connect" and op(addr):
    op(addr).inputConnectors[args[1]].connect(op("/project1" + args[2]))

  elif args[0] == "parameter" and op(addr):
    pars = op(addr).pars(args[1])
    if len(pars) > 0:
      if isfloat(args[2]):
        pars[0].val = args[2]
      else:
        pars[0].expr = args[2]

  return

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False
