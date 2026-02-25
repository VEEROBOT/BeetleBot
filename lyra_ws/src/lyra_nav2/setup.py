from setuptools import find_packages, setup
import os

package_name = 'lyra_nav2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'), [
            'launch/nav2_amcl.launch.py',
            'launch/full_nav.launch.py'
        ]),

        (os.path.join('share', package_name, 'config'),
            ['config/nav2_params.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Praveen Kumar',
    maintainer_email='praveen.kumar@siliris.com',
    description='Nav2 configuration and launch files for autonomous navigation with AMCL localization',
    license='GPLv3',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'auto_initial_pose.py = lyra_nav2.auto_initial_pose:main',
        ],
    },
)
