# Dot Scanner
> Software designed for analysis of microscope imaging data

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate/?business=UA5NL9MJSFMVY)

Dot Scanner is designed to simplify analysis of microscope imaging data. The program runs entirely within a window-based graphical user interface, so as to not require any programming knowledge from the user in order to complete their image analysis (see the images below for examples). This software is *especially* useful for noisy image data, where manual "by-eye" analysis is unreliable.

## Getting Started

### Dependencies

[Python 3](https://www.python.org/downloads/) must be installed before Dot Scanner can be installed. 

### Installation

To install Dot Scanner, open a terminal window and run the following command:

```
pip install dotscanner
```

*(Note that the* `pip3` *command may be required instead of* `pip` *for some Python installations.)*

### Running the Software

To launch the main graphical user interface (GUI), run the following command:

```
dotscanner
```

Some demo images are included in the `images/demo/` folder, which can be downloaded and used as explained below to familiarize oneself with how the software works. 

## The Configurations Window
The first window displayed in the GUI is the Configurations Window:
![](https://github.com/bdavis222/dotscanner/blob/main/images/3.png)

If the **File** or **Folder** buttons are clicked, another window opens, allowing the user to select a file or folder for analysis (the images in the `images/demo/` folder can be downloaded to try this out for oneself):
![](https://github.com/bdavis222/dotscanner/blob/main/images/4.png)

If repeated analysis is being performed at the same target filepath, the user can avoid continuously repeating this step by setting a default filepath. This is done by clicking the "Edit defaults" button. An entire configurations file is editable for other defaults as well. Any of the variables in this configurations file can be modified to change the default behavior of the software.

The software will run as expected on any folder where the most common file extension within the folder belongs to the images wanting to be analyzed. By default, the entire folder will be scanned, and the most common file type found within the folder will be set as the file type to analyze. If the user is experiencing issues with the wrong file type being selected, it is recommended that they reorganize their data into folders containing only their images to be analyzed. 

If a folder containing several images is selected, the user has the option to change the default program from **Density** to **Lifetime**. *(Note that trying to run a lifetime program on a single image will not be allowed by the software.)* This selection is made through the **Program** dropdown menu:
![](https://github.com/bdavis222/dotscanner/blob/main/images/5.png)

If **Lifetime** is selected, some additional options will appear:
![](https://github.com/bdavis222/dotscanner/blob/main/images/6.png)

### Descriptions of Configuration Options

#### Save figures
Selecting this option will output graphical plots to a `figures` folder that will be created within the folder containing the data being analyzed. These plots serve to allow the user to quickly verify their selections made during analysis.

#### Blob size
This option sets the radius (or, more accurately, roughly the half width of a square) of exclusion around "blobs" (in pixels). Blobs are regions of the image that are saturated and overexposed. For example, if the blob size is set to 5, then a square region extending 5 pixels in each direction (left, right, up, and down) will be defined from each overexposed pixel (meaning the square will span 11 pixels on each side, including the central pixel), and all of the pixels within those regions will be ignored during analysis. This ensures that the “dots”—the dimmer particles of interest in the image—are not too close to any of these regions, and thus the outer edges of blobs are not confused as dots.

#### Dot size
Similar to the blob size option, this sets the size of a "dot" in the dataset. Because dots should not overlap, the larger the dot size, the fewer dots will be detected, as dimmer pixels within a brighter dot's region will not be recognized as dots, and will therefore be removed.

#### Thresholds
There are three thresholds that can be set to adjust the detection sensitivity for "dots" and "blobs" in a given image. The three editable text boxes correspond to the following variables (displayed from left to right in the Configurations Window):
1. `LOWER_DOT_THRESH_SCALE`: Scaling for the lower threshold defining the brightness of the dots. The default is 1.5, which corresponds to 1.5 standard deviations above the mean of the data. Lower this value to increase the number of faint dots detected, or raise it to reduce the number.
2. `UPPER_DOT_THRESH_SCALE`: Scaling for the upper threshold defining the brightness of the dots. The default is 5, which corresponds to 5 standard deviations above the mean. Lower this value to reduce the number of bright dots detected, or raise it to increase the number.
3. `LOWER_BLOB_THRESH_SCALE`: Scaling for the lower threshold defining the brightness of the blobs. The default is 2, which corresponds to 2 times the value of `UPPER_DOT_THRESH_SCALE`. Lower this value to increase the number of blobs detected, or raise it to reduce the number.

### Descriptions of Configuration Options for the Lifetime Program

#### Start image
This option sets the first image to be considered in a lifetime calculation. The default is the first image in the folder (as the images *must be numbered sequentially*).

#### Skips allowed
This sets the number of consecutive images that are allowed to be skipped in a lifetime calculation. This can be useful for dimmer dots where an image or two in a series are relatively out of focus, resulting in an unwanted non-detection for those frames. By increasing the number of skips allowed, these particles will be retained as long as they are back in focus and bright enough for detection in subsequent frames.
      
#### Remove edge frames
This dictates whether edge frames should be removed from a lifetime calculation. If a particle is detected in the first frame of an image, for example, it cannot be determined whether the particle existed before the first image was taken, so it might not make sense to include this in a lifetime calculation (and the same may also be true for particles in the last frame). If the number of skips allowed in the lifetime calculation is greater than zero, this will increase how many edge frames are removed from analysis.

#### Edit defaults
This opens a new window that allows the user to edit or reset the configuration file directly.

Clicking **Next**, or pressing the **return** key on the keyboard, will save the user’s selections and open the Threshold Adjustment Window.

## The Threshold Adjustment Window
This window shows the image data with the dots and blobs identified, and features several button groups on the left sidebar:
![](https://github.com/bdavis222/dotscanner/blob/main/images/7.png)

From top to bottom, these button groups perform the following actions:

#### View
These buttons allow four different viewing options: zooming in on the top left, top right, bottom left, bottom right, or zooming back out to show the full image. The user can also press the **spacebar** on the keyboard to cycle through these different views.

#### Contrast
These buttons adjust the contrast of the image.

#### Dots
These buttons adjust the sensitivity for detecting “dots” in the image (the fainter, smaller dots, as opposed to the much brighter and larger “blobs”). The user can also press the **up** and **down** arrow keys on the keyboard to make these adjustments.

#### Blobs
These buttons adjust the sensitivity for detecting “blobs” in the image. The user can also press the **right** and **left** arrow keys on the keyboard to make these adjustments.

#### Edit
This button changes the left button bar view to display some manual threshold adjustment options:
![](https://github.com/bdavis222/dotscanner/blob/main/images/8.png)

*(Once the thresholds are changed by entering new numbers into the text boxes, the* **Done** *button saves the settings and returns the left button bar to the original button configuration.)*

#### Reset
This button resets the adjusted thresholds back to the default values.

#### Skip
This button skips the current image (for example, if the user decides the data quality is not sufficient for measurement). The **escape** key on the keyboard can also be pressed to perform a skip.

## The Region Selector Window
Clicking the **Done** button, or pressing the **return** key on the keyboard, from the main Threshold Adjustment Window saves the threshold settings selected by the user and advances to the Region Selector Window:
![](https://github.com/bdavis222/dotscanner/blob/main/images/9.png)

This window allows the user to click different locations on the image to set the vertices of a polygon within which the measurements will be made. At any point, the polygon can be reset by clicking the **Reset** button, or by pressing the **backspace** key on the keyboard. It is important to note that after at least three vertices have been placed, the dotted line shows how the program will enclose the polygon once the **Done** button, or the **return** key on the keyboard, is pressed. *(In other words, it is not necessary to re-click the first vertex created to close the polygon.)*

Information about the image processing will be displayed in the terminal, including progress bars to estimate the time to completion of longer processes, like lifetime calculations and the saving of multiple figures.

## Authors

Holly Allen (holly.allen@colorado.edu)

Brian Davis

## Release History

* 1.2.7
     * Bug fixes
* 1.2.0
     * Added options for editing the configuration file
     * Added startup processes to check the configuration file for errors
* 1.1.0
     * Migrated the remaining portions of the app from a terminal interface to a GUI
* 1.0.0
     * Initial Release

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/bdavis222/dotscanner/blob/main/LICENSE) file for details.

## Development

To contribute, download or clone the project. From the top level of the project's folder structure, one can use the following command to run a local version of the software (e.g., for UI testing):

```
python -m dotscanner
```

*(Note that the* `python3` *command may be required instead of* `python` *for some Python installations.)*

### Testing

Unit tests for this software were written for use with [Python's built-in unittest framework](https://docs.python.org/3/library/unittest.html), and are stored in the `tests` folder. To run tests, download the project, navigate to the top level of the project's folder structure and run the following command:

```
python -m unittest
```

*(Note that the* `python3` *command may be required instead of* `python` *for some Python installations.)*

### Bug Reports and Feature Requests

To report a bug, visit the [issues page](https://github.com/bdavis222/dotscanner/issues). New feature requests are also welcome!

## Citations

When using this program on data used in published works, please cite:

Allen, H., Davis, B., Patel, J., & Gu, Y. 2022 (in prep.)
