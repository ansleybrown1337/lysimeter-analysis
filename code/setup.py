from setuptools import setup, find_packages

setup(
    name='lysimeter-analysis',
    version='0.5.5',  # See documentation folder for notes on versioning
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'matplotlib>=3.0.0',
        'plotly>=4.0.0',
        'numpy>=1.18.0',
        'scipy>=1.4.0',
        'pyfao56>=1.0.0',
        'colorama>=0.4.0',
    ],
    entry_points={
        'console_scripts': [
            'run_analysis=lysimeter_analysis.run_analysis:main'
        ]
    },
    author='A.J. Brown',
    author_email='Ansley.Brown@colostate.edu',
    description='A package for lysimeter data processing and analysis.',
    url='https://github.com/ansleybrown1337/lysimeter-data-2023',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Hydrology'
    ],
    python_requires='>=3.6',
)
