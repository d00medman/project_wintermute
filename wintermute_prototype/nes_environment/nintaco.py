# to 125 is main method. importing brings in these constants
import time
import copy
import socket
import sys
import traceback

GRAY = 0x00
DARK_BLUE = 0x01
DARK_INDIGO = 0x02
DARK_VIOLET = 0x03
DARK_MAGENTA = 0x04
DARK_RED = 0x05
DARK_ORANGE = 0x06
DARK_BROWN = 0x07
DARK_OLIVE = 0x08
DARK_CHARTREUSE = 0x09
DARK_GREEN = 0x0A
DARK_MINT = 0x0B
DARK_CYAN = 0x0C
BLACKER_THAN_BLACK = 0x0D
BLACK3 = 0x0E
BLACK = 0x0F

LIGHT_GRAY = 0x10
BLUE = 0x11
INDIGO = 0x12
VIOLET = 0x13
MAGENTA = 0x14
RED = 0x15
ORANGE = 0x16
BROWN = 0x17
OLIVE = 0x18
CHARTREUSE = 0x19
GREEN = 0x1A
MINT = 0x1B
CYAN = 0x1C
BLACK2 = 0x1D
BLACK4 = 0x1E
BLACK5 = 0x1F

WHITE = 0x20
LIGHT_BLUE = 0x21
LIGHT_INDIGO = 0x22
LIGHT_VIOLET = 0x23
LIGHT_MAGENTA = 0x24
LIGHT_RED = 0x25
LIGHT_ORANGE = 0x26
LIGHT_BROWN = 0x27
LIGHT_OLIVE = 0x28
LIGHT_CHARTREUSE = 0x29
LIGHT_GREEN = 0x2A
LIGHT_MINT = 0x2B
LIGHT_CYAN = 0x2C
DARK_GRAY = 0x2D
BLACK6 = 0x2E
BLACK7 = 0x2F

WHITE2 = 0x30
PALE_BLUE = 0x31
PALE_INDIGO = 0x32
PALE_VIOLET = 0x33
PALE_MAGENTA = 0x34
PALE_RED = 0x35
PALE_ORANGE = 0x36
CREAM = 0x37
YELLOW = 0x38
PALE_CHARTREUSE = 0x39
PALE_GREEN = 0x3A
PALE_MINT = 0x3B
PALE_CYAN = 0x3C
PALE_GRAY = 0x3D
BLACK8 = 0x3E
BLACK9 = 0x3F

PreRead = 0
PostRead = 1
PreWrite = 2
PostWrite = 3
PreExecute = 4
PostExecute = 5

_Activate = 1
_Deactivate = 3
_Stop = 5
_Access = 9
_Controllers = 11
_Frame = 13
_Scanline = 15
_ScanlineCycle = 17
_SpriteZero = 19
_Status = 21

_EVENT_TYPES = [ _Activate, _Deactivate, _Stop, _Access, _Controllers,
    _Frame, _Scanline, _ScanlineCycle, _SpriteZero, _Status ]

_EVENT_REQUEST = 0xFF
_EVENT_RESPONSE = 0xFE
_HEARTBEAT = 0xFD
_READY = 0xFC
_RETRY_SECONDS = 1

_BLOCK_SIZE = 4096
_ARRAY_LENGTH = 1024

_host = None
_port = -1
_remoteAPI = None

def _isNotBlank(s):
  return s and s.strip()

# First part of API retrieval, sets global host and  port values
def initRemoteAPI(host, port):
  global _host
  global _port
  _host = host
  _port = port

# Second part of API retrieval. Creates new remote API object and returns it
def getAPI():
  global _remoteAPI
  if _remoteAPI == None and _isNotBlank(_host):
    _remoteAPI = _RemoteAPI(_host, _port)
  return _remoteAPI

class _AccessPoint(object):

  def __init__(self, listener, accessPointType, minAddress, maxAddress = -1,
      bank = -1):
    self.listener = listener;
    self.accessPointType = accessPointType;
    self.bank = bank;

    if maxAddress < 0:
      self.minAddress = self.maxAddress = minAddress
    elif minAddress <= maxAddress:
      self.minAddress = minAddress
      self.maxAddress = maxAddress
    else:
      self.minAddress = maxAddress
      self.maxAddress = minAddress

class _ScanlineCyclePoint(object):

  def __init__(self, listener, scanline, scanlineCycle):
    self.listener = listener
    self.scanline = scanline
    self.scanlineCycle = scanlineCycle

class _ScanlinePoint(object):

  def __init__(self, listener, scanline):
    self.listener = listener
    self.scanline = scanline

