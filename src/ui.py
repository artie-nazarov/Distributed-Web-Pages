from flask import Blueprint, render_template, request, redirect, url_for
from broadcast import broadcast
import globals

ui = Blueprint("ui", import_name=__name__, url_prefix="/")

@ui.route('/')
def index():
    if (globals.view == []):
        return render_template('new_network.html')
    return redirect(url_for('searchbar'))

@ui.route('/search')
def searchbar():
    return render_template('searchbar.html', keys=globals.data.keys())
