from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="Dot Scanner",  # Required
    version="0.1.0",  # Required
    description="A program designed for analysis of microscope imaging data",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional
    url="https://github.com/bdavis222/dotscanner",  # Optional
    author="Holly Allen and Brian Davis",  # Optional
    author_email="holly.allen@colorado.edu",  # Optional
    classifiers=[  # Optional
        "Intended Audience :: Scientists",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    package_dir={"": "dotscanner"},  # Optional
    packages=find_packages(where="dotscanner"),  # Required
    python_requires=">=3.7, <4",
    install_requires=["matplotlib", "numpy"],
    project_urls={  # Optional
        "Bug Reports": "https://github.com/bdavis222/dotscanner/issues",
        "Funding": "https://www.paypal.com/donate/?business=UA5NL9MJSFMVY",
        "Source": "https://github.com/bdavis222/dotscanner",
    },
)
