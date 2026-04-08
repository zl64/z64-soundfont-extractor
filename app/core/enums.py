from enum import Enum


class Game(Enum):
    ''' Represents various uniqe Nintendo 64 game codes. '''
    OCARINA_OF_TIME = 'ZL'
    MAJORAS_MASK = 'ZS'


class Endian(Enum):
    ''' Represents binary data byte ordering. '''
    BIG = 0
    LITTLE = 1
    BYTESWAPPED_BIG = 2
    BYTESWAPPED_LITTLE = 3


class CategoryCode(Enum):
    ''' Represents various Nintendo 64 data storage category codes. '''
    GAME_PAK = 'N'
    DISK_DRIVE = 'D'
    EXPANDABLE_GAME_PAK = 'C'
    EXPANDABLE_DISK_DRIVE = 'E'
    ALECK64_GAME_PAK = 'Z'


class DestinationCode(Enum):
    ''' Represents various Nintendo 64 country codes. '''
    ALL = 'A'
    BRAZIL = 'B'
    CHINA = 'C'
    GERMANY = 'D'
    NORTH_AMERICA = 'E'
    FRANCE = 'F'
    GATEWAY_64_NTSC = 'G'
    NETHERLANDS = 'H'
    ITALY = 'I'
    JAPAN = 'J'
    KOREA = 'K'
    GATEWAY_64_PAL = 'L'
    CANADA = 'N'
    EUROPE_P = 'P'
    SPAIN = 'S'
    AUSTRALIA = 'U'
    SCANDINAVIA = 'W'
    EUROPE_X = 'X'
    EUROPE_Y = 'Y'
    EUROPE_Z = 'Z'