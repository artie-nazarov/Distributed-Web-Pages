from flask import Blueprint, render_template, request
from broadcast import broadcast
import globals

ui = Blueprint("ui", import_name=__name__, url_prefix="/")

@ui.route('/')
def index():
    if (globals.view == []):
        return render_template('new_network.html', addrs=[globals.addr])
    return render_template('searchbar.html',files=globals.data.keys())

@ui.route('/edit/<file>')
def edit_file(file):
    return render_template("docedit.html", file=globals.data.get(file))

@ui.route('/tmp')
def tmp():
    return render_template("network.html")

@ui.route('/network')
def network_page():
    return render_template('new_network.html', addrs= globals.view, )

@ui.route('/view/<file>')
def view_file(file):
    if file in globals.data.keys():
        return globals.data.get(file)
    else:
        return 404
