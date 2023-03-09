import random
import math

# Define the number of agents
NUM_NODES = 10

# Define the communication range
COMM_RANGE = 5

# Define the number of faulty agents
NUM_BYZANTINE = math.floor(NUM_NODES * 0.3)

# Define the distance function
def euclideanDistance(agent1, agent2):
    dx = agent1['x'] - agent2['x']
    dy = agent1['y'] - agent2['y']
    return (dx ** 2 + dy ** 2) ** 0.5

# Define the communication protocol
def messageBroadcast(agent, message):
    for neighbor in nodes:
        if neighbor != agent and euclideanDistance(agent, neighbor) < COMM_RANGE:
            neighbor['inbox'].append(message)

def receiveMessages(agent):
    messages = agent['inbox']
    agent['inbox'] = []
    return messages

# Implement the flocking behavior
def flock(agent):
    neighbors = []
    for neighbor in nodes:
        if neighbor != agent and euclideanDistance(agent, neighbor) < COMM_RANGE:
            neighbors.append(neighbor)
    alignment = align(agent, neighbors)
    cohesion = cohere(agent, neighbors)
    separation = separate(agent, neighbors)
    agent['vx'] += alignment[0] + cohesion[0] + separation[0]
    agent['vy'] += alignment[1] + cohesion[1] + separation[1]

def align(agent, neighbors):
    avg_vx = 0
    avg_vy = 0
    for neighbor in neighbors:
        avg_vx += neighbor['vx']
        avg_vy += neighbor['vy']
    if len(neighbors) > 0:
        avg_vx /= len(neighbors)
        avg_vy /= len(neighbors)
    return (avg_vx - agent['vx'], avg_vy - agent['vy'])

def cohere(agent, neighbors):
    avg_x = 0
    avg_y = 0
    for neighbor in neighbors:
        avg_x += neighbor['x']
        avg_y += neighbor['y']
    if len(neighbors) > 0:
        avg_x /= len(neighbors)
        avg_y /= len(neighbors)
    return (avg_x - agent['x'], avg_y - agent['y'])

def separate(agent, neighbors):
    avg_dx = 0
    avg_dy = 0
    for neighbor in neighbors:
        dx = agent['x'] - neighbor['x']
        dy = agent['y'] - neighbor['y']
        dist = euclideanDistance(agent, neighbor)
        if dist > 0:
            weight = 1 / dist
            avg_dx += weight * dx
            avg_dy += weight * dy
    return (avg_dx, avg_dy)

# Define the fault-tolerance mechanism
def checkByzantine(agent):
    faulty = False
    for neighbor in nodes:
        if neighbor != agent and euclideanDistance(agent, neighbor) < COMM_RANGE:
            if neighbor['faulty']:
                faulty = True
    return faulty

def recover(agent):
    count = 0
    for neighbor in nodes:
        if neighbor != agent and euclideanDistance(agent, neighbor) < COMM_RANGE:
            if not neighbor['faulty']:
                count += 1
    if count > NUM_NODES - NUM_BYZANTINE - 1:
        agent['faulty'] = False

#--------------------------------------------------------------------------------------
# Set up the initial network distribution
# 10-node network initial distribution as GossipNode object, indexes 0-9
# Index is THE raw value
nodes = []
for i in range(NUM_NODES):
    nodes.append({'x': random.uniform(-10, 10), 'y': random.uniform(-10, 10), 'vx': 0, 'vy': 0, 'inbox': [], 'faulty': False})
    print("NODES: ", nodes)
    print("-----------------------------------")

#--------------------------------------------------------------------------------------
# Choose a random subset of nodes to be Byzantine
# Arbitrary 33% case of BFT, still holds
for i in range(100):
    for agent in nodes:
        if not agent['faulty']:
            flock(agent)
            messageBroadcast(agent, {'x': agent['x'], 'y': agent['y'], 'vx': agent['vx'], 'vy': agent['vy']})
            messages = receiveMessages(agent)
            for message in messages:
                if checkByzantine(message):
                    agent['faulty'] = True
                    break
            if not agent['faulty']:
                recover(agent)
            agent['x'] += agent['vx']
            agent['y'] += agent['vy']
#--------------------------------------------------------------------------------------