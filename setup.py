
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(name='proofpoint_itm',
    version='0.0.6',
    description='Proofpoint ITM API client library',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Mike Olden',
    author_email='michael.olden@oldendigital.com',
    url = 'https://github.com/drizzo-tech/proofpoint_itm',
    project_urls={
        'Bug Tracker': 'https://github.com/drizzo-tech/proofpoint_itm/issues'
    },
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    ],
    license='Apache 2.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6, <4',
    install_requires=[
        'requests'
    ],
    keywords='Proofpoint, ITM, ObserveIT'
)
