# https://n64brew.dev/wiki/ROM_Header


from dataclasses import dataclass

from app.core.enums import CategoryCode, DestinationCode
from app.core.n64_reader import BinaryReader


@dataclass
class DomConfig:
    ''' Represents the Nintendo 64 PI DOM1 configuration stored in the Nintendo 64 ROM header. '''
    release: int = 0
    page_size: int = 0
    pulse_width: int = 0
    latency: int = 0

    @classmethod
    def from_reader(cls, reader: BinaryReader, offset: int) -> 'DomConfig':
        ''' Parse a DomConfig from a BinaryReader at the given offset. '''
        dom_config = cls()

        b = reader.read_bytes(offset, 0x3)

        dom_config.release = (b[0] & 0b11110000) >> 4
        dom_config.page_size = b[0] & 0b00001111
        dom_config.pulse_width = b[1]
        dom_config.latency = b[2]

        return dom_config


@dataclass
class LibUltraVersion:
    ''' Represents the Nintendo 64 LibUltra version stored in a Nintendo 64 ROM header. '''
    major: int = 0
    minor: int = 0
    revision: str = ''

    @classmethod
    def from_reader(cls, reader: BinaryReader, offset: int) -> 'LibUltraVersion':
        ''' Parse a LibUltra version from a BinaryReader at the given offset. '''
        libultra_version = cls()

        b = reader.read_bytes(offset, 0x4)

        libultra_version.major = b[2] // 10
        libultra_version.minor = b[2] % 10
        libultra_version.revision = chr(b[3])

        return libultra_version


@dataclass
class GameCode:
    ''' Represents the Nintendo 64 game information stored in the Nintendo 64 ROM header. '''
    category_code: CategoryCode = CategoryCode.GAME_PAK
    unique_code: str = ''
    destination_code: DestinationCode = DestinationCode.ALL

    @classmethod
    def from_reader(cls, reader: BinaryReader, offset: int) -> 'GameCode':
        ''' Parse a GameCode from a BinaryReader at the given offset. '''
        game_code = cls()

        b = reader.read_bytes(offset, 0x4)

        game_code.category_code = CategoryCode(chr(b[0]))
        game_code.unique_code = chr(b[1]) + chr(b[2])
        game_code.destination_code = DestinationCode(chr(b[3]))

        return game_code


class RomHeader:
    ''' Represents a Nintendo 64 ROM header. '''
    DOM_CONFIG_OFFSET: int = 0x01
    CLOCK_RATE_OFFSET: int = 0x04
    BOOT_ADDRESS_OFFSET: int = 0x08
    LIBULTRA_VERSION_OFFSET: int = 0x0C
    CHECK_CODE_OFFSET: int = 0x10
    GAME_TITLE_OFFSET: int = 0x20
    GAME_TITLE_SIZE: int = 0x14
    GAME_CODE_OFFSET: int = 0x3B
    ROM_VERSION_OFFSET: int = 0x3F
    # BOOT_CODE_OFFSET: int = 0x40
    # BOOT_CODE_SIZE: int = 0xFC0

    def __init__(self) -> None:
        self.dom_config: DomConfig = DomConfig()
        self.clock_rate: int = 0
        self.boot_address: int = 0
        self.libultra_version: LibUltraVersion = LibUltraVersion()
        self.check_code: int = 0
        self.game_title: str = ''
        self.game_code: GameCode = GameCode()
        self.rom_version: int = 0
        # self.boot_code: bytes = bytes()

    @classmethod
    def from_reader(cls, reader: BinaryReader, base: int = 0) -> 'RomHeader':
        ''' Parse a full ROM header from a BinaryReader. '''
        rom_header = cls()

        rom_header.dom_config = DomConfig.from_reader(reader, base + cls.DOM_CONFIG_OFFSET)
        rom_header.clock_rate = reader.read_u32(base + cls.CLOCK_RATE_OFFSET)
        rom_header.boot_address = reader.read_u32(base+ cls.BOOT_ADDRESS_OFFSET)
        rom_header.libultra_version = LibUltraVersion.from_reader(reader, base+ cls.LIBULTRA_VERSION_OFFSET)
        rom_header.check_code = reader.read_u64(base+ cls.CHECK_CODE_OFFSET)
        rom_header.game_title = reader.read_ascii(base + cls.GAME_TITLE_OFFSET, cls.GAME_TITLE_SIZE)
        rom_header.game_code = GameCode.from_reader(reader, base + cls.GAME_CODE_OFFSET)
        rom_header.rom_version = reader.read_u8(base + cls.ROM_VERSION_OFFSET)
        # rom_header.boot_code = reader.read_bytes(base + cls.BOOT_CODE_OFFSET, cls.BOOT_CODE_SIZE)

        return rom_header
