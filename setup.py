from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
	readme = readme_file.read()

requirements = []

setup(
	name="simplevc",
	version="0.0.3",
	author="Alden Leung",
	author_email="alden.leung@gmail.com",
	description="A simple Python version control package",
	long_description=readme,
	long_description_content_type="text/markdown",
	url="https://github.com/aldenleung/simplevc/",
	packages=find_packages(),
	install_requires=requirements,
	classifiers=[
		"Programming Language :: Python :: 3.9",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
	],
)
