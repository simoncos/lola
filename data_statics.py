from cassiopeia import riotapi
from cassiopeia import core
from cassiopeia import type
from cassiopeia.type.api.exception import APIError
from data_crawl import riotapi_setting

def champions():
    try:
        # set your api key and region here
        riotapi_setting(api_key='', region='NA')
        championlist = core.staticdataapi.get_champions()
    except APIError as e:
        raise e
    return championlist