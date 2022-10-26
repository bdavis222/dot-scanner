import settings.config as cfg

configurationsWindowTitle = "Dot Scanner - Configurations"

defaultConfigurationsEditorWindowTitle = "Dot Scanner - Default Configurations"

densityOutputFileHeader = f"# filename | density (per sq {'pix' if cfg.SCALE is None else 'um'}) | \
error | lowerDotThreshScale | upperDotThreshScale | lowerBlobThreshScale | blobSize | dotSize | \
polygon vertices (x, y)\n"

fileNumberingException = "Filenames must contain sequentially-ordered numbers to calculate \
lifetimes."

fileNumberingWarning = "WARNING: Filenames must contain sequentially-ordered numbers to calculate \
lifetimes."

filepathException = "Filepath must point to a file or directory."

invalidPolygonWarning = "\nNo valid, enclosed polygon drawn. No measurements made."

invalidThresholdEdit = "\nInvalid input. Previous threshold values will be retained."

lifetimeSingleFileException = "Lifetimes must be calculated using a directory of images, \
not a single image."

lifetimeSingleFileWarning = "WARNING: Lifetimes must be calculated using a directory of images, \
not a single image."

lowerBlobThreshScaleWarning = "\nWARNING: Lower blob threshold scale set below 1.0, which means \
blobs can be dimmer than the brightest dots, which shouldn't happen. Setting to 1.0."

noFilesException = "No files selected. Check the values of 'FILEPATH' and 'START_IMAGE' in the \
configurations file."

programNameException = "Invalid program name selected in configurations file."

regionSelectorWindowTitle = "Dot Scanner - Region Selection (click the plot to add polygon \
vertices)"

startImageDirectoryWarning = "WARNING: Start image must be in the same directory as the other \
lifetime files."

thresholdAdjusterWindowTitle = "Dot Scanner - Threshold Adjustment"

tooFewFramesException = "There are not enough images to get meaningful lifetimes."

unitsInconsistentException = f"Inconsistent units with other measurements already recorded in \
{cfg.DENSITY_OUTPUT_FILENAME}. To record measurements in units of per sq pix, set SCALE to None \
in configurations file. Otherwise, set the scale to the scale that was selected for the previous \
measurements."

upperDotThreshScaleWarning = "\nWARNING: Upper dot threshold scale set below lower dot threshold \
scale. Previous threshold values will be retained."

windowSizeWarning = "\nWARNING: The current window height is smaller than 550 pixels, potentially \
resulting in some buttons not being visible. However, the Return key will still allow confirmation \
in each window, and the Escape key will allow for skipping files, when the option is available."

def alreadyMeasuredNotification(filename):
	return f"\nFile {filename} already measured in {cfg.DENSITY_OUTPUT_FILENAME} file. Skipping."

def densityOutput(filename, density, error, thresholds, dotSize, blobSize, polygon):
	verticesStringList = []
	for vertex in polygon[:-1]:
		y, x = vertex
		verticesStringList.append(f"({x}, {y})")
	verticesString = ", ".join(verticesStringList)
	
	return f"{filename} {density} {error} {thresholds[0]} {thresholds[1]} {thresholds[2]} \
{blobSize} {dotSize} {verticesString}\n"

def fileSkippedNotification(filename):
	return f"\nFile {filename} skipped"

def lifetimeOutputFileHeader(polygon, userSettings):
	verticesStringList = []
	for vertex in polygon[:-1]:
		y, x = vertex
		verticesStringList.append(f"({x}, {y})")
	verticesString = ", ".join(verticesStringList)
	
	thresholdsStringList = []
	for threshold in userSettings.thresholds:
		thresholdsStringList.append(str(threshold))
	thresholdsString = ", ".join(thresholdsStringList)
	
	return f"# Polygon vertices (x, y): {verticesString}\n\
# Threshold scales: {thresholdsString}\n\
# Dot size: {userSettings.dotSize} | Blob size: {userSettings.blobSize} | Remove edge frames: \
{userSettings.removeEdgeFrames} | Skips allowed: {userSettings.skipsAllowed}\n\
#\n# x | y | lifetime | starting image\n"

###################################################################################################

