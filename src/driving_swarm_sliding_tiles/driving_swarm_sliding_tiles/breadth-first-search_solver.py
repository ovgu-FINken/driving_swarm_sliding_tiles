import data_configuration
import networkx as nx


class TreeNode:
    def __init__(self, parent, prev_robot, config):
        self.parent = parent
        self.prev_robot = prev_robot
        self.config = config


def find_neighbors(node, edge_list):
    n_list = []
    for k in edge_list:
        if k[0] == node:
            n_list.append(k[1])
        else:
            if k[1] == node:
                n_list.append(k[0])
    return n_list


def get_robot_node(configuration, robot, node_list, ):
    k = 0
    for i in configuration:
        if i == robot:
            break
        k = k+1
    return node_list[k]


def swap_neighbor(config, node, node_list):
    k = 0
    for i in node_list:
        if i == node:
            break
        k = k+1
    m = 0
    for i in config:
        if i == 'x0':
            config[m] = config[k]
            config[k] = 'x0'
            break
        m = m+1

    return config


# This function finds neighbours of the empty node occupied by 'x0'.
# It returns a list of neighbor nodes.
def find_neighbors_of_x(configuration, node_list, edge_list):
    node = get_robot_node(configuration, 'x0', node_list)
    return find_neighbors(node, edge_list)



def recursive(config, target_config, h_list, config_dict, node_list, edge_list):
    nb = find_neighbors_of_x(config, node_list, edge_list)
    for i in nb:
        t_config = swap_neighbor(config, i, node_list)
        if t_config == target_config:
            h_list.append(i)
            return True

        config_hash = hash(tuple(t_config))
        if config_hash in config_dict.keys():
            continue
        else:
            config_dict.update({config_hash: t_config})
            h_list.append(i)
            if recursive(t_config, target_config, h_list, config_dict, node_list, edge_list):
                return True

            h_list.pop()


# traces the path upwards to the root and returns list of moved robots
def trace_route(treenode):
    h_list = []
    while treenode.parent is not None:
        h_list.append(treenode.prev_robot)
        treenode = treenode.parent

    return h_list


def loop(target_config, config_dict, node_list, edge_list, start_node):

    next_iteration = []
    current_iteration = [start_node]

    while True:

        for k in current_iteration:
            nb = find_neighbors_of_x(k.config, node_list, edge_list)
            for i in nb:
                t_config = swap_neighbor(k.config, i, node_list)
                if t_config == target_config:
                    child = TreeNode(start_node, i, t_config)
                    return trace_route(child)

                config_hash = hash(tuple(t_config))
                if config_hash in config_dict.keys():
                    continue
                else:
                    config_dict.update({config_hash: t_config})
                    child = TreeNode(start_node, i, t_config)
                    next_iteration.append(child)


def solve(init_config, target_config, data_config ):

    start_node = TreeNode(None, None, None)
    start_node.config = init_config

    config_dict = {hash(tuple(init_config)): init_config}

    if init_config == target_config:

        return []

    return loop(target_config, config_dict, data_config.get_vectors(), data_config.get_edges(), start_node)
