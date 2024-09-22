import os
from setuptools import setup, find_packages

# README 파일 읽기
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="easy_langsmith",
    version="0.0.6",
    packages=find_packages(),
    install_requires=[
        "requests",
        "numpy",
        "pyyaml",
        "ipython",
    ],
    author="wooseok",
    author_email="mastav7@gmail.com",
    description="A package for easy integration with LangSmith",
    long_description=long_description,
    long_description_content_type="text/markdown",
)