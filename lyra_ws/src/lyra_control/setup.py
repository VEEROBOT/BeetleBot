from setuptools import setup
import os
from glob import glob

package_name = 'lyra_control'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install config files
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='veerobot',
    maintainer_email='your_email@example.com',
    description='Lyra robot control nodes',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Phase 1: cmd_vel_mux (FIXED - no zero spam)
            'cmd_vel_mux = lyra_control.cmd_vel_mux:main',
            
            # Phase 2: Joystick button handler
            'joy_teleop_wrapper = lyra_control.joy_teleop_wrapper:main',
        ],
    },
)
