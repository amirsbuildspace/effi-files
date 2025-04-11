import math
from dataclasses import dataclass, field
from pathlib import Path


_parsers = {}

# Data type
TYPE_DECIMAL = 0
TYPE_ASCII = 1

# Data corruption detection
NO_DETECTION = 0
PARITY_BIT_DETECTION = 1
CRC_DETECTION = 2

# Data corruption correction
NO_CORRECTION = 0
HAMMING_CORRECTION = 1
REED_SOLOMON_CORRECTION = 2


@dataclass
class EffiFile:
    """Represents an effi file."""

    """Path to the binary file."""
    path: Path

    """Header schema"""
    schema: 'EffiFileHeaderSchema'

    """Get a reader based on header schema"""
    def get_reader(self):
        return EffiFileReader(self)

    """Get a writer based on header schema"""
    def get_writer(self):
        return EffiFileWriter(self)


@dataclass
class EffiFileHeaderSchema:
    """Represents the schema."""

    """Official parser version."""
    official_version: int = 1

    """Derivative parser version. Used for custom parser implementations."""
    derivative_version: int = 0

    """List of field names."""
    field_names: list[str] = field(
        default_factory=list
    )

    """List of field sizes."""
    field_sizes: list[int] = field(
        default_factory=list
    )

    """List of the encoding flags."""
    data_types: list[int] = field(
        default_factory=list
    )

    """
    List of bit detection flags.
    
    0 = None.
    1 = Parity.
    2 = CRC.
    """
    bit_detection_flags: list[int] = field(
        default_factory=list
    )

    """
    List of bit correction flags.
    
    0 = None.
    1 = Hamming Code.
    2 = Reed Solomon code.
    """
    bit_correction_flags: list[int] = field(
        default_factory=list
    )

    def add_field(
            self,
            name: str,
            length: int,
            data_type: int,
            bit_detection_flag: int,
            bit_correction_flag: int
    ):
        self.field_names.append(name)
        self.field_sizes.append(length)
        self.data_types.append(data_type)
        self.bit_detection_flags.append(bit_detection_flag)
        self.bit_correction_flags.append(bit_correction_flag)
        return self

    def get_final_field_sizes(self):
        sizes = []

        for i in range(len(self.field_sizes)):
            size = self.field_sizes[i]

            if self.data_types[i] is TYPE_ASCII:
                size *= 7

            if self.bit_detection_flags[i] is not NO_DETECTION:
                raise NotImplemented

            if self.bit_correction_flags[i] is not NO_CORRECTION:
                raise NotImplemented

            sizes.append(size)

        return tuple(sizes)


@dataclass
class EffiFileReader:
    file: EffiFile


@dataclass
class EffiFileWriter:
    file: EffiFile
    final_sizes: tuple[int, ...] = field(
        init=False
    )

    def __post_init__(self):
        self.final_sizes = self.file.schema.get_final_field_sizes()

    def delete_contents(self):
        self.file.path.open('wb').close()

    def write_row(self, values: tuple):
        assert len(values) == len(self.final_sizes), 'Length of tuple is not equal to length of fields'

        # don't recalculate on every write.
        num_bits = 2 ** bit_length_of_decimal(sum(self.final_sizes))

        bits = ''

        for i, value in enumerate(values):
            binary_value = bin(value)[2:]
            bits += (self.final_sizes[i] - len(binary_value)) * '0' + binary_value

        # final row with padding so we can write bytes
        bits = (num_bits - len(bits)) * '0' + bits

        # convert to bytes
        n = int(bits, 2)
        num_bytes = len(bits) // 8
        bytes_ = n.to_bytes(num_bytes, 'big', signed=False)

        with self.file.path.open(mode='ab') as f:
            f.write(bytes_)


def bit_length_of_decimal(max_n: int):
    return math.ceil(math.log2(max_n + 1))


def bit_length_of_ascii(max_length: int):
    pass