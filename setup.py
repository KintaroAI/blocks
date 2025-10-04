#!/usr/bin/env python3
"""
Setup script for Neuro Flow - Animated Blocks & Curved Arrows
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="neuro-flow",
    version="1.0.0",
    author="KintaroAI",
    author_email="",
    description="Interactive, animated flow diagrams with draggable blocks and curved arrows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kintaroai/neuro-flow",
    py_modules=["blocks_lib"],
    scripts=["blocks.py", "cerebellum.py"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "neuro-flow-blocks=blocks:main",
            "neuro-flow-cerebellum=cerebellum:main",
        ],
    },
)
