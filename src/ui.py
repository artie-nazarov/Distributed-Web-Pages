from flask import Blueprint, render_template, request, Response, redirect
from broadcast import broadcast
import globals
from globals import storage
import requests
import base64

ui = Blueprint("ui", import_name=__name__, url_prefix="/")

@ui.route('/')
def index():
    if (globals.view == []):
        return render_template('new_network.html', addrs=[globals.addr])
    return render_template('searchbar.html',files=storage.get_keys())

@ui.route('/edit/<file>')
def edit_file(file):
    return render_template("docedit.html", file=storage.data.get(file))

@ui.route('/tmp')
def tmp():
    return render_template("network.html")

@ui.route('/network')
def network_page():
    return render_template('new_network.html', addrs= globals.view, )

@ui.route('/view/<file>')
def view_file(file):
    target = f"http://{globals.addr}/data/{file}"
    r = requests.get(target, json={"causal-metadata":{}}, timeout=30)
    res = r.json()
    if res:
        data = res['val']['data'].encode(globals.DATA_ENCODING)
        return Response(data, mimetype=res['val']['dtype'])
    
@ui.route('/upload_file', methods=["POST"])
def upload_file():
    filename = request.files["filename"].filename
    dtype = request.files["filename"].content_type
    data = request.files["filename"].read().decode(globals.DATA_ENCODING)
    target = f"http://{globals.addr}/data/{filename}"
    r = requests.put(target, json={"val": {"data":data, "dtype":dtype}, "causal-metadata":{}}, timeout=60)
    return redirect(f'http://{globals.addr}')