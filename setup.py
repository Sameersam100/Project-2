from setuptools import setup, find_packages

setup(
    name='project 2',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        
        'beautifulsoup4',
        'requests',
        'pandas',
        
    ],
    entry_points={
        'console_scripts': [
            
        ],
    },
    author=' Abdul Sameer Mohammed',
    description='Working with Web Data',
    long_description='A longer description of your project',
    url='https://github.com/Sameersam100/Project-2',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