'''
_DataStream class
'''
class _DataStream(object):

  def __init__(self, sock):
    self._readBuffer = bytearray()
    self._writeBuffer = bytearray()
    self._sock = sock

  def _close(self):
    self._sock.shutdown()
    self._sock.close()

  '''
  While the readBuffer is strictly smaller than the passed count
  Get a 4096 block from sock
  throw IO error if no block
  extend the _readBuffer by block
  '''
  def _fillReadBuffer(self, count):
    while len(self._readBuffer) < count:
      block = self._sock.recv(_BLOCK_SIZE) # 4096
      if len(block) == 0:
        raise IOError("Disconnected.")
      self._readBuffer.extend(block)

  def _read(self):
    # reads first byte in _readBuffer
    return self._readBuffer.pop(0)

  def writeByte(self, value):
    # TODO: what does this operation mean?
    self._writeBuffer.append(value & 0xFF)

  def readByte(self):
    self._fillReadBuffer(1)
    return self._read()

  def writeInt(self, value):
    # same
    self.writeByte(value >> 24)
    self.writeByte(value >> 16)
    self.writeByte(value >> 8)
    self.writeByte(value)

  def readInt(self):
    self._fillReadBuffer(4)
    value = self._read() << 24
    value |= self._read() << 16
    value |= self._read() << 8
    value |= self._read()
    return value

  def writeIntArray(self, array):
    self.writeInt(len(array))
    for i in range(len(array)):
      self.writeInt(array[i])

  def readIntArray(self, array):
    length = self.readInt()
    if length < 0 or length > len(array):
      self._close()
      raise IOError("Invalid array length: %d" % length)
    for i in range(length):
      array[i] = self.readInt()
    return length

  def writeBoolean(self, value):
    self.writeByte(1 if value else 0)

  def readBoolean(self):
    return self.readByte() != 0

  def writeChar(self, value):
    self.writeByte(ord(value[0]))

  def readChar(self):
    return chr(self.readByte())

  def writeCharArray(self, array):
    self.writeString(array)

  def readCharArray(array):
    length = self.readInt()
    if length < 0 or length > len(array):
      self._close()
      raise IOError("Invalid array length: %d" % length)
    for i in range(length):
      array[i] = self.readChar()
    return length

  def writeString(self, value):
    self.writeInt(len(value))
    for i in range(len(value)):
      self.writeByte(ord(value[i]))

  def readString(self):
    length = self.readInt()
    if length < 0 or length > _ARRAY_LENGTH:
      self._close()
      raise IOError("Invalid array length: %d" % length)
    cs = bytearray()
    for i in range(length):
      cs.append(self.readByte())
    return str(cs)

  def writeStringArray(self, array):
    self.writeInt(len(array))
    for i in range(len(array)):
      self.writeString(array[i])

  def readStringArray(self, array):
    length = self.readInt()
    if length < 0 or length > len(array):
      self._close()
      raise IOError("Invalid array length: %d" % length)
    for i in range(length):
      array[i] = self.readString()
    return length

  def readDynamicStringArray(self):
    length = self.readInt()
    if length < 0 or length > _ARRAY_LENGTH:
      self._close()
      raise IOError("Invalid array length: %d" % length)
    array = []
    for i in range(length):
      array.append(self.readString())
    return array

  # Name a bit misleading. flush sends to socket from writebuffer and clears writebuffer
  def flush(self):
    # appears that a bytearray can be manipulated as a string. interesting
    self._sock.sendall(self._writeBuffer)
    # Notation clears _writeBuffer bytearray without deleting it, enabling future use
    del self._writeBuffer[:]

