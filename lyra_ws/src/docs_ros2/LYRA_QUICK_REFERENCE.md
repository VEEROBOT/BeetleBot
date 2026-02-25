# LYRA ROBOT - QUICK COMMAND REFERENCE

## SETUP
```bash
# One-time setup: source the command utility
source lyra_commands.sh

# Verify setup worked
lyra-help
```

---

## DAILY OPERATIONS

### Start the Robot
```bash
# Teleop mode (joystick controlled)
lyra-launch-robot-teleop

# SLAM mode (build map while driving)
lyra-launch-robot-slam

# Navigation mode (autonomous with pre-built map)
lyra-launch-robot-nav ~/maps/house_map.yaml
```

### Control the Robot
```bash
# ARM the motors (use before driving)
lyra-arm

# DISARM the motors (use when done)
lyra-disarm

# EMERGENCY STOP (immediate halt - no graceful stop)
lyra-stop
```

### Monitor Robot Status
```bash
# One-liner health check
lyra-status

# Watch battery voltage in real-time
lyra-battery

# Watch armed status changes
lyra-armed-status

# Watch wheel speeds
lyra-wheel-rpm
```

---

## DEBUGGING

### Quick Hardware Check
```bash
# Test if all hardware is connected
lyra-test-hardware

# Test ROS network connectivity
lyra-test-connectivity
```

### Detailed Bridge Diagnostics
```bash
# Show all bridge parameters and topics
lyra-debug-bridge

# Get specific parameter
lyra-param-get lyra_bridge control.cmd_vel_timeout_s

# Set a parameter
lyra-param-set lyra_bridge control.cmd_vel_timeout_s 1.0
```

### Live Monitoring
```bash
# Monitor telemetry (RPM, battery, IMU)
lyra-wheel-rpm
lyra-wheel-ticks
lyra-battery
lyra-imu

# Monitor sensor data
lyra-scan          # LiDAR
lyra-odom          # Odometry
lyra-diagnostics   # System diagnostics
```

### View ROS Network
```bash
# List all active nodes
lyra-nodes

# List all topics being published
lyra-topics

# List available services
lyra-services

# Show detailed info about a node
lyra-node-info lyra_bridge
```

---

## TROUBLESHOOTING MATRIX

### "Motor won't move after arming"
```bash
# 1. Check battery voltage
lyra-battery                           # Should be > 10.0V

# 2. Verify ARM command succeeded
lyra-arm                               # Should see "ARM command sent"

# 3. Check armed status is actually true
lyra-armed-status                      # Should show "True"

# 4. Check cmd_vel is being published
lyra-node-info cmd_vel_gate            # Should show /cmd_vel publishing

# 5. Last resort: check bridge health
lyra-debug-bridge
```

### "No telemetry data appearing"
```bash
# 1. Check serial port is accessible
ls -la /dev/ttyAMA0                    # Should exist

# 2. Check bridge is running and connected
lyra-node-info lyra_bridge

# 3. Check for STM32 communication errors
lyra-log-bridge

# 4. Restart bridge node
lyra-kill
sleep 2
lyra-launch-bridge
```

### "EKF node not starting / odometry not working"
```bash
# 1. Check IMU is being published
lyra-imu                               # Should see sensor data

# 2. Check wheel encoder data
lyra-wheel-ticks                       # Should see changing tick values

# 3. Check EKF node is running
ros2 node list | grep ekf              # Should show ekf_filter_node

# 4. Check EKF subscriptions
lyra-node-info ekf_filter_node
```

### "Joystick not responding"
```bash
# 1. Check if joystick is detected
lyra-test-hardware                     # Should show joystick device

# 2. Check joy_node is publishing
ros2 topic echo /joy --once            # Should show button/axis values

# 3. Check permissions
groups | grep input                    # Should include 'input' group
# If not: sudo usermod -a -G input $USER (then logout/login)
```

### "Navigation/SLAM not starting"
```bash
# 1. Check base robot is fully ready
lyra-nodes | grep -E "odom|ekf"        # Should show odometry and EKF nodes

# 2. Check LiDAR is publishing scans
ros2 topic hz /scan                    # Should show frequency > 0

# 3. Check SLAM/Nav2 parameters
ros2 param list /slam_toolbox
ros2 param list /nav2_bringup
```

### "Need to kill everything and start fresh"
```bash
# Graceful shutdown (kills only Lyra nodes)
lyra-kill

# Full cleanup (clears logs and temp files)
lyra-cleanup

# Nuclear reset (kills everything, clears all)
lyra-reset
```

---

## ADVANCED COMMANDS

### Direct ROS 2 Commands (no aliases)
```bash
# List all parameters on a node
ros2 param list /lyra_bridge

# Get specific parameter value
ros2 param get /lyra_bridge serial.port

# Set parameter (hot reload if supported)
ros2 param set /lyra_bridge control.cmd_vel_timeout_s 1.0

# Call a service directly
ros2 service call /lyra/arm std_srvs/srv/Trigger

# Monitor a topic
ros2 topic echo /battery_voltage

# Check topic frequency
ros2 topic hz /wheel_rpm

# Display topic message definition
ros2 interface show std_msgs/msg/Float32MultiArray
```

