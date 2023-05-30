from flask import Blueprint, request, jsonify

from clocks import compare_clocks, new_clock
import globals
from globals import storage

#blueprint containing all the endpoints for internal replication
replication = Blueprint("replication", import_name=__name__, url_prefix="/replication")

#implementation of GET on data key
#returns with the data or 404
@replication.route("/<key>", methods=['GET'])
def get_data(key):
    """responds with data if it exists, otherwise 404's"""
    data = storage.get(key)
    if data:
        return jsonify(data)
    else:
        return "", 404

@replication.route("/<key>", methods=['PUT'])
def put_data(key):
    """Writes data to the key, tiebreaks concurrent requests"""
    # Retrieve data from disk into memory
    storage._get_from_disk(key)
    json = request.get_json()
    clock = json.get('clock')
    sender_id = json.get('id')
    storage.data_clocks[key] = storage.data_clocks.get(key, new_clock(1))
    comparison_result = compare_clocks(storage.data_clocks.get(key, [0]), clock)
    if comparison_result == 0:
        #request is concurrent, tiebreak between the two
        if sender_id < storage.last_writer.get(key, len(globals.view)+1):
            storage.data[key] = json.get('val')
            storage.last_writer[key] = sender_id
            globals.combine_clocks(storage.data_clocks[key], clock)
            globals.update_known_clocks({key:storage.data_clocks[key]}) 
    else:
        #request is in our future or comes from local machine, so do it
        storage.data[key] = json.get('val')
        storage.last_writer[key] = sender_id
        globals.combine_clocks(storage.data_clocks[key], clock)
        globals.update_known_clocks({key:storage.data_clocks[key]})
    return jsonify(storage.get(key))

@replication.route("/<key>", methods=['DELETE'])
def delete_data(key):
    """Deletes the data if the clock is in our future, tiebreaks concurrent requests"""
    #if data doesn't exist, return 404
    if globals.data.get(key) == None:
        return "", 404
    
    #get info from request
    json = request.get_json()
    clock = json.get('clock')
    sender_id = json.get('id')
    comparison_result = compare_clocks(globals.data_clocks.get(key, [0]), clock) 
    if comparison_result >= 1:
        #operation is in the causal past of current data or equal, no-op
        pass
    elif comparison_result == 0:
        #concurrent, so we need to tiebreak between the operations
        #if sender_id is less than last writer, it wins
        #otherwise it loses and it's a no-op
        if sender_id < globals.last_writer.get(key):
            globals.data[key] = None
            globals.last_writer[key] = sender_id
            globals.combine_clocks(globals.data_clocks[key], clock)
    else:
        #request is from the future so do it
        globals.data[key] = None
        globals.last_writer[key] = sender_id
        globals.combine_clocks(globals.data_clocks[key], clock)
    return jsonify(
            val = globals.data[key], 
            clock=globals.data_clocks[key],
            last_writer=globals.last_writer[key]
            )
