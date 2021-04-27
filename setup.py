#Create Setup.py file to make the module installable
from setuptools import setup, find_packages

setup(
	name = "loko",
	version = "0.0.1",
	author = "Mcflyhalf",
	author_email = "mcflyhalf@live.com",
	description = ("Store, send and receive money in different currencies"),
	keywords = "currency exchange forex",
	packages= find_packages(),
)