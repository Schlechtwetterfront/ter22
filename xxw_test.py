from struct import unpack, pack
import logging
import ter03
logging.basicConfig(format='%(message)s',
                    filename='cw.log',
                    filemode='w',
                    level=logging.DEBUG)

FILENAMES = ('samples/geonosis1.xxw', 'samples/geonosis3.xxw',
             'samples/kashyyyk3.xxw', 'samples/multi1.xxw',
             'samples/multi2.xxw', 'samples/multi3.xxw',
             'samples/multi4.xxw', 'samples/multi5.xxw', 'samples/multi6.xxw',
             'samples/multi8.xxw', 'samples/multi9.xxw',
             'samples/multi10.xxw', 'samples/multi12.xxw',
             'samples/multi13.xxw', 'samples/multi14.xxw',
             'samples/multi15.xxw', 'samples/multi17.xxw'
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


def to_obj(file_index=0):
    t = ter03.Terrain.load(FILENAMES[file_index])
    t.save_as_obj('test.obj')


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
    # test_heights(1, '<b')

    to_obj(1)
