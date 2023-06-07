from flask import Blueprint, request, jsonify 

import globals
from globals import storage
from broadcast import broadcast, broadcast_shards
from math import floor, sqrt
import requests

shard = Blueprint("shard", import_name=__name__)

@shard.route("/admin/view", methods=['GET'])
def get_view():
    return globals.shard_view

@shard.route("/admin/view", methods=['PUT'])
def put_view():
    json = request.get_json()
    view_list = json.get("view")
    # Determine
    n = get_num_shards(view_list)
    shard_list = [[] for _ in range(n)]
    for i, node in enumerate(view_list):
        shard_list[i % n].append(node)
    # Send shard views to each shard

    for shard in shard_list:
        requests.put(f"http://{shard[0]}/shard/admin/view",
                      json={
                          "view": shard,
                          "shard_view": shard_list
                      })
    return "", 200

@shard.route("/data/<file>", methods=['PUT'])
def put(file):
    json = request.get_json()
    data = json.get("val")['data'].encode(globals.DATA_ENCODING)
    # Perform data partitioning
    data_partitions = storage.prepare_data_partitions(data, len(globals.shard_view))
    dtype = json.get("val")['dtype']
    data = [dict(val=dict(data=i.decode(globals.DATA_ENCODING), dtype=dtype)) for i in data_partitions]
    # Broadcast partitions across all shards
    broadcast_shards(f"shard/data/{file}", "PUT", data, globals.shard_view)

    return "", 200

@shard.route("/data/<file>", methods=['GET'])
def get(file):
    responses = broadcast_shards(f"shard/data/{file}", 'GET', [{} for _ in range(len(globals.shard_view))], globals.shard_view)
    partitions = []
    dtype = None
    for resp in responses:
        data = resp.json().get('val')
        dtype = data['dtype']
        partitions.append(data['data'].encode(globals.DATA_ENCODING))
    data = storage.compose_data_from_partitions(partitions).decode(globals.DATA_ENCODING)
    return dict(val=dict(data=data, dtype=dtype))


# Determine number of shards
def get_num_shards(l):
    return floor(sqrt(len(l)))