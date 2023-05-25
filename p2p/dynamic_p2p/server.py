from flask import Flask, request
import Pyro4
from app import app, db
from models import User
from sovrin_utils import *
with app.app_context():
    # Perform operations within the application context
    db.create_all()
    
def initialize_database():
    with app.app_context():
        db.create_all()

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

nodes = {}  # Dictionar ay to store the node information

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.next_node_uri = None

    def set_next_node(self, next_node_uri):
        self.next_node_uri = next_node_uri

    def send_message(self, message):
        if self.next_node_uri:
            print(f"Node {self.node_id} is sending '{message}' to next node")
            next_node = Pyro4.Proxy(self.next_node_uri)
            next_node.send_message(message)
            print(f"Node {self.node_id} sent the message '{message}'")
        else:
            print(f"Node {self.node_id} received the message '{message}'")

@app.route('/register', methods=['POST'])
def register_node():
    node_id = request.json['node_id']
    node = Node(node_id)
    nodes[node_id] = node
    return f"Node {node_id} registered successfully."

@app.route('/register/user', methods=['POST'])  # New endpoint for user registration
def register_user():
    # Retrieve the username, password, and email from the request's JSON data
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']

    try:
        # Create a new user object and save it to the database
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()

        return f"User {username} registered successfully."
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {str(e)}"

@app.route('/connect', methods=['POST'])
def connect_nodes():
    sender_id = request.json['sender_id']
    receiver_id = request.json['receiver_id']
    sender_node = nodes.get(sender_id)
    receiver_node = nodes.get(receiver_id)

    if sender_node and receiver_node:
        sender_node.set_next_node(receiver_node.node_id)
        return f"Node {sender_id} connected to Node {receiver_id}."
    else:
        return "Invalid node IDs."

@app.route('/send', methods=['POST'])
def send_message():
    sender_id = request.json['sender_id']
    message = request.json['message']
    sender_node = nodes.get(sender_id)

    if sender_node:
        sender_node.send_message(message)
        return f"Node {sender_id} sent the message '{message}'."
    else:
        return "Invalid node ID."
    
@app.route('/authenticate', methods=['POST'])
def authenticate_user():
    wallet_name = request.json['wallet_name']
    wallet_pass = request.json['wallet_pass']
    their_did = request.json['their_did']

    authenticated = authenticate_user(wallet_name, wallet_pass, their_did)

    if authenticated:
        return "User authenticated successfully."
    else:
        return "Authentication failed."

if __name__ == '__main__':
    app.run(port=5001)
