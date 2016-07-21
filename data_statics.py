from cassiopeia import core
from cassiopeia import type
from cassiopeia.type.api.exception import APIError

def champions():
	try:
		championlist = core.staticdataapi.get_champions()
	except APIError as e:
		raise e
	return champions
