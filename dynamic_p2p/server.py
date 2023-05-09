from flask import Flask, request
import Pyro4

app = Flask(__name__)
nodes = {}  # Dictionary to store the node information

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

if __name__ == '__main__':
    app.run()
