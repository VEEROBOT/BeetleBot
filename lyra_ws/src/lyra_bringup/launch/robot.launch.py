#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════╗
║                   LYRA ROBOT - MASTER LAUNCH FILE                        ║
╚══════════════════════════════════════════════════════════════════════════╝

QUICK START:
  Mapping:      ros2 launch lyra_bringup robot.launch.py mode:=slam
  Navigation:   ros2 launch lyra_bringup robot.launch.py mode:=nav map:=$HOME/maps/house_map.yaml
  Manual Drive: ros2 launch lyra_bringup robot.launch.py mode:=teleop

ALL COMMANDS:
  # SLAM (build map while driving)
  mode:=slam imu:=true                          # With IMU (default)
  mode:=slam imu:=false                         # Without IMU : Default
  mode:=slam camera:=true                       # With Camera
  mode:=slam imu:=true camera:=true             # With IMU and Camera
  
  # Navigation (autonomous with saved map)
  mode:=nav map:=/path/to/map.yaml imu:=true    # With IMU
  mode:=nav map:=/path/to/map.yaml   			# Without IMU (default)

  # Teleop (joystick only)
  mode:=teleop imu:=true                        # With IMU
  mode:=teleop                       # Without IMU (default)

STARTUP SEQUENCE:
  1. Base robot launches (motors, odometry, EKF, joystick)
  2. Script waits for EKF to be ready (checks /ekf_filter_node exists)
  3. LiDAR launches
  4. Script waits for LiDAR to publish scans
  5. SLAM/Nav2 launches (only after base + lidar are ready)
  6. Final "READY" message appears

NOTES:
  - Automatic sequencing - no manual delays needed!
  - Each component waits for previous to be ready
  - IMU is ON by default (better accuracy)
  - Save map: ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map

