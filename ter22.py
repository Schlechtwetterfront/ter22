from struct import unpack, pack
import logging
from os import stat


class zeter(object):
    def i(*args):
        logging.info(' '.join(str(arg) for arg in args))


class Reader(zeter):
    def __init__(self, filehandler):
        self.fh = filehandler

    def r(self, size):
        return self.fh.read(size)

    def l(self):
        return unpack('<L', self.fh.read(4))[0]

    def h(self):
        return unpack('<H', self.fh.read(2))[0]

    def uh(self):
        return unpack('<h', self.fh.read(2))[0]

    def b(self):
        return unpack('<B', self.fh.read(1))[0]

    def f(self):
        return unpack('<f', self.fh.read(4))[0]

    def c(self, t='L', count=1, size=4):
        return unpack('<{0}'.format(t * count), self.fh.read(size))


class Packer(zeter):
    def l(self, data):
        return pack('<L', data)

    def h(self, data):
        return pack('<H', data)

    def uh(self, data):
        return pack('<h', data)

    def b(self, data):
        return pack('<B', data)

    def f(self, data):
        return pack('<f', data)

    def c(self, t, count, data):
        return pack('<{0}'.format(t * count), *data)


class Color(Packer):
    red = 0
    green = 0
    blue = 0
    alpha = 0

    def __init__(self, r, g, b, a=255):
        self.red = r
        self.green = g
        self.blue = b
        self.alpha = a

    @property
    def rgba(self):
        return self.red, self.green, self.blue, self.alpha

    def __repr__(self):
        return 'Color(r={0}, g={1}, b={2}, a={3})'.format(self.red, self.green,
                                                          self.blue, self.alpha)

    def pack(self):
        return self.c('B', 4, self.rgba)


class TextureLayer(zeter):
    tile_range = 1/32
    texture = ''
    detail_texture = ''
    mapping = 0

    def __init__(self, tile_range=1/32, tex='', detail='', mapping=0):
        self.tile_range = tile_range
        self.texture = tex
        self.detail_texture = detail
        self.mapping = mapping

    def __repr__(self):
        return 'TextureLayer(tile={0}, tex={1}, detail={2}, mapping={3})'.format(self.tile_range,
                                                                                 self.texture,
                                                                                 self.detail_texture, self.mapping)

    def pack_tex(self):
        return ''.join((self.texture.ljust(32, '\x00'), self.detail_texture.ljust(32, '\x00')))


class WaterLayer(Packer):
    height = (.0, .0)
    unknown = (0, 0)
    animation_velocity = (.0, .0)
    animation_repeat = (.0, .0)
    color = Color(0, 0, 0)
    texture = ''

    def __init__(self, height=(.0, .0), unknown=(0, 0), animation_repeat=(.0, .0),
                 animation_velocity=(.0, .0), color=Color(0, 0, 0), texture=''):
        self.height = height
        self.unknown = unknown
        self.animation_velocity = animation_velocity
        self.animation_repeat = animation_repeat
        self.color = color
        self.texture = texture

    def __repr__(self):
        return 'Water(height={0}, unknown={1}, vel={2}, rep={3}, col={4}, tex={5})'.format(self.height,
                self.unknown, self.animation_velocity, self.animation_repeat, self.color, self.texture)

    def pack(self):
        data = []
        a = data.append
        a(self.c('f', 2, self.height))
        a(self.c('L', 2, self.unknown))
        a(self.c('f', 2, self.animation_velocity))
        a(self.c('f', 2, self.animation_repeat))
        a(self.color.pack())
        a(self.texture.ljust(32, '\x00'))
        return ''.join(data)


class TextureAlphas(Packer):
    alphas = (0) * 16

    def __init__(self, alphas=(0)*16):
        self.alphas = alphas

    def __getitem__(self, key):
        return self.alphas[key]

    def pack(self):
        return self.c('B', 16, self.alphas)


class Water(zeter):
    data = None


