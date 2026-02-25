#!/usr/bin/env python3
"""
Lyra Robot Base Launch File - Adaptive Sensor Fusion

Production bringup with graceful sensor degradation:
- Robot description + TF
- STM32 bridge
- Joystick control + safety gate
- Adaptive localization (auto-adapts to sensor availability)

Sensor hierarchy:
1. Wheel odometry (REQUIRED)
2. IMU (optional - auto-ignored if fails)
3. Camera (Optional - true by default)
4. LiDAR odometry (Phase 4+ - auto-ignored if unavailable)
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # ================================================================
    # Launch Arguments
    # ================================================================
    use_camera_arg = DeclareLaunchArgument(
        'use_camera',
        default_value='true',
        description='Enable camera sensor'
    )

    use_camera = LaunchConfiguration('use_camera')

    use_imu_arg = DeclareLaunchArgument(
        'use_imu',
        default_value='true',
        description='Enable IMU filter node'
    )

    use_imu = LaunchConfiguration('use_imu')

    # ================================================================
    # Package directories
    # ================================================================
    lyra_control_dir = get_package_share_directory('lyra_control')
    lyra_localization_dir = get_package_share_directory('lyra_localization')
    lyra_bridge_dir = get_package_share_directory('lyra_bridge')

    joystick_config = os.path.join(
        lyra_control_dir, 'config', 'joystick.yaml'
    )

    # Single adaptive EKF config (handles all sensor scenarios)
    ekf_config = os.path.join(
        lyra_localization_dir, 'config', 'ekf_adaptive.yaml'
    )

    imu_config = os.path.join(
        lyra_localization_dir, 'config', 'imu_filter.yaml'
    )
    
    # FIX: Add lyra_bridge params path
    lyra_params = os.path.join(
        lyra_bridge_dir, 'config', 'lyra_params.yaml'
    )

    # ================================================================
    # Robot Description (URDF + static TF)
    # ================================================================
    robot_description = Command([
        'cat ',
        PathJoinSubstitution([
            FindPackageShare('beetlebot_description'),
            'urdf',
            'beetlebot.urdf'
        ])
    ])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False
        }],
        respawn=True,  # ✅ KEEP - Stateless
        respawn_delay=2.0
    )

    wheel_state_publisher = Node(
        package='lyra_visualization',
        executable='wheel_state_publisher',
        name='wheel_state_publisher',
        output='screen',
        respawn=True,  # ✅ KEEP - Visualization only
        respawn_delay=2.0
    )

    # ================================================================
    # STM32 Bridge (Motor Controller + Sensors)
    # ================================================================

    lyra_bridge_node = Node(
        package='lyra_bridge',
        executable='lyra_node',
        name='lyra_bridge',
        parameters=[lyra_params],
        output='screen',
        respawn=True,
        respawn_delay=2.0
    )

    # ================================================================
    # Camera (OPTIONAL)
    # ================================================================
    camera_node = Node(
        package='camera_ros',
        executable='camera_node',
        name='pi_camera',
        output='screen',
        parameters=[{
            'camera': 0,
            'width': 320,
            'height': 240,
            'format': 'BGR888',
            'frame_id': 'camera_optical_link'
        }],
        condition=IfCondition(use_camera),
        respawn=False
    )

    # ================================================================
    # Localization
    # ================================================================
    wheel_odom_node = Node(
        package='lyra_localization',
        executable='wheel_odom_node',
        name='wheel_odometry',
        output='screen',
        respawn=False
    )

    imu_filter_node = Node(
        package='imu_filter_madgwick',
        executable='imu_filter_madgwick_node',
        name='imu_filter',
        parameters=[imu_config],
        output='screen',
        respawn=False,
        condition=IfCondition(use_imu)
    )

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        parameters=[ekf_config],
        output='screen',
        respawn=False
    )

    # ================================================================
    # Joystick Input
    # ================================================================
    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        parameters=[joystick_config],
        output='screen',
        respawn=True,
        respawn_delay=2.0
    )

    teleop_twist_joy_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_twist_joy_node',
        parameters=[joystick_config],
        remappings=[('/cmd_vel', '/cmd_vel_joy')],
        output='screen',
        respawn=True,
        respawn_delay=2.0
    )

    cmd_vel_gate_node = Node(
        package='lyra_cmd_vel_gate',
        executable='cmd_vel_gate',
        name='cmd_vel_gate',
        output='screen',
        respawn=True,
        respawn_delay=1.0
    )

    joy_teleop_wrapper_node = Node(
        package='lyra_control',
        executable='joy_teleop_wrapper',
        name='joy_teleop_wrapper',
        parameters=[joystick_config],
        output='screen',
        respawn=True,
        respawn_delay=2.0
    )

    # ================================================================
    # Launch Order
    # ================================================================
    return LaunchDescription([
        use_camera_arg,
        use_imu_arg,

        # Core robot model
        robot_state_publisher_node,
        wheel_state_publisher,

        # Hardware interface
        lyra_bridge_node,
        camera_node,

        # Localization (wheel MUST start before EKF)
        wheel_odom_node,
        imu_filter_node,
        ekf_node,

        # Human input
        joy_node,
        joy_teleop_wrapper_node,
        teleop_twist_joy_node,
        cmd_vel_gate_node,
    ])
