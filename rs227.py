import struct
import sys

START_CODE = 0xff
CARRIAGE_RETURN = 0x8d
LINE_FEED = 0x8a

class RS227():
	def __init__(self,file, feeder_code=b"\xff", trailer_code=b"\x00"):
		self.filename = file
		
		self.fp = None
		self.feeder_code = feeder_code
		self.trailer_code = trailer_code
		
	def _read_tape_leader(self):
		a = 0x00
		while a != CARRIAGE_RETURN:
			a = ord(self.fp.read(1))

		if ord(self.fp.read(1)) != LINE_FEED:
			raise ValueError
			
	def _read_tape_code(self):
		return ord(self.fp.read(1))

	def _read_tape_frame(self):
		check = 0
		check2 = 0
		error = False
		frame = []
		try:
			rawbytes = self.fp.read(108)
			rawframe = struct.unpack("108B",rawbytes)
			frame = [rawframe[i] << 16 | rawframe[i + 1] << 8 | rawframe[i + 2] for i in range(0, len(rawframe), 3)]
			x = self.fp.read(2)
			check = struct.unpack(">h",x)[0]
			crlf = struct.unpack("BB",self.fp.read(2))
			check2 = self._crc(struct.unpack(">54H",rawbytes))
		except:
			error = True
			
		return (check,check2,frame,error)

	def read_contents(self, ignore_errors=False):
		self.fp = open(self.filename,"rb")
		self._read_tape_leader()
		tc = self._read_tape_code()

		full_tape = []
		
		while tc in [START_CODE, 0x00]:
			(check, check2, frame,error) = self._read_tape_frame()
			if ignore_errors != True:
				if check == check2:
					print("check",check,"check2",check2)
					raise ValueError
			full_tape = full_tape + frame
			if error:
				return full_tape
			tc = self._read_tape_code()
#			print(full_tape)
		self.close()
		
		return full_tape

	def _crc(self,contents): # takes a list of shorts
		check = 0x0000
		for i in contents:
			check = (check + i)  & 0xffff
		return struct.unpack(">h",struct.pack(">H",check))[0] * -1

	def write_contents(self, contents,  leader_len=20, trailer_len=20):
		self.fp = open(self.filename,"wb")

		#fixme
		for i in range(leader_len):
			self.fp.write(self.feeder_code)
			
		for i in range(0,len(contents),108):
			self.fp.write(b"\xff");
			self.fp.write(b"\x8d\x8a");
			self.fp.write(contents[i:i+108])
			crc = self._crc(struct.unpack(">%dH" % (len(contents[i:i+108])/2),contents[i:i+108]))
			self.fp.write(struct.pack(">H",crc))
			
		for i in range(trailer_len):
			self.fp.write(self.trailer_code)

		self.close()
		
	def close(self):
		self.fp.close()


if __name__ == '__main__':
	tape = RS227(sys.argv[1])
	print (tape.read_contents())
