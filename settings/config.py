# Default selections run by the software (can be changed by the user):

FILEPATH = ""
# Path to the file or directory of files that should be used. The default value is an empty string: ""

PROGRAM = "density"
# Whether a "density" program or "lifetime" program should be run

SCALE = None
# Scale of the image (in nanometers per pixel). If unknown, leave as None.

############################################
############ THRESHOLD SETTINGS ############
############################################

LOWER_DOT_THRESH_SCALE = 1.5
# Scaling for the lower threshold defining the brightness of the dots. The default is 1.5, which corresponds to 1.5 standard deviations above the mean. Lower this value to increase the number of faint dots detected, or raise it to reduce the number.

UPPER_DOT_THRESH_SCALE = 5.0
# Scaling for the upper threshold defining the brightness of the dots. The default is 5, which corresponds to 5 standard deviations above the mean. Lower this value to reduce the number of bright dots detected, or raise it to increase the number.

LOWER_BLOB_THRESH_SCALE = 2.0
# Scaling for the lower threshold defining the brightness of the blobs. The default is 2, which corresponds to 2 times the value of UPPER_DOT_THRESH_SCALE. Lower this value to increase the number of blobs detected, or raise it to reduce the number.

THRESHOLD_DELTA = 0.1
# Amount by which a threshold will change when clicking the up and down arrows in the plotting UI. The default value is 0.1, and will be rounded to the nearest 0.1.

#################################################
############ IMAGE CONTRAST SETTINGS ############
#################################################

LOWER_CONTRAST = 0.0
# The lower bound of the plotting range for the data. The default value is 0.0, or 0 standard deviations above the mean of the dataset. Decrease this value if the image is too dark.

UPPER_CONTRAST = 5.0
# The upper bound of the plotting range for the data. The default value is 5.0, or 5 standard deviations above the mean of the dataset. Increase this value if the image is too saturated.

CONTRAST_DELTA = 0.5
# Amount by which the contrast will change when clicking the up and down arrows in the plotting UI. The default value is 0.5, and will be rounded to the nearest 0.1.

###########################################
############ LIFETIME SETTINGS ############
###########################################

SKIPS_ALLOWED = 1
# The number of consecutive images that are allowed to be skipped in a lifetime calculation

REMOVE_EDGE_FRAMES = True
# Whether edge frames should be removed from a lifetime calculation

LIFETIME_MIN_FOR_PLOT = 1
# Minimum lifetime to mark a dot in the output figure. The default value is 1, so that all dots with a lifetime of 1 or greater are plotted.

######################################
############ DOT SETTINGS ############
######################################

DOT_SIZE = 2
# Radius of exclusion between other dots (in pixels)

DOT_COLOR = "lime"
# The color used for dot markers in output plots. Only use default Python colors (https://matplotlib.org/3.5.0/gallery/color/named_colors.html)

DOT_THICKNESS = 0.5
# The line thickness used for dots in output plots. Default is 0.5.

#######################################
############ BLOB SETTINGS ############
#######################################

BLOB_SIZE = 5
# Radius of exclusion around blobs (in pixels)

PLOT_BLOBS = False
# Whether to plot markers on the blobs in outputted figures. Default is False.

BLOB_COLOR = "red"
# The color used for blob markers in output plots. Only use default Python colors (https://matplotlib.org/3.5.0/gallery/color/named_colors.html)

BLOB_THICKNESS = 0.5
# The line thickness used for blobs in output plots. Default is 0.5.

##########################################
############ POLYGON SETTINGS ############
##########################################

PLOT_POLYGON = True
# Whether to plot the polygon in outputted figures. Default is True.

POLYGON_COLOR = "darkorange"
# The color used for the polygon in output plots. Only use default Python colors (https://matplotlib.org/3.5.0/gallery/color/named_colors.html)

POLYGON_THICKNESS = 0.5
# The line thickness used for the polygon in output plots. Default is 0.5.

#########################################
############ WINDOW SETTINGS ############
#########################################

DYNAMIC_WINDOW = True
# Whether the window dynamically scales to the detected screen size.

WINDOW_HEIGHT = 550
WINDOW_WIDTH = 650
# Dimensions of “threshold adjustment” and “region selection” windows in pixels. DYNAMIC_WINDOW must be set to False to set these values manually.

WINDOW_X = 10
WINDOW_Y = 30
# Starting position of the upper left corner of all GUI windows in pixels

#########################################
############ OUTPUT SETTINGS ############
#########################################

SAVE_FIGURES = False
# Whether the displayed figures should be saved in a "figures" directory. Default is False.

DENSITY_OUTPUT_FILENAME = "densities.txt"
# The filename to be saved in the directory containing the images used for density measurement. This file will contain the measurements for each of those image files.

LIFETIME_OUTPUT_FILENAME = "lifetimes.txt"
# The filename to be saved in the directory containing the images used for lifetime measurement.

FIGURE_DIRECTORY_NAME = "figures/"
# The directory name where figures are to be saved (only if SAVE_FIGURES = True). The default is "figures/", but this can be changed if the user typically keeps a similarly named folder in their file structure for something else.
