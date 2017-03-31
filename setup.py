# coding: utf-8
# python setup.py sdist register upload
from setuptools import setup

setup(
    name='es-loghandler',
    version='0.0.5',
    description='Elasticsearch log handler.',
    author='Telminov Sergey',
    url='https://github.com/telminov/python-elasticsearch-loghandler',
    packages=[
        'es_loghandler',
    ],
    include_package_data=True,
    license='The MIT License',
    test_suite='nose.collector',
    install_requires=[
        'requests', 'elasticsearch', 'pytz'
    ],
)
