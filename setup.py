import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pyhstr',
    version='0.0.2',
    author='xvm32',
    author_email='dedmauz69@gmail.com',
    description=('python shell history'),
    license='MIT',
    keywords='python shell history',
    url='https://github.com/xvm32/pyhstr',
    packages=['pyhstr'],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ]
)