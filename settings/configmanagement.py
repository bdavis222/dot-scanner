from dotscanner.ui.DialogWindow import DialogWindow
import traceback

def runChecks():
	try:
		scanConfigFileForErrors()
	except Exception as exception:
		print("\n", traceback.format_exc())
		showStartupErrorDialog()
		quit()

def scanConfigFileForErrors():
	import settings.config as cfg
	import matplotlib.colors as colors
	
	matplotlibColors = set(colors.BASE_COLORS.keys())
	for color in colors.TABLEAU_COLORS.keys():
		matplotlibColors.add(color)
	for color in colors.CSS4_COLORS.keys():
		matplotlibColors.add(color)
	
	assert type(cfg.FILEPATH) == str
	assert cfg.PROGRAM in ["density", "lifetime"]
	assert cfg.SCALE is None or type(cfg.SCALE) in [int, float]
	
	assert type(cfg.LOWER_DOT_THRESH_SCALE) in [int, float]
	assert type(cfg.UPPER_DOT_THRESH_SCALE) in [int, float]
	assert cfg.LOWER_DOT_THRESH_SCALE <= cfg.UPPER_DOT_THRESH_SCALE
	assert type(cfg.LOWER_BLOB_THRESH_SCALE) in [int, float]
	assert cfg.LOWER_BLOB_THRESH_SCALE >= 1
	assert type(cfg.THRESHOLD_DELTA) in [int, float]
	
	assert type(cfg.LOWER_CONTRAST) in [int, float]
	assert type(cfg.UPPER_CONTRAST) in [int, float]
	assert cfg.LOWER_CONTRAST < cfg.UPPER_CONTRAST
	assert type(cfg.CONTRAST_DELTA) in [int, float]
	
	assert type(cfg.SKIPS_ALLOWED) == int
	assert cfg.SKIPS_ALLOWED >= 0
	assert type(cfg.REMOVE_EDGE_FRAMES) == bool
	assert type(cfg.LIFETIME_MIN_FOR_PLOT) == int
	
	assert type(cfg.DOT_SIZE) == int
	assert cfg.DOT_COLOR in matplotlibColors
	assert type(cfg.DOT_THICKNESS) in [int, float]
	
	assert type(cfg.BLOB_SIZE) == int
	assert type(cfg.PLOT_BLOBS) == bool
	assert cfg.BLOB_COLOR in matplotlibColors
	assert type(cfg.BLOB_THICKNESS) in [int, float]
	
	assert type(cfg.PLOT_POLYGON) == bool
	assert cfg.POLYGON_COLOR in matplotlibColors
	assert type(cfg.POLYGON_THICKNESS) in [int, float]
	
	assert type(cfg.DYNAMIC_WINDOW) == bool
	assert type(cfg.WINDOW_HEIGHT) in [int, float]
	assert type(cfg.WINDOW_WIDTH) in [int, float]
	assert type(cfg.WINDOW_X) in [int, float]
	assert type(cfg.WINDOW_Y) in [int, float]
	
	assert type(cfg.SAVE_FIGURES) == bool
	assert type(cfg.DENSITY_OUTPUT_FILENAME) == str
	assert type(cfg.LIFETIME_OUTPUT_FILENAME) == str
	assert type(cfg.FIGURE_DIRECTORY_NAME) == str

def showEditConfigFileDialog():
	DialogWindow(
		title="Edit config file?",
		message="\
Are you sure you want to edit this file? \n\
Dot scanner will close during editing. \n\
The edited file must be saved to retain any changes.",
		positiveButtonText="Edit file",
		negativeButtonText="Cancel",
		positiveButtonAction=editConfigFile,
		windowWidth=400
		)

def showResetConfigFileDialog():
	DialogWindow(
		title="Reset config file?",
		message="\
Are you sure you want to reset this file? \n\
Doing so will close Dot Scanner and restore the default values.",
		positiveButtonText="Reset file",
		negativeButtonText="Cancel",
		positiveButtonAction=resetConfigFile,
		windowWidth=420,
		windowHeight=125
		)

def showStartupErrorDialog():
	DialogWindow(
		title="Config file error",
		message="\
Errors found in config file. \n\
Fix the errors manually or reset the file.\n\
See terminal output for details.",
		positiveButtonText="Reset",
		negativeButtonText="Edit",
		positiveButtonAction=showResetConfigFileDialog,
		negativeButtonAction=showEditConfigFileDialog,
		windowWidth=400,
		windowX=10,
		windowY=30
		)

