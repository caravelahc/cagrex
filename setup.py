from setuptools import setup, find_packages


setup(
    name='cagrex',
    packages=find_packages(),
    install_requires=['requests', 'bs4', 'mechanicalsoup'],
)
