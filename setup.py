from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='optopus',
    packages=[
        'optopus'
    ],
    version='0.0.1',
    description='Options with ib-insync',
    long_description=long_description,
    url='https://github.com/ciherraiz/optopus',
    author='ciherraiz',
    author_email='a@a.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='options trading',
    install_requires=[
        'ib-insync'
    ],
)
