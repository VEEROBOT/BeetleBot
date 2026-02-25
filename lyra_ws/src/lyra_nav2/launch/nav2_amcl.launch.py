#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    pkg_share = get_package_share_directory('lyra_nav2')
    params_file = os.path.join(pkg_share, 'config', 'nav2_params.yaml')

    # Launch arguments
    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([

        DeclareLaunchArgument(
            'map',
            description='Full path to map yaml file'
        ),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time'
        ),

        # ----------------------------
        # Map Server
        # ----------------------------
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{
                'yaml_filename': map_yaml,
                'use_sim_time': use_sim_time
            }],
        ),

        # ----------------------------
        # AMCL Localization
        # ----------------------------
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
        ),

        # ----------------------------
        # Planner
        # ----------------------------
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
        ),

        # ----------------------------
        # Controller
        # ----------------------------
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
        ),

        # ----------------------------
        # Behaviors (REPLACES recoveries)
        # ----------------------------
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
        ),

        # ----------------------------
        # BT Navigator
        # ----------------------------
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
        ),

        # ----------------------------
        # Lifecycle Manager (MANDATORY)
        # ----------------------------
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'autostart': True,
                'node_names': [
                    'map_server',
                    'amcl',
                    'planner_server',
                    'controller_server',
                    'behavior_server',
                    'bt_navigator'
                ]
            }],
        ),
    ])
