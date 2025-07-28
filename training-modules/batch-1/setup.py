from setuptools import setup, find_packages

setup(
    name="goldfish",
    version="0.1.0",
    description="surgical robot training environment, batch 1",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24",
        "gymnasium>=0.29",
        "stable-baselines3>=2.0",
        "torch>=2.0",
    ],
    python_requires=">=3.10",
)
