import os 

from flask import Flask, request

from client_side import client_side
from admin import admin
from replication import replication
from show_keys import show_keys
from ui import ui
import globals

app = Flask(__name__)

# @app.before_request
# def check_initialized():
#     if globals.id == -1:
#         if request.path == "/admin/view" or request.path == "/admin/new_view":
#             pass
#         else:
#             return {"error":"uninitialized"}, 418

app.register_blueprint(ui)
app.register_blueprint(client_side, url_prefix="/data")
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(show_keys, url_prefix="/data")
app.register_blueprint(replication)


if __name__ == "__main__":
    try: 
        globals.addr = os.environ['ADDRESS']
    except:
        print("NO ADDRESS FOUND")
        exit(1)
    app.run(host="0.0.0.0", port=8080)
