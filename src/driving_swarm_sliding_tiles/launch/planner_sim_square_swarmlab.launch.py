#!/usr/bin/env python

import os
import yaml

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, OpaqueFunction, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, TextSubstitution
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def controller_spawning(context, *args, **kwargs):
    controllers = []

    n_robots = LaunchConfiguration('n_robots').perform(context)
    robots_file = LaunchConfiguration('robots_file').perform(context)
    use_sim_time = TextSubstitution(text='true')
    node_file = LaunchConfiguration('node_file').perform(context)
    with open(robots_file, 'r') as stream:
        robots = yaml.safe_load(stream)
        
    controllers.append(Node(
       package='driving_swarm_sliding_tiles',
       executable='planner',
       parameters=[{
        'use_sim_time': use_sim_time,
        'robot_names': [robot['name'] for robot in robots[:int(n_robots)]],
        'tiling': LaunchConfiguration('tiling'),
        'nodes_file': node_file,
        # graph file can either be a .yaml for a map, or a file containing an xml-representation for the graph
        'graph_file': os.path.join(
           get_package_share_directory('driving_swarm_bringup'),
           'maps',
           'swarmlab-2022-05-03.yaml'),
        }],
       output='screen',
    ))
    
    for robot in robots[:int(n_robots)]:
        controllers.append(Node(
           package='driving_swarm_nav_graph',
           executable='nav_graph_planner',
           namespace=robot['name'],
           parameters=[{
            'use_sim_time': use_sim_time,
            'vehicle_model': 3,
            'turn_radius': 0.2,
            'turn_speed': 1.0,
            'step_size': 0.1,
            'tiling': LaunchConfiguration('tiling'),
            # graph file can either be a .yaml for a map, or a file containing an xml-representation for the graph
            'graph_file': os.path.join(
               get_package_share_directory('driving_swarm_bringup'),
               'maps',
               'swarmlab-2022-05-03.yaml'),
            }],
           output='screen',
        ))
        controllers.append(Node(
           package='trajectory_follower',
           executable='trajectory_follower',
           namespace=robot['name'],
           parameters=[
              {
                  "use_sim_time": use_sim_time,
                  "dt": 2.0,
                  "w1": 0.5,
                  "w2": 0.5,
                  "fail_radius": 0.3
              }
           ],
           output='screen',
        ))
    
    return controllers


def generate_launch_description():

    args = {
         'behaviour': 'false',
         'world': 'swarmlab-2022-05-03.world',
         'map': os.path.join(get_package_share_directory('driving_swarm_bringup'), 'maps' ,'swarmlab-2022-05-03.yaml'),
         'robots_file': os.path.join(get_package_share_directory('driving_swarm_sliding_tiles'), 'params', 'swarmlab-2022-05-03_square.yaml'),
         'rosbag_topics_file': os.path.join(get_package_share_directory('trajectory_follower'), 'params', 'rosbag_topics.yaml'),
         'qos_override_file': os.path.join(get_package_share_directory('experiment_measurement'), 'params', 'qos_override.yaml'),
         'node_file': os.path.join(get_package_share_directory('driving_swarm_sliding_tiles'), 'params', 'knoten_swarmlab.txt')
    }
    multi_robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('driving_swarm_bringup'), 'launch', 'multi_robot.launch.py')),
        launch_arguments=args.items())


    declare_tiling_cmd = DeclareLaunchArgument(
        'tiling',
        default_value='square'
    )

    ld = LaunchDescription()
    ld.add_action(declare_tiling_cmd)
    ld.add_action(multi_robot_launch)
    ld.add_action(OpaqueFunction(function=controller_spawning))
    return ld
