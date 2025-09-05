from setuptools import setup, find_packages

setup(
    name='goldfish',
    version='0.2.0',
    description='Surgical Robot Training Environment - Needle Insertion with Biological Cost Functions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Goldfish Team',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'torch>=2.0.0',
        'gymnasium>=0.28.0',
        'stable-baselines3[extra]>=2.0.0',
        'scipy>=1.9.0',
        'matplotlib>=3.5.0',
        'tqdm>=4.65.0',
        'tensorboard>=2.13.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
        ],
        # Future high-fidelity physics (optional, large install)
        'physics': [
            'mujoco>=3.0.0',
        ],
    },
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
