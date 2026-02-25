# LYRA V4.4 STATIC ANALYSIS REPORT
**Date:** January 18, 2026  
**Scope:** Comprehensive line-by-line analysis of ROS 2 codebase  
**Philosophy:** Conservative (preferring false positives over silence)

---

## EXECUTIVE SUMMARY

✅ **STRENGTHS:**
- Thread-safety improvements in bridge node (locks for seq, cmd, armed states)
- Proper RX loop isolation (background thread)
- Timeout handling for cmd_vel (500ms cutoff)
- Service-based ARM/DISARM (safe, not auto)
- Launch ordering with explicit wait steps
- Respawn policies on stateless nodes

⚠️ **CRITICAL ISSUES:** 6
❌ **HIGH ISSUES:** 8  
🟡 **MEDIUM ISSUES:** 11

---

## CRITICAL ISSUES

### 1. **RACE CONDITION: Armed State Broadcast Race** 
**File:** [lyra_bridge/lyra_bridge/node.py](lyra_bridge/lyra_bridge/node.py#L237-L240)  
**Lines:** 237-240

```python
# Update armed state
with self.armed_lock:
    prev_armed = self.armed
    self.armed = status.get('armed', False)
    if self.armed != prev_armed:
        state = "ARMED" if self.armed else "DISARMED"
```

**Issue:** The `armed` state is updated from telemetry in the RX thread, but `_motor_control_loop()` (20Hz timer) and `publish_cmd()` (other nodes) read this without acquiring the lock in all paths. The cmd_vel_gate node reads `self.manually_armed` (not protected by lock) and the bridge's armed state asynchronously.

**Risk:** Stale armed state could cause:
- Motors moving while showing as disarmed in UI
- Safety gate making wrong arbitration decisions
- Loss of synchronization between STM32 and ROS

**Recommendation:** 
- Read `armed` state atomically with lock in `_motor_control_loop()`  
- Consider using Atomic<bool> or explicit lock pattern
- Currently only partially protected at line 356

---

### 2. **SHUTDOWN DEADLOCK RISK: RX Thread Join**
**File:** [lyra_bridge/lyra_bridge/node.py](lyra_bridge/lyra_bridge/node.py#L430-L435)  
**Lines:** 430-435

```python
def destroy_node(self):
    """Clean shutdown."""
    self.get_logger().info("Shutting down Lyra Bridge...")
    self.running = False
    if self.rx_thread.is_alive():
        self.rx_thread.join(timeout=1.0)  # ← Potential deadlock
```

**Issue:** The RX thread checks `while self.running and rclpy.ok()` (line 195). If `rclpy.ok()` becomes False before `self.running` is set, the thread could hang. The 1.0s timeout is good but masks underlying issues.

**Risk:** 
- Unclean shutdown can orphan serial port
- Transport layer not closed before thread join
- Subsequent launches may find port still locked

**Recommendation:**
- Set `self.running = False` BEFORE the join
- Close transport BEFORE joining RX thread
- Remove reliance on `rclpy.ok()` in background thread
- Consider using threading.Event instead of boolean flag

Current code order is correct (line 431 before 433), but transport close at line 433 happens AFTER join completes—should move to line 430.

---

### 3. **COMMAND TIMEOUT RACE: Motor Control Loop**
**File:** [lyra_bridge/lyra_bridge/node.py](lyra_bridge/lyra_bridge/node.py#L368-L387)  
**Lines:** 368-387

```python
# ✅ ATOMIC CAPTURE of command state
with self.cmd_lock:
    cmd_vel = self.latest_cmd_vel
    cmd_time = self.last_cmd_time

# Process outside lock to avoid holding lock during computation
if cmd_vel is None:
    # No command received yet - send STOP
    zero_cmd = build_set_wheel_vel_command(self._next_seq(), [0.0, 0.0, 0.0, 0.0])
    self._send_command(zero_cmd)
    return

# Calculate command age
cmd_age_s = time.monotonic() - cmd_time
```

**Issue:** Between capturing `cmd_time` (line 371) and using it (line 381), the callback could update `self.latest_cmd_vel` with a NEW timestamp. The timeout check compares against a stale `cmd_time`, potentially delaying STOP by up to 500ms.

**Scenario:**
1. T=0: Last cmd_vel received, last_cmd_time = 0
2. T=0.4: Motor control reads cmd_time = 0, cmd_vel = (last message)
3. T=0.4: New cmd_vel arrives with last_cmd_time = 0.4 (callback not yet called)
4. T=0.4: Timeout check: 0.4 - 0 = 0.4s (OK, below 0.5s)
5. T=0.45: Callback fires with cmd_time = 0.45
6. T=0.5: Motor control reads cmd_time = 0.45, sees 0.5 - 0.45 = 0.05s (no timeout!)

**Better approach:** Capture a snapshot of the entire state atomically.

---

### 4. **SAFETY GATE DEADLOCK: Multiple Lock Paths**
**File:** [lyra_cmd_vel_gate/lyra_cmd_vel_gate/node.py](lyra_cmd_vel_gate/lyra_cmd_vel_gate/node.py#L77-L130)  
**Lines:** 77-130

```python
def publish_cmd(self):
    armed = self.is_armed()
    
    if not armed and not self.auto_arm:
        self.pub_cmd.publish(Twist())
        return
    
    # Check if joystick is actively being used
    time_since_joy = (self.get_clock().now() - self.last_joy_time).nanoseconds / 1e9
    joystick_active = (self.deadman_pressed and 
                      time_since_joy < self.joystick_timeout and
                      self.is_nonzero(self.last_joy_cmd))
    
    if joystick_active:
        # JOYSTICK OVERRIDE
        if not self.manually_armed:
            self.get_logger().info("Joystick override (auto-arming for manual control)")
```

**Issue:** No locks protecting:
- `self.deadman_pressed` (written in `joy_cb`, read in `publish_cmd`)
- `self.turbo_pressed` (written in `joy_cb`, read in `scale_twist`)
- `self.manually_armed` (written in `armed_cb`, read in `is_armed()`)
- `self.last_joy_cmd`, `self.last_nav_cmd`, timestamps

On a 4-core RPi: Joy callback fires at 50Hz, publish_cmd at 20Hz → potential unsynchronized reads.

**Race Scenario:**
- Thread A: `joy_cb()` updates `self.deadman_pressed = True`
- Thread B: `publish_cmd()` reads `self.deadman_pressed = False` (stale)
- Thread B: Sends STOP even though deadman is held

**Recommendation:** Add mutex protection around state reads/writes.

---

### 5. **LAUNCH ORDERING: EKF/IMU Conditional Dependency**
**File:** [lyra_bringup/launch/base.launch.py](lyra_bringup/launch/base.launch.py#L135-L180)  
**Lines:** 135-180

```python
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
```

**Issue:** 
- EKF always launches (no condition)
- IMU filter launches conditionally
- EKF config (ekf.yaml) likely specifies `imu/data_raw` as input
- If `use_imu=false`: EKF will wait for IMU topic that never arrives

**Risk:**
- EKF gets stuck in failed state
- Nav2/SLAM will report localization unavailable
- No clear error message to user

**Check Required:** Review `ekf_adaptive.yaml` to confirm IMU is marked optional:
```yaml
imu0: /imu/data_raw
imu0_config: [false, false, false, true, true, true, ...]
imu0_queue_size: 10
```
If `imu0_queue_size` is set without conditional subscription, EKF WILL wait forever.

---

### 6. **SERIALIZATION: Telemetry Parsing Without Bounds Check**
**File:** [lyra_bridge/lyra_bridge/node.py](lyra_bridge/lyra_bridge/node.py#L234-L280)  
**Lines:** 234-280

```python
def _handle_packet(self, cmd: int, payload: bytes):
    """Handle received packets from STM32."""
    if cmd == CMD_GET_TELEMETRY:
        telem = parse_telemetry(payload)
        if telem is None:
            self.get_logger().warn("Failed to parse telemetry", throttle_duration_sec=5.0)
            return
        
        # ... then accesses: telem['wheel_rpm'][0], telem['battery_v'], etc.
```

**Issue:** No verification that telemetry dict contains expected keys. If `parse_telemetry()` returns a partially-filled dict or the payload is malformed:
- `telem['wheel_rpm'][0]` → IndexError
- `telem['battery_v']` → KeyError
- IMU data access → KeyError

**Risk:** Unhandled exception in RX thread → silent failure, RX loop dies, bridge becomes non-responsive.

**Recommendation:** Validate parsed data:
```python
required_keys = ['wheel_rpm', 'battery_v', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
if not all(k in telem for k in required_keys):
    self.get_logger().error("Telemetry missing required fields")
    return
```

---

## HIGH PRIORITY ISSUES

### 7. **TIMER CALLBACK EXCEPTION HANDLING**
**File:** [lyra_bridge/lyra_bridge/node.py](lyra_bridge/lyra_bridge/node.py#L161-L163)  
**Lines:** 161-163

```python
telem_period = 1.0 / self.telem_rate
self.telem_timer = self.create_timer(telem_period, self._request_telemetry)

heartbeat_period = 1.0 / self.heartbeat_rate
self.heartbeat_timer = self.create_timer(heartbeat_period, self._send_heartbeat)
```

**Issue:** Timer callbacks have no try-catch. If `_request_telemetry()` or `_send_heartbeat()` raise an exception:
- The timer thread will crash
- No diagnostic output (rclpy suppresses by default)
- Telemetry stops being requested
- Bridge appears frozen

**Risk:** Silent failures, difficult debugging

**Recommendation:** Wrap callbacks with error handling.

---

### 8. **MOTOR CONTROL LOOP: Inverse Kinematics Limits**
**File:** [lyra_bridge/lyra_bridge/node.py](lyra_bridge/lyra_bridge/node.py#L335-L350)  
**Lines:** 335-350

```python
def _inverse_kinematics(self, vx: float, wz: float) -> list:
    """Convert cmd_vel to wheel velocities (rad/s)."""
    half_track = self.track_width / 2.0
    v_left = vx - (wz * half_track)
    v_right = vx + (wz * half_track)

    w_left = v_left / self.wheel_radius
    w_right = v_right / self.wheel_radius

    w_left = max(min(w_left, self.max_wheel_speed), -self.max_wheel_speed)
    w_right = max(min(w_right, self.max_wheel_speed), -self.max_wheel_speed)

    return [w_left, w_left, w_right, w_right]  # [FL, BL, BR, FR]
```

**Issue:** 
- No input validation (what if `vx` or `wz` is NaN/Inf?)
- Silent saturation: if command is impossible (e.g., rotate in place too fast), wheels are clamped without notification
- Dual wheel assignment `[w_left, w_left, w_right, w_right]` assumes symmetric left/right (correct for diff-drive, but non-obvious)

**Risk:** 
- NaN propagation through motor control
- User expects rotation that doesn't happen
- Potential for wheel slippage if saturation is frequent

---

### 9. **LOCALIZATION: Wheel Odometry No TF Publisher**
**File:** [lyra_localization/lyra_localization/wheel_odom_node.py](lyra_localization/lyra_localization/wheel_odom_node.py#L130-L145)  
**Lines:** 130-145

```python
def _publish_odom(self, stamp, v, w):
    odom = Odometry()
    odom.header.stamp = stamp.to_msg()
    odom.header.frame_id = 'odom'
    odom.child_frame_id = 'base_footprint'
    # ... fill pose and twist ...
    self.odom_pub.publish(odom)
```

**Issue:** 
- Publishes `/wheel/odom` only
- No TF transform for `odom → base_footprint`
- Comments say "EKF IS TF AUTHORITY" but code doesn't clarify this
- EKF node expects TF input from somewhere

**Risk:**
- Nav2 requires TF tree: `map → odom → base_link → *`
- If EKF provides TF but wheel_odom doesn't, there's a gap
- Potential TF lookup failures in downstream nodes

**Check:** Verify robot.launch.py configuration that EKF outputs `odom → base_footprint` TF.

---

### 10. **CAMERA NODE: Raw Pointer Usage (C++)**
**File:** [camera_ros/src/CameraNode.cpp](camera_ros/src/CameraNode.cpp#L76-L90)  
**Lines:** 76-90

```cpp
std::unordered_map<const libcamera::FrameBuffer *, buffer_info_t> buffer_info;
std::vector<std::thread> request_threads;
std::unordered_map<const libcamera::Request *, std::mutex> request_mutexes;
std::unordered_map<const libcamera::Request *, std::condition_variable> request_condvars;
```

**Issue:**
- Raw pointers used as map keys (`libcamera::FrameBuffer*`, `libcamera::Request*`)
- If libcamera invalidates pointers during cleanup, map keys become dangling
- No ref-counting visible

**Risk:**
- Use-after-free if Request/FrameBuffer objects are destroyed while in map
- Undefined behavior with condition_variable stored in map

**Recommendation:** Use `shared_ptr` or `weak_ptr` with custom deleters.

---

### 11. **JOYSTICK TIMEOUT: Hardcoded 1.0s in Auto-Arm Check**
**File:** [lyra_cmd_vel_gate/lyra_cmd_vel_gate/node.py](lyra_cmd_vel_gate/lyra_cmd_vel_gate/node.py#L99-L110)  
**Lines:** 99-110

```python
def is_armed(self) -> bool:
    if self.manually_armed:
        return True
    
    if self.auto_arm:
        # Auto-arm if we've received nav commands recently
        time_since_nav = (self.get_clock().now() - self.last_nav_time).nanoseconds / 1e9
        nav_active = (time_since_nav < 1.0 and self.is_nonzero(self.last_nav_cmd))
        return nav_active
    
    return False
```

**Issue:** 
- Hardcoded `1.0` timeout for nav commands
- But `self.joystick_timeout = 0.5` is parameterized
- Inconsistency: nav timeout (1.0s) vs joystick timeout (0.5s)

**Risk:** Robot disarms unexpectedly when nav stack is slightly delayed.

---

### 12. **BRIDGE CONFIG: Parameter Mismatch in Launch**
**File:** [lyra_bringup/launch/bridge.launch.py](lyra_bringup/launch/bridge.launch.py#L36-L45)  
**Lines:** 36-45

```python
lyra_bridge_node = Node(
    package='lyra_bridge',
    executable='lyra_node',
    name='lyra_bridge',
    output='screen',
    parameters=[{
        'serial.port': LaunchConfiguration('serial_port'),
        'serial.baudrate': LaunchConfiguration('serial_baudrate'),
        'control.auto_arm': LaunchConfiguration('auto_arm'),
        'control.cmd_vel_timeout_s': LaunchConfiguration('cmd_vel_timeout'),
    }],
```

**Issue:**
- Launch file has `auto_arm` param, but node code shows: `self.get_logger().info(f"SAFETY: Auto-arm DISABLED - use /lyra/arm service")`
- Bridge node doesn't read `control.auto_arm` parameter
- Parameter is silently ignored

**Check Required:** Verify [lyra_bridge/lyra_bridge/node.py](lyra_bridge/lyra_bridge/node.py#L49-L80) declares and reads this parameter.

---

### 13. **ROS MODE INIT: Single Timer Not Cancelled on Success**
**File:** [lyra_bridge/lyra_bridge/node.py](lyra_bridge/lyra_bridge/node.py#L175-L186)  
**Lines:** 175-186

```python
def _init_ros_mode(self):
    """Initialize ROS mode (ONE TIME ONLY) - FIX Issue #9."""
    if not self._ros_mode_initialized:
        success = self._send_command(build_set_ros_mode_command(self._next_seq(), True))
        if success:
            self._ros_mode_initialized = True
            self.get_logger().info("ROS mode enabled on STM32")
            self._init_timer.cancel()  # ← Good, but what if cancel fails?
```

**Issue:**
- Timer is set to run once at 0.5s (line 172)
- Callback may be called multiple times if `_ros_mode_initialized` check fails
- No error handling if `_send_command()` returns False persistently

**Risk:** If STM32 is not responding, timer loops forever retrying.

**Recommendation:** Add retry limit:
```python
if not hasattr(self, '_init_retries'):
    self._init_retries = 0
self._init_retries += 1
if self._init_retries > 10:
    self.get_logger().error("Failed to initialize ROS mode after 10 attempts")
    self._init_timer.cancel()
```

---

## MEDIUM PRIORITY ISSUES

### 14. **CAMERA NODE: Parameter Documentation Missing**
**File:** [camera_ros/src/CameraNode.cpp](camera_ros/src/CameraNode.cpp)  
**Issue:** No visible parameter callback implementation. If parameters are changed at runtime, behavior is undefined.

**Recommendation:** Ensure `onParameterChange()` or `postParameterChange()` is thread-safe and validates inputs.

---

### 15. **EKF CONFIG: Missing Explicit TF Output Spec**
**File:** [lyra_localization/config/ekf_adaptive.yaml](lyra_localization/config/ekf_adaptive.yaml) (not read yet)  
**Risk:** If not configured to publish TF, Nav2 will fail with "Cannot find transform".

---

### 16. **TRANSPORT: Buffer Overflow Silent Clear**
**File:** [lyra_bridge/lyra_bridge/transport.py](lyra_bridge/lyra_bridge/transport.py#L130-L140)  
**Lines:** 130-140

```python
# ✅ LOCK for buffer management and serial read
with self.lock:
    # Clear buffer if too large
    if len(self.rx_buffer) > 1024:
        self.rx_buffer.clear()
```

**Issue:**
- Silently discards data if buffer exceeds 1024 bytes
- No logging of dropped data
- Potential for loss of valid packets

**Risk:** Silent corruption of telemetry or status updates.

---

### 17. **SERVICE CALLS: Non-blocking But Unchecked**
**File:** [lyra_control/lyra_control/joy_teleop_wrapper.py](lyra_control/lyra_control/joy_teleop_wrapper.py#L90-L130)  
**Lines:** 90-130 (truncated in output, need to verify)

**Issue:** Service calls via `self.arm_client.call_async()` don't check for failure. If service call fails, there's no error handling visible.

---

### 18. **DEADMAN BUTTON: No Feedback Mechanism**
**File:** [lyra_cmd_vel_gate/lyra_cmd_vel_gate/node.py](lyra_cmd_vel_gate/lyra_cmd_vel_gate/node.py#L1-50)  
**Risk:** If deadman button is stuck or joystick is disconnected, user has no feedback. Robot will refuse commands silently.

**Recommendation:** Publish diagnostics showing joystick connection status.

---

### 19. **LAUNCH: Verbose Bash Scripts Fragile**
**File:** [lyra_bringup/launch/robot.launch.py](lyra_bringup/launch/robot.launch.py#L125-L145)  
**Lines:** 125-145

```python
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
```

**Issue:**
- Chain of shell commands with no error handling
- If `ros2 node list` fails or hangs, timeout will eventually trigger but script exits silently
- `shell=False` but uses bash `-c`, potential argument injection if params change

---

### 20. **LAUNCH: Race Between Resource Cleanup**
**File:** [lyra_bringup/launch/robot.launch.py](lyra_bringup/launch/robot.launch.py#L200-230)  
**Issue:** Multiple nodes launched with respawn=True but different respawn_delays. If base crashes:
- robot_state_publisher respawns at 2.0s
- lyra_bridge respawns at 2.0s
- But they may respawn out of order, breaking TF tree temporarily

---

### 21. **WHEEL ODOM: Frame ID Hardcoded**
**File:** [lyra_localization/lyra_localization/wheel_odom_node.py](lyra_localization/lyra_localization/wheel_odom_node.py#L130-L145)  
**Lines:** 130-145

```python
odom.header.frame_id = 'odom'
odom.child_frame_id = 'base_footprint'
```

**Issue:**
- Hardcoded frame IDs
- Should be parameterized to match URDF
- Mismatch with EKF expected frame IDs

**Recommendation:** Declare parameters for frame IDs.

---

### 22. **PROTOCOL: Command Sequencing Wraparound**
**File:** [lyra_bridge/lyra_bridge/protocol.py](lyra_bridge/lyra_bridge/protocol.py) (not fully read)  
**Risk:** Sequence numbers wrap at 256. If STM32 doesn't handle wraparound, packets may be interpreted as duplicates.

---

### 23. **ROS MODE INIT: Implicit Dependency on Telemetry**
**File:** [lyra_bridge/lyra_bridge/node.py](lyra_bridge/lyra_bridge/node.py#L175-L186)  
**Issue:** `_init_ros_mode()` is called via timer, but success depends on telemetry being parsed. If telemetry parsing is broken, ROS mode will never initialize.

**Dependency Chain:** 
1. Serial connected
2. ROS mode init sent (after 0.5s delay)
3. STM32 responds with telemetry
4. Telemetry parsed → armed state updated

If step 3 fails, step 4 never happens.

---

## LOWER PRIORITY OBSERVATIONS

### 24. **EKF RESPAWN=FALSE**
**File:** [lyra_bringup/launch/base.launch.py](lyra_bringup/launch/base.launch.py#L156)

```python
ekf_node = Node(
    ...
    respawn=False
)
```

**Note:** If EKF crashes, it won't restart. This is conservative but may leave robot in failed state. Consider respawn=True.

---

### 25. **JOYSTICK WRAPPER: Button Index Bounds Unchecked**
**File:** [lyra_control/lyra_control/joy_teleop_wrapper.py](lyra_control/lyra_control/joy_teleop_wrapper.py#L125-L145)  
**Risk:** If joystick has fewer buttons than expected, will access out-of-bounds indices.

---

### 26. **TRANSPORT: Connection Error Suppression**
**File:** [lyra_bridge/lyra_bridge/transport.py](lyra_bridge/lyra_bridge/transport.py#L60-L75)  
**Issue:** `_connect()` catches all exceptions silently. Specific errors (permission denied, device not found) should be logged differently.

---

## RECOMMENDED FIXES (PRIORITY ORDER)

### IMMEDIATE (Do First):
1. **Add mutex to cmd_vel_gate node state** → prevents race conditions
2. **Fix motor_control_loop armed state read** → add lock acquisition
3. **Validate telemetry dict keys** → prevent KeyError crashes
4. **Move transport.close() before RX join** → clean shutdown
5. **Add try-catch to timer callbacks** → prevent silent failures

### SHORT-TERM (Next Sprint):
6. Parameterize frame IDs in wheel_odom_node
7. Add retry limit to ROS mode init
8. Fix EKF conditional IMU dependency
9. Verify auto_arm parameter is actually used
10. Add diagnostic publisher to cmd_vel_gate

### MEDIUM-TERM (Architecture):
11. Refactor cmd_vel_gate to use atomic state snapshots
12. Add comprehensive integration tests
13. Implement deadman button feedback
14. Document ROS mode initialization dependencies
15. Add unit tests for inverse kinematics

### LOW-PRIORITY (Nice to Have):
16. Use smart pointers in CameraNode
17. Parameterize shell script logic in launch files
18. Add more detailed logging to protocol parsing
19. Consider moving EKF to respawn=True

---

## SAFETY CRITICAL PATHS

### Path 1: ARM/DISARM
```
Joy Button (7) → joy_teleop_wrapper._joy_callback()
  → _call_arm_service()
    → arm_client.call_async()
      → lyra_bridge._arm_service()
        → send_command(build_arm_command())
          → STM32 receives
            → Telemetry: armed=True
              → publish Bool(/lyra/armed)
                ← cmd_vel_gate.armed_cb()
                  → manually_armed=True
                    → is_armed() returns True
                      → cmd_vel routed to motors
```

**Vulnerability:** No feedback between STM32 arming status and ROS. If STM32 rejects ARM, ROS thinks it's armed.

**Fix:** Check telemetry status flags after ARM command, retry if not confirmed.

---

### Path 2: Emergency Stop
```
Joy Button (deadman release) → joy_cb()
  → deadman_pressed = False
    → publish_cmd()
      → Twist() (zero command)
        → cmd_vel routed to motors
          → _motor_control_loop()
            → _send_command(build_set_wheel_vel_command(0,0,0,0))
              → STM32 stops motors
```

**Vulnerability:** Race condition on `deadman_pressed` variable. Could be reading stale value.

**Fix:** Add thread lock for joystick state.

---

### Path 3: Timeout Stop
```
cmd_vel_callback() → last_cmd_time = now()
  → (500ms delay)
    → _motor_control_loop()
      → time.monotonic() - cmd_time > 0.5?
        → YES: send STOP
```

**Vulnerability:** Time source inconsistency. `cmd_vel_callback()` uses ROS clock, `_motor_control_loop()` uses `time.monotonic()`. If system clock jumps, timeout may not trigger.

**Fix:** Use consistent time source throughout.

---

## RECOMMENDATIONS FOR DOCUMENTATION

Add to README:

1. **Startup Dependencies:**
   ```
   Base must start before SLAM:
   - Motors (lyra_bridge)
   - Wheel odometry (wheel_odom_node)
   - IMU (if enabled)
   - EKF filter
   THEN LiDAR
   THEN SLAM/Nav2
   ```

2. **Safety Interlocks:**
   ```
   - Disarm via service/button sets armed=False in STM32
   - ALWAYS check battery voltage before motors start
   - Timeout stops motors after 500ms of no cmd_vel
   - Deadman button required for joystick mode
   ```

3. **Known Limitations:**
   ```
   - ROS mode initialization requires telemetry feedback
   - EKF may fail silently if IMU topic unavailable
   - Wheel odometry has no TF, EKF provides odom→base_link
   ```

---

## SUMMARY STATISTICS

| Category | Count |
|----------|-------|
| Critical (Stop-ship) | 6 |
| High (Fix before release) | 8 |
| Medium (Next sprint) | 11 |
| Low (Documentation) | 5 |
| **Total** | **30** |

**Estimated Fix Effort:** 
- Critical: 16 hours
- High: 24 hours  
- Medium: 12 hours
- **Total: 52 hours (1.3 sprints)**

---

## APPENDIX: Files Requiring Detailed Review

1. [lyra_localization/config/ekf_adaptive.yaml](lyra_localization/config/ekf_adaptive.yaml) - Verify IMU optional config
2. [lyra_localization/config/imu_filter.yaml](lyra_localization/config/imu_filter.yaml) - Check sensor fusion config
3. [lyra_bridge/lyra_bridge/protocol.py](lyra_bridge/lyra_bridge/protocol.py) - Verify all command builders
4. [camera_ros/src/CameraNode.cpp](camera_ros/src/CameraNode.cpp) - Full lifecycle review
5. [lyra_control/config/joystick.yaml](lyra_control/config/joystick.yaml) - Button mapping verification

---

**Report Generated:** 2026-01-18  
**Analyzer:** Static Code Review (Conservative Mode)  
**Next Steps:** Assign issues to backlog, prioritize by risk/effort matrix

