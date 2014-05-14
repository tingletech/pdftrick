from setuptools import setup, find_packages
setup(
    name='pdftrick',
    version = "0.0.3",
    description = "One weird PDF trick",
    url='https://github.com/tingletech/pdftrick',
    download_url = 'https://github.com/tingletech/pdftrick/tarball/0.0.3',
    author="Brian Tingle",
    author_email="brian.tingle.cdlib.org@gmail.com",
    license = "BSD",
    keywords = "PDF compression",
    packages = find_packages(),
    entry_points={
        'console_scripts': [
            'pdftrick = pdftrick.pdftrick:main'
            'pdfdensity = pdftrick.pdfdensity:main'
        ]
    }
)
