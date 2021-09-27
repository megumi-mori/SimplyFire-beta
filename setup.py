from setuptools import setup, find_packages
setup(
    name='PyMini',
    version='b0.1.0',
    author='Megumi Mori GitHub@megumi-mori',
    packages=['PyMini'],
    install_requires=[
        'astropy',
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'pyyaml'
    ]
)