from setuptools import setup
from tdw.version import __version__
from pathlib import Path

setup(
    name='tdw',
    version=__version__,
    description='3D simulation environment',
    long_description=Path('../README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    url='https://github.com/threedworld-mit/tdw',
    author_email='alters@mit.edu',
    author='???',
    download_url='???',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    keywords='unity simulation',
    install_requires=['pyzmq', 'pymongo', 'numpy', 'scipy', 'pillow', 'tqdm', 'psutil', 'boto3', 'botocore'],
)
