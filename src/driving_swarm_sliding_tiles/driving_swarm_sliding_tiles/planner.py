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
        self.current_trajectory = None

        self.declare_parameter('robot_names')
        self.robots = self.get_parameter('robot_names').get_parameter_value().string_array_value
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
        self.node_list=['n1','n2','n3','n4','n5','n6']
        self.config_list=None
        
    def transform_config(self):
        config=[]
        if None in self.node_occupancies.values():
            return
        for i in self.node_list:
            flag=0
            for x,y in self.node_occupancies.items():
                if y==i:
                    config.append(x)
                    flag=1
                    break
            if flag==0:
                config.append("x0")
        return config 
      
    def actualize_list(self):
        actual_config=self.transform_config()
        if self.node_list[actual_config.index("x0")]==self.config_list[0]:
            self.config_list.pop(0)
        return	
        
    def make_plan(self):
        self.plan=[]
        actual_config=self.transform_config()
        index_x0=self.node_list.index(self.config_list[0])
        for i in range(len(self.robot_list)):
            self.plan.append([])
            if i==index_x0:
                self.plan[i].append(actual_config.index("x0"))
            else:
                self.plan[i].append(i)
        return self.plan 
      
    def timer_cb(self):
        self.get_logger().info(f'agents @: {self.node_occupancies}')
        if None in self.node_occupancies.values():
            return
        #if None in self.config_list:
            #target_config=randomize_mulit_steps()
            #config_list=solve(transform_config,target_config,data_config)
        self.plans = self.make_plan()
        self.execute_plans(self.plans)
       
    def execute_plans(self, plans):
        for k in range(len(plans)):
            robot_plan=[]
            robot_plan=[x[0] for x in groupby(plans[k])]
            self.send_plan_to_robot(robot_plan, self.robots[k])
        str_plan = String()
        str_plan.data = yaml.dump({'plan': plans, 'constraints': nv})
        self.plan_publisher.publish(str_plan)
        self.get_logger().info(f'plans: {plans}')
        self.get_logger().info(f'constraints: {nv}')
        
        
def main():
    rclpy.init()
    node = NavGraphGlobalPlanner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    
    x,y = start_conf()

if __name__ == '__main__':
    main()
