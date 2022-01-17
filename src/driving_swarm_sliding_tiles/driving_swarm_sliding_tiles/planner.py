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
        
def main():
    rclpy.init()
    node = NavGraphGlobalPlanner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    
    x,y = start_conf()

if __name__ == '__main__':
    main()
