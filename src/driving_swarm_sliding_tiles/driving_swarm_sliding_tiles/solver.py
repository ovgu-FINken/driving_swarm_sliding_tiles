def find_neighbors(node, edge_list ):
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


# This function finds neighbours of the empty node defined as 'x0'.
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


def solve(data_config, target_config):

    h_list = []
    config_dict = {hash(tuple(data_config)): data_config}

    if data_config == target_config:
        return h_list

    nb = find_neighbors_of_x(data_config.getconfig(), data_config.get_vectors(), data_config.get_edges)
    return recursive(nb, data_config, target_config, config_dict, data_config.get_vectors())






