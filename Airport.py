import networkx as nx
import os
import random
import json
import csv
import logging as log
from networkx.readwrite import json_graph
import itertools

def load_airport_connectivity(dataFile):
    log.info("This function is to load the dataset and analyze it")
    G1 = nx.DiGraph()
    # Read the file and create the nodes
    with open(dataFile) as f:
        lines = f.readlines()

    # Creating the edge
    for line in lines:
        airports_connectivity = line.split()
        log.debug("%s , %s", airports_connectivity[0], airports_connectivity[1])
        # Verify if the nodes exist in the graph, if not add it
        if not G1.has_node(airports_connectivity[0]):
            node_props = get_node_props()
            G1.add_node(airports_connectivity[0], node_props)

        if not G1.has_node(airports_connectivity[1]):
            node_props = get_node_props()
            G1.add_node(airports_connectivity[1], node_props)

        # Create the edge from node[0] to node[1]
        G1.add_edge(airports_connectivity[0],airports_connectivity[1] )
        G1.edge[airports_connectivity[0]][airports_connectivity[1]]['weight'] = 0.1
        # Add random weight to the edges
        # TODO: Add weight and other edge properties


        # Generate target-selection weights, and choose target nodes to infect.
        degrees = network.degree()
        weights = dict()
        for airport, degree in degrees.items():
            weights[airport] = network.out_degree(airport) + \
                               network.in_degree(airport)
        targets = list()
        for ind in range(0, NUM_SIMULATIONS):
            target_round = list()
            while len(target_round) < 20:
                chosen_airport = weighted_random(weights)
                if chosen_airport not in target_round:
                    target_round.append(chosen_airport)
            targets.append(target_round)



    return G1


def retrieve_infected_nodes(G, attr_name, attr_value):
    return dict((n, d) for n, d in G.node.items() if (attr_name in d and d[attr_name] == attr_value))

def get_node_props():
    infection_status = ["susceptible", "infected", "cured"]
    node_props = {"group": infection_status[0]}
    log.debug("Filtering criteria is %s ", node_props)
    return node_props


def simulate_infection(G, no_of_days, metrics_filename):
    # TODO: Write the simulation logic here. Refer add_nodes_in_timestep()
    print("Simulating the nodes")
    # Here write a for loop to go over the number of days, simulation cycle / steps
    # At each function compute the number iterate over each nodes in the graph
        # for each node, assess the probabilit of infection based on the incoming edges
        # If infected change their states. i.e update the meta data properties
    compute_metrics(G,metrics_filename)

def compute_metrics(G, metrics_files):
    print("Computing simulation metrics")

def get_graph_properties(G):
    '''
        Compute the graph properties and return dictionary
        :param G:  Graph for which the properties needs to be assessed
        :return: returns a graph properties dictionary
    '''
    # Print the graph properties, to be used for analysis
    log.info("Analyzing the graph : ")
    graph_properties = {}
    total_no_of_terminals = G.nodes()
    graph_properties["node_count"] = total_no_of_terminals
    log.debug("Graph Node count is: %s", total_no_of_terminals)
    total_no_of_flight_routes = G.edges()
    graph_properties["edge_count"] = total_no_of_flight_routes
    log.debug("Graph edge count is: %s", total_no_of_flight_routes)

    return graph_properties


def write_graph_in_json(G, filename):
    data = json_graph.node_link_data(G)
    f = open(filename, 'w+')
    json.dump(data, f)

if __name__ == "__main__":
    # Setting the default log level to INFO
    log.basicConfig(level=log.INFO)

    # To be used if a subset of stanford dataset to be used
    # connectivity = "test.edgelist"
    connectivity = "Airport_Routes_Trimmed.txt"
    G1 = load_airport_connectivity(connectivity)
    print(get_graph_properties(G1))
    simulate_infection(G1,50,'metrics_files')
    write_graph_in_json(G1, 'flight_sim_data.json')
