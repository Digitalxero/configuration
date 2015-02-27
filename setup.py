import os
import io
from setuptools import setup, find_packages


cwd = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(cwd, 'README.rst'), encoding='utf-8') as fd:
    long_description = fd.read()


setup(
    name='configuration',
    version='0.4.1',
    description=('Thin wrapper around PyYAML that allows you to '
                 'access values in dot notation config.value...'),
    long_description=long_description,
    url='https://github.com/Digitalxero/configuration',
    author='Dj Gilcrease',
    author_email='digitalxero',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    keywords=('yaml config configuration'),
    packages=find_packages(),
    install_requires=['PyYAML']
)
