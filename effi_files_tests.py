import os.path
import gzip
import shutil
from pathlib import Path
import lzma

from effi_files import (
    EffiFile,
    EffiFileHeaderSchema,
    bit_length_of_decimal,
    TYPE_DECIMAL,
    NO_DETECTION,
    NO_CORRECTION,
)

def compress_file(input_path: str | Path, output_path: str | Path):
    with open(input_path, 'rb') as f_in:
        with gzip.open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    return output_path


def compress_file_xz(input_path, output_path):
    with open(input_path, 'rb') as f_in:
        with lzma.open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    return os.path.getsize(output_path)


def base_test():
    path = Path('sample.bin')

    schema = {
        'version': [1, 0],
        'headers': [
            {
                'label': 'Id',
                'type': 'decimal',
                'max_value': 1000,
                'bit_detection': 'None',
                'bit_correction': 'None'
            },
            {
                'label': 'Age',
                'type': 0,
                'max_value': 100,
                'bit_detection': 0,
                'bit_correction': 0
            },
            {
                'label': 'PhoneNumber',
                'type': 0,
                'max_value': 9999999999,
                'bit_detection': 0,
                'bit_correction': 0
            }
        ]
    }

    schema = EffiFileHeaderSchema(
        1
    )
    schema.add_field(
        'Id',
        bit_length_of_decimal(1_000_000),
        TYPE_DECIMAL,
        NO_DETECTION,
        NO_CORRECTION
    )
    schema.add_field(
        'Age',
        bit_length_of_decimal(200),
        TYPE_DECIMAL,
        NO_DETECTION,
        NO_CORRECTION
    )
    schema.add_field(
        'PhoneNumber',
        bit_length_of_decimal(999_999_9999),
        TYPE_DECIMAL,
        NO_DETECTION,
        NO_CORRECTION
    )

    file = EffiFile(
        path,
        schema
    )

    n = 500_000

    # TESTING EFFI-FILE

    print("Testing for", n, "row:")

    writer = file.get_writer()
    writer.delete_contents()
    writer.open_file(mode='wb')

    for i in range(n):
        writer.write_row((i, 50, 121_121_1212))

    writer.close_file()
    print('Effi    :', os.path.getsize(file.path))

    # TESTING CSV

    Path('sample.csv').touch()

    with open('sample.csv', 'w', encoding='utf-8') as f:
        content = ''
        for i in range(n):
            content += f'{i},50,1211211212\n'
        f.write(content)

    print('CSV     :', os.path.getsize('sample.csv'))

    # check compressions

    effi_compressed = compress_file('sample.bin', 'sample.bin.gz')
    csv_compressed = compress_file('sample.csv', 'sample.csv.gz')

    print('Effi .gz:', os.path.getsize(effi_compressed))
    print('CSV  .gz:', os.path.getsize(csv_compressed))

    effi_xz = compress_file_xz('sample.bin', 'sample.bin.xz')
    csv_xz = compress_file_xz('sample.csv', 'sample.csv.xz')

    print("Effi .xz:", effi_xz)
    print("CSV  .xz:", csv_xz)



if __name__ == '__main__':
    base_test()
