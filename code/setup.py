# setup.py
from setuptools import setup, find_packages

setup(
    name='lysimeter-analysis',
    version='0.4.0',  # See documentation folder for notes on versioning
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'plotly'
    ],
    entry_points={
        'console_scripts': [
            'run_analysis=scripts.run_analysis:main'
        ]
    },
    author='A.J. Brown',
    author_email='Ansley.Brown@colostate.edu',
    description='A package for lysimeter data processing and analysis.',
    url='https://github.com/your-repo/lysimeter-analysis',
)
