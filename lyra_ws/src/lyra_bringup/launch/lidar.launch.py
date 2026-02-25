from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='sllidar_ros2',
            executable='sllidar_node',
            name='sllidar_node',
            output='screen',
            parameters=[{
                'serial_port': '/dev/lyra_lidar',
                'serial_baudrate': 460800,
                'frame_id': 'lidar_link',
                'scan_mode': 'Standard',
            }]
        )
    ])
