from flask import Blueprint

import globals
from globals import storage

show_keys = Blueprint("show_keys", import_name=__name__, url_prefix="/data")

@show_keys.route('/', methods=['GET'])
def get_keys():
    keys = storage.get_keys()
    return {
            "count": len(keys), 
            "keys": keys, 
            "casual-metadata": globals.known_clocks
            }, 200
