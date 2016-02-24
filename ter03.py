'''
   ZeroEngine Terrain.
   Refer to
       schlechtwetterfront.github.io/ze_filetypes/ter.html
       schlechtwetterfront.github.io/ze_filetypes/xxw.html
   for more information regarding the file format.
'''

import struct
import ntpath
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Input file path.')
parser.add_argument('-output_file', help='Output file path.')
parser.add_argument('-output_type', help='Output file type.', choices=['obj', 'ter', 'xxw'])



TERRAIN_UNKNOWN = 0
TERRAIN_XXW = 3
TERRAIN_TER_221 = 21
TERRAIN_TER_22 = 22

MSG_TO_OBJ = '# Converted "{}" from ZeroEngine terrain with github.com/Schlechtwetterfront/ter22.\n\n'


class Unpacker(object):
    '''UNpacking helper.'''
    def __init__(self, filehandle=None):
        self.filehandle = filehandle

    def parse(self, size=4, type_string='<L'):
        '''Unpack some bytes.'''
        length = len(type_string) - 1
        if length == 1:
            return struct.unpack(type_string, self.filehandle.read(size))[0]
        else:
            return struct.unpack(type_string, self.filehandle.read(size * length))


class Color(object):
    def __init__(self, r=0, g=0, b=0, a=1, recalculate=False):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        if recalculate:
            self.recalculate()

    @property
    def rgba(self):
        return self.r, self.g, self.b, self.a

    def recalculate(self):
        self.r = self.r / 255
        self.g = self.g / 255
        self.b = self.b / 255
        self.a = self.a / 255

    def __repr__(self):
        return 'Color({0.r}, {0.g}, {0.b}, {0.a})'.format(self)

    def to_json(self):
        return {'r': self.r, 'g': self.g, 'b': self.b, 'a': self.a}

    @classmethod
    def from_json(cls, data):
        color = cls()
        color.r = data['r']
        color.g = data['g']
        color.b = data['b']
        color.a = data['a']
        return color

    @classmethod
    def from_bgra(cls, b, g, r, a, recalculate=False):
        color = cls()
        color.r = r
        color.g = g
        color.b = b
        color.a = a
        if recalculate:
            color.recalculate
        return color


class TextureLayer(object):
    '''Texture layer.'''
    def __init__(self, color_map='', detail_map=''):
        self.color_map = color_map
        self.detail_map = detail_map
        self.tile_range = 1.0

        self.mapping = 0

    def __repr__(self):
        return 'TextureLayer(color: {}, detail: {}, mapping: {})'.format(self.color_map,
                                                                         self.detail_map,
                                                                         self.mapping)

    def to_json(self):
        return {'color_map': self.color_map,
                'detail_map': self.detail_map,
                'mapping': self.mapping}

    @classmethod
    def from_json(cls, data):
        layer = cls()
        layer.color_map = data['color_map']
        layer.detail_map = data['detail_map']
        layer.mapping = data['mapping']
        return layer


class WaterLayer(object):
    def __init__(self):
        self.height = .0, .0
        self.unknown = 0, 0
        self.animation_velocity = .0, .0
        self.animation_repeat = .0, .0
        self.color = Color()
        self.texture = ''

    def to_json(self):
        return {'height': self.height,
                'unknown': self.unknown,
                'animation_velocity': self.animation_velocity,
                'animation_repeat': self.animation_repeat,
                'color': self.color.to_json(),
                'texture': self.texture}

    @classmethod
    def from_json(cls, data):
        layer = cls()
        layer.height = data['height']
        layer.unknown = data['unknown']
        layer.animation_velocity = data['animation_velocity']
        layer.animation_repeat = data['animation_repeat']
        layer.color = Color.from_json(data['color'])
        layer.texture = data['texture']
        return layer


