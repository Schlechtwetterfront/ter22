import ter22
import logging


PRINT_FIELDS = [
	'ter_ver',
	'map_extents',
	'unknown',
	'map_height',
	'grid_size',
	'map_size',
]





def load(filename):
	terrain = ter22.Terrain.load(filename)

	logging.info('\n---\n{}'.format(filename))
	for field in PRINT_FIELDS:
		logging.info('{}: {}'.format(field, getattr(terrain, field)))


load('kashyyyk3.xxw')
load('geo1.ter')