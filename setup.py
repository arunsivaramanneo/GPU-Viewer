#!/usr/bin/python
from setuptools import setup
setup(
	name="GPU-Viewer",
	version="1.0.0",
	description="A GPU Info Viewer",
	author="Arun Sivaraman",
	author_email="arunsivaraman1994@gmail.com",
	keywords=["gpu","opengl","vulkan","gtk3","glxinfo"],
        url=["https://www.facebook.com/arunsivaramanneo"],
	install_requires=["nose"],
	test_suite='nose.collector',
	tests_require=['nose']
)
