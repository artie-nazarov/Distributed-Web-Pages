from flask import Blueprint, request, jsonify 

import globals
from globals import storage
from broadcast import broadcast
from math import floor, sqrt
import requests

shard = Blueprint("shard", import_name=__name__)

@shard.route("/admin/view", methods=['GET'])
def get_view():
    return globals.view

@shard.route("/admin/view", methods=['PUT'])
def put_view():
    json = request.get_json()
    view_list = json.get("view")
    # Determine
    n = get_num_shards(view_list)
    shard_list = [[] * n]
    for i, node in enumerate(view_list):
        shard_list[i % n].append(node)
    # Send shard views to each shard

    for shard in shard_list:
        requests.put(f"http://{shard[0]}/shard/admin/view",
                      json={
                          "view": shard,
                          "shards": shard_list
                      })
    return "", 200

@shard.route("/data/<file>")
def put(file):
    # Perform data partitioning
    return "", 200

# Determine nuber of shards
def get_num_shards(l):
    return floor(sqrt(len(l)))