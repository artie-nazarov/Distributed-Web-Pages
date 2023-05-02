from flask import Blueprint, render_template, request
from broadcast import broadcast
import globals

ui = Blueprint("ui", import_name=__name__, url_prefix="/")

@ui.route('/')
def index():
    if (globals.view == []):
        return render_template('new_network.html')
    return render_template('network.html', addr = globals.view)


