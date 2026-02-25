# 🤖 BeetleBot - Complete User Guide

> An autonomous indoor/outdoor robot built on **ROS2 Jazzy**

---

## 📚 **Documentation Inside This Repository**

**Complete documentation is included:**
- [docs_ros2/README.md](docs_ros2/README.md) - Overview of all tools
- [docs_ros2/LYRA_QUICK_REFERENCE.md](docs_ros2/LYRA_QUICK_REFERENCE.md) - Command cheat sheet
- [docs_ros2/LYRA_COMMAND_UTILITY_SETUP.md](docs_ros2/LYRA_COMMAND_UTILITY_SETUP.md) - Detailed setup

**Hardware and system setup** is typically done during initial robot deployment. If you need to reconfigure the robot (WiFi, network, etc.), contact your system administrator.

---

## 🎯 What is BeetleBot?

**BeetleBot** is a mobile robot that can:

- ✅ **Map environments autonomously** - SLAM (Simultaneous Localization & Mapping)
- ✅ **Navigate without human control** - Autonomous path planning with obstacle avoidance
- ✅ **Manual joystick control** - Real-time remote driving
- ✅ **Vision sensing** - Onboard camera for scene understanding
- ✅ **360° obstacle detection** - RPLiDAR scanner
- ✅ **Precise localization** - IMU + encoders + odometry fusion

**Hardware:** Raspberry Pi 5, STM32 microcontroller, RPLiDAR A1, Pi Camera

---

## 🚀 Quick Start (For Existing Users)

### Robot is Running and Ready?

Use the command shortcut utility (fastest way):

```bash
# Enable commands (one-time setup)
source ~/lyra_ws/lyra_commands.sh

# Now use simple commands:
lyra-launch-robot-teleop          # Manual joystick control
lyra-launch-robot-slam            # Map while driving
lyra-launch-robot-nav <map.yaml>  # Autonomous navigation
lyra-battery                      # Check battery voltage
lyra-status                        # Quick health check
lyra-launch-rviz                  # Visualize robot & sensors
```

