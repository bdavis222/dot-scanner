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

To install this software and its dependencies:

1. Download this project
2. Navigate to the top-level directory of the downloaded project in a terminal window
3. Run the following command:

```
python setup.py install
```

(Note that the `python3` command may be required instead of `python` for some Python installations.)

This should automate the dependency installation process. Alternatively, the [matplotlib](https://pypi.org/project/matplotlib/) and [numpy](https://pypi.org/project/numpy/) dependencies can be installed independently via the following commands:

```
pip install matplotlib
pip install numpy
```

(Note that the `pip3` command may be required instead of `pip` for some Python installations.)

### How to run the software

To launch the main graphical user interface (GUI), navigate to the top level of the project's directory structure and run the following command:

```
python -m dotscanner
```

(Note that the `python3` command may be required instead of `python` for some Python installations.)

When launched, the user must select the file or directory of files to be analyzed. The "File" and "Folder" buttons will allow the user to navigate their filesystem to select the desired filepath.

If repeated analysis is being performed at the same target filepath, the user can avoid continuously repeating this step by setting a default filepath. This is done by modifying the `FILEPATH` variable in the `config.py` file. Any of the variables in this configurations file can be modified to change the default behavior of the software. However, users should be *very careful* when changing values in the configurations file, only selecting values that are explicitly allowed, as explained in the comments within the file.

The software will run as expected on any directory where the most common file extension within the directory belongs to the images wanting to be analyzed. By default, the entire directory will be scanned, and the most common file type found within the directory will be set as the file type to analyze. If the user is experiencing issues with the wrong file type being selected, it is recommended that they reorganize their data into directories containing only their images to be analyzed. 

#### Density Measurement

To measure the density of particles detected in a microscope image, one will run the "density" program. This is selected via a dropdown list in the GUI, and may already be set as the default program, depending on the preferences set in `config.py`.

For a "density" program setting, the user will use the next window that loads to adjust the detection thresholds used by the program. After this, another window will load to allow the user to click on the screen to draw the vertices of a polygon that will enclose a custom region for density measurement. 

A major benefit of this software is its ability to automatically reject portions of this custom region with bright, overexposed, or saturated data. Because of this, the user doesn't have to draw around those regions when defining the polygon, as the program will calculate the area used in the density measurement by subtracting the area taken up by the rejected portions of the image within the polygon.

#### Lifetime Measurement

In addition to the density measuremnt program, a "lifetime" measurement program is also available, selected via the dropdown list button in the initial GUI window when the software is launched. This program will similarly do two things:

1. Allow the user to adjust thresholds
2. Define a study region where the lifetimes of the particles in a series of images will be measured

Because this only works with a series of images, the user must initially select a directory, not a single file.

### Other Configuration Options

Several configuration options are available for both the density and lifetime programs, as described below. All of these have default values that can be modified in the `config.py` file. For more information, see the publication listed in the Citations section at the bottom of this readme file.

#### Save Figures

Selecting this option will output graphical plots to a `figures` directory that will be created within the working directory of the data being analyzed. These plots serve to allow the user to quickly verify their selections made during analysis. 

#### Blob Size

This option sets the radius (or, more accurately, roughly the half width of a square) of exclusion around "blobs" (in pixels). Blobs are regions of the image that are saturated and overexposed. For example, if the blob size is set to 5, then a square region extending 5 pixels in each direction (left, right, up, and down) will be defined from each overexposed pixel (meaning the square will span 11 pixels on each side, including the central pixel), and all of the pixels within those regions will be ignored during analysis. This ensures that the "dots"---the dimmer particles of interest in the image---are not too close to any of these regions, and thus the outer edges of blobs are not confused as dots. 

#### Dot Size

Similar to the blob size option, this sets the size of a "dot" in the dataset. Because dots should not overlap, the larger the dot size, the fewer dots will be detected, as dimmer pixels within a brighter dot's region will not be recognized as dots, and will therefore be removed. 

#### Thresholds

There are three thresholds that can be set to adjust the detection sensitivity for "dots" and "blobs" in a given image. The three editable text boxes in the startup GUI correspond to the following variables in `config.py` (displayed from left to right in the GUI):

1. LOWER_DOT_THRESH_SCALE: Scaling for the lower threshold defining the brightness of the dots. The default is 1.5, which corresponds to 1.5 standard deviations above the mean. Lower this value to increase the number of faint dots detected, or raise it to reduce the number.
2. UPPER_DOT_THRESH_SCALE: Scaling for the upper threshold defining the brightness of the dots. The default is 5, which corresponds to 5 standard deviations above the mean. Lower this value to reduce the number of bright dots detected, or raise it to increase the number.
3. LOWER_BLOB_THRESH_SCALE: Scaling for the lower threshold defining the brightness of the blobs. The default is 2, which corresponds to 2 times the value of UPPER_DOT_THRESH_SCALE. Lower this value to increase the number of blobs detected, or raise it to reduce the number.

#### Skips Allowed

This sets the number of consecutive images that are allowed to be skipped in a lifetime calculation. This can be useful for dimmer dots where an image or two in a series are relatively out of focus, resulting in an unwanted non-detection for those frames. By increasing the number of skips allowed, these particles will be retained as long as they are back in focus and bright enough for detection in subsequent frames. 

#### Start Image

This option sets the first image to be considered in a lifetime calculation.

#### Remove Edge Frames

This dictates whether edge frames should be removed from a lifetime calculation. If a particle is detected in the first frame of an image, for example, it cannot be determined whether the particle existed before the first image was taken, so it might not make sense to include this in a lifetime calculation (and the same may also be true for particles in the last frame). If the number of skips allowed in the lifetime calculation is greater than zero, this will increase how many edge frames are removed from analysis. 

## Authors

Holly Allen (holly.allen@colorado.edu)

Brian Davis

## Release History

* 1.0.0
    * Initial Release

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/bdavis222/dotscanner/LICENSE) file for details.

## Development

### Testing

Unit tests for this software were written for use with [Python's built-in unittest framework](https://docs.python.org/3/library/unittest.html), and are stored in the `tests` directory. To run tests, navigate to the top level of the project's directory structure and run the following command:

```
python -m unittest
```

(Note that the `python3` command may be required instead of `python` for some Python installations.)

### Bug Reports and Feature Requests

To report a bug, visit the [issues page](https://github.com/bdavis222/dotscanner/issues). New feature requests are also welcome!

## Citations

When using this program on data used in published works, please cite:

Allen, H., & Davis, B., Patel, J., & Gu, Y. 2022 (in prep.)
