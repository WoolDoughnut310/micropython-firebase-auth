from setuptools import setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="micropython-firebase-auth",
    version="1.0.6",
    author="WoolDoughnut310",
    author_email="wooldoughnutspi@outlook.com",
    description="Firebase Auth implementation for Micropython optimized for ESP32.",
    url="https://github.com/WoolDoughnut310/micropython-firebase-auth",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=["firebase_auth"]
)