def getConfigFilePath():
	pathArray = __file__.split("/")
	completePathArray = []
	for directory in pathArray[:-2]:
		completePathArray.append(directory)
		completePathArray.append("/")
	completePathArray.append("settings")
	completePathArray.append("/")
	completePathArray.append("config.py")
	return "".join(completePathArray)

def editConfigFile():
	import os
	import subprocess
	
	configFilePath = getConfigFilePath()
	
	if os.name == 'nt': # Windows operating system
		commandArray = ["Notepad", configFilePath]
	else:
		commandArray = ["open", "-a", "TextEdit", configFilePath]
	
	subprocess.call(commandArray)
	
	quit()

def resetConfigFile():	
	configFilePath = getConfigFilePath()
	
	with open(configFilePath, "w") as file:
		file.write('\
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
# Scaling for the lower threshold defining the brightness of the dots. The default is 1.5,which corresponds to 1.5 standard deviations above the mean. Lower this value to increase the number of faint dots detected, or raise it to reduce the number.\n\
\n\
UPPER_DOT_THRESH_SCALE = 5.0\n\
# Scaling for the upper threshold defining the brightness of the dots. The default is 5, which corresponds to 5 standard deviations above the mean. Lower this value to reduce the number of bright dots detected, or raise it to increase the number.\n\
\n\
LOWER_BLOB_THRESH_SCALE = 2.0\n\
# Scaling for the lower threshold defining the brightness of the blobs. The default is 2, which corresponds to 2 times the value of UPPER_DOT_THRESH_SCALE. Lower this value to increase the number of blobs detected, or raise it to reduce the number.\n\
\n\
THRESHOLD_DELTA = 0.1\n\
# Amount by which a threshold will change when clicking the up and down arrows in the plotting UI. The default value is 0.1, and will be rounded to the nearest 0.1.\n\
\n\
#################################################\n\
############ IMAGE CONTRAST SETTINGS ############\n\
#################################################\n\
\n\
LOWER_CONTRAST = 0.0\n\
# The lower bound of the plotting range for the data. The default value is 0.0, or 0 standard deviations above the mean of the dataset. Decrease this value if the image is too dark.\n\
\n\
UPPER_CONTRAST = 5.0\n\
# The upper bound of the plotting range for the data. The default value is 5.0, or 5 standard deviations above the mean of the dataset. Increase this value if the image is too saturated.\n\
\n\
CONTRAST_DELTA = 0.5\n\
# Amount by which the contrast will change when clicking the up and down arrows in the plotting UI. The default value is 0.5, and will be rounded to the nearest 0.1.\n\
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
LIFETIME_MIN_FOR_PLOT = 1\n\
# Minimum lifetime to mark a dot in the output figure. The default value is 1, so that all dots with a lifetime of 1 or greater are plotted.\n\
\n\
######################################\n\
############ DOT SETTINGS ############\n\
######################################\n\
\n\
DOT_SIZE = 2\n\
# Radius of exclusion between other dots (in pixels)\n\
\n\
DOT_COLOR = "lime"\n\
# The color used for dot markers in output plots. Only use default Python colors (https://matplotlib.org/3.5.0/gallery/color/named_colors.html)\n\
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
# The color used for blob markers in output plots. Only use default Python colors (https://matplotlib.org/3.5.0/gallery/color/named_colors.html)\n\
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
# The color used for the polygon in output plots. Only use default Python colors (https://matplotlib.org/3.5.0/gallery/color/named_colors.html)\n\
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
# Dimensions of “threshold adjustment” and “region selection” windows in pixels. DYNAMIC_WINDOW must be set to False to set these values manually.\n\
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
# The filename to be saved in the directory containing the images used for density measurement. This file will contain the measurements for each of those image files.\n\
\n\
LIFETIME_OUTPUT_FILENAME = "lifetimes.txt"\n\
# The filename to be saved in the directory containing the images used for lifetime measurement.\n\
\n\
FIGURE_DIRECTORY_NAME = "figures/"\n\
# The directory name where figures are to be saved (only if SAVE_FIGURES = True). The default is "figures/", but this can be changed if the user typically keeps a similarly named folder in their file structure for something else.\
')
	
	quit()
