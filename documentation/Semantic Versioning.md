# Versioning Best Practices

Versioning in `setup.py` follows the Semantic Versioning (SemVer) principles. This system provides a clear and structured approach to version numbering, which helps users understand the level of changes in new releases. Here are the key points and best practices:

## Semantic Versioning

The version number is typically structured as `MAJOR.MINOR.PATCH`, where:

1. **MAJOR** version increment (X.0.0):
    - Introduces incompatible API changes.
    - Indicates significant changes that might require users to adjust their code.
    - Example: Adding a new class that changes how the package is used, or removing a previously existing feature.

2. **MINOR** version increment (0.X.0):
    - Adds functionality in a backward-compatible manner.
    - Introduces new features, enhancements, or substantial changes that don’t break existing functionality.
    - Example: Adding new methods, improving performance, or introducing optional parameters.

3. **PATCH** version increment (0.0.X):
    - Introduces backward-compatible bug fixes.
    - Fixes issues, errors, or small improvements that don’t add new features.
    - Example: Fixing a bug in an existing function or improving documentation.

## Best Practices for Versioning

1. **Start with 0.x.x**:
    - During the initial development, before a stable public API is released, it’s common to start with `0.1.0` and increment the MINOR and PATCH versions as necessary.
  
2. **Increment PATCH version for bug fixes**:
    - When you fix bugs or make minor improvements, increment the PATCH version.
    - Example: `0.1.0` -> `0.1.1`

3. **Increment MINOR version for new features**:
    - When you add new features or significant improvements that are backward-compatible, increment the MINOR version.
    - Example: `0.1.1` -> `0.2.0`

4. **Increment MAJOR version for breaking changes**:
    - When you make changes that are not backward-compatible, increment the MAJOR version.
    - Example: `0.2.0` -> `1.0.0`

5. **Document changes**:
    - Maintain a changelog or release notes to document the changes made in each version. This helps users understand what has changed and why the version was incremented.

6. **Pre-release versions**:
    - Use pre-release labels (alpha, beta, rc) for versions that are not yet stable.
    - Example: `1.0.0-alpha`, `1.0.0-beta`, `1.0.0-rc.1`

## Example

Here’s how you might increment versions based on changes:

- **Initial development**: `0.1.0`
- **Bug fix**: `0.1.1`
- **New feature**: `0.2.0`
- **Major overhaul with breaking changes**: `1.0.0`
- **Bug fix in stable release**: `1.0.1`
- **Minor feature addition**: `1.1.0`
- **Another bug fix**: `1.1.1`

## Applying These Principles

In your `setup.py`, you would adjust the `version` parameter based on the changes you make. For instance, if you’re making a backward-compatible improvement or adding a new feature to your existing package:

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name='lysimeter-analysis',
    version='0.2.0',  # Incremented MINOR version for new features
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'plotly'  # Add plotly as a dependency
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
```