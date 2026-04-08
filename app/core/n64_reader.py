from enum import Enum, auto


class ReaderMode(Enum):
    ''' Defines the byte order (endianness) for reading ROM data. '''
    BigEndian = auto()
    LittleEndian = auto()
    ByteswappedBig = auto()
    ByteswappedLittle = auto()


class BinaryReader:
    ''' Reads Nintendo 64 ROM binary data from a buffer, handling various Nintendo 64 ROM byte orders. '''
    def __init__(self, buffer, *, mode: ReaderMode):
        self._buffer = buffer
        self.mode = mode

    def _normalize_word(self, b: bytes) -> bytes:
        ''' Normalizes a 4-byte word from the buffer's byte order to big endian. '''
        b = b.ljust(4, b'\x00')

        match self.mode:
            case ReaderMode.BigEndian:
                return b
            case ReaderMode.LittleEndian:
                return b[::-1]
            case ReaderMode.ByteswappedBig:
                return b[1::-1] + b[3:1:-1]
            case ReaderMode.ByteswappedLittle:
                return b[2:4] + b[0:2]

    def read_bytes(self, offset: int, size: int) -> bytes:
        ''' Reads a sequence of bytes and normalizes the buffer's byte order to big endian. '''
        if offset < 0 or size < 0 or offset + size > len(self._buffer):
            raise ValueError('Out of bounds read')

        normalized = bytearray()
        end = offset + size
        i = offset & ~0x3

        while i < end:
            word = self._buffer[i:i+4]
            normalized.extend(self._normalize_word(word))
            i += 4

        start = offset & 0x3
        return bytes(normalized[start:start+size])

    def _read_uint(self, offset: int, size: int) -> int:
        ''' Reads an unsigned integer of `size` bytes at the given offset. '''
        return int.from_bytes(self.read_bytes(offset, size), 'big', signed=False)

    def _read_int(self, offset: int, size: int) -> int:
        ''' Reads a signed integer of `size` bytes at the given offset. '''
        return int.from_bytes(self.read_bytes(offset, size), 'big', signed=True)

    def read_u8(self, offset: int) -> int:
        ''' Reads a 1-byte unsigned integer. '''
        return self._read_uint(offset, 1)

    def read_u16(self, offset: int) -> int:
        ''' Reads a 2-byte unsigned integer. '''
        return self._read_uint(offset, 2)

    def read_u32(self, offset: int) -> int:
        ''' Reads a 4-byte unsigned integer. '''
        return self._read_uint(offset, 4)

    def read_u64(self, offset: int) -> int:
        ''' Reads an 8-byte unsigned integer. '''
        return self._read_uint(offset, 8)

    def read_i8(self, offset: int) -> int:
        ''' Reads a 1-byte signed integer. '''
        return self._read_int(offset, 1)

    def read_i16(self, offset: int) -> int:
        ''' Reads a 2-byte signed integer. '''
        return self._read_int(offset, 2)

    def read_i32(self, offset: int) -> int:
        ''' Reads a 4-byte signed integer. '''
        return self._read_int(offset, 4)

    def read_i64(self, offset: int) -> int:
        ''' Reads an 8-byte signed integer. '''
        return self._read_int(offset, 8)

    def read_ascii(self, offset: int, size: int, *, strip=True) -> str:
        ''' Reads an ASCII string of `size` bytes at the given offset. '''
        s = self.read_bytes(offset, size).decode('ascii')
        return s.rstrip('\x00 ').strip() if strip else s