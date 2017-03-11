from setuptools import setup, find_packages
import sys, os

# Don't import gym module here, since deps may not be installed
for package in find_packages():
    if '_gym_' in package:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), package))
from package_info import USERNAME, VERSION

setup(name='{}-{}'.format(USERNAME, 'gym-super-mario'),
    version=VERSION,
    description='Gym User Env - 32 levels of Super Mario Bros',
    url='https://github.com/ppaquette/gym_super_mario',
    author='Philip Paquette',
    author_email='pcpaquette@gmail.com',
    license='MIT License',
    packages=[package for package in find_packages() if package.startswith(USERNAME)],
    package_data={ '{}_{}'.format(USERNAME, 'gym_super_mario'): ['lua/*.lua', 'roms/*.nes' ] },
    zip_safe=False,
    install_requires=[ 'gym>=0.8.0' ],
)
