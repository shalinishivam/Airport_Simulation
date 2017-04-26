import networkx as nx
import json
import random
import csv
import os
import logging as log
from networkx.readwrite import json_graph


def load_airport_connectivity(dataFile):
    print("This function is to load the graph dataset and analyze it")
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
        G1.add_edge(airports_connectivity[0], airports_connectivity[1])
        G1.edge[airports_connectivity[0]][airports_connectivity[1]]['weight'] = 0.1
        # Add random weight to the edges

    return G1


def retrieve_infected_nodes(G, attr_name, attr_value):
    return dict((n, d) for n, d in G.node.items() if (attr_name in d and d[attr_name] == attr_value))


def get_node_props():
    infection_status = ["susceptible", "infected", "cured"]
    node_props = {"infection_status": infection_status[0]}
    log.debug("Filtering criteria is %s ", node_props)
    return node_props


def run_simulation_cycle(G, no_of_days, metrics_filename):
    print("Simulating the nodes")
    # Here write a for loop to go over the number of days, simulation cycle / steps
    # At each function compute the number iterate over each nodes in the graph
    # for each node, assess the probability of infection based on the incoming edges
    # If infected change their states. i.e update the meta data properties

    # Iterate through the nodes which
    #  -  in the infected status and add iterate through the neighbors and update their status
    #  - infected status nodes to be iterated and can that be moved to recovered
    #  -  susceptible and see they change the states as well
    # Compute the edge weights and infect based on the total edge weight
    # Modify the edge weight, based on the nodes infection status

    output_file = open(metrics_filename, 'w+', newline='')
    for i in range(1,no_of_days):
        recal_edge_weights(G)
        simulate_infection(G, 0.10)
        simulate_curing(G)
        compute_metrics(G, metrics_filename)


def simulate_infection(G, prob_cutoff_rate ):
    print("Run infection cycle")
    infected_nodes = retrieve_infected_nodes(G, "infection_status", "infected")
    #print("No:of nodes infected before one step : ", len(infected_nodes))
    susceptible_nodes = retrieve_infected_nodes(G, "infection_status", "susceptible")
    for j in susceptible_nodes:

        in_bound_edges = G.in_edges(j[0])
        #print(j,in_bound_edges)
        summed_prob = 0
        for e in in_bound_edges:
            summed_prob = summed_prob + G.edge[e[0]][e[1]]['weight']
        node_infection_prob = summed_prob / len(in_bound_edges)
        #print(summed_prob, len(in_bound_edges),node_infection_prob, prob_cutoff_rate,G.node[j[0]]["infection_status"])
        if prob_cutoff_rate > node_infection_prob:
            G.node[j[0]]["infection_status"] = "infected"
        #print("---",summed_prob, len(in_bound_edges), node_infection_prob, prob_cutoff_rate, G.node[j[0]]["infection_status"])

    infected_nodes = retrieve_infected_nodes(G, "infection_status", "infected")
    #print("No:of nodes infected after one step : ", len(infected_nodes))

def simulate_curing(G):
    print("Run curing cycle")
    # Curing "curing_rate" number of infected nodes
    infected_nodes = retrieve_infected_nodes(G, "infection_status", "infected")
    no_of_infected_node = len(infected_nodes)
    print("No:of nodes infected before curing : ", no_of_infected_node)
    node_count = random.randint(0, int(no_of_infected_node/3))
    rand_nodes = random.sample(infected_nodes.items(), int(node_count))
    # print("----", node_count, len(rand_nodes))
    for j in rand_nodes:
        print(j[0])
        G.node[j[0]]["infection_status"] = "cured"


    infected_nodes = retrieve_infected_nodes(G, "infection_status", "infected")
    no_of_infected_node = len(infected_nodes)
    print("No:of nodes infected after curing : ", no_of_infected_node)

def find_avg_edge_weights(G):
    infected_nodes = retrieve_infected_nodes(G, "infection_status", "infected")
    # print("No:of nodes infected before one step : ", len(infected_nodes))
    total_weight = 0
    counter = 0
    for n in infected_nodes:
        print(n)
        in_bound_edges = G.in_edges(n)

        for e in in_bound_edges:
            total_weight = total_weight +  G.edge[e[0]][e[1]]['weight']
            counter = counter + 1
    avg_weight = total_weight / counter
    return avg_weight

