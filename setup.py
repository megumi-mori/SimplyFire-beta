from setuptools import setup, find_packages
setup(
    name='SimplyFire',
    version='b3.0.0',
    author='Megumi Mori GitHub@megumi-mori',
    packages=['PyMini'],
    pakage_dir={'PyMini': 'PyMini'},
    package_data={'PyMini': ['config/*.yaml', 'img/*.png', 'temp/*.*']},

    install_requires=[
        'astropy',
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'pyyaml',
        'pyabf'

    ]
)