from flask import Blueprint, request, jsonify 

import globals
from globals import storage
from broadcast import broadcast

admin = Blueprint("admin", import_name=__name__, url_prefix="/admin")

@admin.route("/view", methods=['GET'])
def get_view():
    if (globals.view == []):
        return jsonify({"error": "uninitialized"}), 418
    return jsonify(view=globals.view)

@admin.route("/view", methods=['PUT'])
def put_view():
    json = request.get_json()
    #if no view in message, error out
    new_view = json.get('view')
    if new_view is None:
        return jsonify({"error": "bad request"}), 404

    #get the list of nodes being deleted from the view
    delete_nodes = []
    for node in globals.view:
        if node not in new_view:
            delete_nodes.append(node)

    #broadcast a delete to all nodes no longer in the view
    broadcast("admin/view", "DELETE", {}, delete_nodes)
    
    #data to be sent to nodes in the new view
    data ={ 
            "new_view":new_view,
            "data":storage.data, 
            "data_clocks":storage.data_clocks,
            "last_writer":storage.last_writer,
            "known_clocks":globals.known_clocks
           }

    broadcast("admin/new_view", "PUT", data, new_view)

    return "", 200

@admin.route("/view", methods=["DELETE"])
def delete_view():
    """Deletes all data stored on node"""
    storage.data = {}
    storage.data_clocks = {}
    storage.last_writer = {}
    globals.known_clocks = {}
    globals.view = []
    globals.id = -1
    
    return "", 200

@admin.route("/new_view", methods=["PUT"])
def put_new_view():
    """Takes info sent and saves it"""
    json = request.get_json()
    globals.view = json.get('new_view')
    storage.data = json.get('data')
    storage.data_clocks = json.get('data_clocks')
    storage.last_writer = json.get('last_writer')
    globals.known_clocks = json.get('known_clocks')
    globals.id = globals.view.index(globals.addr)
    return "", 200
