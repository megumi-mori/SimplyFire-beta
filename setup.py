"""
SimplyFire - Customizable analysis of electrophysiology data
Copyright (C) 2022 Megumi Mori
This program comes with ABSOLUTELY NO WARRANTY

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from setuptools import setup, find_packages
with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='SimplyFire',
    version='3.0.1b2',
    author='Megumi Mori',
    description='Customizable electrophysiology analysis software',
    long_description=readme,
    pakage_dir={'SimplyFire':'SimplyFire'},
    packages = find_packages(),
    entry_points={
        'console_scripts': [
            'SimplyFire = SimplyFire.__main__:SimplyFire'
        ]
    },
    include_package_data = True,
    package_data={
        'SimplyFire': ['config/default_config.yaml',
                       'config/modules.yaml',
                       'img/*.*',
                       'temp/*.*',
                       'Modules/*/config.yaml',
                       'Modules/*/default_values.yaml']
        # 'Modules':['*/config.yaml', '*/default_values.yaml']
    },
    install_requires=[
        'numpy>=1.22.0',
        'pandas>=1.3.5',
        'matplotlib>=3.5.1',
        'scipy>=1.7.3',
        'pyyaml>=6.0',
        'pyabf>=2.3.5'

    ],
    license='GNU General Public License v3',
    zip_safe = False,
    keywords ='neuroscience',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows'
    ]
)