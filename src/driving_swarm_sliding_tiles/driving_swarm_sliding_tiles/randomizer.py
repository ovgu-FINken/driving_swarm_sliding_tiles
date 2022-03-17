#!/usr/bin/env python
# coding: utf-8

# In[1]:
#get_ipython().run_line_magic('matplotlib', 'widget')
import breadth_search
import solver
import matplotlib.pyplot as plt
import networkx as nx
import random
import data_configuration


# In[2]:


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
#edge_list = [('n1','n2'), ('n1','n3'), ('n1','n4'), ('n2','n3'), ('n2','n4'), ('n3','n4'), ('n3','n5'), ('n3','n6'), ('n4','n5'), ('n4','n6'),('n5','n6')]
#E5.add_edges_from(edge_list)


# In[3]:


def edges(g, edge_list, nodes):
    a = random.choice(nodes)
    b = random.choice(nodes)
    #TO DO: check: E5 zusammenhängend
    if (a != b) and ((a,b) not in edge_list) and ((b,a) not in edge_list):
        edge_list.append((a, b))
        print(edge_list)
        g.add_edges_from(edge_list)
        print ("n1 = ", g.degree['n1'], ", n2 = ", g.degree['n2'], ", n3 = ", g.degree['n3'], ", n4 = ", g.degree['n4'], ", n5 = ", g.degree['n5'], ", n6 = ", g.degree['n6'])
        for i in nodes:
            while (g.degree[i] < 2):
                edges(g, edge_list, nodes)
    return edge_list


# In[4]:


edge_list = edges(E5, edge_list, nodes)
E5.add_edges_from(edge_list)


# In[5]:


plt.figure()
pos = {'n1': (0,2), 'n2': (1,2), 'n3': (0.25,1), 'n4': (1.25,1), 'n5': (0,0), 'n6': (1,0)}
nx.draw(E5, pos=pos, with_labels=True, edge_color='gray', font_weight='bold', font_color='white')


# In[6]:


#Zuordnung: Index stimmt mit Knotennr überein
def place_robots(placement_list, graph):
    p = placement_list
    rob_list = []
    for i in range(0,6):
        a = random.choice(p)
        rob_list.append(a)
        p.remove(a)

    return rob_list


# In[7]:


s=place_robots(placement_list,E5)
#print(s)


# In[8]:


def find_element(element,set_a):
    k = -1
    for i in set_a:
        k = k+1
        if i == element:
            n = nodes[k]
            return n


# In[9]:


def find_element_tuple(element,set_a):
    element_pair = [item for item in set_a
          if item[0] == element or item[1] == element]
    
    return element_pair


# In[10]:


n = find_element('x0', s)


# In[11]:


def find_node_element(element,set_a):
    for i in set_a:
        if i[0] == element:
            node = i[1]
        if i[1] == element:
            node = i[0] 
    
    return node


# In[12]:


def find_neighbors(set_a, edge_list):
    neighbor_list = []
    p_list = []
    n = find_element('x0',set_a)
    p_list = find_element_tuple(n,edge_list)
    while (len(p_list) != 0):
        nb = find_node_element(n,p_list) 
        neighbor_list.append(nb)
        p_list.pop()
    
    return neighbor_list


# In[13]:


nb_list = find_neighbors(s,edge_list)


# In[14]:


def randomize_one_step(s,edge_list,nb_list):
    #welche Roboter stehen auf den benachbarten Knoten zu x0?
    rob_list = []
    dummy_list = ['n1', 'n2', 'n3', 'n4','n5', 'n6']
    
    for i in nb_list:
        x = 0
        for j in dummy_list:
            if i==j:
                rob = s[x] 
                rob_list.append(rob)
            x = x+1
    c = random.choice(rob_list)
    
    #x0 und c tauschen Plätze (funktioniert)
    k = -1
    for i in s:
        k = k+1
        if i == 'x0':
            s[k] = c
        if i == c:
            s[k] = 'x0'
        
    return s


# In[15]:


#result = randomize_one_step(s,edge_list,nb_list)
#print(result)


# In[16]:


def randomize_multi_steps(s,edge_list,nb_list):
    for x in range(1,5):
        #welche Roboter stehen auf den benachbarten Knoten zu x0?
        rob_list = []
        dummy_list = ['n1', 'n2', 'n3', 'n4','n5', 'n6']

        for i in nb_list:
            x = 0
            for j in dummy_list:
                if i==j:
                    rob = s[x] 
                    rob_list.append(rob)
                x = x+1
        c = random.choice(rob_list)

        #x0 und c tauschen Plätze (funktioniert)
        k = -1
        for i in s:
            k = k+1
            if i == 'x0':
                s[k] = c
            if i == c:
                s[k] = 'x0'

    return s


# In[17]:

#['n1', 'n2', 'n3', 'n4','n5', 'n6']
#['x0','r1','r2','r3','r4','r5']

result = randomize_multi_steps(s,edge_list,nb_list)
print("edge list:")
print(edge_list)
data = data_configuration.Data_config(result, E5, nodes, edge_list)
print("result is:")
print(result)
plist = ['x0','r1','r2','r3','r4','r5']
print("target is")
print(plist)
print('running')
solution = breadth_search.solve(result, plist, data)
print("solution is: ")
print(solution)

plt.show()




# In[ ]:




