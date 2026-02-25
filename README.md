# 🤖 BeetleBot - User Guide

> An autonomous indoor/outdoor robot built on ROS2 (Robot Operating System 2)

---

## 📋 Quick Overview

**BeetleBot** is a small differential-drive robot that can:

- ✅ **Map your space** - Create maps while driving around
- ✅ **Navigate autonomously** - Drive to locations automatically  
- ✅ **Manual control** - Drive it like an RC car with a joystick
- ✅ **See the environment** - Camera for visual feedback
- ✅ **Detect obstacles** - 360° LiDAR scanner
- ✅ **Know its position** - IMU and encoders for precise movement

**What's inside:** Raspberry Pi 5, STM32 microcontroller, RPLiDAR A1, Pi Camera, and more.

---

## 🚀 Getting Started (5 Minutes)

### Step 0: Check Your Hardware

Before starting, make sure you have:

- ✓ BeetleBot robot (powered on)
- ✓ **Joystick controller** (wireless recommended)
- ✓ **Computer running ROS 2 Humble** (Ubuntu 22.04 or WSL2)
- ✓ **Network wireless connection** between computer and robot
- ✓ Maps folder (included if you want autonomous navigation)

### Step 1: Connect to the Robot's WiFi Network

The robot broadcasts its own WiFi network:

- **Network name:** `LYRA-xxxx` (where xxxx is a unique ID)
- **Password:** Check the label on your robot or ask your administrator

Once connected, open a terminal and test the connection:

```bash
ping 192.168.4.1
# Should see replies like: 64 bytes from 192.168.4.1
```

### Step 2: Set Up Your Computer

Install ROS 2 Humble on your computer:

```bash
# For Ubuntu 22.04
sudo apt update
sudo apt install ros-humble-desktop

# Verify installation
source /opt/ros/humble/setup.bash
ros2 --version  # Should show version info
```

**For Windows users:** Use WSL 2 with Ubuntu 22.04. See [Windows Setup Guide](docs_ros2/WINDOWS_WSL_SETUP_GUIDE.md)

### Step 3: Get the Robot Code

Clone the repository:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/VEEROBOT/BeetleBot.git
cd ..

