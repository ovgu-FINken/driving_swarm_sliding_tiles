import rclpy

from driving_swarm_nav_graph.nav_graph import NavGraphNode

import numpy as np
import traceback
from geometry_msgs.msg import PoseStamped, Pose2D, Quaternion
from nav_msgs.msg import Path
from std_msgs.msg import String, Int32
from std_srvs.srv import Empty
from driving_swarm_nav_graph.utils import *
from functools import partial
from itertools import groupby
from testplanner.data_configuration import *
from testplanner.breadth_search import *

import networkx as nx
import random
import solver

def start_conf():
    placement_list = ['x0','r1','r2','r3','r4','r5']
    E5 = nx.Graph()
    nodes = ['n1','n2','n3','n4','n5','n6']
    E5.add_nodes_from(nodes)
    return E5, placement_list

class NavGraphGlobalPlanner(NavGraphNode):
    def __init__(self):
        super().__init__()
        self.get_logger().info("Starting")
        self.own_frame = "base_link"
        self.reference_frame = "map"
        self.goal = None
        self.started = False
        self.empty_node = 52
        self.config_list = []
        self.mid = 54
        self.current_trajectory = None

        self.declare_parameter('robot_names')
        self.robots = self.get_parameter('robot_names').get_parameter_value().string_array_value
        self.tiling = self.get_parameter('tiling').get_parameter_value().string_value
        qos_profile = rclpy.qos.qos_profile_system_default
        qos_profile.reliability = (
            rclpy.qos.QoSReliabilityPolicy.RMW_QOS_POLICY_RELIABILITY_RELIABLE
        )
        qos_profile.durability = (
            rclpy.qos.QoSDurabilityPolicy.RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL
        )

        self.plans = None
        self.node_occupancies = {}
        self.robot_publishers = {}
        self.get_logger().info(str(self.robots))
        self.plan_publisher = self.create_publisher(String, f'/plan', qos_profile)
        for robot in self.robots:
            self.create_subscription(Int32, f"/{robot}/nav/cell", partial(self.cell_cb,robot=robot), 10)
            self.node_occupancies[robot] = None
            self.robot_publishers[robot] = self.create_publisher(String, f'/{robot}/nav/plan', qos_profile)
        self.create_timer(1.0, self.timer_cb)
        self.nodes=[]
           

    def make_plan(self) -> dict:
        if None in self.node_occupancies.values():
            return
        # create start and goal assignments
        sg = self.node_occupancies.values()
        plans = []
        i = 0
        for x in self.node_occupancies.values():
            plans.append([])
            plans[i].append(x)
            if x == self.config_list[0]:
                if self.tiling == 'hex':
                    plans[i].append(self.mid)
                plans[i].append(self.empty_node)
            else:
                plans[i].append(x)
            i = i+1
        self.get_logger().info(f'{plans}')
        plans = {k: v for k, v in zip(self.node_occupancies.keys(), plans)}
        return plans
      
    def timer_cb(self):
        # if no current plan: make plan
        self.get_logger().info(f'{self.tiling}')
        self.get_logger().info(f'agents @: {self.node_occupancies}')
        self.get_logger().info(f'config_list @: {self.config_list}')
        if None in self.node_occupancies.values():
            return
        if len(self.config_list)==0:
            self.get_logger().info('done!')
            return
        if self.plans is None:
            self.get_logger().info('Start planning')
            edges = []
            graph = nx.Graph()
            if self.tiling == 'hex':
                nodes_hex = [51,42,41,50,55,52]
                for k in range(len(self.robots)+1):
                    self.nodes.append(nodes_hex[k])
                for node in self.nodes[:len(self.nodes)-1]:
                    i = 1
                    for second_node in self.nodes[i:]:
                        if node != second_node:
                            edges.append((node,second_node))
                    i=i+1
            elif self.tiling == 'square':
                nodes_square = [58,61,82,78,79,80,85,81,83]
                for k in range(len(self.robots)+1):
                    self.nodes.append(nodes_square[k])  
                for node in self.nodes:
                    for h in self.g.vertex(node).all_neighbors():
                        if self.g.vertex_index[h] in self.nodes:
                            if (h,node) not in edges:
                                edges.append((node,h))               
            config = []
            for node in self.nodes:
                graph.add_node(node)
                if node in self.node_occupancies.values():
                    keys = list(self.node_occupancies.keys())
                    vals = list(self.node_occupancies.values())
                    config.append(keys[vals.index(node)])
                else:
                    config.append('x0')
                    self.empty_node = node
            for edge in edges:
                graph.add_edge(*edge)
            nx.draw(graph)
            plt.savefig("graph1.png")
            data = Data_config(config,graph,self.nodes,edges)
            target_config = []
            for robot in self.robots:
                target_config.append(str(robot))
            target_config.append('x0')
            self.get_logger().info(f'{edges}')
            self.get_logger().info(f'{self.nodes}')
            self.get_logger().info(f'{config}')
            self.get_logger().info(f'{target_config}')
            self.get_logger().info('Solver is solving!')
            self.config_list = list(solve(config,target_config,data))
            self.get_logger().info('Solver solved riddle to solve!')
            self.get_logger().info(f'{self.config_list}')
            if len(self.config_list) == 0:
                self.get_logger().info('Done!')
                return
            self.plans = self.make_plan()
            self.node_constraints = self.make_node_constraints(self.plans)
            self.get_logger().info(f'{self.plans}')
        if self.config_list[0] not in self.node_occupancies.values() and self.empty_node in self.node_occupancies.values():
            self.empty_node=self.config_list.pop(0)
            if len(self.config_list)==0:
                self.get_logger().info('done!')
                return    
            self.plans=self.make_plan()
            self.node_constraints = self.make_node_constraints(self.plans)
            self.get_logger().info(f'{self.plans}')

        # execute plans
        self.execute_plans(self.plans)


    def cell_cb(self, msg, robot=None):
        if robot in self.node_occupancies and self.plans is not None:
            old = self.node_occupancies[robot]
            new = msg.data
            if new != old:
                # when node occupancies change, we can remove old nodes from plan
                if new in self.plans[robot]:
                    i = self.plans[robot].index(new)
                    self.plans[robot] = self.plans[robot][i:]
                # remove constraint for node no longer occupied
                if old in self.node_constraints and \
                        self.node_constraints[old] and \
                        self.node_constraints[old][0] == robot:
                    del self.node_constraints[old][0]
        self.node_occupancies[robot] = msg.data



    def make_node_constraints(self, plans) -> dict:
        # get preconditions from plan
        node_visits = {}
        # node visits contains the order of robots visiting each node in the graph
        for robot, plan in plans.items():
            for t, n in enumerate(plan):
                if n in node_visits.keys():
                    node_visits[n].append((t, robot))
                else:
                    node_visits[n] = [(t, robot)]
        for k in node_visits.keys():
            node_visits[k] = [robot for _, robot in sorted(node_visits[k], key=lambda x: x[0])]
            node_visits[k] = [x[0] for x in groupby(node_visits[k])]
        return node_visits


       
    def execute_plans(self, plans: dict):

        # send message to all participating robots
        for robot, plan in plans.items():
            nv = self.node_constraints
            robot_plan = []
            for node in plan:
                # do not insert one node twice
                #if robot_plan and node == robot_plan[-1]:
                #    continue
                if nv[node] and nv[node][0] != robot:
                    break
                else:
                    robot_plan.append(node)
                    #del nv[node][0]
            # remove duplicates [1,1,1,2,1,3,3,1] -> [1,2,1,3,1]
            # https://stackoverflow.com/questions/5738901/removing-elements-that-have-consecutive-duplicates
            robot_plan = [x[0] for x in groupby(robot_plan)]
            #self.get_logger().info(f'sending plan to {robot}: {robot_plan}')
            self.send_plan_to_robot(robot_plan, robot)
        str_plan = String()
        str_plan.data = yaml.dump({'plan': plans, 'constraints': nv})
        self.plan_publisher.publish(str_plan)
        self.get_logger().info(f'plans: {plans}')
        self.get_logger().info(f'constraints: {nv}')

    def send_plan_to_robot(self, plan, robot):
        if plan:
            msg = String(data=yaml.dump(plan))
            self.robot_publishers[robot].publish(msg)
        
        
def main():
    rclpy.init()
    node = NavGraphGlobalPlanner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    
    x,y = start_conf()

if __name__ == '__main__':
    main()
