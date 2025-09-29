from setuptools import setup, find_packages
import os

def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()

setup(
    name="linux-api-server",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "start-server=linux_api.start_script:main"
        ]
    },
    package_data={
        "linux_api": [
            "../start.sh",
            "../requirements.txt",
            "../start_debug.sh",
            "../config.env",
            "../api/*",
            "../core_functions/*"
        ]
    },
    zip_safe=False,
)