# Build the workspace
colcon build --symlink-install
source install/setup.bash
```

### Step 4: Launch Your Robot!

Pick one of these options:

#### **Manual Control (Easiest - Start Here!)**
```bash
ros2 launch lyra_bringup robot.launch.py mode:=teleop
```
- **Connect your joystick**
- **Left stick:** Move forward/backward and turn
- **Done!** Your robot should respond to the joystick

#### **Mapping Mode (Create a Map)**
```bash
ros2 launch lyra_bringup robot.launch.py mode:=slam
```
- Drive the robot around your space using the joystick
- It creates a map as it moves
- **Save the map when done:**
  ```bash
  ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map
  ```

#### **Autonomous Navigation (Advanced)**
```bash
ros2 launch lyra_bringup robot.launch.py mode:=nav map:=~/maps/house_map.yaml
```
- Uses a saved map to drive automatically
- Point-to-point navigation with obstacle avoidance
- See [Navigation Guide](#navigation-guide) below

---

## 🎮 Operating Modes Explained

### 1. **Teleop (Manual Drive)**
- Drive the robot like an RC car
- Use joystick for full control
- Perfect for testing and learning

**Command:**
```bash
ros2 launch lyra_bringup robot.launch.py mode:=teleop
```

**Joystick Mapping:**
- **Left Stick Up/Down:** Move forward/backward
- **Left Stick Left/Right:** Rotate left/right
- **Right Triggers:** Fine movement control

---

### 2. **SLAM (Simultaneous Localization and Mapping)**
- Robot creates a map while you drive it around
- "Sees" the environment with LiDAR
- Understands its own position

**Command:**
```bash
ros2 launch lyra_bringup robot.launch.py mode:=slam
```

**What to do:**
1. Launch the command above (wait for "READY" message)
2. Drive the robot around your space
3. Try to revisit places you've already mapped (helps improve map quality)
4. When done, save the map:
   ```bash
   ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map
   ```
5. You'll get a `.pgm` image file and a `.yaml` config file

**Tips:**
- Drive slowly for better accuracy
- Cover all areas you want to navigate
- Revisit hallways from different directions

---

### 3. **Nav2 (Autonomous Navigation)**
- Robot automatically drives to a target location
- Avoids obstacles using the LiDAR
- Finds the best path around obstacles

**Requirements:**
- A saved map from SLAM mode

**Command:**
```bash
ros2 launch lyra_bringup robot.launch.py mode:=nav map:=~/maps/house_map.yaml
```

**How to send a goal:**
1. Window opens showing the map
2. Click on the map to place the goal
3. Robot drives there automatically
4. It avoids obstacles if they appear

---

## 🔧 Enabling Optional Sensors

### With IMU (Better Accuracy)
```bash
ros2 launch lyra_bringup robot.launch.py mode:=teleop imu:=true
```
- More stable movement
- Better odometry tracking

### With Camera
```bash
ros2 launch lyra_bringup robot.launch.py mode:=slam camera:=true
```
- View live camera feed
- Useful for visual inspection

### With Both IMU and Camera
```bash
ros2 launch lyra_bringup robot.launch.py mode:=slam imu:=true camera:=true
```

---

## 📊 Monitoring Robot Status

### Battery Level
```bash
# See the battery voltage live
ros2 topic echo /battery_voltage
```
- Voltage reading updates every second
- **Alert:** Below 10V, robot may shut down

### Speed and Rotation
```bash
# See current speeds
ros2 topic echo /odometry/filtered
```

### LiDAR Scans
```bash
# See what LiDAR detects
ros2 topic echo /scan | head -5
```

### Motor RPM
```bash
ros2 topic echo /motor_rpm
```

### RViz Visualization (See Everything Visually!)
```bash
# While robot is running, in a new terminal:
ros2 launch lyra_visualization rviz.launch.py
```
- See the map being created
- See robot position
- Monitor sensor data
- Very helpful for SLAM and navigation

---

## ❌ Troubleshooting

### "Connection refused" when trying to control robot
**Solution:**
- Check WiFi connection to robot network
- Verify robot IP: `ping 192.168.4.1`
- Check if robot is powered on

### Robot doesn't move with joystick
**Solution:**
- Check joystick is detected: `ros2 topic echo /joy`
- Check battery level
- Restart robot and try again

### Map looks weird or incomplete
**Solution:**
- Save and retry SLAM
- Drive more slowly
- Make sure you cover all areas
- Check LiDAR is working: `ros2 topic echo /scan`

### "Mode not recognized"
**Solution:**
- Use exactly: `teleop`, `slam`, or `nav`
- Example: `ros2 launch lyra_bringup robot.launch.py mode:=teleop`

### Robot keeps turning left/right
**Solution:**
- IMU may need calibration
- Try without IMU first: `mode:=teleop imu:=false`
- Call your system administrator

---

## 🗺️ Navigation Guide

### Step-by-Step Autonomous Navigation

**Phase 1: Create a Map (First Time Only)**
```bash
# Terminal 1
ros2 launch lyra_bringup robot.launch.py mode:=slam

# Terminal 2 (after map is good)
ros2 run nav2_map_server map_saver_cli -f ~/maps/house_map
```

**Phase 2: Use the Map**
```bash
ros2 launch lyra_bringup robot.launch.py mode:=nav map:=~/maps/house_map.yaml
```

**Phase 3: Send Navigation Goals**

Option A - Using RViz (Visual):
```bash
ros2 launch lyra_visualization rviz.launch.py
# Click "2D Pose Estimate" to set start location
# Click "Nav2 Goal" to set target location
```

Option B - Command Line:
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{goal_pose: {pose: {position: {x: 2.0, y: 1.0, z: 0}, orientation: {w: 1.0}}}}"
```

---

## 🛠️ Command Cheat Sheet

For quick commands without remembering long ROS syntax, use the provided command utility:

```bash
# Activate command shortcuts
source ~/ros2_ws/install/setup.bash

# Now use simple commands:
lyra-launch-robot-teleop      # Manual control
lyra-launch-robot-slam         # Mapping mode
lyra-launch-robot-nav          # Navigation mode
lyra-monitor-battery           # Check battery
lyra-monitor-imu               # Check IMU data
lyra-stop-robot                # Emergency stop
lyra-cleanup                   # Clean up all processes
```

See [Command Utility Reference](docs_ros2/LYRA_QUICK_REFERENCE.md) for full list.

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
