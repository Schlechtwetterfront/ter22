from struct import unpack, pack
import logging
logging.basicConfig(format='%(message)s',
                    filename='cw.log',
                    filemode='w',
                    level=logging.DEBUG)

FILENAMES = ('geonosis1.xxw', 'geonosis3.xxw', 'kashyyyk3.xxw', 'multi1.xxw',
             'multi2.xxw', 'multi3.xxw', 'multi4.xxw', 'multi5.xxw', 'multi6.xxw',
             'multi8.xxw', 'multi9.xxw', 'multi10.xxw', 'multi12.xxw',
             'multi13.xxw', 'multi14.xxw', 'multi15.xxw', 'multi17.xxw'
            )

def test_types():
    offset = 0#1666
    filename = 'multi3.xxw'
    logging.info('Analyzing "{}" with offset "{}".'.format(filename, offset))
    with open(filename, 'rb') as fh:
        fh.read(offset)
        for n in range(64):
            data = fh.read(4)
            logging.info('{:>3} / {:>4}: {:>16} / {:>24}'.format(n, n * 4 + offset, unpack('<L', data)[0], unpack('<f', data)[0]))

    with open(filename, 'rb') as fh:
        fh.read(offset)
        for n in range(128):
            data = fh.read(2)
            logging.info('{:>3} / {:>4}: {:>16} / {:>16}'.format(n, n * 2 + offset, unpack('<h', data)[0], unpack('<H', data)[0]))

    with open(filename, 'rb') as fh:
        fh.read(offset)
        for n in range(256):
            data = fh.read(1)
            logging.info('{:>3} / {:>4}: {:>16}'.format(n, n + offset, unpack('<B', data)[0]))


def test_types2(stride=4, unpack_type='<L', format_string='{:>10}'):
    lines = []
    length_to_read = 256

    lines = [[] for n in range(int(length_to_read / stride))]
    for filename in FILENAMES:
        with open(filename, 'rb') as filehandle:
            for position in range(int(length_to_read / stride)):
                data = filehandle.read(stride)
                lines[position].append(unpack(unpack_type, data)[0])

    logging.info('Files: {}'.format(FILENAMES))
    for index, line in enumerate(lines):
        string = '|| {:>4} ||' + ' '.join([format_string] * len(line))
        logging.info(string.format(index * stride, *line))


def test_heights(stride, type_string):
    offset = 543848 # 1152
    with open(FILENAMES[0], 'rb') as filehandle:
        filehandle.read(offset)
        for n in range(1024):
            logging.info(unpack(type_string, filehandle.read(stride))[0])


if __name__ == '__main__':
    # test_types2(4, '<L')
    # test_types2(4, '<l')
    # test_types2(4, '<f')
    # test_types2(2, '<H')
    # test_types2(2, '<h')
    # test_types2(1, '<B')
    # test_types2(1, '<b')

    # test_heights(4, '<f')
    # test_heights(4, '<L')
    # test_heights(4, '<l')
    # test_heights(2, '<h')
    # test_heights(2, '<H')
    test_heights(1, '<b')