class _RemoteBase(object):

  def __init__(self, host, port):
    self._host = host
    self._port = port
    self._stream = None
    self._nextID = 0
    self._listenerIDs = {}
    self._running = False

    # eventType -> listenerID -> listenerObject(listener)
    self._listenerObjects = { eventType : {} for eventType in _EVENT_TYPES }

  def run(self):
    # If running flag is on, cancel. If off, turn running flag on
    if self._running:
      return
    else:
      self._running = True

    while True:
      self._fireStatusChanged("Connecting to %s:%d..."
          % (self._host, self._port))
      sock = None
      try:
          # to establish a connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._host, self._port))
        self._stream = _DataStream(sock)
      except:
        self._fireStatusChanged("Failed to establish connection.")
      if self._stream != None:
        try:
          self._fireStatusChanged("Connection established.")
          self._sendListeners()
          self._sendReady()
          while True:
            self._probeEvents()
        except IOError:
          self._fireDeactivated()
          self._fireStatusChanged("Disconnected.")
        except:
          ex_type, ex_value, ex_traceback = sys.exc_info()
          trace_back = traceback.extract_tb(ex_traceback)
          print("%s: %s" % (ex_type.__name__, ex_value))
          for trace in trace_back:
            print("  File \"%s\", line %d, in %s"
                % (trace[0], trace[1], trace[2]))
            print("    %s" % trace[3])
          self._fireDeactivated()
          self._fireStatusChanged("Disconnected.")
        finally:
          self._stream = None
      time.sleep(_RETRY_SECONDS)

  def _fireDeactivated(self):
    for listenerID, listener in copy.copy(self._listenerObjects[_Deactivate]
        .items()):
      listener()

 # uncertain of what message does. fires listener
  def _fireStatusChanged(self, message):
    for listenerID, listener in copy.copy(self._listenerObjects[_Status]
        .items()):
      listener(message)

  def _sendReady(self):
    if self._stream != None:
      try:
        self._stream.writeByte(_READY)
        self._stream.flush()
      except:
        pass

  def _sendListeners(self):
    for eventType, listObjs in self._listenerObjects.items():
      for listenerID, listenerObject in listObjs.items():
        self._sendListener(listenerID, eventType, listenerObject)

  def _probeEvents(self):
    # make event request _EVENT_REQUEST = 0xFF
    self._stream.writeByte(_EVENT_REQUEST)
    self._stream.flush()

    eventType = self._stream.readByte()

    # Heartbeat if event type was a heartbeat
    if eventType == _HEARTBEAT:
      self._stream.writeByte(_EVENT_RESPONSE) #0xFE
      self._stream.flush()
      return

    # get listener object from the stream
    listenerID = self._stream.readInt()
    obj = self._listenerObjects[eventType].get(listenerID, None)

    if obj != None:
      # weird design here
      if eventType == _Access:
        accessPointType = self._stream.readInt()
        address = self._stream.readInt()
        value = self._stream.readInt()
        result = obj.listener(accessPointType, address, value)
        self._stream.writeByte(_EVENT_RESPONSE)
        self._stream.writeInt(result)
      else:
        if (   eventType == _Activate
            or eventType == _Deactivate
            or eventType == _Stop
            or eventType == _Controllers
            or eventType == _Frame):
          # uncertain of role that obj and listener play, but imagine that they are relevant
          obj()
        elif eventType == _Scanline:
          obj.listener(self._stream.readInt())
        elif eventType == _ScanlineCycle:
          obj.listener(self._stream.readInt(), self._stream.readInt(),
              self._stream.readInt(), self._stream.readBoolean())
        elif eventType == _SpriteZero:
          obj.listener(self._stream.readInt(), self._stream.readInt())
        elif eventType == _Status:
          obj.listener(self._stream.readString())
        else:
          raise IOError("Unknown listener type: %d" % eventType)

        self._stream.writeByte(_EVENT_RESPONSE)

    self._stream.flush()

  def _sendListener(self, listenerID, eventType, listenerObject):
    if self._stream != None:
      try:
        # TODO: What exactly are the listener objects? are they relevant?
        self._stream.writeByte(eventType)
        self._stream.writeInt(listenerID)
        if eventType == _Access:
          self._stream.writeInt(listenerObject.accessPointType)
          self._stream.writeInt(listenerObject.minAddress)
          self._stream.writeInt(listenerObject.maxAddress)
          self._stream.writeInt(listenerObject.bank)
        elif eventType == _Scanline:
          self._stream.writeInt(listenerObject.scanline)
        elif eventType == _ScanlineCycle:
          self._stream.writeInt(listenerObject.scanline)
          self._stream.writeInt(listenerObject.scanlineCycle)
        self._stream.flush()
      except:
        pass

  def _addListener(self, listener, eventType):
    if listener != None:
      self._sendListener(self._addListenerObject(listener, eventType),
          eventType, listener)

  def _removeListener(self, listener, eventType, methodValue):
    if listener != None:
      listenerID = self._removeListenerObject(listener, eventType)
      if listenerID >= 0 and self._stream != None:
        try:
          self._stream.writeByte(methodValue)
          self._stream.writeInt(listenerID)
          self._stream.flush()
        except:
          pass

  def _addListenerObject(self, listener, eventType, listenerObject = None):
    if listenerObject == None:
      listenerObject = listener
    listenerID = self._nextID
    self._nextID += 1
    self._listenerIDs[listener] = listenerID
    self._listenerObjects[eventType][listenerID] = listenerObject
    return listenerID

  def _removeListenerObject(self, listener, eventType):
    listenerID = self._listenerIDs.pop(listener, None)
    if listenerID != None:
      self._listenerObjects[eventType].pop(listenerID)
      return listenerID
    else:
      return -1

  def addActivateListener(self, listener):
    self._addListener(listener, _Activate)

  def removeActivateListener(self, listener):
    self._removeListener(listener, _Activate, 2)

  def addDeactivateListener(self, listener):
    self._addListener(listener, _Deactivate)

  def removeDeactivateListener(self, listener):
    self._removeListener(listener, _Deactivate, 4)

  def addStopListener(self, listener):
    self._addListener(listener, _Stop)

  def removeStopListener(self, listener):
    self._removeListener(listener, _Stop, 6)

  def addAccessPointListener(self, listener, accessPointType, minAddress,
      maxAddress = -1, bank = -1):
    if listener != None:
      point = _AccessPoint(listener, accessPointType, minAddress, maxAddress,
          bank)
      self._sendListener(self._addListenerObject(listener, _Access, point),
          _Access, point)

  def removeAccessPointListener(self, listener):
    self._removeListener(listener, _Access, 10)

  def addControllersListener(self, listener):
    self._addListener(listener, _Controllers)

  def removeControllersListener(self, listener):
    self._removeListener(listener, _Controllers, 12)

  def addFrameListener(self, listener):
    self._addListener(listener, _Frame)

  def removeFrameListener(self, listener):
    self._removeListener(listener, _Frame, 14)

  def addScanlineListener(self, listener, scanline):
    if listener != None:
      point = _ScanlinePoint(listener, scanline)
      self._sendListener(self._addListenerObject(listener, _Scanline, point),
          _Scanline, point)

  def removeScanlineListener(self, listener):
    self._removeListener(listener, _Scanline, 16)

  def addScanlineCycleListener(self, listener, scanline, scanlineCycle):
    if listener != None:
      point = _ScanlineCyclePoint(listener, scanline, scanlineCycle)
      self._sendListener(self._addListenerObject(listener, _ScanlineCycle,
          point), _ScanlineCycle, point)

  def removeScanlineCycleListener(self, listener):
    self._removeListener(listener, _ScanlineCycle, 18)

  def addSpriteZeroListener(self, listener):
    self._addListener(listener, _SpriteZero)

  def removeSpriteZeroListener(self, listener):
    self._removeListener(listener, _SpriteZero, 20)

  def addStatusListener(self, listener):
    self._addListener(listener, _Status)

  def removeStatusListener(self, listener):
    self._removeListener(listener, _Status, 22)

