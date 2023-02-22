import random
import time
from collections import defaultdict

class GossipNode:
    def __init__(self, id, neighbors):
        self.id = id
        self.neighbors = set(neighbors)
        self.status = "alive"
        self.leader = None
        self.gossip_counter = 0
        self.gossip_time = time.time()
        self.message_queue = []

    def add_neighbor(self, node_id):
        self.neighbors.add(node_id)

    def remove_neighbor(self, node_id):
        self.neighbors.discard(node_id)

    def gossip(self, network):
        if self.status == "dead":
            return

        # Check if gossip time has elapsed
        if time.time() - self.gossip_time >= 1:
            self.gossip_time = time.time()
            self.gossip_counter += 1

            # Add a message to the message queue
            self.message_queue.append((self.id, self.gossip_counter))

            # Send a message to a random neighbor
            neighbor_id = random.choice(list(self.neighbors))
            neighbor = network[neighbor_id]
            neighbor.receive_message(self.id, self.gossip_counter)

            # Check if the leader has been elected
            if self.leader is None:
                self.check_leader()

    def receive_message(self, sender_id, gossip_counter):
        if self.status == "dead":
            return

        # Add the message to the message queue
        self.message_queue.append((sender_id, gossip_counter))

        # Check if the leader has been elected
        if self.leader is None:
            self.check_leader()

    def check_leader(self):
        message_counts = defaultdict(int)
        for sender_id, gossip_counter in self.message_queue:
            message_counts[sender_id] += 1

        max_count = max(message_counts.values())
        leader_candidates = [node_id for node_id, count in message_counts.items() if count == max_count]

        # If this node is a candidate for leader, update its leader status
        if self.id in leader_candidates:
            self.leader = self.id
        else:
            self.leader = random.choice(leader_candidates)

        # Broadcast leader status to all neighbors
        for neighbor_id in self.neighbors:
            neighbor = network[neighbor_id]
            neighbor.receive_leader(self.id, self.leader)

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

    def die(self):
        self.status = "dead"
        for neighbor_id in self.neighbors:
            neighbor = network[neighbor_id]
            neighbor.remove_neighbor(self.id)

# Set up the network
network = {}
for i in range(10):
    neighbors = set(random.sample(range(10), random.randint(1, 3)))
    node = GossipNode(i, neighbors)
    network[i] = node
    for neighbor_id in neighbors:
        neighbor = network[neighbor_id]
        neighbor.add_neighbor(i)

# Choose a random subset of nodes to be Byzantine
num_byzantine_nodes = 3
byzantine_nodes = set(random.sample(range(10), num_byzantine_nodes))
print("Byzantine nodes:", byzantine_nodes)

# Start the gossip process
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
