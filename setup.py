import subprocess

from setuptools import Command, find_packages, setup

# -----------------------------------------------------------------------------


def system(command):
    class SystemCommand(Command):
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            subprocess.check_call(command, shell=True)

    return SystemCommand


# -----------------------------------------------------------------------------

setup(
    name="tqp",
    version="0.3.0",
    description="An opinionated library for pub/sub over SQS and SNS",
    url="https://github.com/4Catalyzer/tqp",
    author="Giacomo Tagliabue",
    author_email="giacomo@gmail.com",
    license="MIT",
    python_requires=">=3.6",
    classifiers=(
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ),
    keywords="pub sub pubsub flask",
    packages=find_packages(),
    install_requires=("boto3",),
    cmdclass={
        "clean": system("rm -rf build dist *.egg-info"),
        "package": system("python setup.py sdist bdist_wheel"),
        "publish": system("twine upload dist/*"),
        "release": system("python setup.py clean package publish"),
    },
)
