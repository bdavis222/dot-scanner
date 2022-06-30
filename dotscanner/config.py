# Default selections run by the software (can be changed by the user):

FILEPATH = ""
# Path to the file or directory of files that should be used

PROGRAM = "density"
# Whether a "density" program or "lifetime" program should be run

LOWER_DOT_THRESH_SCALE = 1.5
# Scaling for the lower threshold defining the brightness of the dots. The default is 1.5,
# which corresponds to 1.5 standard deviations above the mean.
# Lower this value to increase the number of faint dots detected, or raise it to reduce the number.

UPPER_DOT_THRESH_SCALE = 5
# Scaling for the upper threshold defining the brightness of the dots. The default is 5,
# which corresponds to 5 standard deviations above the mean.
# Lower this value to reduce the number of bright dots detected, or raise it to increase the number.

LOWER_BLOB_THRESH_SCALE = 2
# Scaling for the lower threshold defining the brightness of the blobs. The default is 2,
# which corresponds to 2 times the value of UPPER_DOT_THRESH_SCALE.
# Lower this value to increase the number of blobs detected, or raise it to reduce the number.

THRESHOLD_DELTA = 0.1
# Amount by which a threshold will change when clicking the up and down arrows in the plotting UI.
# The default value is 0.1.

BLOB_SIZE = 5
# Radius of exclusion around blobs (in pixels)

DOT_SIZE = 2
# Radius of exclusion between other dots (in pixels)

SCALE = None
# Scale of the image (in nanometers per pixel). If unknown, leave as None.

SKIPS_ALLOWED = 1
# The number of consecutive images that are allowed to be skipped in a lifetime calculation

REMOVE_EDGE_FRAMES = True
# Whether edge frames should be removed from a lifetime calculation

SAVE_FIGURES = False
# Whether the displayed figures should be saved in a "figures" directory. Default is False.

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
# Dimensions of “threshold adjustment” and “region selection” windows in pixels

WINDOW_X = 10
WINDOW_Y = 30
# Starting position of the upper left corner of all GUI windows in pixels

DOT_COLOR = "lime"
# The color used for dot markers in plots. 
# Only use default Python colors (https://matplotlib.org/3.5.0/gallery/color/named_colors.html)

BLOB_COLOR = "red"
# The color used for blob markers in plots. 
# Only use default Python colors (https://matplotlib.org/3.5.0/gallery/color/named_colors.html)

DENSITY_OUTPUT_FILENAME = "densities.txt"
# The filename to be saved in the directory containing the images used for density measurement.
# This file will contain the measurements for each of those image files.

LIFETIME_OUTPUT_FILENAME = "lifetimes.txt"
# The filename to be saved in the directory containing the images used for lifetime measurement.

FIGURE_DIRECTORY_NAME = "figures/"
# The directory name where figures are to be saved (only if SAVE_FIGURES = True).
# The default is "figures/", but this can be changed if the user typically keeps a similarly
# named folder in their file structure for something else.
