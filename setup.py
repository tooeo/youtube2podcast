#!/usr/bin/env python3
"""
Setup script for YouTube2Podcast
"""

from setuptools import setup, find_packages
import os

# Читаем README файл
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Читаем requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="youtube2podcast",
    version="1.0.0",
    author="tooeo",
    author_email="",  # Добавьте ваш email
    description="YouTube to Podcast converter with RSS feed generation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tooeo/youtube2podcast",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "youtube2podcast=main:main",
            "youtube2podcast-loop=main_loop:main_loop",
            "youtube2podcast-channel=channel_downloader:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
