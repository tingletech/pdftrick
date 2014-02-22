from setuptools import setup, find_packages
setup(
    name='pdftrick',
    version = "0.0.0",
    packages = find_packages(),
    entry_points={
        'console_scripts': [
            'pdftrick = pdftrick.pdftrick:main'
        ]
    }
)
