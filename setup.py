from setuptools import setup, find_packages

setup(
    name="flask_app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        "flask-migrate",
        "flask-cors",
        "flask-session",
        "python-dotenv",
    ],
)
