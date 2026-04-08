from dataclasses import dataclass
from functools import cached_property
import hashlib
import mmap
from pathlib import Path

from app.core.enums import Game, Endian
from app.core.n64_reader import BinaryReader, ReaderMode
from app.core.n64_header import RomHeader


@dataclass(slots=True)
class Item:
    ''' Represents the offset and length of arbitrary data on a Nintendo 64 ROM. '''
    offset: int
    length: int


@dataclass(slots=True)
class TableEntry:
    ''' Represents a single table entry pointing to a soundfont on an Ocarina of Time or Majora's Mask ROM. '''
    index: int
    offset: int
    length: int
    data: bytes

    @classmethod
    def from_rom(cls, rom: 'ROM', base_offset: int, index: int) -> 'TableEntry':
        ''' Parse a TableEntry from a Nintendo 64 ROM at a specific index. '''
        entry_offset = base_offset + ROM._TABLE_ENTRY_SIZE + index * ROM._TABLE_ENTRY_SIZE

        # The first 8 bytes of the table entry are the offset to the
        # soundfont and the total size of the soundfont
        offset = rom.reader.read_u32(entry_offset)
        length = rom.reader.read_u32(entry_offset + 0x4)

        data = rom.reader.read_bytes(entry_offset, ROM._TABLE_ENTRY_SIZE)

        return cls(index, offset, length, data)


@dataclass(slots=True)
class Soundfont:
    ''' Represents a soundfont stored on an Ocarina of Time or Majora's Mask ROM. '''
    index: int
    offset: int
    length: int
    soundfont_data: bytes
    table_entry_data: bytes

    _hash: str | None = None

    @property
    def hash(self) -> str:
        ''' Returns the MD5 hash of the soundfont's binary data. '''
        if self._hash is None:
            self._hash = hashlib.md5(self.soundfont_data).hexdigest()
        return self._hash

    @property
    def display_name(self) -> str:
        ''' Returns a human-readable name for the soundfont. '''
        return f'Soundfont 0x{self.index:02X}'

    def is_vanilla(self, vanilla_hashes: list[str]) -> bool:
        ''' Checks if the soundfont's binary data matches a known vanilla hash. '''
        if self.index >= len(vanilla_hashes):
            return False
        return self.hash == vanilla_hashes[self.index]

    def write_soundfont(self, out_path: Path):
        ''' Writes the soundfont binary data to a file. '''
        out_path.write_bytes(self.soundfont_data)

    def write_table_entry(self, out_path: Path):
        ''' Writes the soundfont's table entry binary data to a file. (Truncated)'''
        out_path.write_bytes(self.table_entry_data[0x08:])


