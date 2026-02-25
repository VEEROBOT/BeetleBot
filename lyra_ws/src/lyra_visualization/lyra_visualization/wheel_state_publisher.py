#!/usr/bin/env python3
"""
Wheel State Publisher (VISUAL ONLY)

Publishes joint_states to animate wheels in RViz.
Does NOT affect odometry, TF, or navigation.
"""

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from sensor_msgs.msg import JointState
from rclpy.qos import QoSProfile, ReliabilityPolicy

class WheelStatePublisher(Node):
    def __init__(self):
        super().__init__('wheel_state_publisher')

        # MUST match STM + README
        self.declare_parameter('ticks_per_rev', 3600)
        self.ticks_per_rev = self.get_parameter('ticks_per_rev').value
        self.rad_per_tick = (2.0 * math.pi) / self.ticks_per_rev

        # MUST match URDF joint names
        self.joint_names = [
            'fl_joint',
            'bl_joint',
            'br_joint',
            'fr_joint',
        ]

        self.prev_ticks = None
        self.joint_positions = {j: 0.0 for j in self.joint_names}

        qos = QoSProfile(
            depth=50,
            reliability=ReliabilityPolicy.BEST_EFFORT
        )
        
        self.create_subscription(
            Int32MultiArray,
            '/wheel_ticks',
            self._ticks_cb,
            qos
        )

        self.pub = self.create_publisher(JointState, '/joint_states', 10)

        self.get_logger().info("Wheel animation (visual-only) started")

    def _ticks_cb(self, msg: Int32MultiArray):
        if len(msg.data) != 4:
            return

        if self.prev_ticks is None:
            self.prev_ticks = list(msg.data)
            return

        # Order from STM: [FL, BL, BR, FR]
        fl, bl, br, fr = msg.data
        pfl, pbl, pbr, pfr = self.prev_ticks

        deltas = {
            'fl_joint': fl - pfl,
            'bl_joint': bl - pbl,
            'br_joint': br - pbr,
            'fr_joint': fr - pfr,
        }

        for joint, delta in deltas.items():
            self.joint_positions[joint] += delta * self.rad_per_tick

        self.prev_ticks = list(msg.data)

        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = self.joint_names
        js.position = [self.joint_positions[j] for j in self.joint_names]

        self.pub.publish(js)


def main():
    rclpy.init()
    node = WheelStatePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # rclpy.shutdown() removed - let launch system handle it


if __name__ == '__main__':
    main()