class Terrain(object):
    '''ZeroEngine generic terrain.'''

    def __init__(self):
        self.name = ''

        self.format_version = 3
        self.size = 0
        self.grid_scale = 32.0
        self.height_scale = 1.0
        self.extents = (-128, 128, -128, 128)
        self.tile_ranges = [1.0] * 16
        self.texture_layers = [TextureLayer()] * 16

        self.heights = []

        self.coordinate_scale = 0.5

    def get_heights_as_coordinates(self):
        '''Converts height grid data into 3D coordinates.'''
        coordinates = []
        for index, height in enumerate(self.heights):
            row = index / self.size
            column = index % self.size
            x = column * self.grid_scale * self.coordinate_scale
            y = height * self.height_scale * self.coordinate_scale
            z = row * self.grid_scale * self.coordinate_scale
            coordinates.append((x, y, z))
        return coordinates

    def save(self, filepath, output_type='xxw'):
        '''Save this terrain to _filepath_ as _output_type_.'''
        if 'obj' in output_type:
            self.save_as_obj(filepath)
        elif 'ter' in output_type:
            self.save_as_ter(filepath)
        elif 'xxw' in output_type:
            self.save_as_xxw(filepath)
        else:
            raise Exception('Invalid output type "{}".'.format(output_type))

    def save_as_xxw(self, filepath):
        '''Save the terrain to _filepath_ in .xxw format.'''
        raise Exception('.XXW saving is not supported yet.')

    def save_as_ter(self, filepath):
        '''Save the terrain to _filepath_ in .ter format.'''
        raise Exception('.TER saving is not supported yet.')

    def save_as_obj(self, filepath):
        '''Save the terrain to _filepath_ in .obj format.'''
        logging.info('Saving terrain as .obj to "%s".', filepath)
        with open(filepath, 'w') as filehandle:
            write = filehandle.write
            write(MSG_TO_OBJ.format(self.name))
            number_of_rows = int(len(self.heights) / self.size)
            for coordinate in self.get_heights_as_coordinates():
                write('v {} {} {}\n'.format(*coordinate))
            for row_index in range(number_of_rows - 1):
                for column in range(self.size - 1):
                    indices = (column + row_index * self.size + 1,
                               column + row_index * self.size + 2,
                               column + (row_index + 1) * self.size + 2,
                               column + (row_index + 1) * self.size + 1
                              )
                    write('f {} {} {} {}\n'.format(*indices))
        logging.info('Finished saving terrain as .obj.')

    @classmethod
    def load(cls, filepath):
        terrain_type = TERRAIN_UNKNOWN
        with open(filepath, 'rb') as filehandle:
            header = filehandle.read(4)
            version = struct.unpack('<L', filehandle.read(4))[0]
            if version == 3:
                terrain_type = TERRAIN_XXW
            elif version == 21:
                terrain_type = TERRAIN_TER_221
            elif version == 22:
                terrain_type = TERRAIN_TER_22
            else:
                raise Exception('Unknown terrain version "{}".'.format(version))

        if terrain_type == 3:
            return Terrain03.load(filepath)
        elif terrain_type == 21 or terrain_type == 22:
            return Terrain2X.load(filepath)
        else:
            return None


