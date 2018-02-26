from setuptools import setup, find_packages


setup(
    name='cagrex',
    version='0.4.1',
    packages=find_packages(),
    install_requires=['requests', 'grequests', 'bs4', 'mechanicalsoup'],
)
