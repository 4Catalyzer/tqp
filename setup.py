from setuptools import find_packages, setup

setup(
    name="tqp",
    version="0.4.3",
    description="An opinionated library for pub/sub over SQS and SNS",
    url="https://github.com/4Catalyzer/tqp",
    author="Giacomo Tagliabue",
    author_email="giacomo@gmail.com",
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="pub sub pubsub flask",
    packages=find_packages(),
    install_requires=("boto3",),
)
