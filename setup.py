from setuptools import setup, find_packages


setup(
    name='cagrex',
    version='0.4.0',
    packages=find_packages(),
    install_requires=['requests', 'grequests', 'bs4', 'mechanicalsoup'],
)
