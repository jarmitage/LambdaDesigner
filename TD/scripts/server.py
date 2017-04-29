# me is this DAT.
# 
# dat is the DAT that received a message.
# rowIndex is the row number the message was placed into.
# message is an ascii representation of the message.
# bytes is a byte array of the message.
#
# peer, a Peer object describing the originating message
#   peer.close()    #close the connection
#   peer.owner  #the operator to whom the peer belongs
#   peer.address    #network address associated with the peer
#   peer.port       #network port associated with the peer

import binascii
import hashlib
import base64
import struct
import array
import socket
import json

def receive(dat, rowIndex, message, bytes, peer):
    peerList = me.fetch('peerList',{})


    if message.startswith('GET '):
        fullMsg = bytes.decode("utf-8")
        msgList = [s for s in fullMsg.splitlines() if s]
        path = msgList[0].split(' ')[1]
        header = {}
        header['GET'] = msgList[0].split(' ')[1]
        msgList.pop(0)
        for i in msgList:
            keyValue = i.split(': ')
            if len(keyValue) == 2:
                header[keyValue[0]] = keyValue[1]
        
        if header['GET'] == '/':
            sendHeader = getHeader(hType='default')
            peer.sendBytes(sendHeader)
            website = op('website').text
            peer.sendBytes(website)
            op('closePeer').run(peer,delayFrames=1)

        elif header['GET'] == '/connect':
            peerList[peer.port] = peer
            me.store('peerList',peerList)
            sendHeader = getHeader(hType='websocket',recHeader=header)
            sendHello = json.dumps({'type':'system','message':'Hello from ' + app.product +'!'})
            packedMsg = encode(sendHello.encode('utf-8'))
            packedMsg = b''.join(packedMsg)
            peer.sendBytes(sendHeader)  
            peer.sendBytes(packedMsg)

    else:
        fullMsg = unpack_frame(bytes)
        try:
            payload = eval(fullMsg['payload'])
            voteNum = payload.get('votenum',None)
            op('voteNum' + str(voteNum)).par.value0.pulse(1, frames=2)
        except:
            if fullMsg['payload'] == b'\x03\xe9':
                peerList.pop(peer.port,None)
                me.store('peerList',peerList)
                peer.close()

    return

def sendAMessage(message):
    peerList = op('myPeers').fetch('peerList')
    returnMsg = json.dumps({'type':'system','message':message})
    packedMsg = encode(returnMsg.encode('utf-8'))
    packedMsg = b''.join(packedMsg)
    for port in peerList:
        peerList[port].sendBytes(packedMsg)
    return


def getHeader(hType=None, recHeader=None):
    if hType == 'default':
        header = b'HTTP/1.x 200 OK\n\rContent-Type: text/html; charset=UTF-8\n\r\n\r'
    elif hType == 'websocket':
        SecKey = recHeader.get('Sec-WebSocket-Key',None)
        h = hashlib.sha1()
        h.update(str.encode(SecKey+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'))
        responseKey = base64.b64encode(h.digest())
        header = b'HTTP/1.1 101 Web Socket Protocol Handshake\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nWebSocket-Origin: localhost\r\nWebSocket-Location: localhost:7000/demo/shout\r\nSec-WebSocket-Accept:'+responseKey+b'\r\n\r\n'
    return header


def unpack_frame(data):
    frame = {}
    byte1, byte2 = struct.unpack_from('!BB', data)  
    frame['fin'] = (byte1 >> 7) & 1  
    frame['opcode'] = byte1 & 0xf  
    masked = (byte2 >> 7) & 1  
    frame['masked'] = masked  
    mask_offset = 4 if masked else 0  
    payload_hint = byte2 & 0x7f  
    if payload_hint < 126:  
        payload_offset = 2  
        payload_length = payload_hint                 
    elif payload_hint == 126:  
        payload_offset = 4  
        payload_length = struct.unpack_from('!H',data,2)[0]  
    elif payload_hint == 127:  
        payload_offset = 8  
        payload_length = struct.unpack_from('!Q',data,2)[0]  
    frame['length'] = payload_length  
    payload = array.array('B')  
    payload.fromstring(data[payload_offset + mask_offset:])  
    if masked:  
        mask_bytes = struct.unpack_from('!BBBB',data,payload_offset)  
        for i in range(len(payload)):  
            payload[i] ^= mask_bytes[i % 4]
    frame['payload'] = payload.tostring()
    return frame


def encode(bytesRaw):
    bytesFormatted = []
    bytesFormatted.append(struct.pack('B', 129))
    if (len(bytesRaw) <= 125):
        bytesFormatted.append(struct.pack('B', len(bytesRaw)))
    elif (len(bytesRaw) >= 126 and len(bytesRaw) <= 65535):
        bytesFormatted.append(struct.pack('B', 126));
        bytesFormatted.append(struct.pack('B', ( len(bytesRaw) >> 8 ) & 255));
        bytesFormatted.append(struct.pack('B', ( len(bytesRaw)      ) & 255));
        
    else:
        bytesFormatted.append(struct.pack('B', 127));
        bytesFormatted.append(struct.pack('B', ( len(bytesRaw) >> 56 ) & 255));
        bytesFormatted.append(struct.pack('B', ( len(bytesRaw) >> 48 ) & 255));
        bytesFormatted.append(struct.pack('B', (len( bytesRaw) >> 40 ) & 255));
        bytesFormatted.append(struct.pack('B', (len( bytesRaw) >> 32 ) & 255));
        bytesFormatted.append(struct.pack('B', (len( bytesRaw) >> 24 ) & 255));
        bytesFormatted.append(struct.pack('B', (len( bytesRaw) >> 16 ) & 255));
        bytesFormatted.append(struct.pack('B', ( len(bytesRaw) >>  8 ) & 255));
        bytesFormatted.append(struct.pack('B', ( len(bytesRaw)       ) & 255));
    
    for i in range(len(bytesRaw)):
        #bytesFormatted.append(struct.pack('B', ord(bytesRaw[i])))
        bytesFormatted.append(struct.pack('B', bytesRaw[i]))
    return bytesFormatted;