def recal_edge_weights(G):
    # print("Re-calculating the edge weight", G.out_edges('446'))

    for n in G.nodes_iter(data=True):
        #print(n, n[0])
        out_bound_edges = G.out_edges(n[0])
        if n[1]["infection_status"] == "infected":
            prob_from = 0.50
            prob_to = 0.75
        elif n[1]["infection_status"] == "cured":
            prob_from = 0.25
            prob_to = 0.49
        elif n[1]["infection_status"] == "susceptible":
            prob_from = 0.02
            prob_to = 0.49
        #print(out_bound_edges)
        for e in out_bound_edges:
            new_prob_of_infection = random.uniform(prob_from, prob_to)
            G.edge[e[0]][e[1]]['weight'] = new_prob_of_infection
            G.edge[e[0]][e[1]]['from_node'] = e[0]
            G.edge[e[0]][e[1]]['to_node'] = e[1]
            #print(n, e[0], e[1], new_prob_of_infection)


    write_graph_in_json(G, 'flight_sim_data.json')


def compute_metrics(G, metrics_files):
    print("Computing simulation metrics")
    # ["susceptible", "infected", "cured"]
    infected_nodes = retrieve_infected_nodes(G, "infection_status", "infected")
    no_of_infected_nodes = len(infected_nodes)
    susceptible_nodes = retrieve_infected_nodes(G, "infection_status", "susceptible")
    no_of_susceptible_nodes = len(susceptible_nodes)
    cured_nodes = retrieve_infected_nodes(G, "infection_status", "cured")
    no_of_cured_nodes = len(cured_nodes)
    avg_inbound_edge_weight_infected = find_avg_edge_weights(G)
    print(no_of_susceptible_nodes,no_of_infected_nodes,no_of_cured_nodes,avg_inbound_edge_weight_infected)
    if metrics_files != "":
        # Assume the file exist
        output_file = open(metrics_files, 'a', newline='')
        writer = csv.writer(output_file)
        writer.writerow([no_of_susceptible_nodes,no_of_infected_nodes,no_of_cured_nodes, avg_inbound_edge_weight_infected])
        output_file.close()

def find_graph_properties(G):
    '''
        We are computing the graph properties and returning to dictionary
    '''
    # Printing the graph properties
    print("Analyzing the graph : ")
    graph_properties = {}
    total_no_of_terminals = G.nodes()
    graph_properties["node_count"] = len(total_no_of_terminals)
    print("Graph Node count is:", len(total_no_of_terminals))
    total_no_of_flight_routes = G.edges()
    graph_properties["edge_count"] = len(total_no_of_flight_routes)
    print("Graph edge count is:", len(total_no_of_flight_routes))

    return graph_properties

def infect_nodes(G, node_count):
    # Infect the nodes
    rand_nodes = random.sample(G.nodes(), node_count)
    for j in rand_nodes:
        G.node[j]["infection_status"] = "infected"
        print(j)

def write_graph_in_json(G, filename):
    data = json_graph.node_link_data(G)
    f = open(filename, 'w+')
    json.dump(data, f)
    
def generate_ErdosRenyiGraph(n, p, seed=None):
    """
        This function generates graph of node n with random number of edges, with probability p

        NOTE:This function implementation is inspired from networkx implementaiton nx.gnp_random_graph()and being modified 
        to cater the needs of this simulation. We are overriding the function, so meta data can be updated.

    """
    G = nx.DiGraph()
    # Replace this function with node addition
    compute_metrics(G, n, 0, 0)

    G.name = "gnp_random_graph(%s,%s)" % (n, p)

    if p <= 0:
        return G

    if not seed is None:
        random.seed(seed)

    if G.is_directed():
        edges = itertools.permutations(range(n), 2)
    else:
        edges = itertools.combinations(range(n), 2)

    if p >= 1:
        G.add_edges_from(edges)
        return G

    for e in edges:
        if random.random() < p:
            # print(e[0],e[1], e)
            # Updating the meta data, to keep count of number of in bound and outbound edges
            get_node_props(G, e[0], e[1])
    if G.number_of_nodes() < 1000:
        write_graph_in_json(G, 'ErdosRenyi.json')
    log.info("Number of nodes and edges in Erdos Renyi graph are :%s , %s", G.number_of_nodes(),
             G.number_of_edges())

    return G


if __name__ == "__main__":
    # connectivity = "test.edgelist"
    connectivity = "Airport_Routes_Trimmed.txt"
    G1 = load_airport_connectivity(connectivity)
    infect_nodes(G1, 20)
    run_simulation_cycle(G1,50, 'metrics_files.csv')
    find_avg_edge_weights(G1)
    
    run_erdo_simulation = False
    if run_erdo_simulation == True:
        # Creating a scalable graph model (Erdos-Renyi) and study the  simulation properties
        # Set the probability for ErdosRenyi Graph
        erdos_probability = 0.3
        G2 = generate_ErdosRenyiGraph(345, erdos_probability)
        erdos_renyi_graph_properties = find_graph_properties(G2)
        erdos_metrics_file = 'erdos_renyi_metrics.csv'
        initialize_csv_file(erdos_metrics_file)
        run_simulation_cycle(G2, 50, erdos_metrics_file)
