from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import ExecuteProcess
import os

def generate_launch_description():

    slam_params = os.path.join(
        get_package_share_directory('lyra_slam'),
        'config',
        'slam_toolbox.yaml'
    )

    slam_node = ExecuteProcess(
        cmd=[
            'bash', '-c',
            f'ros2 run slam_toolbox async_slam_toolbox_node '
            f'--ros-args -r __node:=slam_toolbox '
            f'--params-file {slam_params} '
            f'-r scan:=/scan '
            f'-r odom:=/odometry/filtered '
            f'2>&1 | grep -v "LaserRangeScan contains"'
        ],
        name='slam_toolbox',
        output='screen',
    )

    lifecycle_mgr = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='slam_lifecycle_manager',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['slam_toolbox'],
            'bond_timeout': 0.0 
        }]
    )

    return LaunchDescription([
        slam_node,
        lifecycle_mgr
    ])

