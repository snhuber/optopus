import os
import sys
import codecs
from setuptools import setup

if sys.version_info < (3, 6, 0):
    raise RuntimeError("optopus requires Python 3.6 or higher")

here = os.path.abspath(os.path.dirname(__file__))

__version__ = None
exec(open(os.path.join(here, 'optopus', 'version.py')).read())

with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='optopus',
    version=__version__,
    description='Python trading tool for options using ib_insync',
    long_description=long_description,
    url='https://github.com/ciherraiz/optopus',
    author='ciherraiz',
    author_email='a@a.com',
    license='BSD',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='ibapi asyncio jupyter interactive brokers async',
    packages=['optopus']
)