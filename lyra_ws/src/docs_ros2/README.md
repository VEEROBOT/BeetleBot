# Lyra V4.4 Fixes

## What's Fixed

1. **rclpy.shutdown() removed** from all nodes (was causing shutdown errors)
2. **Log spam fixed** in cmd_vel_gate (joystick override message now logs once)
3. **EKF IMU config fixed** (vyaw now true, eliminates warning)
4. **Parameters centralized** in lyra_config package

## Installation

### Step 1: Copy Fixed Python Files

```bash
# From your lyra_ws/src directory:

# lyra_bridge
cp lyra_fixes/lyra_bridge/lyra_bridge/node.py lyra_bridge/lyra_bridge/node.py

# lyra_cmd_vel_gate
cp lyra_fixes/lyra_cmd_vel_gate/lyra_cmd_vel_gate/node.py lyra_cmd_vel_gate/lyra_cmd_vel_gate/node.py

# lyra_control
cp lyra_fixes/lyra_control/lyra_control/joy_teleop_wrapper.py lyra_control/lyra_control/joy_teleop_wrapper.py
cp lyra_fixes/lyra_control/lyra_control/cmd_vel_mux.py lyra_control/lyra_control/cmd_vel_mux.py

# lyra_visualization
cp lyra_fixes/lyra_visualization/lyra_visualization/wheel_state_publisher.py lyra_visualization/lyra_visualization/wheel_state_publisher.py

# lyra_localization
cp lyra_fixes/lyra_localization/lyra_localization/wheel_odom_node.py lyra_localization/lyra_localization/wheel_odom_node.py
cp lyra_fixes/lyra_localization/lyra_localization/odom_node.py lyra_localization/lyra_localization/odom_node.py
```

### Step 2: Install lyra_config Package

```bash
# Copy entire lyra_config package to src
cp -r lyra_fixes/lyra_config ~/lyra_ws/src/

# Rebuild
cd ~/lyra_ws
colcon build --packages-select lyra_config
source install/setup.bash
```

### Step 3: Update EKF Config (Quick Fix Without lyra_config)

If you just want the EKF fix without restructuring configs:

Edit `lyra_localization/config/ekf_adaptive.yaml`, find line ~6139:
```yaml
# BEFORE:
imu0_config: [
  false, false, false,
  false, false, false,
  false, false, false,
  false, false, false,   # <-- vyaw was false
  false, false, false
]

# AFTER:
imu0_config: [
  false, false, false,
  false, false, false,
  false, false, false,
  false, false, true,    # <-- vyaw now true
  false, false, false
]
```

### Step 4: Rebuild

```bash
cd ~/lyra_ws
colcon build
source install/setup.bash
```

## Files Changed

| File | Change |
|------|--------|
| lyra_bridge/node.py | Removed rclpy.shutdown() |
| lyra_cmd_vel_gate/node.py | Removed rclpy.shutdown(), added log spam fix |
| lyra_control/joy_teleop_wrapper.py | Removed rclpy.shutdown() |
| lyra_control/cmd_vel_mux.py | Removed rclpy.shutdown() |
| lyra_visualization/wheel_state_publisher.py | Removed rclpy.shutdown() |
| lyra_localization/wheel_odom_node.py | Removed rclpy.shutdown() |
| lyra_localization/odom_node.py | Removed rclpy.shutdown() |
| lyra_config/* | NEW - centralized config package |

## Parameter Consolidation

With lyra_config installed, you can update launch files to load from centralized configs:

```python
# In base.launch.py:
from ament_index_python.packages import get_package_share_directory

lyra_config_dir = get_package_share_directory('lyra_config')
robot_config = os.path.join(lyra_config_dir, 'config', 'robot.yaml')
control_config = os.path.join(lyra_config_dir, 'config', 'control.yaml')
localization_config = os.path.join(lyra_config_dir, 'config', 'localization.yaml')

# Then use in Node():
parameters=[robot_config, control_config]
```

## Testing

After installation, verify:

1. **Clean shutdown** - no more "rcl_shutdown already called" errors
2. **No log spam** - joystick override logs once, not continuously
3. **No EKF warning** - "all update variables are false" warning gone
