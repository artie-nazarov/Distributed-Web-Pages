from flask import Blueprint, render_template, request
from broadcast import broadcast
import globals

ui = Blueprint("ui", import_name=__name__, url_prefix="/")

@ui.route('/')
def index():
    if (globals.view == []):
        return render_template('index.html')    
    
    return render_template('init.html', addr = globals.view)

# @ui.route('/create_view', methods=['GET'])
# def create_view():
#     return render_template('init.html', addr = globals.view)

