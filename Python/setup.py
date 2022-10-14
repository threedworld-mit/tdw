from setuptools import setup, find_packages
from pathlib import Path
import re

__version__ = "1.10.8.1"
readme_path = Path('../README.md')
if readme_path.exists():
    long_description = readme_path.read_text(encoding='utf-8')
    # Replace relative markdown links with absolute https links.
    long_description = re.sub(r'\[(.*?)\]\((Documentation/(.*?))\)',
                              r'[\1](https://github.com/threedworld-mit/tdw/blob/master/\2)',
                              long_description,
                              flags=re.MULTILINE)
    long_description = long_description.replace("![](splash.jpg)",
                                                '<img src="https://raw.githubusercontent.com/threedworld-mit/tdw/master/splash.jpg">')
else:
    long_description = "See: https://github.com/threedworld-mit/tdw"

setup(
    name='tdw',
    version=__version__,
    description='3D simulation environment',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/threedworld-mit/tdw',
    author_email='alters@mit.edu',
    author='Massachusetts Institute of Technology',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    packages=find_packages(),
    include_package_data=True,
    keywords='unity simulation ml machine-learning',
    install_requires=['pyzmq', 'numpy', 'scipy', 'pillow', 'tqdm', 'psutil', 'boto3', 'botocore', 'requests',
                      'pyinstaller', 'overrides', 'packaging', 'pydub', 'ikpy==3.1', 'screeninfo']
)
