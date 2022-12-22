from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='dotscanner',
    version='1.2.11', # Required 
    description='A program designed for analysis of microscope imaging data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bdavis222/dotscanner',
    author='Holly Allen and Brian Davis',
    author_email='holly.allen@colorado.edu',
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows'
    ],
    packages=find_packages(),
    py_modules=['dotscanner', 'dotscanner.ui', 'settings', 'tests'],
    python_requires='>=3.7, <4',
    install_requires=['matplotlib', 'numpy'],
    project_urls={
        'Bug Reports': 'https://github.com/bdavis222/dotscanner/issues',
        'Funding': 'https://www.paypal.com/donate/?business=UA5NL9MJSFMVY',
        'Source': 'https://github.com/bdavis222/dotscanner',
    },
    entry_points={
        'console_scripts': [
            'dotscanner = dotscanner.__main__:main'
        ]
    }
)
