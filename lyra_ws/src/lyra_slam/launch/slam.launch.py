#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg_share = get_package_share_directory('lyra_slam')
    slam_params = os.path.join(pkg_share, 'config', 'slam_toolbox.yaml')

    lifecycle_mgr = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='slam_lifecycle_manager',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['slam_toolbox']
        }]
    )

    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[slam_params],
            remappings=[
                ('scan', '/scan'),
                ('odom', '/odometry/filtered'),
            ],
        )
    ])
