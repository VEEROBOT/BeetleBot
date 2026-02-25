#!/usr/bin/env python3
"""
cmd_vel_mux - Command Velocity Multiplexer
Merges multiple cmd_vel sources with priority management.

FIXED VERSION:
- Only publishes when active source exists (no zero spam)
- Proper timeout handling
- Clean priority switching
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import time


class CmdVelMux(Node):
    """
    Multiplexes multiple cmd_vel sources based on priority and timeouts.
    
    Sources (in priority order):
    1. Joystick (/cmd_vel_joy) - Highest priority, 0.2s timeout
    2. Navigation (/cmd_vel_nav) - Medium priority, 1.0s timeout  
    3. Manual (/cmd_vel_manual) - Lowest priority, 0.5s timeout
    """
    
    def __init__(self):
        super().__init__('cmd_vel_mux')
        
        # Source configuration
        # Format: {name: {topic, priority, timeout, msg, timestamp}}
        self.sources = {
            'joystick': {
                'topic': '/cmd_vel_joy',
                'priority': 10,
                'timeout': 0.2,  # Very responsive - release deadman → stop fast
                'msg': None,
                'time': 0.0
            },
            'navigation': {
                'topic': '/cmd_vel_nav',
                'priority': 5,
                'timeout': 1.0,  # Tolerant of brief nav hiccups
                'msg': None,
                'time': 0.0
            },
            'manual': {
                'topic': '/cmd_vel_manual',
                'priority': 1,
                'timeout': 0.5,  # Balance for testing
                'msg': None,
                'time': 0.0
            }
        }
        
        # Create subscribers for each source
        self.subscribers = {}
        for name, config in self.sources.items():
            self.subscribers[name] = self.create_subscription(
                Twist,
                config['topic'],
                lambda msg, n=name: self._source_callback(n, msg),
                10
            )
            self.get_logger().info(f"Subscribed to {config['topic']} (priority {config['priority']})")
        
        # Output publisher
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel_raw', 10)
        
        # Active source publisher (for monitoring)
        self.pub_active = self.create_publisher(String, '/cmd_vel_mux/active', 10)
        
        # Timer to check timeouts and publish (20 Hz)
        self.create_timer(0.05, self._timer_callback)
        
        self.get_logger().info("cmd_vel_mux started - NO ZERO SPAM mode enabled")
    
    def _source_callback(self, source_name: str, msg: Twist):
        """Store incoming message from a source."""
        self.sources[source_name]['msg'] = msg
        self.sources[source_name]['time'] = time.time()
        
        # Log when source becomes active (throttled)
        self.get_logger().info(
            f"Source '{source_name}' active: vx={msg.linear.x:.2f} vz={msg.angular.z:.2f}",
            throttle_duration_sec=2.0
        )
    
    def _timer_callback(self):
        """
        Check all sources and publish the highest priority active one.
        
        CRITICAL: Only publishes if an active source exists.
        This prevents zero-spam when all sources are idle/timed out.
        """
        current_time = time.time()
        
        # Find highest priority active source
        best_source = None
        best_priority = -1
        
        for name, config in self.sources.items():
            # Skip if never received a message
            if config['msg'] is None:
                continue
            
            # Check if source has timed out
            age = current_time - config['time']
            if age > config['timeout']:
                # Source timed out - ignore it
                continue
            
            # Source is active - check if it's highest priority
            if config['priority'] > best_priority:
                best_priority = config['priority']
                best_source = name
        
        # Publish best source (or nothing if no active source)
        if best_source is not None:
            # Publish the velocity command
            self.pub_cmd_vel.publish(self.sources[best_source]['msg'])
            
            # Publish active source name
            active_msg = String()
            active_msg.data = best_source
            self.pub_active.publish(active_msg)
            
            # Log active source (throttled)
            self.get_logger().info(
                f"Active: {best_source}",
                throttle_duration_sec=2.0
            )
        else:
            # CRITICAL: No active source - publish NOTHING
            # This is the fix for zero-spam!
            
            # Publish "none" to active source topic (for monitoring)
            active_msg = String()
            active_msg.data = "none"
            self.pub_active.publish(active_msg)
            
            # Log idle state (throttled)
            self.get_logger().info(
                "All sources idle - not publishing",
                throttle_duration_sec=5.0
            )


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelMux()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # rclpy.shutdown() removed - let launch system handle it


if __name__ == '__main__':
    main()
