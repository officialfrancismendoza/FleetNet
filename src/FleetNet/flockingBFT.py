import random
import time
from collections import defaultdict

class FlockNode:
    def __init__(self, id, neighbors, position, velocity):
        self.id = id
        self.neighbors = set(neighbors)
        self.status = "alive"
        self.position = position
        self.velocity = velocity
        self.leader = None
        self.flockmates = set()
        self.message_queue = []

    def add_neighbor(self, node_id):
        self.neighbors.add(node_id)

    def remove_neighbor(self, node_id):
        self.neighbors.discard(node_id)

    def update_position(self):
        self.position = (self.position[0] + self.velocity[0], self.position[1] + self.velocity[1])

    def gossip(self, network):
        if self.status == "dead":
            return

        # Check if leader has been elected
        if self.leader is None:
            self.check_leader()

        # Check if flockmates have been identified
        if not self.flockmates:
            self.identify_flockmates()

        # Update position
        self.update_position()

        # Send position and velocity to flockmates
        message = {"type": "position", "node_id": self.id, "position": self.position, "velocity": self.velocity}
        for flockmate_id in self.flockmates:
            flockmate = network[flockmate_id]
            flockmate.receive_message(self.id, message)

    def receive_message(self, sender_id, message):
        if self.status == "dead":
            return

        message_type = message["type"]
        if message_type == "position":
            position = message["position"]
            velocity = message["velocity"]

            # Add sender to flockmates
            self.flockmates.add(sender_id)

            # Update position and velocity
            self.position = position
            self.velocity = velocity

            # Send position and velocity to all neighbors
            for neighbor_id in self.neighbors:
                if neighbor_id != sender_id:
                    neighbor = network[neighbor_id]
                    neighbor.receive_message(self.id, message)

        elif message_type == "leader":
            leader_id = message["leader_id"]

            # If this node has not yet elected a leader, update its leader status
            if self.leader is None:
                self.leader = leader_id

            # If the received leader is better than the current leader, update the leader status
            if leader_id < self.leader:
                self.leader = leader_id

            # Broadcast leader status to all neighbors
            for neighbor_id in self.neighbors:
                if neighbor_id != sender_id:
                    neighbor = network[neighbor_id]
                    neighbor.receive_message(self.id, message)

    def check_leader(self):
        message = {"type": "leader", "node_id": self.id, "leader_id": self.id}

        # Send message to random neighbor
        neighbor_id = random.choice(list(self.neighbors))
        neighbor = network[neighbor_id]
        neighbor.receive_message(self.id, message)

    def identify_flockmates(self):
        # Collect positions of all neighbors
        positions = []
        for neighbor_id in self.neighbors:
            if neighbor_id != self.id:
                neighbor = network[neighbor_id]
                positions.append(neighbor.position)

        # Calculate distance to all neighbors
        distances = {}
        for position in positions:
            distance = ((position[0] - self.position[0])**2 + (position[1] - self.position[1])**2)**0.5
            distances[position] = distance

        # Find the closest neighbors
        closest_positions = sorted(distances, key=distances.get)[:3]
        flockmates = set()
        for neighbor_id in self.neighbors:
            if neighbor_id != self.id:
                neighbor = network[neighbor_id]
                if neighbor.position in closest_positions:
                    flockmates.add(neighbor_id)

        # Send flockmates to all neighbors
        message = {"type": "flockmates", "node_id": self.id, "flockmates": flockmates}
        for neighbor_id in self.neighbors:
            neighbor = network[neighbor_id]
            neighbor.receive_message(self.id, message)

    def receive_leader(self, sender_id, leader_id):
        if self.status == "dead":
            return

        # If this node has not yet elected a leader, update its leader status
        if self.leader is None:
            self.leader = leader_id

        # If the received leader is better than the current leader, update the leader status
        if leader_id < self.leader:
            self.leader = leader_id

        # Broadcast leader status to all neighbors
        for neighbor_id in self.neighbors:
            if neighbor_id != sender_id:
                neighbor = network[neighbor_id]
                neighbor.receive_leader(self.id, self.leader)

    def receive_message(self, sender_id, message):
        if self.status == "dead":
            return

        message_type = message["type"]
        if message_type == "position":
            position = message["position"]
            velocity = message["velocity"]

            # Add sender to flockmates
            self.flockmates.add(sender_id)

            # Update position and velocity
            self.position = position
            self.velocity = velocity

            # Send position and velocity to all neighbors
            for neighbor_id in self.neighbors:
                if neighbor_id != sender_id:
                    neighbor = network[neighbor_id]
                    neighbor.receive_message(self.id, message)

        elif message_type == "leader":
            leader_id = message["leader_id"]

            # If this node has not yet elected a leader, update its leader status
            if self.leader is None:
                self.leader = leader_id

            # If the received leader is better than the current leader, update the leader status
            if leader_id < self.leader:
                self.leader = leader_id

            # Broadcast leader status to all neighbors
            for neighbor_id in self.neighbors:
                if neighbor_id != sender_id:
                    neighbor = network[neighbor_id]
                    neighbor.receive_message(self.id, message)

        elif message_type == "flockmates":
            flockmates = message["flockmates"]

            # Update flockmates
            self.flockmates.update(flockmates)

            # Send flockmates to all neighbors
            for neighbor_id in self.neighbors:
                if neighbor_id != sender_id:
                    neighbor = network[neighbor_id]
                    neighbor.receive_message(self.id, message)

    def die(self):
        self.status = "dead"
        for neighbor_id in self.neighbors:
            neighbor = network[neighbor_id]
            neighbor.remove_neighbor(self.id)

# Set up the network
network = {}
for i in range(10):
    neighbors = set(random.sample(range(10), random.randint(1, 3)))
    position = (random.uniform(0, 10), random.uniform(0, 10))
    velocity = (random.uniform(-1, 1), random.uniform(-1, 1))
    node = FlockNode(i, neighbors, position, velocity)
    network[i] = node
    for neighbor_id in neighbors:
        neighbor = network[neighbor_id]
        neighbor.add_neighbor(i)

# Choose a random subset of nodes to be Byzantine
num_byzantine_nodes = 3
byzantine_nodes = set(random.sample(range(10), num_byzantine_nodes))
print("Byzantine nodes:", byzantine_nodes)

# Start the flocking process
for i in range(100):
    for node in network.values():
        if node.id in byzantine_nodes:
            # Byzantine node sends random leader to neighbors
            neighbor_id = random.choice(list(node.neighbors))
            neighbor = network[neighbor_id]
            leader_id = random.choice(list(network.keys()))
            neighbor.receive_leader(node.id, leader_id)
        else:
            node.gossip(network)
