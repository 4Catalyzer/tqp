from setuptools import find_packages, setup

setup(
    name="tqp",
    version="1.0.0",
    description="An opinionated library for pub/sub over SQS and SNS",
    url="https://github.com/4Catalyzer/tqp",
    author="Giacomo Tagliabue",
    author_email="giacomo@gmail.com",
    license="MIT",
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="pub sub pubsub flask",
    packages=find_packages(),
    install_requires=("boto3",),
    extras_require={
        "dev": [
            "pytest",
            "fourmat~=0.11.1",
            "pre-commit",
            "moto[server]",
            "boto3",
        ]
    },
)
