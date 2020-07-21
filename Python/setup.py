from setuptools import setup
from pathlib import Path

version = "v1.6.0.2"

setup(
    name='tdw',
    version=version,
    description='3D simulation environment',
    long_description=Path('README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    url='https://github.com/threedworld-mit/tdw',
    download_url=f'https://github.com/threedworld-mit/tdw/archive/v{version}.tar.gz',
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
    keywords='unity simulation ml machine-learning',
    install_requires=['pyzmq', 'pymongo', 'numpy', 'scipy', 'pillow', 'tqdm', 'psutil', 'boto3', 'botocore'],
)