defaultConfigFileText = '\
# Default selections run by the software (can be changed by the user):\n\
\n\
FILEPATH = ""\n\
# Path to the file or directory of files that should be used. The default value is an empty string: ""\n\
\n\
PROGRAM = "density"\n\
# Whether a "density" program or "lifetime" program should be run\n\
\n\
SCALE = None\n\
# Scale of the image (in nanometers per pixel). If unknown, leave as None.\n\
\n\
############################################\n\
############ THRESHOLD SETTINGS ############\n\
############################################\n\
\n\
LOWER_DOT_THRESH_SCALE = 1.5\n\
# Scaling for the lower threshold defining the brightness of the dots. The default is 1.5,\n\
# which corresponds to 1.5 standard deviations above the mean.\n\
# Lower this value to increase the number of faint dots detected, or raise it to reduce the number.\n\
\n\
UPPER_DOT_THRESH_SCALE = 5.0\n\
# Scaling for the upper threshold defining the brightness of the dots. The default is 5,\n\
# which corresponds to 5 standard deviations above the mean.\n\
# Lower this value to reduce the number of bright dots detected, or raise it to increase the number.\n\
\n\
LOWER_BLOB_THRESH_SCALE = 2.0\n\
# Scaling for the lower threshold defining the brightness of the blobs. The default is 2,\n\
# which corresponds to 2 times the value of UPPER_DOT_THRESH_SCALE.\n\
# Lower this value to increase the number of blobs detected, or raise it to reduce the number.\n\
\n\
THRESHOLD_DELTA = 0.1\n\
# Amount by which a threshold will change when clicking the up and down arrows in the plotting UI.\n\
# The default value is 0.1, and will be rounded to the nearest 0.1.\n\
\n\
#################################################\n\
############ IMAGE CONTRAST SETTINGS ############\n\
#################################################\n\
\n\
LOWER_CONTRAST = 0.0\n\
# The lower bound of the plotting range for the data. The default value is 0.0, or 0 standard\n\
# deviations above the mean of the dataset. Decrease this value if the image is too dark.\n\
\n\
UPPER_CONTRAST = 5.0\n\
# The upper bound of the plotting range for the data. The default value is 5.0, or 5 standard\n\
# deviations above the mean of the dataset. Increase this value if the image is too saturated.\n\
\n\
CONTRAST_DELTA = 0.5\n\
# Amount by which the contrast will change when clicking the up and down arrows in the plotting UI.\n\
# The default value is 0.5, and will be rounded to the nearest 0.1.\n\
\n\
###########################################\n\
############ LIFETIME SETTINGS ############\n\
###########################################\n\
\n\
SKIPS_ALLOWED = 1\n\
# The number of consecutive images that are allowed to be skipped in a lifetime calculation\n\
\n\
REMOVE_EDGE_FRAMES = True\n\
# Whether edge frames should be removed from a lifetime calculation\n\
\n\
######################################\n\
############ DOT SETTINGS ############\n\
######################################\n\
\n\
DOT_SIZE = 2\n\
# Radius of exclusion between other dots (in pixels)\n\
\n\
DOT_COLOR = "lime"\n\
# The color used for dot markers in output plots. \n\
# Only use default Python colors (https://matplotlib.org/3.5.0/gallery/color/named_colors.html)\n\
\n\
DOT_THICKNESS = 0.5\n\
# The line thickness used for dots in output plots. Default is 0.5.\n\
\n\
#######################################\n\
############ BLOB SETTINGS ############\n\
#######################################\n\
\n\
BLOB_SIZE = 5\n\
# Radius of exclusion around blobs (in pixels)\n\
\n\
PLOT_BLOBS = False\n\
# Whether to plot markers on the blobs in outputted figures. Default is False.\n\
\n\
BLOB_COLOR = "red"\n\
# The color used for blob markers in output plots. \n\
# Only use default Python colors (https://matplotlib.org/3.5.0/gallery/color/named_colors.html)\n\
\n\
BLOB_THICKNESS = 0.5\n\
# The line thickness used for blobs in output plots. Default is 0.5.\n\
\n\
##########################################\n\
############ POLYGON SETTINGS ############\n\
##########################################\n\
\n\
PLOT_POLYGON = True\n\
# Whether to plot the polygon in outputted figures. Default is True.\n\
\n\
POLYGON_COLOR = "darkorange"\n\
# The color used for the polygon in output plots. \n\
# Only use default Python colors (https://matplotlib.org/3.5.0/gallery/color/named_colors.html)\n\
\n\
POLYGON_THICKNESS = 0.5\n\
# The line thickness used for the polygon in output plots. Default is 0.5.\n\
\n\
#########################################\n\
############ WINDOW SETTINGS ############\n\
#########################################\n\
\n\
DYNAMIC_WINDOW = True\n\
# Whether the window dynamically scales to the detected screen size.\n\
\n\
WINDOW_HEIGHT = 550\n\
WINDOW_WIDTH = 650\n\
# Dimensions of “threshold adjustment” and “region selection” windows in pixels.\n\
# DYNAMIC_WINDOW must be set to False to set these values manually.\n\
\n\
WINDOW_X = 10\n\
WINDOW_Y = 30\n\
# Starting position of the upper left corner of all GUI windows in pixels\n\
\n\
#########################################\n\
############ OUTPUT SETTINGS ############\n\
#########################################\n\
\n\
SAVE_FIGURES = False\n\
# Whether the displayed figures should be saved in a "figures" directory. Default is False.\n\
\n\
DENSITY_OUTPUT_FILENAME = "densities.txt"\n\
# The filename to be saved in the directory containing the images used for density measurement.\n\
# This file will contain the measurements for each of those image files.\n\
\n\
LIFETIME_OUTPUT_FILENAME = "lifetimes.txt"\n\
# The filename to be saved in the directory containing the images used for lifetime measurement.\n\
\n\
FIGURE_DIRECTORY_NAME = "figures/"\n\
# The directory name where figures are to be saved (only if SAVE_FIGURES = True).\n\
# The default is "figures/", but this can be changed if the user typically keeps a similarly\n\
# named folder in their file structure for something else.\
'
