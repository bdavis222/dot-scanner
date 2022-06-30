# Dot Scanner
> Software designed for analysis of microscope imaging data

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate/?business=UA5NL9MJSFMVY)

One to two paragraph statement about the product and what it does.

## Getting Started

### Dependencies

The requirements to run this software are:
- [Python 3](https://www.python.org/downloads/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- [numpy](https://pypi.org/project/numpy/)

### Installation

To install this software and its dependencies, download this project, navigate to the top-level directory of the downloaded project in a terminal window, and run the following command:

```
python setup.py install
```

This should automate the dependency installation process. Alternatively, the matplotlib and numpy dependencies can be installed independently via the following commands:

```
pip install matplotlib
pip install numpy
```

### How to run the software

To launch the main graphical user interface (GUI), navigate to the top level of the project's directory structure and run the following command:

```
python -m dotscanner
```

When launched, the user must select the file or directory of files to be analyzed. The "File" and "Folder" buttons will allow the user to navigate their filesystem to select the desired filepath.

If repeated analysis is being performed at the same target filepath, the user can avoid continuously repeating this step by setting a default filepath. This is done by modifying the `FILEPATH` variable in the `config.py` file. Any of the variables in this configurations file can be modified to change the default behavior of the software.

#### Density Measurement

To measure the density of particles detected in a microscope image, one will run the "density" program. This is selected via a dropdown list in the GUI, and may already be set as the default program, depending on the preferences set in `config.py`.

For a "density" program setting, the user will use the next window that loads to adjust the detection thresholds used by the program. After this, another window will load to allow the user to click on the screen to draw the vertices of a polygon that will enclose a custom region for density measurement. A major benefit of this software is its ability to automatically reject portions of this custom region with bright, overexposed, or saturated data. Because of this, the user doesn't have to draw around those regions when defining the polygon, as the program will calculate the area used in the density measurement by subtracting the area taken up by the rejected portions of the image within the polygon.

#### Lifetime Measurement

In addition to the density program, a "lifetime" program is also available, selected via the dropdown list button in the initial GUI window when the software is launched. This program will similarly 1) allow the user to adjust thresholds, and then 2) define a study region where the lifetimes of the particles in a series of images will be measured. Because this only works with a series of images, the user must initially select a directory, not a single file.

For each of these programs, there are several configuration options. For more information, see the publication listed in the Citations section at the bottom of this readme file.

## Development

### Testing

Unit tests for this software were written for use with [Python's built-in unittest framework](https://docs.python.org/3/library/unittest.html), and are stored in the `tests` directory. To run tests, navigate to the top level of the project's directory structure and run the following command:

```
python -m unittest
```

### Bug Reporting

To report a bug, visit our [issues page](https://github.com/bdavis222/dotscanner/issues). New feature requests are also welcome!

## Authors

Holly Allen (holly.allen@colorado.edu)

Brian Davis

## Release History

* 1.0.0
    * Initial Release

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citations

When using this program on data used in published works, please cite:

Allen, H., & Davis, B., Patel, J., & Gu, Y. 2022 (in prep.)
