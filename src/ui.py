from flask import Blueprint, render_template

ui = Blueprint("ui", import_name=__name__, url_prefix="/")

@ui.route('/')
def index():
    return render_template('index.html')
