#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

requirements = []

test_requirements = [
    "pytest>=3",
]

setup(
    author="Confluency LLC",
    author_email="info@confluency.ai",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Python implementation of an Antecedent Moisture Model (AMM)",
    entry_points={
        "console_scripts": [],
    },
    install_requires=requirements,
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="antecedent_moisture_model",
    name="antecedent_moisture_model",
    packages=find_packages(
        include=["antecedent_moisture_model", "antecedent_moisture_model.*"]
    ),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/confluencywater/antecedent_moisture_model",
    version="0.1.0",
    zip_safe=False,
)