class Terrain2X(Terrain):
    def __init__(self):
        super(Terrain2X, self).__init__()

        self.water_layers = [WaterLayer()] * 16
        self.colors = []
        self.texture_layer_opacity = []

    @classmethod
    def load(cls, filepath):
        '''Load a Terrain from _filepath_.'''
        terrain = cls()

        terrain.name = ntpath.basename(filepath)

        with open(filepath, 'rb') as filehandle:
            logging.info('Loading SWBF (v21/22) terrain from "%s".', filepath)

            unpacker = Unpacker(filehandle)
            parse = unpacker.parse
            read = filehandle.read

            read(4) # TERR header
            terrain.format_version = parse(4, '<L')
            terrain.extents = parse(2, '<hhhh')
            read(4) # Unknown
            for layer in terrain.texture_layers:
                layer.tile_range = parse(4, '<f')
            for layer in terrain.texture_layers:
                layer.mapping = parse(1, '<B')
            read(64) # Unknown
            terrain.height_scale = parse(4, '<f')
            terrain.grid_scale = parse(4, '<f')
            read(4) # Unknown
            terrain.size = parse(4, '<L')
            read(4) # Unknown
            if terrain.format_version == TERRAIN_TER_22:
                read(1) # Unknown
            for layer in terrain.texture_layers:
                layer.color_map = read(32).strip(b'\x00')
                layer.detail_map = read(32).strip(b'\x00')
            for layer in terrain.water_layers:
                layer.height = parse(4, '<ff')
                layer.unknown = parse(4, '<LL')
                layer.animation_velocity = parse(4, '<ff')
                layer.animation_repeat = parse(4, '<ff')
                layer.color = Color(*parse(1, '<BBBB'), recalculate=True)
                layer.texture = read(32).strip(b'\x00')
            read(254) # Unknown

            logging.info('''Terrain header data:
    size: %s
    grid_scale: %s
    height_scale: %s
    extents: %s
            ''', terrain.size, terrain.grid_scale, terrain.height_scale, terrain.extents)

            # Height
            heights = []
            for _ in range(terrain.size * terrain.size):
                heights.append(parse(2, '<h'))
            terrain.heights = heights
            logging.info('Loaded %s heights.', len(heights))

            # Colors
            colors = []
            for _ in range(terrain.size * terrain.size):
                colors.append(Color.from_bgra(*parse(1, '<BBBB'), recalculate=True))
            terrain.colors = colors

            # Another 2 color blocks
            for _ in range(terrain.size * terrain.size):
                read(8)

            # Texture layer opacity
            opacity = []
            for _ in range(terrain.size * terrain.size):
                opacity.append(parse(1, '<BBBBBBBBBBBBBBBB'))
            terrain.texture_layer_opacity = opacity

            logging.info('Current offset: %s', filehandle.tell())

        logging.info('Finished loading terrain.')

        return terrain


class Terrain03(Terrain):
    '''ZeroEngine (TCW branch) terrain.'''
    def __init__(self):
        super(Terrain03, self).__init__()
        self.format_version = 3

    @classmethod
    def load(cls, filepath):
        '''Load a Terrain from _filepath_.'''
        terrain = cls()

        terrain.name = ntpath.basename(filepath)

        with open(filepath, 'rb') as filehandle:
            logging.info('Loading TCW (v3) terrain from "%s".', filepath)

            unpacker = Unpacker(filehandle)
            parse = unpacker.parse
            read = filehandle.read

            read(4) # Header size indicator.
            terrain.format_version = parse(4, '<L')
            read(4) # Unknown
            terrain.size = parse(4, '<L')
            read(4) # Unknown
            terrain.grid_scale = parse(4, '<f')
            terrain.height_scale = parse(4, '<f')
            terrain.extents = parse(4, '<llll')
            read(20) # Unknown
            for layer in terrain.texture_layers:
                layer.tile_range = parse(4, '<f')
            for layer in terrain.texture_layers:
                layer.color_map = read(32).strip(b'\x00')
                layer.detail_map = read(32).strip(b'\x00')

            logging.info('''Terrain header data:
    size: %s
    grid_scale: %s
    height_scale: %s
    extents: %s
            ''', terrain.size, terrain.grid_scale, terrain.height_scale, terrain.extents)

            # Heights
            heights = []
            for _ in range(terrain.size * terrain.size):
                heights.append(parse(2, '<h'))
            terrain.heights = heights
            logging.info('Loaded %s heights.', len(heights))

        logging.info('Finished loading terrain.')
        return terrain


def convert():
    '''Convert a .xxw file.'''
    arguments = parser.parse_args()
    input_file = arguments.input_file
    output_file = arguments.output_file
    output_type = arguments.output_type

    print('Converting from "{}" to "{}" with type "{}".'.format(input_file,
                                                                output_file,
                                                                output_type))
    logging.info('Converting from "%s" to "%s" with type "%s".', input_file,
                 output_file, output_type)


    terrain = Terrain.load(input_file)
    if output_file:
        terrain.save(output_file, output_type)
        print('Finished converting.')
        logging.info('Finished converting.')



if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s (%(lineno)d, %(funcName)s): %(message)s',
                        filename='terrain.log',
                        filemode='w',
                        level=logging.DEBUG)
    convert()

