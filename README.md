# Dot Scanner

> Software designed for analysis of microscope imaging data

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate/?business=UA5NL9MJSFMVY)

Dot Scanner is designed to simplify analysis of microscope imaging data. The program runs entirely within a window-based graphical user interface, so as to not require any programming knowledge from the user in order to complete their image analysis (see the images below for examples). This software is _especially_ useful for noisy image data, where manual "by-eye" analysis is unreliable.

## Getting Started

### Dependencies

[Python 3](https://www.python.org/downloads/) must be installed before Dot Scanner can be installed.
**Python 2 is not supported.**
To make sure you have Python 3 installed, open a terminal window and run the following command:

```
python3 --version
```

_(Note: Running this command might require installing command line developer tools. This is normal, and it is ok to install this.)_

This should give version number (i.e., Python 3.x.x). If a "command not found" message is shown instead, then Python 3 is not properly installed.

### Installation

To install Dot Scanner, open a terminal window and run the following command:

```
pip3 install dotscanner
```

_(Note that the_ `pip` _command may be required instead of_ `pip3` _for some Python 3 installations.)_

To update Dot Scanner to the latest version, run the following command _(again, using_ `pip` _instead of_ `pip3` _for some Python 3 installations)_:

```
pip3 install dotscanner --upgrade
```

Dot Scanner can also be uninstalled at any time using the following command _(again, using_ `pip` _instead of_ `pip3` _for some Python 3 installations)_:

```
pip3 uninstall dotscanner
```

### Running the Software

To launch the main graphical user interface (GUI), run the following command:

```
dotscanner
```

**Note:** if you are getting an error when trying to run the program, run the following command to check your Python version:

```
python3 --version
```

Python 2 is _not_ supported, and Python 3 _must_ be installed to run Dot Scanner.

Some demo images are included in the [demo images folder](https://github.com/bdavis222/dot-scanner/blob/main/images/demo/) of this GitHub project, which can be downloaded and used as explained below to familiarize oneself with how the software works.

## The Configurations Window

The first window displayed in the GUI is the Configurations Window:

![](https://github.com/bdavis222/dot-scanner/blob/main/images/3.png)

If the **File** or **Folder** buttons are clicked, another window opens, allowing the user to select a file or folder for analysis (the images in the [demo images folder](https://github.com/bdavis222/dot-scanner/blob/main/images/demo/) can be downloaded to try this out for oneself):

![](https://github.com/bdavis222/dot-scanner/blob/main/images/4.png)

If repeated analysis is being performed at the same target filepath, the user can avoid continuously repeating this step by setting a default filepath. This is done by clicking the "Edit defaults" button. An entire configurations file is editable for other defaults as well. Any of the variables in this configurations file can be modified to change the default behavior of the software.

The software will run as expected on any folder where the most common file extension within the folder belongs to the images wanting to be analyzed. By default, the entire folder will be scanned, and the most common file type found within the folder will be set as the file type to analyze. If the user is experiencing issues with the wrong file type being selected, it is recommended that they reorganize their data into folders containing only their images to be analyzed.

If a folder containing several images is selected, the user has the option to change the default program from **Density** to **Lifetime**. _(Note that trying to run a lifetime program on a single image will not be allowed by the software.)_ This selection is made through the **Program** dropdown menu:

![](https://github.com/bdavis222/dot-scanner/blob/main/images/5.png)

If **Lifetime** is selected, some additional options will appear:

![](https://github.com/bdavis222/dot-scanner/blob/main/images/6.png)

### Descriptions of Configuration Options

#### Save figures

Selecting this option will output graphical plots to a `figures` folder that will be created within the folder containing the data being analyzed. These plots serve to allow the user to quickly verify their selections made during analysis.

#### Blob size

This option sets the radius (or, more accurately, roughly the half width of a square) of exclusion around "blobs" (in pixels). Blobs are regions of the image that are saturated and overexposed. For example, if the blob size is set to 5, then a square region extending 5 pixels in each direction (left, right, up, and down) will be defined from each overexposed pixel (meaning the square will span 11 pixels on each side, including the central pixel), and all of the pixels within those regions will be ignored during analysis. This ensures that the “dots” (the dimmer particles of interest in the image) are not too close to any of these regions, and thus the outer edges of blobs are not confused as dots.

#### Dot size

Similar to the blob size option, this sets the size of a "dot" in the dataset. Because dots should not overlap, the larger the dot size, the fewer dots will be detected, as dimmer pixels within a brighter dot's region will not be recognized as dots, and will therefore be removed.

#### Thresholds

There are three thresholds that can be set to adjust the detection sensitivity for "dots" and "blobs" in a given image. The three editable text boxes correspond to the following variables (displayed from left to right in the Configurations Window):

1. `LOWER_DOT_THRESH_SCALE`: Scaling for the lower threshold defining the brightness of the dots. The default is 1.5, which corresponds to 1.5 standard deviations above the mean of the data. Lower this value to increase the number of faint dots detected, or raise it to reduce the number.
2. `UPPER_DOT_THRESH_SCALE`: Scaling for the upper threshold defining the brightness of the dots. The default is 5, which corresponds to 5 standard deviations above the mean. Lower this value to reduce the number of bright dots detected, or raise it to increase the number.
3. `LOWER_BLOB_THRESH_SCALE`: Scaling for the lower threshold defining the brightness of the blobs. The default is 2, which corresponds to 2 times the value of `UPPER_DOT_THRESH_SCALE`. Lower this value to increase the number of blobs detected, or raise it to reduce the number.

#### Edit defaults

This opens a new window that allows the user to edit the default filepath or edit/reset the entire configuration file directly.

#### Use previous settings

This opens a new window that allows the user to browse for a previous .txt analysis file to use to repeat analysis. Information on which settings are reused during re-analysis is included in the header of each analysis file. There are two main scenarios for using this feature:

1. **Re-analyzing the same image or set of images.** _This is useful if the user wants to tweak one or two parameters of an analysis without running through the entire folder of images one by one again._
2. **Analyzing a new image or set of images with the same analysis settings as a previous analysis.** _This is useful if the user has already run analysis on a set of green images and wants to run the exact same analysis on their red counterparts, for example._

Clicking **Next**, or pressing the **return** key on the keyboard, will save the user’s selections and open the Threshold Adjustment Window.

### Descriptions of Configuration Options for the Lifetime Program

#### Start image

This option sets the first image to be considered in a lifetime calculation. The default is the first image in the folder (as the images _must be numbered sequentially_).

#### Skips allowed

This sets the number of consecutive images that are allowed to be skipped in a lifetime calculation. This can be useful for dimmer dots where an image or two in a series are relatively out of focus, resulting in an unwanted non-detection for those frames. By increasing the number of skips allowed, these particles will be retained as long as they are back in focus and bright enough for detection in subsequent frames.

#### Remove edge frames

This dictates whether edge frames should be removed from a lifetime calculation. If a particle is detected in the first frame of an image, for example, it cannot be determined whether the particle existed before the first image was taken, so it might not make sense to include this in a lifetime calculation (and the same may also be true for particles in the last frame). If the number of skips allowed in the lifetime calculation is greater than zero, this will increase how many edge frames are removed from analysis.

_Note: If the user is working with particularly noisy datasets where noise tends to be incorrectly marked as short-lived particles, the `LIFETIME_THRESHOLD` value in the configurations file can be adjusted to mark them as potentially unreliable in the output file._

## The Threshold Adjustment Window

Clicking the **Next** button, or pressing the **return** key on the keyboard, from the Configurations Window saves the configuration settings selected by the user and advances to the Threshold Adjustment Window. This window shows the image data with the dots and blobs identified, and features several button groups on the left sidebar:

![](https://github.com/bdavis222/dot-scanner/blob/main/images/7.png)

From top to bottom, these button groups perform the following actions:

#### View

These buttons allow four different viewing options: zooming in on the top left, top right, bottom left, bottom right, or zooming back out to show the full image. The user can also press the **spacebar** on the keyboard to cycle through these different views.

#### Contrast

These buttons adjust the contrast of the image.

#### Dots

These buttons adjust the sensitivity for detecting “dots” in the image (the fainter, smaller dots, as opposed to the much brighter and larger “blobs”). The user can also press the **up** and **down** arrow keys on the keyboard to make these adjustments.

#### Blobs

These buttons adjust the sensitivity for detecting “blobs” in the image. The user can also press the **right** and **left** arrow keys on the keyboard to make these adjustments. _Note: since increasing the blob sensitivity changes the threshold between blobs and dots, this results in a different number of dots being detected as well._

#### Edit

This button changes the left button bar view to display some manual threshold and size adjustment options:

![](https://github.com/bdavis222/dot-scanner/blob/main/images/8.png)

_(Once the thresholds or sizes are changed by entering new numbers into the text boxes, clicking the_ **Done** _button, or pressing the_ **return** _key on the keyboard, saves the settings and returns the left button bar to the original button configuration.)_

#### Reset

This button resets the adjusted thresholds back to the default values.

#### Skip

This button skips the current image (for example, if the user decides the data quality is not sufficient for measurement). The **escape** key on the keyboard can also be pressed to perform a skip.

## The Region Selector Window

Clicking the **Done** button, or pressing the **return** key on the keyboard, from the main Threshold Adjustment Window saves the threshold settings selected by the user and advances to the Region Selector Window:

![](https://github.com/bdavis222/dot-scanner/blob/main/images/9.png)

This window allows the user to click different locations on the image to set the vertices of a polygon within which the measurements will be made. At any point, the polygon can be reset by clicking the **Reset** button, or by pressing the **backspace** key on the keyboard. It is important to note that after at least three vertices have been placed, the dotted line shows how the program will enclose the polygon once the **Done** button, or the **return** key on the keyboard, is pressed. _(In other words, it is not necessary to re-click the first vertex created to close the polygon.)_

Information about the image processing will be displayed in the terminal, including progress bars to estimate the time to completion of longer processes, like lifetime calculations and the saving of multiple figures.

_Note: the extraneous `+[CATransaction synchronize]` output in the terminal window is a [known bug](https://developer.apple.com/forums/thread/722889) in macOS that will not affect your data._

## Authors

Holly Allen (holly.allen@colorado.edu)

Brian Davis

## Release History

- 1.5.8
  - Bug fixes
- 1.5.0
  - Added ability to remove unreliable lifetime data from noisy datasets
- 1.4.0
  - Added option to re-analyze data on different images using previous analysis settings
- 1.3.0
  - Added option to re-analyze data on the same image without redrawing regions
  - Added particle displacement tracking during lifetime measurement
  - Added histogram output for lifetimes measurements
- 1.2.0
  - Added options for editing the configuration file
  - Added startup processes to check the configuration file for errors
- 1.1.0
  - Migrated the remaining portions of the app from a terminal interface to a GUI
- 1.0.0
  - Initial Release

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/bdavis222/dot-scanner/blob/main/LICENSE) file for details.

## Development

To contribute, download or clone the project. From the top level of the project's folder structure, one can use the following command to run a local version of the software (e.g., for UI testing):

```
python -m dotscanner
```

_(Note that the_ `python3` _command may be required instead of_ `python` _for some Python installations.)_

### Testing

Unit tests for this software were written for use with [Python's built-in unittest framework](https://docs.python.org/3/library/unittest.html), and are stored in the `tests` folder. To run tests, download the project, navigate to the top level of the project's folder structure and run the following command:

```
python -m unittest
```

_(Note that the_ `python3` _command may be required instead of_ `python` _for some Python installations.)_

### Bug Reports and Feature Requests

To report a bug, visit the [issues page](https://github.com/bdavis222/dot-scanner/issues). New feature requests are also welcome!

## Citations

When using this program on data used in published works, please cite:

Allen, H., Davis, B., Patel, J., & Gu, Y. 2024 _(in prep.)_
