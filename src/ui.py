from flask import Blueprint, render_template, request
from .admin import admin

ui = Blueprint("ui", import_name=__name__, url_prefix="/")

@ui.route('/')
def index():
    return render_template('index.html')

@ui.route('/create_view', methods=['POST'])
def create_view():
    addresses = request.form.getlist('addresses[]')

