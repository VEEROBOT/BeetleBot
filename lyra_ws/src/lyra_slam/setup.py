from setuptools import setup, find_packages
import os

package_name = 'lyra_slam'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Required by ROS2
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        # Package manifest
        ('share/' + package_name, ['package.xml']),

        # Launch files
        (os.path.join('share', package_name, 'launch'),
            [
                'launch/slam.launch.py',
                'launch/slam_bringup.launch.py',
            ]),

        # Config files
        (os.path.join('share', package_name, 'config'),
            ['config/slam_toolbox.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='veerobot',
    maintainer_email='veerobot@todo.todo',
    description='SLAM Toolbox configuration for Lyra robot',
    license='Apache License 2.0',
    tests_require=['pytest'],
)
