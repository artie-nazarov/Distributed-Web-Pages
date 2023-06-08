import socket
import uuid
import sys
class Node:
    def __init__(self, ip_address):
        self.node_id = str(uuid.uuid4())
        print(f"Node ID: {self.node_id}")
        self.next_node_address = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_address = ip_address

    def set_next_node(self, next_node_address):
        self.next_node_address = next_node_address

    def get_node_id(self):
        return self.node_id

    def send_message(self, message, target_ip):
        if self.next_node_address:
            print(f"{self.node_id} is sending '{message}' to next node")
            target_address = (target_ip, self.next_node_address[1])
            self.socket.sendto(message.encode(), target_address)
            print(f"{self.node_id} sent the message '{message}'")
        else:
            print(f"{self.node_id} received the message '{message}'")

    def register_node(self):
        print(f"Registered node with ID: {self.node_id}")

    def unregister_node(self):
        pass


if __name__ == '__main__':
    machine_addresses = ['192.168.0.2', '192.168.0.3', '192.168.0.4', '192.168.0.5', '192.168.0.6', '192.168.0.7']
    print("Available machine addresses:")
    for i, address in enumerate(machine_addresses):
        print(f"{i+1}. {address}")

    index = input("Enter the index of the desired IP address: ")
    try:
        index = int(index)
        if index < 1 or index > len(machine_addresses):
            raise ValueError
    except ValueError:
        print("Invalid index. Please provide a valid index.")
        sys.exit(1)

    ip_address = machine_addresses[index - 1]

    port = input("Enter the port number: ")
    try:
        port = int(port)
        if port < 1024 or port > 65535:
            raise ValueError
    except ValueError:
        print("Invalid port number. Please provide a valid port number between 1024 and 65535.")
        sys.exit(1)

    node = Node(ip_address)
    node.socket.bind((ip_address, port))
    node.socket.listen(1)

    print(f"Node listening on port {port}")

    while True:
        conn, addr = node.socket.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode()
                node.send_message(message, ip_address)
                