### Graph Visualization
```bash
# Generate and view ROS2 computation graph
ros2 run rqt_graph rqt_graph

# View transform tree (generates frames.pdf)
lyra-tf-tree

# Live system monitoring
ros2 run rqt_monitor rqt_monitor
```

---

## TYPICAL WORKFLOWS

### Session 1: Teleop Testing
```bash
# Terminal 1: Launch robot
lyra-launch-robot-teleop

# Terminal 2: Monitor battery
lyra-battery

# When robot is running:
lyra-arm                               # ARM
# (use joystick to drive)
lyra-disarm                            # DISARM when done
lyra-kill                              # Shutdown
```

### Session 2: SLAM Mapping
```bash
# Terminal 1: Launch with SLAM
lyra-launch-robot-slam

# Terminal 2: Monitor progress
lyra-nodes | grep slam
ros2 topic echo /map --once            # Check map is being built

# Terminal 3: Monitor hardware
lyra-battery
lyra-wheel-rpm

# When done mapping:
ros2 run nav2_map_server map_saver_cli -f ~/maps/house_map

lyra-kill
```

### Session 3: Navigation Testing
```bash
# Terminal 1: Launch with saved map
lyra-launch-robot-nav ~/maps/house_map.yaml

# Terminal 2: Monitor nav status
ros2 node list | grep nav2

# When robot is running:
lyra-arm
# (In RViz: set initial pose, then click Nav Goal)

# Monitor progress:
lyra-diagnostics
```

### Session 4: Debugging an Issue
```bash
# 1. Quick health check
lyra-status

# 2. Detailed diagnostics
lyra-test-hardware
lyra-test-connectivity

# 3. Check specific subsystem
lyra-debug-bridge              # If bridge issue
lyra-imu                       # If IMU issue
lyra-wheel-ticks              # If odometry issue
lyra-scan                     # If LiDAR issue

# 4. If ROS is stuck
lyra-cleanup
lyra-reset                     # If needed

# 5. Restart specific node
lyra-kill
lyra-launch-base              # or whichever you need
```

---

## SETTING CUSTOM PARAMETERS

### Example: Change cmd_vel timeout
```bash
# Current value:
lyra-param-get lyra_bridge control.cmd_vel_timeout_s

# Set to 1.0 second:
lyra-param-set lyra_bridge control.cmd_vel_timeout_s 1.0

# Note: Some parameters require node restart to take effect
lyra-kill
lyra-launch-base
```

### Example: Change joystick button mapping
```bash
# See current mapping:
lyra-params lyra_control

# Modify joystick.yaml and restart:
lyra-kill
lyra-launch-robot-teleop
```

---

## MAINTENANCE COMMANDS

### Check Disk Usage
```bash
# See how much disk is used
du -sh ~/.ros/log

# Clear old logs (only do when nodes aren't running!)
rm -rf ~/.ros/log/*
```

### System Information
```bash
# Check ROS version
ros2 --version

# Check distro
echo $ROS_DISTRO

# Check available workspace
df -h

# Check CPU/Memory usage while running
htop
```

---

## EMERGENCY PROCEDURES

### Robot is driving erratically
```bash
# Immediate: press joystick deadman button (left shoulder button)
# This stops all motion immediately

# If that doesn't work:
lyra-stop                     # Emergency stop service call

# If still moving:
lyra-kill                     # Force kill all nodes
```

### Serial connection lost
```bash
# Check if port exists:
ls /dev/ttyAMA0

# Check permissions:
ls -la /dev/ttyAMA0

# If permission denied:
sudo chmod 666 /dev/ttyAMA0    # Temporary fix
# OR add user to dialout group:
sudo usermod -a -G dialout $USER
```

### Entire robot unresponsive
```bash
# Power cycle (safest):
# 1. Remove battery
# 2. Wait 5 seconds
# 3. Reattach battery
# 4. SSH back in and restart ROS

# If you can SSH:
lyra-reset
lyra-launch-robot-teleop      # Start fresh
```

---

## USEFUL ALIASES (Add to ~/.bashrc)

```bash
# Add these to your ~/.bashrc for even faster access:
alias lyra='source ~/lyra_ws/lyra_commands.sh'
alias lyra-log='cat ~/.ros/log/latest/*/stdout'
alias lyra-clean-maps='rm -rf ~/maps/*.pgm ~/maps/*.yaml'
alias lyra-check='lyra-test-hardware && lyra-test-connectivity'
```

Then use:
```bash
source ~/.bashrc
lyra                          # Loads all commands
lyra-arm                      # Works everywhere
```

---

## NEED HELP?

```bash
lyra-help                     # Full documentation
lyra-commands                 # List all available commands
lyra-node-info <node>         # Details about a specific node
ros2 -h                       # ROS 2 help
```

---

**Created:** 2026-01-18  
**For:** Lyra V4.4 Robot  
**Last Updated:** Check repository for latest version

