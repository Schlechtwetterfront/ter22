'''
   ZeroEngine The Clone Wars Terrain.
   Refer to schlechtwetterfront.github.io/ze_filetypes/xxw.html for more
   information regarding the file format.
'''

import struct
import ntpath
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Input file path.')
parser.add_argument('output_file', help='Output file path.')
parser.add_argument('output_type', help='Output file type (obj).')


MSG_TO_OBJ = '# Converted "{}" from Star Wars: The Clone Wars terrain with github.com/Schlechtwetterfront/ter22.\n\n'


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


class TextureLayer(object):
    '''Texture layer.'''
    def __init__(self, color_map='', detail_map=''):
        self.color_map = color_map
        self.detail_map = detail_map
        self.tile_range = 1.0


class Terrain(object):
    '''ZeroEngine (TCW branch) terrain.'''
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
            print('Invalid output type "{}".'.format(output_type))

    def save_as_xxw(self, filepath):
        '''Save the terrain to _filepath_ in .xxw format.'''
        print('.XXW saving is not supported yet.')

    def save_as_ter(self, filepath):
        '''Save the terrain to _filepath_ in .ter format.'''
        print('.TER saving is not supported yet.')

    def save_as_obj(self, filepath):
        '''Save the terrain to _filepath_ in .obj format.'''
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

    @classmethod
    def load(cls, filepath):
        '''Load a Terrain from _filepath_.'''
        terrain = cls()

        terrain.name = ntpath.basename(filepath)

        with open(filepath, 'rb') as filehandle:
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

            # Heights
            heights = []
            for _ in range(terrain.size * terrain.size):
                heights.append(parse(2, '<h'))
            terrain.heights = heights

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

    terrain = Terrain.load(input_file)
    terrain.save(output_file, output_type)
    print('Finished converting.')



if __name__ == '__main__':
    convert()