# holdover from the java methodology. You need to pass it an array instantiated with 256*240 empty locations in it
  def getPixels(self, pixels):
    try:
      self._stream.writeByte(119)
      self._stream.flush()
      self._stream.readIntArray(pixels)
    except:
      pass

# THIS IS AN AUTOGENERATED CLASS. DO NOT MODIFY.
class _RemoteAPI(_RemoteBase):

  def __init__(self, host, port):
    _RemoteBase.__init__(self, host, port)

  def setPaused(self, paused):
    try:
      self._stream.writeByte(23)
      self._stream.writeBoolean(paused)
      self._stream.flush()
    except:
      pass

  def isPaused(self):
    try:
      self._stream.writeByte(24)
      self._stream.flush()
      return self._stream.readBoolean()
    except:
      pass
    return false

  def getFrameCount(self):
    try:
      self._stream.writeByte(25)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def getA(self):
    try:
      self._stream.writeByte(26)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setA(self, A):
    try:
      self._stream.writeByte(27)
      self._stream.writeInt(A)
      self._stream.flush()
    except:
      pass

  def getS(self):
    try:
      self._stream.writeByte(28)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setS(self, S):
    try:
      self._stream.writeByte(29)
      self._stream.writeInt(S)
      self._stream.flush()
    except:
      pass

  def getPC(self):
    try:
      self._stream.writeByte(30)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setPC(self, PC):
    try:
      self._stream.writeByte(31)
      self._stream.writeInt(PC)
      self._stream.flush()
    except:
      pass

  def getX(self):
    try:
      self._stream.writeByte(32)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setX(self, X):
    try:
      self._stream.writeByte(33)
      self._stream.writeInt(X)
      self._stream.flush()
    except:
      pass

  def getY(self):
    try:
      self._stream.writeByte(34)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setY(self, Y):
    try:
      self._stream.writeByte(35)
      self._stream.writeInt(Y)
      self._stream.flush()
    except:
      pass

  def getP(self):
    try:
      self._stream.writeByte(36)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setP(self, P):
    try:
      self._stream.writeByte(37)
      self._stream.writeInt(P)
      self._stream.flush()
    except:
      pass

  def isN(self):
    try:
      self._stream.writeByte(38)
      self._stream.flush()
      return self._stream.readBoolean()
    except:
      pass
    return false

  def setN(self, N):
    try:
      self._stream.writeByte(39)
      self._stream.writeBoolean(N)
      self._stream.flush()
    except:
      pass

  def isV(self):
    try:
      self._stream.writeByte(40)
      self._stream.flush()
      return self._stream.readBoolean()
    except:
      pass
    return false

  def setV(self, V):
    try:
      self._stream.writeByte(41)
      self._stream.writeBoolean(V)
      self._stream.flush()
    except:
      pass

  def isD(self):
    try:
      self._stream.writeByte(42)
      self._stream.flush()
      return self._stream.readBoolean()
    except:
      pass
    return false

  def setD(self, D):
    try:
      self._stream.writeByte(43)
      self._stream.writeBoolean(D)
      self._stream.flush()
    except:
      pass

  def isI(self):
    try:
      self._stream.writeByte(44)
      self._stream.flush()
      return self._stream.readBoolean()
    except:
      pass
    return false

  def setI(self, I):
    try:
      self._stream.writeByte(45)
      self._stream.writeBoolean(I)
      self._stream.flush()
    except:
      pass

  def isZ(self):
    try:
      self._stream.writeByte(46)
      self._stream.flush()
      return self._stream.readBoolean()
    except:
      pass
    return false

  def setZ(self, Z):
    try:
      self._stream.writeByte(47)
      self._stream.writeBoolean(Z)
      self._stream.flush()
    except:
      pass

  def isC(self):
    try:
      self._stream.writeByte(48)
      self._stream.flush()
      return self._stream.readBoolean()
    except:
      pass
    return false

  def setC(self, C):
    try:
      self._stream.writeByte(49)
      self._stream.writeBoolean(C)
      self._stream.flush()
    except:
      pass

  def getPPUv(self):
    try:
      self._stream.writeByte(50)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setPPUv(self, v):
    try:
      self._stream.writeByte(51)
      self._stream.writeInt(v)
      self._stream.flush()
    except:
      pass

  def getPPUt(self):
    try:
      self._stream.writeByte(52)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setPPUt(self, t):
    try:
      self._stream.writeByte(53)
      self._stream.writeInt(t)
      self._stream.flush()
    except:
      pass

  def getPPUx(self):
    try:
      self._stream.writeByte(54)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setPPUx(self, x):
    try:
      self._stream.writeByte(55)
      self._stream.writeInt(x)
      self._stream.flush()
    except:
      pass

  def isPPUw(self):
    try:
      self._stream.writeByte(56)
      self._stream.flush()
      return self._stream.readBoolean()
    except:
      pass
    return false

  def setPPUw(self, w):
    try:
      self._stream.writeByte(57)
      self._stream.writeBoolean(w)
      self._stream.flush()
    except:
      pass

  def getCameraX(self):
    try:
      self._stream.writeByte(58)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setCameraX(self, scrollX):
    try:
      self._stream.writeByte(59)
      self._stream.writeInt(scrollX)
      self._stream.flush()
    except:
      pass

  def getCameraY(self):
    try:
      self._stream.writeByte(60)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setCameraY(self, scrollY):
    try:
      self._stream.writeByte(61)
      self._stream.writeInt(scrollY)
      self._stream.flush()
    except:
      pass

  def getScanline(self):
    try:
      self._stream.writeByte(62)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def getDot(self):
    try:
      self._stream.writeByte(63)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def isSpriteZeroHit(self):
    try:
      self._stream.writeByte(64)
      self._stream.flush()
      return self._stream.readBoolean()
    except:
      pass
    return false

  def setSpriteZeroHit(self, sprite0Hit):
    try:
      self._stream.writeByte(65)
      self._stream.writeBoolean(sprite0Hit)
      self._stream.flush()
    except:
      pass

  def getScanlineCount(self):
    try:
      self._stream.writeByte(66)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def requestInterrupt(self):
    try:
      self._stream.writeByte(67)
      self._stream.flush()
    except:
      pass

  def acknowledgeInterrupt(self):
    try:
      self._stream.writeByte(68)
      self._stream.flush()
    except:
      pass

  def peekCPU(self, address):
    try:
      self._stream.writeByte(69)
      self._stream.writeInt(address)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def readCPU(self, address):
    try:
      self._stream.writeByte(70)
      self._stream.writeInt(address)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def writeCPU(self, address, value):
    try:
      self._stream.writeByte(71)
      self._stream.writeInt(address)
      self._stream.writeInt(value)
      self._stream.flush()
    except:
      pass

  def peekCPU16(self, address):
    try:
      self._stream.writeByte(72)
      self._stream.writeInt(address)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def readCPU16(self, address):
    try:
      self._stream.writeByte(73)
      self._stream.writeInt(address)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def writeCPU16(self, address, value):
    try:
      self._stream.writeByte(74)
      self._stream.writeInt(address)
      self._stream.writeInt(value)
      self._stream.flush()
    except:
      pass

  def peekCPU32(self, address):
    try:
      self._stream.writeByte(75)
      self._stream.writeInt(address)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def readCPU32(self, address):
    try:
      self._stream.writeByte(76)
      self._stream.writeInt(address)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def writeCPU32(self, address, value):
    try:
      self._stream.writeByte(77)
      self._stream.writeInt(address)
      self._stream.writeInt(value)
      self._stream.flush()
    except:
      pass

  def readPPU(self, address):
    try:
      self._stream.writeByte(78)
      self._stream.writeInt(address)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def writePPU(self, address, value):
    try:
      self._stream.writeByte(79)
      self._stream.writeInt(address)
      self._stream.writeInt(value)
      self._stream.flush()
    except:
      pass

  def readPaletteRAM(self, address):
    try:
      self._stream.writeByte(80)
      self._stream.writeInt(address)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def writePaletteRAM(self, address, value):
    try:
      self._stream.writeByte(81)
      self._stream.writeInt(address)
      self._stream.writeInt(value)
      self._stream.flush()
    except:
      pass

  def readOAM(self, address):
    try:
      self._stream.writeByte(82)
      self._stream.writeInt(address)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def writeOAM(self, address, value):
    try:
      self._stream.writeByte(83)
      self._stream.writeInt(address)
      self._stream.writeInt(value)
      self._stream.flush()
    except:
      pass

  def readGamepad(self, gamepad, button):
    try:
      self._stream.writeByte(84)
      self._stream.writeInt(gamepad)
      self._stream.writeInt(button)
      self._stream.flush()
      return self._stream.readBoolean()
    except:
      pass
    return false

  def writeGamepad(self, gamepad, button, value):
    try:
      self._stream.writeByte(85)
      self._stream.writeInt(gamepad)
      self._stream.writeInt(button)
      self._stream.writeBoolean(value)
      self._stream.flush()
    except:
      pass

  def isZapperTrigger(self):
    try:
      self._stream.writeByte(86)
      self._stream.flush()
      return self._stream.readBoolean()
    except:
      pass
    return false

  def setZapperTrigger(self, zapperTrigger):
    try:
      self._stream.writeByte(87)
      self._stream.writeBoolean(zapperTrigger)
      self._stream.flush()
    except:
      pass

  def getZapperX(self):
    try:
      self._stream.writeByte(88)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setZapperX(self, x):
    try:
      self._stream.writeByte(89)
      self._stream.writeInt(x)
      self._stream.flush()
    except:
      pass

  def getZapperY(self):
    try:
      self._stream.writeByte(90)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setZapperY(self, y):
    try:
      self._stream.writeByte(91)
      self._stream.writeInt(y)
      self._stream.flush()
    except:
      pass

  def setColor(self, color):
    try:
      self._stream.writeByte(92)
      self._stream.writeInt(color)
      self._stream.flush()
    except:
      pass

  def getColor(self):
    try:
      self._stream.writeByte(93)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def setClip(self, x, y, width, height):
    try:
      self._stream.writeByte(94)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.flush()
    except:
      pass

  def clipRect(self, x, y, width, height):
    try:
      self._stream.writeByte(95)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.flush()
    except:
      pass

  def resetClip(self):
    try:
      self._stream.writeByte(96)
      self._stream.flush()
    except:
      pass

  def copyArea(self, x, y, width, height, dx, dy):
    try:
      self._stream.writeByte(97)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.writeInt(dx)
      self._stream.writeInt(dy)
      self._stream.flush()
    except:
      pass

  def drawLine(self, x1, y1, x2, y2):
    try:
      self._stream.writeByte(98)
      self._stream.writeInt(x1)
      self._stream.writeInt(y1)
      self._stream.writeInt(x2)
      self._stream.writeInt(y2)
      self._stream.flush()
    except:
      pass

  def drawOval(self, x, y, width, height):
    try:
      self._stream.writeByte(99)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.flush()
    except:
      pass

  def drawPolygon(self, xPoints, yPoints, nPoints):
    try:
      self._stream.writeByte(100)
      self._stream.writeIntArray(xPoints)
      self._stream.writeIntArray(yPoints)
      self._stream.writeInt(nPoints)
      self._stream.flush()
    except:
      pass

  def drawPolyline(self, xPoints, yPoints, nPoints):
    try:
      self._stream.writeByte(101)
      self._stream.writeIntArray(xPoints)
      self._stream.writeIntArray(yPoints)
      self._stream.writeInt(nPoints)
      self._stream.flush()
    except:
      pass

  def drawRect(self, x, y, width, height):
    try:
      self._stream.writeByte(102)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.flush()
    except:
      pass

  def drawRoundRect(self, x, y, width, height, arcWidth, arcHeight):
    try:
      self._stream.writeByte(103)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.writeInt(arcWidth)
      self._stream.writeInt(arcHeight)
      self._stream.flush()
    except:
      pass

  def draw3DRect(self, x, y, width, height, raised):
    try:
      self._stream.writeByte(104)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.writeBoolean(raised)
      self._stream.flush()
    except:
      pass

  def drawArc(self, x, y, width, height, startAngle, arcAngle):
    try:
      self._stream.writeByte(105)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.writeInt(startAngle)
      self._stream.writeInt(arcAngle)
      self._stream.flush()
    except:
      pass

  def fill3DRect(self, x, y, width, height, raised):
    try:
      self._stream.writeByte(106)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.writeBoolean(raised)
      self._stream.flush()
    except:
      pass

  def fillArc(self, x, y, width, height, startAngle, arcAngle):
    try:
      self._stream.writeByte(107)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.writeInt(startAngle)
      self._stream.writeInt(arcAngle)
      self._stream.flush()
    except:
      pass

  def fillOval(self, x, y, width, height):
    try:
      self._stream.writeByte(108)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.flush()
    except:
      pass

  def fillPolygon(self, xPoints, yPoints, nPoints):
    try:
      self._stream.writeByte(109)
      self._stream.writeIntArray(xPoints)
      self._stream.writeIntArray(yPoints)
      self._stream.writeInt(nPoints)
      self._stream.flush()
    except:
      pass

  def fillRect(self, x, y, width, height):
    try:
      self._stream.writeByte(110)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.flush()
    except:
      pass

  def fillRoundRect(self, x, y, width, height, arcWidth, arcHeight):
    try:
      self._stream.writeByte(111)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.writeInt(arcWidth)
      self._stream.writeInt(arcHeight)
      self._stream.flush()
    except:
      pass

  def drawChar(self, c, x, y):
    try:
      self._stream.writeByte(112)
      self._stream.writeChar(c)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.flush()
    except:
      pass

  def drawChars(self, data, offset, length, x, y, monospaced):
    try:
      self._stream.writeByte(113)
      self._stream.writeCharArray(data)
      self._stream.writeInt(offset)
      self._stream.writeInt(length)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeBoolean(monospaced)
      self._stream.flush()
    except:
      pass

  def drawString(self, str, x, y, monospaced):
    try:
      self._stream.writeByte(114)
      self._stream.writeString(str)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeBoolean(monospaced)
      self._stream.flush()
    except:
      pass

  def createSprite(self, id, width, height, pixels):
    try:
      self._stream.writeByte(115)
      self._stream.writeInt(id)
      self._stream.writeInt(width)
      self._stream.writeInt(height)
      self._stream.writeIntArray(pixels)
      self._stream.flush()
    except:
      pass

  def drawSprite(self, id, x, y):
    try:
      self._stream.writeByte(116)
      self._stream.writeInt(id)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.flush()
    except:
      pass

  def setPixel(self, x, y, color):
    try:
      self._stream.writeByte(117)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.writeInt(color)
      self._stream.flush()
    except:
      pass

  def getPixel(self, x, y):
    try:
      self._stream.writeByte(118)
      self._stream.writeInt(x)
      self._stream.writeInt(y)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def powerCycle(self):
    try:
      self._stream.writeByte(120)
      self._stream.flush()
    except:
      pass

  def reset(self):
    try:
      self._stream.writeByte(121)
      self._stream.flush()
    except:
      pass

  def deleteSprite(self, id):
    try:
      self._stream.writeByte(122)
      self._stream.writeInt(id)
      self._stream.flush()
    except:
      pass

  def setSpeed(self, percent):
    try:
      self._stream.writeByte(123)
      self._stream.writeInt(percent)
      self._stream.flush()
    except:
      pass

  def stepToNextFrame(self):
    try:
      self._stream.writeByte(124)
      self._stream.flush()
    except:
      pass

  def showMessage(self, message):
    try:
      self._stream.writeByte(125)
      self._stream.writeString(message)
      self._stream.flush()
    except:
      pass

  def getWorkingDirectory(self):
    try:
      self._stream.writeByte(126)
      self._stream.flush()
      return self._stream.readString()
    except:
      pass
    return null

  def getContentDirectory(self):
    try:
      self._stream.writeByte(127)
      self._stream.flush()
      return self._stream.readString()
    except:
      pass
    return null

  def open(self, fileName):
    try:
      self._stream.writeByte(128)
      self._stream.writeString(fileName)
      self._stream.flush()
    except:
      pass

  def openArchiveEntry(self, archiveFileName, entryFileName):
    try:
      self._stream.writeByte(129)
      self._stream.writeString(archiveFileName)
      self._stream.writeString(entryFileName)
      self._stream.flush()
    except:
      pass

  def getArchiveEntries(self, archiveFileName):
    try:
      self._stream.writeByte(130)
      self._stream.writeString(archiveFileName)
      self._stream.flush()
      return self._stream.readDynamicStringArray()
    except:
      pass
    return null

  def getDefaultArchiveEntry(self, archiveFileName):
    try:
      self._stream.writeByte(131)
      self._stream.writeString(archiveFileName)
      self._stream.flush()
      return self._stream.readString()
    except:
      pass
    return null

  def openDefaultArchiveEntry(self, archiveFileName):
    try:
      self._stream.writeByte(132)
      self._stream.writeString(archiveFileName)
      self._stream.flush()
    except:
      pass

  def close(self):
    try:
      self._stream.writeByte(133)
      self._stream.flush()
    except:
      pass

  def saveState(self, stateFileName):
    try:
      self._stream.writeByte(134)
      self._stream.writeString(stateFileName)
      self._stream.flush()
    except:
      pass

  def loadState(self, stateFileName):
    try:
      self._stream.writeByte(135)
      self._stream.writeString(stateFileName)
      self._stream.flush()
    except:
      pass

  def quickSaveState(self, slot):
    try:
      self._stream.writeByte(136)
      self._stream.writeInt(slot)
      self._stream.flush()
    except:
      pass

  def quickLoadState(self, slot):
    try:
      self._stream.writeByte(137)
      self._stream.writeInt(slot)
      self._stream.flush()
    except:
      pass

  def setTVSystem(self, tvSystem):
    try:
      self._stream.writeByte(138)
      self._stream.writeString(tvSystem)
      self._stream.flush()
    except:
      pass

  def getTVSystem(self):
    try:
      self._stream.writeByte(139)
      self._stream.flush()
      return self._stream.readString()
    except:
      pass
    return null

  def getDiskSides(self):
    try:
      self._stream.writeByte(140)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def insertDisk(self, disk, side):
    try:
      self._stream.writeByte(141)
      self._stream.writeInt(disk)
      self._stream.writeInt(side)
      self._stream.flush()
    except:
      pass

  def flipDiskSide(self):
    try:
      self._stream.writeByte(142)
      self._stream.flush()
    except:
      pass

  def ejectDisk(self):
    try:
      self._stream.writeByte(143)
      self._stream.flush()
    except:
      pass

  def insertCoin(self):
    try:
      self._stream.writeByte(144)
      self._stream.flush()
    except:
      pass

  def pressServiceButton(self):
    try:
      self._stream.writeByte(145)
      self._stream.flush()
    except:
      pass

  def screamIntoMicrophone(self):
    try:
      self._stream.writeByte(146)
      self._stream.flush()
    except:
      pass

  def glitch(self):
    try:
      self._stream.writeByte(147)
      self._stream.flush()
    except:
      pass

  def getFileInfo(self):
    try:
      self._stream.writeByte(148)
      self._stream.flush()
      return self._stream.readString()
    except:
      pass
    return null

  def setFullscreenMode(self, fullscreenMode):
    try:
      self._stream.writeByte(149)
      self._stream.writeBoolean(fullscreenMode)
      self._stream.flush()
    except:
      pass

  def saveScreenshot(self):
    try:
      self._stream.writeByte(150)
      self._stream.flush()
    except:
      pass

  def addCheat(self, address, value, compare, description, enabled):
    try:
      self._stream.writeByte(151)
      self._stream.writeInt(address)
      self._stream.writeInt(value)
      self._stream.writeInt(compare)
      self._stream.writeString(description)
      self._stream.writeBoolean(enabled)
      self._stream.flush()
    except:
      pass

  def removeCheat(self, address, value, compare):
    try:
      self._stream.writeByte(152)
      self._stream.writeInt(address)
      self._stream.writeInt(value)
      self._stream.writeInt(compare)
      self._stream.flush()
    except:
      pass

  def addGameGenie(self, gameGenieCode, description, enabled):
    try:
      self._stream.writeByte(153)
      self._stream.writeString(gameGenieCode)
      self._stream.writeString(description)
      self._stream.writeBoolean(enabled)
      self._stream.flush()
    except:
      pass

  def removeGameGenie(self, gameGenieCode):
    try:
      self._stream.writeByte(154)
      self._stream.writeString(gameGenieCode)
      self._stream.flush()
    except:
      pass

  def addProActionRocky(self, proActionRockyCode, description, enabled):
    try:
      self._stream.writeByte(155)
      self._stream.writeString(proActionRockyCode)
      self._stream.writeString(description)
      self._stream.writeBoolean(enabled)
      self._stream.flush()
    except:
      pass

  def removeProActionRocky(self, proActionRockyCode):
    try:
      self._stream.writeByte(156)
      self._stream.writeString(proActionRockyCode)
      self._stream.flush()
    except:
      pass

  def getPrgRomSize(self):
    try:
      self._stream.writeByte(157)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def readPrgRom(self, index):
    try:
      self._stream.writeByte(158)
      self._stream.writeInt(index)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def writePrgRom(self, index, value):
    try:
      self._stream.writeByte(159)
      self._stream.writeInt(index)
      self._stream.writeInt(value)
      self._stream.flush()
    except:
      pass

  def getChrRomSize(self):
    try:
      self._stream.writeByte(160)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def readChrRom(self, index):
    try:
      self._stream.writeByte(161)
      self._stream.writeInt(index)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def writeChrRom(self, index, value):
    try:
      self._stream.writeByte(162)
      self._stream.writeInt(index)
      self._stream.writeInt(value)
      self._stream.flush()
    except:
      pass

  def getStringWidth(self, str, monospaced):
    try:
      self._stream.writeByte(163)
      self._stream.writeString(str)
      self._stream.writeBoolean(monospaced)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1

  def getCharsWidth(self, chars, monospaced):
    try:
      self._stream.writeByte(164)
      self._stream.writeCharArray(chars)
      self._stream.writeBoolean(monospaced)
      self._stream.flush()
      return self._stream.readInt()
    except:
      pass
    return -1
