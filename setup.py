#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="lidlplus-api",
    version="0.0.2",
    author="Zsombor Kalmar",
    description="Implementation of the Lidl Plus mobile app api in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "GitHub": "https://github.com/zsobix/lidlplus-api",
        "PyPI": "https://pypi.org/project/lidlplus-api/",
    },
    license="GPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    platforms="any",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.1",
        "qrcode >= 8.2"
    ],
    extras_require={
        "auth": [
            "pyjwkest>=1.4.4",
            "playwright>=1.58.0"
        ]
    },
)