class ROM:
    ''' Represents a Nintendo 64 ROM. '''
    # A decompressed ROM could work (audio binary files remain uncompressed),
    # but those who would want this tool should be using decompressed ROMs
    # that work with SEQ64
    _ROM_SIZE: int = 64 * 1024 * 1024 # 64 MiB
    _TABLE_ENTRY_SIZE: int = 0x10

    _AUDIOBIN_ITEMS: dict[Game, dict[str, Item]] = {
        Game.OCARINA_OF_TIME: {
            'Audiobank': Item(offset=0x0000D390, length=0x0001CA50),
            'Audiobank_index': Item(offset=0x00B896A0, length=0x00000270),
        },
        Game.MAJORAS_MASK: {
            'Audiobank': Item(offset=0x00020700, length=0x000263F0),
            'Audiobank_index': Item(offset=0x00C776C0, length=0x000002A0),
        }
    }

    _ENDIAN_TO_READER_MODE: dict[Endian, ReaderMode] = {
        Endian.BIG: ReaderMode.BigEndian,
        Endian.LITTLE: ReaderMode.LittleEndian,
        Endian.BYTESWAPPED_BIG: ReaderMode.ByteswappedBig,
        Endian.BYTESWAPPED_LITTLE: ReaderMode.ByteswappedLittle
    }

    def __init__(self, file_path: str) -> None:
        self.file_path: Path = Path(file_path)

        if not self.file_path.exists() or self.file_path.stat().st_size != self._ROM_SIZE:
            raise ValueError(f'Invalid ROM size, expected {self._ROM_SIZE}, got {self.file_path.stat().st_size} ')

        self._file = self.file_path.open('rb')
        self._mmap = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)

        # Detect the ROM file's endianness (proper ROM files are always big endian)
        self.endian: Endian | None = self._detect_endianness()
        if self.endian is None:
            raise ValueError('Unknown ROM endianness')

        # Create a reader for the ROM that can normalize data from whatever
        # the ROM's endianness is to the Nintendo 64's native endian - big endian.
        self.reader: BinaryReader = BinaryReader(
            self._mmap,
            mode=self._ENDIAN_TO_READER_MODE[self.endian]
        )

        self.game: Game = self._detect_game()

    def _detect_endianness(self) -> Endian:
        ''' Detects the ROM file's byte order based on its first 4 bytes. '''
        # The 32-bit word of Nintendo 64 ROM files is generally used to determine
        # endianness. This value is expected to always be the same for normal
        # Nintendo 64 ROM files, but it does not need to be.
        magic_word: int = BinaryReader(self._mmap, mode=ReaderMode.BigEndian).read_u32(0)

        # There are four different endiannesses available for ROM files:
        # 1. Big Endian - words store their MSB at the lowest possible address
        # 2. Little Endian - words store their LSB at the lowest possible address
        # 3. Byteswapped Big - big endian, but 16-bit words have their bytes swapped
        # 4. Byteswapped Little - little endian, but 16-bit words have their bytes swapped
        return {
            0x80371240: Endian.BIG,
            0x40123780: Endian.LITTLE,
            0x37804012: Endian.BYTESWAPPED_BIG,
            0x12408037: Endian.BYTESWAPPED_LITTLE,
        }.get(magic_word)

    def _detect_game(self) -> Game:
        ''' Detects the Nintendo 64 game the ROM file belongs to. '''
        # Normally, an MD5 checksum calculation would be the best way to determine
        # the game (and other useful things), but users extracting a soundfont have
        # generally modified data on the ROM, so the MD5 checksum would be different.
        # Instead, there is data within the ROM header that can be used to determine
        # the game instead, such as the check code, game title, or game code.
        code: str = self.header.game_code.unique_code

        # Every Nintendo 64 game contains a unique code as part of the game code
        # structure in the ROM file's header:
        # 1. Ocarina of Time - ZL
        # 2. Majora's Mask - ZS
        match code:
            case Game.OCARINA_OF_TIME.value:
                return Game.OCARINA_OF_TIME
            case Game.MAJORAS_MASK.value:
                return Game.MAJORAS_MASK
            case _:
                raise ValueError(f'Unknown or unsupported Nintendo 64 game: {code}')

    def get_soundfonts(self) -> list[Soundfont]:
        ''' Extract all soundfonts from the ROM file. '''
        audiobank, audiobank_index = self.items

        base = audiobank_index.offset
        count = self.reader.read_u16(base)

        soundfonts: list[Soundfont] = []

        for i in range(count):
            entry = TableEntry.from_rom(self, base, i)

            start = audiobank.offset + entry.offset
            data = self.reader.read_bytes(start, entry.length)

            soundfonts.append(
                Soundfont(
                    index=i,
                    offset=entry.offset,
                    length=entry.length,
                    soundfont_data=data,
                    table_entry_data=entry.data,
                )
            )

        self._soundfonts = soundfonts
        return soundfonts

    @cached_property
    def items(self) -> tuple[Item, Item]:
        ''' Return the ROM offsets and lengths for its `audiobank` and their table entries. '''
        if self.game is None:
            raise ValueError('Game not detected, cannot get items')
        entry = self._AUDIOBIN_ITEMS[self.game]
        return (entry['Audiobank'], entry['Audiobank_index'])

    @cached_property
    def header(self) -> RomHeader:
        ''' Return the ROM file's header. '''
        return RomHeader.from_reader(self.reader)

    @property
    def is_valid(self) -> bool:
        ''' Checks if the ROM file is valid. '''
        return (
            self.file_path.stat().st_size == self._ROM_SIZE
            and self.game is not None
            and self.endian is not None
        )

    # Context manager support
    def close(self):
        ''' Closes the ROM file and its memory map. '''
        try:
            self._mmap.close()
        finally:
            self._file.close()

    def __enter__(self):
        ''' Enter the context manager. '''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ''' Exit the context manager and close resources. '''
        self.close()