Author: Praveen Kumar / Siliris Technologies Pvt. Ltd. 
"""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    LogInfo,
    ExecuteProcess,
    RegisterEventHandler,
    TimerAction
)
from launch.event_handlers import OnProcessExit
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # ================================================================
    # Launch Arguments
    # ================================================================
    mode_arg = DeclareLaunchArgument(
        'mode',
        default_value='teleop',
        description='Operating mode: slam, nav, or teleop'
    )

    map_arg = DeclareLaunchArgument(
        'map',
        default_value='',
        description='Full path to map YAML file (required for nav mode)'
    )

    imu_arg = DeclareLaunchArgument(
        'imu',
        default_value='false',
        description='Enable IMU sensor fusion (true/false). Default: false'
    )

    camera_arg = DeclareLaunchArgument(
        'camera',
        default_value='false',
        description='Enable camera sensor (true/false)'
    )

    # ================================================================
    # Launch Configurations
    # ================================================================
    mode = LaunchConfiguration('mode')
    map_yaml = LaunchConfiguration('map')
    use_imu = LaunchConfiguration('imu')
    use_camera = LaunchConfiguration('camera')

    # Condition helpers
    is_slam = PythonExpression(["'", mode, "' == 'slam'"])
    is_nav = PythonExpression(["'", mode, "' == 'nav'"])
    is_teleop = PythonExpression(["'", mode, "' == 'teleop'"])

    # ================================================================
    # Package directories
    # ================================================================
    lyra_bringup_dir = get_package_share_directory('lyra_bringup')
    lyra_slam_dir = get_package_share_directory('lyra_slam')
    lyra_nav2_dir = get_package_share_directory('lyra_nav2')

    # ================================================================
    # STEP 1: Launch Base Robot
    # ================================================================
    log_base = LogInfo(msg='[1/4] Launching base robot (motors, odometry, EKF)...')
    
    base_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(lyra_bringup_dir, 'launch', 'base.launch.py')
        ),

        launch_arguments={
            'use_imu': use_imu,
            'use_camera': use_camera
        }.items()
    )

    # ================================================================
    # STEP 2: Wait for Base to be Ready
    # ================================================================
    wait_for_base = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'echo "[2/4] Waiting for base robot to be ready..." && '
            'timeout 30 bash -c "until ros2 node list | grep -q ekf_filter_node; do sleep 0.5; done" && '
            'echo "[2/4] ✓ Base robot ready!" && '
            'sleep 1'
        ],
        output='screen',
        shell=False
    )

    # ================================================================
    # STEP 3: Launch LiDAR
    # ================================================================
    log_lidar = LogInfo(msg='[3/4] Launching LiDAR...')
    
    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(lyra_bringup_dir, 'launch', 'lidar.launch.py')
        )
    )

    launch_lidar_when_ready = RegisterEventHandler(
        OnProcessExit(
            target_action=wait_for_base,
            on_exit=[log_lidar, lidar_launch]
        )
    )

    # ================================================================
    # STEP 4: Wait for LiDAR to be Ready
    # ================================================================
    wait_for_lidar = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'sleep 2 && '
            'echo "[4/4] Waiting for LiDAR to publish scans..." && '
            'timeout 30 bash -c "until ros2 topic list | grep -q /scan; do sleep 0.5; done" && '
            'ros2 topic echo /scan --once --qos-reliability best_effort > /dev/null 2>&1 && '
            'echo "[4/4] ✓ LiDAR ready!" && '
            'sleep 5'
        ],
        output='screen',
        shell=False
    )

    check_lidar_when_launched = RegisterEventHandler(
        OnProcessExit(
            target_action=wait_for_base,
            on_exit=[wait_for_lidar]
        )
    )

    # ================================================================
    # STEP 5: Launch SLAM
    # ================================================================
    log_slam = LogInfo(msg='[5/5] Launching SLAM Toolbox...')
    
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(lyra_slam_dir, 'launch', 'slam_bringup.launch.py')
        )
    )

    launch_slam_when_ready = RegisterEventHandler(
        OnProcessExit(
            target_action=wait_for_lidar,
            on_exit=[log_slam, slam_launch]
        ),
        condition=IfCondition(is_slam)
    )

    # ================================================================
    # STEP 5: Launch Nav2
    # ================================================================
    log_nav = LogInfo(msg='[5/5] Launching Nav2 stack...')
    
    nav_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(lyra_nav2_dir, 'launch', 'full_nav.launch.py')
        ),
        launch_arguments={'map': map_yaml, 'rviz': 'false'}.items()
    )

    launch_nav_when_ready = RegisterEventHandler(
        OnProcessExit(
            target_action=wait_for_lidar,
            on_exit=[log_nav, nav_launch]
        ),
        condition=IfCondition(is_nav)
    )

    # ================================================================
    # FINAL: Ready Messages (delayed to ensure everything initialized)
    # ================================================================
    ready_message_slam = TimerAction(
        period=8.0,  # Wait 8 seconds after lidar ready
        actions=[
            LogInfo(msg=''),
            LogInfo(msg='╔════════════════════════════════════════════════════════╗'),
            LogInfo(msg='║  - LYRA ROBOT READY - SLAM MODE                        ║'),
            LogInfo(msg='║  Drive with joystick to build map                      ║'),
            LogInfo(msg='║  Save map: ros2 run nav2_map_server map_saver_cli \\    ║'),
            LogInfo(msg='║            -f ~/maps/my_map                            ║'),
            LogInfo(msg='╚════════════════════════════════════════════════════════╝'),
            LogInfo(msg=''),
        ],
        condition=IfCondition(is_slam)
    )

    ready_message_nav = TimerAction(
        period=8.0,
        actions=[
            LogInfo(msg=''),
            LogInfo(msg='╔════════════════════════════════════════════════════════╗'),
            LogInfo(msg='║  - LYRA ROBOT READY - NAVIGATION MODE                  ║'),
            LogInfo(msg='║  Set initial pose in RViz, then send navigation goals  ║'),
            LogInfo(msg='║  Joystick can override autonomous navigation           ║'),
            LogInfo(msg='╚════════════════════════════════════════════════════════╝'),
            LogInfo(msg=''),
        ],
        condition=IfCondition(is_nav)
    )

    ready_message_teleop = TimerAction(
        period=3.0,
        actions=[
            LogInfo(msg=''),
            LogInfo(msg='╔════════════════════════════════════════════════════════╗'),
            LogInfo(msg='║  - LYRA ROBOT READY - TELEOP MODE                      ║'),
            LogInfo(msg='║  Drive with joystick (hold LB/deadman button)          ║'),
            LogInfo(msg='╚════════════════════════════════════════════════════════╝'),
            LogInfo(msg=''),
        ],
        condition=IfCondition(is_teleop)
    )

    # ================================================================
    # Build Launch Description
    # ================================================================
    return LaunchDescription([
        # Arguments
        mode_arg,
        map_arg,
        imu_arg,
        camera_arg,

        # Step 1: Launch base
        log_base,
        base_launch,

        # Step 2: Wait for base, then launch lidar
        wait_for_base,
        launch_lidar_when_ready,
        check_lidar_when_launched,

        # Step 3: When lidar ready, launch SLAM or Nav2
        launch_slam_when_ready,
        launch_nav_when_ready,

        # Final: Ready messages
        ready_message_slam,
        ready_message_nav,
        ready_message_teleop,
    ])
