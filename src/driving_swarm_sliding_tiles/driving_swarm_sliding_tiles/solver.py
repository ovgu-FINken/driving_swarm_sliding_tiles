import data_configuration
import networkx as nx

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
        if i is node:
            break
        k = k+1
    m = 0
    for i in config:
        if i == 'x0':
            config[m] = config[k]
            config[k] = 'x0'
        m = m+1

    return config


# This function finds neighbours of the empty node occupied by 'x0'.
# It returns a list of neighbor nodes.
def find_neighbors_of_x(configuration, node_list, edge_list):
    node = get_robot_node(configuration, 'x0', node_list)
    return find_neighbors(node, edge_list)


def recursive(nb, config, target_config, h_list, config_dict, node_list):
    for i in nb:
        t_config = swap_neighbor(config, i, node_list)
        if t_config == target_config:
            h_list.append(i)
            return True

        config_hash = hash(tuple(t_config))
        if config_hash in config_dict:
            continue
        else:
            config_dict.update({config_hash: t_config})
            h_list.append(i)
            if recursive(nb, t_config, target_config, h_list, config_dict):
                return True

            h_list.pop()


def solve(init_config, target_config, data_config ):

    h_list = []
    config_dict = {hash(tuple(init_config)): init_config}

    if init_config == target_config:
        return h_list

    nb = find_neighbors_of_x(data_config.get_config(), data_config.get_vectors(), data_config.get_edges)
    return recursive(nb, init_config, target_config, config_dict, data_config.get_vectors())

##########################################################################################################################

#Endconfiguration with 5 robots
placement_list = ['x0','r1','r2','r3','r4','r5']
E5 = nx.Graph()
nodes = ['n1','n2','n3','n4','n5','n6']
E5.add_nodes_from(nodes)

# neighborhoods (random)
# jede Knoten hat mind. zwei Nachbarn
edge_list = []
list_len = len(edge_list)
#rand_neighb = random.randint(rob_num+1, sum(rob_num+1))
edge_list = [('n1','n2'), ('n1','n3'), ('n1','n4'), ('n2','n3'), ('n2','n4'), ('n3','n4'), ('n3','n5'), ('n3','n6'), ('n4','n5'), ('n4','n6'),('n5','n6')]
E5.add_edges_from(edge_list)

testconfig = ['r2', 'r1', 'r4', 'r5', 'x0']
testdata = data_configuration.Data_config(testconfig, E5, nodes, edge_list)


print(solve(testconfig, placement_list, testdata))