See [Command Reference](#-command-reference) below for all available commands.

### Or Use Raw ROS2 Commands

If you prefer ROS2 commands directly:

```bash
# Manual control (joystick)
ros2 launch lyra_bringup robot.launch.py mode:=teleop

# Mapping mode
ros2 launch lyra_bringup robot.launch.py mode:=slam

# Autonomous navigation
ros2 launch lyra_bringup robot.launch.py mode:=nav map:=~/maps/house_map.yaml

# With IMU enabled (optional)
ros2 launch lyra_bringup robot.launch.py mode:=teleop imu:=true

# With Camera enabled (optional)
ros2 launch lyra_bringup robot.launch.py mode:=slam camera:=true
```

---

## 📖 Operating Modes Explained

The robot can operate in three main modes, controlled by the `mode` parameter:

### 1. **Teleop Mode (Manual Drive)**

Drive the robot like an RC car using a joystick.

**Start it:**
```bash
lyra-launch-robot-teleop
# Or: ros2 launch lyra_bringup robot.launch.py mode:=teleop
```

**Before driving:**
```bash
lyra-arm                         # Enable motors (REQUIRED)
```

**Joystick Control:**
- Left stick: forward/backward and rotation
- Right triggers: fine movement

**When done:**
```bash
lyra-disarm                      # Disable motors
```

---

### 2. **SLAM Mode (Create Maps)**

Robot maps the environment while you drive it around with the joystick.

**Start it:**
```bash
lyra-launch-robot-slam
# Or: ros2 launch lyra_bringup robot.launch.py mode:=slam
```

**Process:**
1. Drive around your entire space with the joystick
2. Try to revisit areas you've already mapped (improves accuracy)
3. When complete, save the map:
   ```bash
   ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map
   ```
4. You'll get `my_map.pgm` (image) and `my_map.yaml` (config)

**Monitor mapping progress:**
```bash
lyra-launch-rviz    # In another terminal - watch the map build in real-time
```

**Tips:**
- Drive slowly for better accuracy  
- Cover all areas including corners and hallways
- Revisit hallways from different directions to improve map quality

---

### 3. **Nav2 Mode (Autonomous Navigation)**

Robot autonomously drives to target locations using a pre-made map.

**Requirements:**
- A saved map from SLAM mode (e.g., `~/maps/house_map.yaml`)

**Start it:**
```bash
lyra-launch-robot-nav ~/maps/house_map.yaml
# Or: ros2 launch lyra_bringup robot.launch.py mode:=nav map:=~/maps/house_map.yaml
```

**Send robot to a location:**
1. Open RViz: `lyra-launch-rviz` (in another terminal)
2. In RViz window: Click "Nav2 Goal" button  
3. Click on the map where you want robot to go
4. Robot drives there, avoiding obstacles
5. Joystick can override navigation at any time

---

## 🔌 Optional Features (IMU and Camera)

The robot can optionally use:
- **IMU:** Improved accuracy (inertial measurement unit)
- **Camera:** Visual monitoring

By default, both are **OFF** (`imu:=false`, `camera:=false`) for reliability.

### Enable IMU (Better Accuracy)
```bash
ros2 launch lyra_bringup robot.launch.py mode:=teleop imu:=true
ros2 launch lyra_bringup robot.launch.py mode:=slam imu:=true
ros2 launch lyra_bringup robot.launch.py mode:=nav map:=~/maps/house_map.yaml imu:=true
```

### Enable Camera
```bash
ros2 launch lyra_bringup robot.launch.py mode:=slam camera:=true
```

### Enable Both IMU and Camera
```bash
ros2 launch lyra_bringup robot.launch.py mode:=slam imu:=true camera:=true
```

**Note:** IMU helps with odometry and turn accuracy. If the robot spins unexpectedly, try disabling it.

---

---

## 📊 Command Reference

All these commands work after sourcing the command utility:

```bash
source ~/lyra_ws/lyra_commands.sh
```

### **Launch Commands**
```bash
lyra-launch-robot-teleop          # Start in manual control mode
lyra-launch-robot-slam            # Start in mapping mode
lyra-launch-robot-nav <map>       # Start autonomous navigation (requires map file)
lyra-launch-base                  # Just the base (motors, odometry, no SLAM/Nav2)
lyra-launch-rviz                  # Open RViz visualization tool
lyra-launch-bridge                # Just the hardware bridge
```

### **Control Commands**
```bash
lyra-arm                          # Enable motors (REQUIRED before driving)
lyra-disarm                       # Disable motors (do when finished)
lyra-stop                         # EMERGENCY STOP (hard stop)
lyra-ros-mode-on                  # Enable ROS mode
lyra-ros-mode-off                 # Disable ROS mode
```

### **Status/Monitoring Commands**
```bash
lyra-status                       # Quick health check (nodes, armed status, battery)
lyra-battery                      # Current battery voltage in real-time
lyra-armed-status                 # Check if motors are armed
lyra-nodes                        # List all running ROS nodes
lyra-topics                       # List all active ROS topics
lyra-info                         # Robot information
```

###  **Diagnostic Commands**
```bash
lyra-test-hardware                # Test hardware components
lyra-test-connectivity            # Check network connection
lyra-help                         # Show all available commands
```

### **Cleanup Commands**
```bash
lyra-cleanup                      # Stop all nodes gracefully
lyra-kill                         # Force stop all processes
lyra-reset-services              # Reset all services
```

**For complete details, see:** [docs_ros2/LYRA_QUICK_REFERENCE.md](docs_ros2/LYRA_QUICK_REFERENCE.md)

---

## 🔍 Monitoring Robot Status

### Battery Voltage
```bash
lyra-battery                      # Simple check
ros2 topic echo /battery_voltage  # Live updates
```
- **Normal:** 12V-13.2V
- **Low:** 10V-12V (reduce usage)
- **Critical:** Below 10V (may shut down)

### Odometry & Positioning
```bash
ros2 topic echo /odom             # Position and velocity
```

### Sensor Data
```bash
ros2 topic echo /scan             # LiDAR scan data
ros2 topic echo /imu/data_raw     # IMU accelerometer/gyro
```

### RViz Visualization
```bash
lyra-launch-rviz
# Shows:
# - Robot position in real-time
# - LiDAR scans
# - Map (if in SLAM mode)
# - Sensor data
```

---

## ⚠️ Common Issues & Solutions

### "Command not found: lyra-*" or "lyra-help not working"

**Problem:** Commands aren't recognized

**Solution:**
```bash
# Make sure you've sourced the command utility:
source ~/lyra_ws/lyra_commands.sh

# Or add to ~/.bashrc for automatic loading:
echo "source ~/lyra_ws/lyra_commands.sh" >> ~/.bashrc
source ~/.bashrc
```

### Robot doesn't respond to joystick

**Check 1: Is joystick detected?**
```bash
ros2 topic echo /joy
# Should show joystick data when you move sticks/buttons
```

**Check 2: Are motors armed?**
```bash
lyra-armed-status
# Should show armed: true
```

**If not armed:**
```bash
lyra-arm
```

**Check 3: Battery voltage**
```bash
lyra-battery
# Should be above 10V
# Below 10V = low battery, may not respond properly
```

### Robot spins in circles when moving forward

**Likely cause:** Wheels aren't calibrated the same

**Solutions:**
1. Check wheel encoder values: `ros2 topic echo /motor_rpm`
2. Try disabling IMU (it may be causing drift):
   ```bash
   ros2 launch lyra_bringup robot.launch.py mode:=teleop imu:=false
   ```
3. Contact your system administrator if problem persists

### Can't see robot from laptopAI (multi-machine ROS2)

This is a network configuration issue. Typically:
- Robot and laptop need to be on same WiFi
- ROS_DOMAIN_ID must match on both machines  
- Firewall may be blocking communication

Contact your system administrator for network help.

### RViz shows no data/visualization

**Check:**
```bash
# Are robot nodes running?
ros2 node list
# Should show /lyra_node, /ekf_filter_node, etc.

# Are topics publishing?
ros2 topic list | grep -E "odom|scan|imu"
# Should show topics
```

**If no nodes:** The robot may not be running. Try `lyra-launch-robot-teleop`

### Map looks incomplete or has scan artifacts

**This is normal for SLAM!** Try:
1. Drive more slowly
2. Revisit areas to improve mapping
3. Cover all spaces including corners
4. Save the map: `ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map`

### Robot won't start (motors disabled)

**Check:**
```bash
lyra-status
# Look for any error messages
```

**Try:**
```bash
lyra-arm     # Enable motors
```

If still doesn't work:
```bash
lyra-reset-services     # Reset services
lyra-cleanup            # Stop all
```

Then restart: `lyra-launch-robot-teleop`

---

## 📁 What's Included in This Repository

---

## 📁 What's Included

```
BeetleBot/
├── lyra_ws/                    # ROS 2 Workspace
│   ├── lyra_bringup/           # Main robot launcher
│   ├── lyra_slam/              # Mapping system
│   ├── lyra_nav2/              # Autonomous navigation
│   ├── lyra_control/           # Motor control
│   ├── lyra_bridge/            # Hardware communication
│   ├── camera_ros/             # Camera driver
│   ├── sllidar_ros2/           # LiDAR driver
│   └── ...other packages...
│
├── maps/                       # Pre-made maps
│   ├── house_map.pgm           # Map image
│   └── house_map.yaml          # Map config
│
└── docs_ros2/                  # Complete documentation
    ├── LYRA_QUICK_REFERENCE.md # Command cheat sheet
    ├── LYRA_COMMAND_UTILITY_SETUP.md # Setup helpers
    └── ...more docs...
```

---

## 📱 Components & Sensors

| Component | Purpose |
|-----------|---------|
| **Raspberry Pi 5** | Main computer running ROS 2 |
| **STM32 Microcontroller** | Talks to motors and sensors |
| **2× Motors** | Drive the wheels |
| **Encoders** | Count wheel rotations |
| **RPLiDAR A1** | 360° laser scanner - creates map |
| **IMU** | Detects acceleration and rotation |
| **Camera** | Sees the environment visually |
| **Joystick Receiver** | Wireless control input |

---

## ⚡ Power Management

### Battery Status
```bash
ros2 topic echo /battery_voltage
```

### Safe Voltage Levels
- **Normal:** 12V - 13.2V
- **Low:** 10V - 12V (reduce usage)
- **Critical:** Below 10V (will shut down)

### Battery Life
- Typical use: 2-3 hours
- Mapping: 1-2 hours (more CPU usage)
- Navigation: 2-3 hours (less CPU usage)

**Charging:** Use provided charger, full charge takes ~4 hours

---

## 🆘 Getting Help

### Check Robot Health
```bash
# Automated diagnostics
./docs_ros2/lyra_doctor.sh

# Verbose output
./docs_ros2/lyra_doctor.sh --verbose

# Try to fix issues automatically
./docs_ros2/lyra_doctor.sh --fix
```

### See All Running Nodes
```bash
ros2 node list
```

### Check Network Connectivity
```bash
ping 192.168.4.1  # Robot IP
ifconfig          # Your network info
```

### Common Issues
See [Troubleshooting](#troubleshooting) section above

---

## 📚 More Information

- **[Quick Reference Guide](docs_ros2/LYRA_QUICK_REFERENCE.md)** - Print-friendly cheat sheet
- **[Command Utility Setup](docs_ros2/LYRA_COMMAND_UTILITY_SETUP.md)** - Easier commands
- **[Windows Setup Guide](docs_ros2/WINDOWS_WSL_SETUP_GUIDE.md)** - For Windows/WSL users
- **[Static Analysis Report](docs_ros2/STATIC_ANALYSIS_FINDINGS.md)** - Technical details

---

## 🔐 Safety Notes

- ⚠️ Always supervise the robot while it's operating
- ⚠️ Keep hands away from spinning wheels
- ⚠️ Use designated areas for autonomous navigation
- ⚠️ Check battery before extended operations
- ⚠️ Never expose to water unless waterproof version
- ⚠️ Keep WiFi network secure

---

## 📖 Learn ROS 2

- **Official Tutorial:** https://docs.ros.org/en/humble/
- **BeetleBot Specific:** See `docs_ros2/` folder
- **Our SLAM System:** Uses Cartographer
- **Our Navigation:** Uses Nav2 stack

---

## 📧 Support & Maintenance

For questions or issues:
1. Check the **Troubleshooting** section
2. Run `./docs_ros2/lyra_doctor.sh --verbose`
3. Check ROS 2 logs: `ros2 log list`
4. Contact your system administrator

---

## 📝 Software License

- **Robot Code:** GPLv3 (See LICENSE files)
- **ROS 2:** Apache License 2.0
- **Dependencies:** See individual package licenses

---

## 🎉 You're Ready!

Your BeetleBot is ready to explore. Start with **Teleop mode** to get familiar with how it moves, then try **SLAM** to create your first map, and finally **Navigation** for autonomous driving.

**Happy exploring! 🚀**

---

*Last Updated: February 2026*  
*BeetleBot Build: ROS 2 Humble Edition*  
*Maintained by: Team @ Siliris Technologies*