class Terrain(Packer):
    ter_ver = 22
    map_extents = (-64, -64, 64, 64)
    texture_layers = None
    water_infos = None
    map_height = 1
    grid_size = 8.0
    map_size = 256
    heights = None
    colors = None
    colors2 = None
    textures = None
    water = None
    foliage = None
    unknown = None

    def __init__(self):
        self.heights = []
        self.colors = []
        self.colors2 = []
        self.textures = []
        self.water = []
        self.foliage = []
        self.unknown = []

        self.texture_layers = [TextureLayer() for n in xrange(16)]
        self.water_infos = [WaterLayer() for n in xrange(16)]

    def pack(self):
        for layer in self.texture_layers:
            self.i(layer)
        data = ['TERR']
        a = data.append
        a(self.l(self.ter_ver))
        for item in self.map_extents:
            a(self.uh(item))
        a(self.l(self.unknown[0]))
        for layer in self.texture_layers:
            a(self.f(layer.tile_range))
        for layer in self.texture_layers:
            a(self.b(layer.mapping))
        a(self.unknown[1])
        a(self.f(self.map_height))
        a(self.f(self.grid_size))
        a(self.l(self.unknown[2]))
        a(self.l(self.map_size))
        a(self.l(self.unknown[3]))
        a(self.unknown[4])
        for layer in self.texture_layers:
            a(layer.pack_tex())
            self.i(layer.pack_tex())
        for info in self.water_infos:
            a(info.pack())
        a(self.unknown[5])

        for row in self.heights:
            a(self.c('h', self.map_size, row))

        for row in self.colors:
            for color in row:
                a(color.pack())

        for row in self.colors2:
            for color in row:
                a(color.pack())

        for row in self.textures:
            for tex in row:
                a(tex.pack())

        for water in self.water:
            a(water.data)

        a(self.foliage)

        return ''.join(data)

    def save(self, filepath):
        with open(filepath, 'wb') as fh:
            data = self.pack()
            self.i('data size', len(data))
            fh.write(data)

    @classmethod
    def load(cls, filepath):
        t = cls()
        logging.basicConfig(format='%(levelname)s (%(lineno)d, %(funcName)s): %(message)s',
                            filename='terparse.log',
                            filemode='w',
                            level=logging.DEBUG)
        info = stat(filepath)
        t.i('data size before', info.st_size)
        with open(filepath, 'rb') as fh:
            r = Reader(fh)
            r.r(4)  # TERR
            t.ter_ver = r.l()
            t.map_extents = unpack('<hhhh', r.r(8))
            t.unknown.append(r.l())
            for n in xrange(16):
                t.texture_layers[n].tile_range = r.f()
            for n in xrange(16):
                t.texture_layers[n].mapping = r.b()
            t.unknown.append(r.r(64))
            t.map_height = r.f()
            t.grid_size = r.f()
            t.unknown.append(r.l())
            t.map_size = r.l()
            t.unknown.append(r.l())
            t.unknown.append(r.b())
            for n in xrange(16):
                t.texture_layers[n].texture = r.r(32).strip('\x00')
                t.texture_layers[n].detail_texture = r.r(32).strip('\x00')
            #i('?', r.r(68))
            for n in xrange(16):
                water = t.water_infos[n]
                water.height = r.f(), r.f()
                water.unknown = r.l(), r.l()
                water.animation_velocity = r.f(), r.f()
                water.animation_repeat = r.f(), r.f()
                water.color = Color(r.b(), r.b(), r.b(), r.b())
                water.texture = r.r(32)
            t.unknown.append(r.r(254))

            # Height
            heights = []
            for n in xrange(t.map_size):
                heights.append(r.c('h', t.map_size, 2 * t.map_size))
            t.heights = heights

            colors = []
            for n in xrange(t.map_size):
                row = []
                for i in xrange(t.map_size):
                    row.append(Color(r.b(), r.b(), r.b(), r.b()))
                colors.append(row)
            t.colors = colors

            colors2 = []
            for n in xrange(t.map_size):
                row2 = []
                for i in xrange(t.map_size):
                    row2.append(Color(r.b(), r.b(), r.b(), r.b()))
                colors2.append(row)
            t.colors2 = colors2

            textures = []
            for n in xrange(t.map_size):
                row = []
                for i in xrange(t.map_size):
                    row.append(TextureAlphas(r.c('B', 16, 16)))
                textures.append(row)
            t.textures = textures

            water = []
            for n in xrange(t.map_size):
                water_inst = Water()
                water_inst.data = r.r(t.map_size / 2)
                water.append(water_inst)
            t.water = water

            foliage = r.r(t.map_size * t.map_size / 2)
            t.foliage = foliage

            return t
