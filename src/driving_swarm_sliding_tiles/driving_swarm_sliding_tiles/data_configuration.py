import networkx as nx

class Data_config:
    def __init__(self, configuration, graph):
        self.configuration = configuration
        self.graph = graph

    def get_config(self):
        return self.configuration

    def get_vectors(self):
        return list(self.graph.nodes)

    def get_edges(self):
        return list(self.graph.edges)

