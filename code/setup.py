# setup.py

from setuptools import setup, find_packages

setup(
    name='lysimeter_analysis',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        # Add other dependencies if needed
    ],
    entry_points={
        'console_scripts': [
            'run_analysis=scripts.run_analysis:main',
        ],
    },
)
