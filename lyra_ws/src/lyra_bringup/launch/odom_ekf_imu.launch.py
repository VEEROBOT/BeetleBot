#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    localization_dir = get_package_share_directory('lyra_localization')

    ekf_config = os.path.join(localization_dir, 'config', 'ekf.yaml')
    imu_config = os.path.join(localization_dir, 'config', 'imu_filter.yaml')

    return LaunchDescription([

        # ------------------------------------------------
        # IMU Filter (Madgwick)
        # ------------------------------------------------
        Node(
            package='imu_filter_madgwick',
            executable='imu_filter_madgwick_node',
            name='imu_filter',
            parameters=[imu_config],
            remappings=[
                ('imu/data_raw', '/imu/data_raw'),
                ('imu/data', '/imu/data')
            ],
            output='screen'
        ),

        # ------------------------------------------------
        # EKF Localization
        # ------------------------------------------------
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_config]
        ),
    ])
