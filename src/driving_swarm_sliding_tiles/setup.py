import os
from setuptools import setup
from glob import glob

package_name = 'driving_swarm_sliding_tiles'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
	(os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'params'), glob('params/*'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bea',
    maintainer_email='bea@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'planner = driving_swarm_sliding_tiles.planner:main'
        ],
    },
)
