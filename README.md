# SimplyFire
A customizable analysis package for electrophysiologists

Read the full manual [here](https://simplyfire-beta.readthedocs.io/).


# Notice for new users 
We are transitioning from the "-beta" repository to the [main repository](https://github.com/megumi-mori/SimplyFire). 
This "-beta" repository will be discontinued. 

## .exe Installation

Download the software zip file from the recent [release](https://github.com/megumi-mori/SimplyFire-beta/releases).
You only need to download the zip file.

Extract the contents of the zip file, and locate SimplyFire.exe to run the software.

## Python Installation
If you have Python, you can install and run SimplyFire as a Python module. 

You can install SimplyFire from [TestPyPI](https://test.pypi.org/project/simplyfirebeta/) using 
`pip` as follows:


```bash 
pip install -i https://test.pypi.org/simple/ simplyfirebeta
```

The package will be made available on PyPI in the future for stable releases. 



Once installed, you can run SimplyFire from any directory: 

```bash
py -m simplyfire
```

SimplyFire is mainly a GUI-based software. 
However, the algorithms for analyses can be imported as packages and used in Python scripts. 

## Development

SimplyFire has been written to make electrophysiology analysis straightforward, automatable, and customizable.
Tools are provided to easily create custom plugins. 

Pull-requests for fixes and additions are welcome! 
Details on the development workflow will be available in the future. 

## License
SimplyFire is released under the GPLv3 or later license. 
