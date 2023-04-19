from flask import Blueprint

import globals

show_keys = Blueprint("show_keys", import_name=__name__, url_prefix="/data")

@show_keys.route('/', methods=['GET'])
def get_keys():
    keys = [i for i,j in globals.data.items() if j is not None]
    return {
            "count": len(keys), 
            "keys": keys, 
            "casual-metadata": globals.known_clocks
            }, 200
