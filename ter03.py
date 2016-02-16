from struct import unpack, pack
import logging
logging.basicConfig(format='%(levelname)s (%(lineno)d, %(funcName)s): %(message)s',
                            filename='cw.log',
                            filemode='w',
                            level=logging.DEBUG)


def test_types():
	offset = 1666
	with open('kashyyyk3.xxw', 'rb') as fh:
		fh.read(offset)
		for n in range(64):
			data = fh.read(4)
			logging.info('{:>3} / {:>4}: {:>16} / {:>24}'.format(n, n * 4 + offset, unpack('<L', data)[0], unpack('<f', data)[0]))

	with open('kashyyyk3.xxw', 'rb') as fh:
		fh.read(offset)
		for n in range(128):
			data = fh.read(2)
			logging.info('{:>3} / {:>4}: {:>16} / {:>16}'.format(n, n * 2 + offset, unpack('<h', data)[0], unpack('<H', data)[0]))

	with open('kashyyyk3.xxw', 'rb') as fh:
		fh.read(offset)
		for n in range(256):
			data = fh.read(1)
			logging.info('{:>3} / {:>4}: {:>16}'.format(n, n + offset, unpack('<B', data)[0]))


if __name__ == '__main__':
	test_types()