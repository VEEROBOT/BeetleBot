#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    ekf_config = PathJoinSubstitution([
        FindPackageShare('lyra_localization'),
        'config',
        'ekf.yaml'
    ])

    wheel_odom_node = Node(
        package='lyra_localization',
        executable='wheel_odom_node',
        name='wheel_odometry',
        output='screen',
        respawn=True,
        respawn_delay=2.0
    )

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config],
        respawn=True,
        respawn_delay=2.0
    )

    return LaunchDescription([
        wheel_odom_node,
        ekf_node
    ])
