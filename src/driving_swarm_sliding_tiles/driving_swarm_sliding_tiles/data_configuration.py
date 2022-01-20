import networkx as nx

class Data_config:
    def __init__(self, configuration, graph, nodes, edges):
        self.configuration = configuration
        self.graph = graph
        self.nodes = nodes
        self.edges = edges

    def get_config(self):
        return self.configuration

    def get_edges(self):
        return self.edges

    def get_vectors(self):
        return self.nodes

