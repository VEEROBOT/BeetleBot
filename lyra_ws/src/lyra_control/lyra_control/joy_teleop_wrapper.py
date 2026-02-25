#!/usr/bin/env python3
"""
joy_teleop_wrapper.py - Joystick Button Handler for Lyra Robot

Monitors joystick buttons and triggers ARM/DISARM services:
- START button (7) → Call /lyra/arm service
- SELECT button (6) → Call /lyra/disarm service

Features:
- Button state tracking (only trigger on press, not hold)
- Debouncing (prevent accidental double-presses)
- Non-blocking service calls (doesn't freeze joystick)
- Graceful degradation (works even if lyra_bridge not running)
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_srvs.srv import Trigger
import time


class JoyTeleopWrapper(Node):
    """
    Wraps joystick input to add ARM/DISARM button functionality.
    
    Subscribes to /joy and calls services when specific buttons are pressed.
    Does NOT interfere with teleop_twist_joy - they work in parallel.
    """
    
    def __init__(self):
        super().__init__('joy_teleop_wrapper')
        
        # ================================================================
        # Parameters (loaded from joystick.yaml)
        # ================================================================
        self.declare_parameters(
            namespace='',
            parameters=[
                ('arm_button', 7),
                ('disarm_button', 6),
                ('arm_service', '/lyra/arm'),
                ('disarm_service', '/lyra/disarm'),
                ('button_debounce_time', 0.3),
                ('service_timeout', 1.0),
                ('log_button_presses', True),
            ]
        )
        
        self.arm_button = self.get_parameter('arm_button').value
        self.disarm_button = self.get_parameter('disarm_button').value
        self.arm_service_name = self.get_parameter('arm_service').value
        self.disarm_service_name = self.get_parameter('disarm_service').value
        self.debounce_time = self.get_parameter('button_debounce_time').value
        self.service_timeout = self.get_parameter('service_timeout').value
        self.log_presses = self.get_parameter('log_button_presses').value
        
        # ================================================================
        # State tracking
        # ================================================================
        self.previous_buttons = []
        self.last_arm_time = 0.0
        self.last_disarm_time = 0.0
        
        # ================================================================
        # Service clients
        # ================================================================
        self.arm_client = self.create_client(Trigger, self.arm_service_name)
        self.disarm_client = self.create_client(Trigger, self.disarm_service_name)
        
        # Wait for services (non-blocking)
        self.services_ready = False
        self.create_timer(1.0, self._check_services)
        
        # ================================================================
        # Subscribe to joystick
        # ================================================================
        self.joy_sub = self.create_subscription(
            Joy,
            '/joy',
            self._joy_callback,
            10
        )
        
        self.get_logger().info("=" * 60)
        self.get_logger().info("Joy Teleop Wrapper Started")
        self.get_logger().info(f"  ARM button:    {self.arm_button} (START)")
        self.get_logger().info(f"  DISARM button: {self.disarm_button} (SELECT)")
        self.get_logger().info(f"  ARM service:   {self.arm_service_name}")
        self.get_logger().info(f"  DISARM service: {self.disarm_service_name}")
        self.get_logger().info("Waiting for services to become available...")
        self.get_logger().info("=" * 60)
    
    def _check_services(self):
        """Periodically check if services are available."""
        if not self.services_ready:
            arm_ready = self.arm_client.wait_for_service(timeout_sec=0.1)
            disarm_ready = self.disarm_client.wait_for_service(timeout_sec=0.1)
            
            if arm_ready and disarm_ready:
                self.services_ready = True
                self.get_logger().info("Services connected! Ready to handle button presses.")
            else:
                self.get_logger().warn(
                    "Waiting for services... (is lyra_bridge running?)",
                    throttle_duration_sec=5.0
                )
    
    def _joy_callback(self, msg: Joy):
        """
        Process joystick messages and detect button presses.
        
        Only triggers on PRESS (rising edge), not while held.
        Implements debouncing to prevent accidental double-presses.
        """
        current_time = time.time()
        
        # Ensure we have button history for comparison
        if not self.previous_buttons:
            self.previous_buttons = [0] * len(msg.buttons)
            return
        
        # Ensure button arrays are same length
        if len(msg.buttons) != len(self.previous_buttons):
            self.get_logger().warn(
                f"Button count mismatch: got {len(msg.buttons)}, expected {len(self.previous_buttons)}"
            )
            self.previous_buttons = [0] * len(msg.buttons)
            return
        
        # Check ARM button (START)
        if self.arm_button < len(msg.buttons):
            button_now = msg.buttons[self.arm_button]
            button_before = self.previous_buttons[self.arm_button]
            
            # Detect rising edge (button just pressed)
            if button_now and not button_before:
                # Check debounce
                if current_time - self.last_arm_time > self.debounce_time:
                    self.last_arm_time = current_time
                    self._call_arm_service()
        
        # Check DISARM button (SELECT)
        if self.disarm_button < len(msg.buttons):
            button_now = msg.buttons[self.disarm_button]
            button_before = self.previous_buttons[self.disarm_button]
            
            # Detect rising edge (button just pressed)
            if button_now and not button_before:
                # Check debounce
                if current_time - self.last_disarm_time > self.debounce_time:
                    self.last_disarm_time = current_time
                    self._call_disarm_service()
        
        # Save current state for next comparison
        self.previous_buttons = list(msg.buttons)
    
    def _call_arm_service(self):
        """Call the ARM service (non-blocking)."""
        if not self.services_ready:
            self.get_logger().warn("ARM service not available (is lyra_bridge running?)")
            return
        
        if self.log_presses:
            self.get_logger().info("START button pressed - sending ARM command")
        
        # Create request
        request = Trigger.Request()
        
        # Call service asynchronously (non-blocking)
        future = self.arm_client.call_async(request)
        future.add_done_callback(self._arm_response_callback)
    
    def _call_disarm_service(self):
        """Call the DISARM service (non-blocking)."""
        if not self.services_ready:
            self.get_logger().warn("DISARM service not available (is lyra_bridge running?)")
            return
        
        if self.log_presses:
            self.get_logger().info("SELECT button pressed - sending DISARM command")
        
        # Create request
        request = Trigger.Request()
        
        # Call service asynchronously (non-blocking)
        future = self.disarm_client.call_async(request)
        future.add_done_callback(self._disarm_response_callback)
    
    def _arm_response_callback(self, future):
        """Handle ARM service response."""
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(f"ARM: {response.message}")
            else:
                self.get_logger().warn(f"ARM failed: {response.message}")
        except Exception as e:
            self.get_logger().error(f"ARM service call failed: {e}")
    
    def _disarm_response_callback(self, future):
        """Handle DISARM service response."""
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(f"DISARM: {response.message}")
            else:
                self.get_logger().warn(f"DISARM failed: {response.message}")
        except Exception as e:
            self.get_logger().error(f"DISARM service call failed: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = JoyTeleopWrapper()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # rclpy.shutdown() removed - let launch system handle it


if __name__ == '__main__':
    main()
