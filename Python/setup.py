from setuptools import setup, find_packages
from pathlib import Path

__version__ = "1.8.18.1"
readme_path = Path('../README.md')
if readme_path.exists():
    long_description = readme_path.read_text(encoding='utf-8')
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
                      'pyinstaller'],
)
