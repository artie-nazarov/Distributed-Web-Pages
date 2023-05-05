import Pyro4

class Node1:
    def __init__(self):
        self.name = "Node1"
        self.next_node_uri = None

    def set_next_node(self, next_node_uri):
        self.next_node_uri = next_node_uri

    def get_name(self):
        return self.name

    def send_message(self, message):
        if self.next_node_uri:
            print(f"{self.name} is sending '{message}' to next node")
            next_node = Pyro4.Proxy(self.next_node_uri)
            next_node.send_message(message)
            print(f"{self.name} sent the message '{message}'")
        else:
            print(f"{self.name} received the message '{message}'")

# Start Pyro4 Name Server
ns = Pyro4.locateNS()

# Register Node1 with Pyro4 Name Server
node1 = Node1()
daemon = Pyro4.Daemon()
node1_uri = daemon.register(node1)
ns.register("Node1.node1", node1_uri)

# Wait for Node2 to join the network
print("Waiting for Node2 to join the network...")
while True:
    try:
        node2_uri = ns.lookup("Node2.node2")
        break
    except Pyro4.errors.NamingError:
        pass

# Connect to Node2 and send a message
node1.set_next_node(node2_uri)
node1.send_message("Hello from Node1!")

# Start the Pyro4 event loop
daemon.requestLoop()
