from dotscanner.programtype import ProgramType
import settings.config as cfg


def outputFileTopHeader(programType):
    return f"\
# Dot Scanner (https://github.com/bdavis222/dotscanner)\n\
# Generated output file for {programType.lower()} measurement\n#"


CONFIGURATIONS_WINDOW_TITLE = "Dot Scanner - Configurations"
DEFAULT_CONFIGURATIONS_EDITOR_WINDOW_TITLE = "Dot Scanner - Default Configurations"
REGION_SELECTOR_WINDOW_TITLE = "Dot Scanner - Region Selection (click the plot to add polygon vertices)"
THRESHOLD_ADJUSTER_WINDOW_TITLE = "Dot Scanner - Threshold Adjustment"

DENSITY_OUTPUT_FILE_HEADER = '''{header}
# If this file is selected for re-analysis, the following settings will be read in and used unless changed in the threshold adjustment window. The re-analyzed data will then be given in a new output file in this same directory.
#
# lowerDotThreshScale | upperDotThreshScale | lowerBlobThreshScale | blob size | dot size | upper contrast | polygon vertices
#
# Any values changed in the threshold adjustment window during re-analysis will be changed for all files listed in the data output below. Other settings can be adjusted in the config file using the "Edit defaults" button in the main configuration window.
#
# The data columns are organized as follows:
# filename | number of dots | number of pixels surveyed | density (per sq {unit}) | error | lowerDotThreshScale | upperDotThreshScale | lowerBlobThreshScale | blobSize | dotSize | lowerContrast | upperContrast | polygon vertices (x, y)
#
'''.format(header=outputFileTopHeader(ProgramType.DENSITY), unit="pix" if cfg.SCALE is None else "um")

FILE_NUMBERING_EXCEPTION = "Filenames must contain sequentially-ordered numbers with no gaps and have valid file extensions to calculate lifetimes."

FILE_NUMBERING_WARNING = "WARNING: Filenames must contain sequentially-ordered numbers to calculate lifetimes."

FILEPATH_EXCEPTION = "Filepath must point to a file or directory."

INVALID_IMAGE_EXTENSION = '''
"{extension}" is not a valid image extension. 
Make sure the most common file type in the folder you've selected has a valid extension.'''

INVALID_POLYGON_WARNING = "\nNo valid, enclosed polygon drawn. No measurements made."

INVALID_DOT_AND_BLOB_SIZE_EDIT = "\nInvalid input. Previous dot and blob size values will be retained."

INVALID_THRESHOLD_EDIT = "\nInvalid input. Previous threshold values will be retained."

LIFETIME_SINGLE_FILE_WARNING = "WARNING: Lifetimes must be calculated using a directory of images, not a single image."

LOWER_BLOB_THRESH_SCALE_WARNING = "\nWARNING: Lower blob threshold scale set below 1.0, which means blobs can be dimmer than the brightest dots, which shouldn't happen. Setting to 1.0."

MAX_CONTRAST_WARNING = "\nWARNING: Max contrast reached. Previous contrast values will be retained."

NO_FILES_EXCEPTION = "No valid files selected. Does the folder you've selected contain files with valid file extensions (e.g., .tiff)? Subfolders within the selected folder will not be scanned for files. Check the values of 'FILEPATH' and 'START_IMAGE' in the configurations file."

NO_LIFETIMES_FOUND_ERROR = """
No lifetimes measured.
Check that your images are arranged as a time series."""

PROGRAM_NAME_EXCEPTION = "Invalid program name selected in configurations file."

REANALYSIS_NOT_IN_FILE = """Filename not found in reanalysis file:
{filename}
Reanalysis requires identical naming."""

REANALYSIS_NOT_IN_FOLDER = """Filename not found in images folder:
{filename}
Reanalysis requires identical naming."""

START_IMAGE_DIRECTORY_WARNING = "WARNING: Start image must be in the same directory as the other lifetime files."

TOO_FEW_FRAMES_EXCEPTION = "There are not enough images to get meaningful lifetimes."

UPPER_DOT_THRESH_SCALE_WARNING = "\nWARNING: Upper dot threshold scale set below lower dot threshold scale. Previous threshold values will be retained."

WINDOW_SIZE_WARNING = "\nWARNING: Due to the device's screen size or the window height that has been manually selected, the window height will be smaller than 650 pixels for the threshold-adjustment and region-selection windows, potentially resulting in some buttons not being visible. However, the Return key will still allow confirmation in each window, and the Escape key will allow for skipping files, when the option is available."


def alreadyMeasuredNotification(filename):
    return f"\nFile {filename} already measured in {cfg.DENSITY_OUTPUT_FILENAME} file. Skipping."


def densityOutput(filename, dotTotal, surveyedArea, density, error, microscopeImage, userSettings):
    thresholds = microscopeImage.thresholds
    polygon = microscopeImage.polygon
    dotSize = userSettings.dotSize
    blobSize = userSettings.blobSize
    lowerContrast = userSettings.lowerContrast
    upperContrast = userSettings.upperContrast

    verticesStringList = []
    for vertex in polygon[:-1]:
        y, x = vertex
        verticesStringList.append(f"({x}, {y})")
    verticesString = ", ".join(verticesStringList)

    return f"{filename} {dotTotal} {surveyedArea} {density} {error} {thresholds[0]} \
{thresholds[1]} {thresholds[2]} {blobSize} {dotSize} {lowerContrast} {upperContrast} \
{verticesString}\n"


def fileSkippedNotification(filename):
    return f"\nFile {filename} skipped"


def invalidAnalysisFileWarning(filepath):
    filename = filepath.split("/")[-1]
    return f'\nInvalid analysis file selected: "{filename}". A valid file has a .txt extension \
and contains density or lifetime data.'


def invalidFilenameInDensityAnalysisFile(lineArray):
    return f"Filename with valid extension not found in the following line in densities file:\n\
{' '.join(lineArray)}"


LIFETIME_OUTPUT_FILE_HEADER_TEMPLATE = '''{header}
# If this file is selected for re-analysis, the following settings will be read in and used unless changed in the threshold adjustment window. The re-analyzed data will then be given in a new output file in this same directory.
#
# Polygon vertices (x, y): {verticesString}
# Threshold scales: {thresholdsString}
# Contrast settings: {lowerContrast}, {upperContrast}
# Dot size: {dotSize} | Blob size: {blobSize}
#
# The following settings were used in this analysis, but will not be read in during re-analysis (these and other settings can be adjusted in the config file using the "Edit defaults" button in the main configuration window):
#
# Remove edge frames: {removeEdgeFrames} | Save figures: {saveFigures} | Skips allowed: {skipsAllowed}{startImageHeaderText}
#
# The data columns are organized as follows:
# x | y | lifetime | starting image | displacement squared (sq px) | potentially unreliable?
#
'''


def lifetimeOutputFileHeader(microscopeImage, userSettings):
    verticesStringList = []
    for vertex in microscopeImage.polygon[:-1]:
        y, x = vertex
        verticesStringList.append(f"({x}, {y})")
    verticesString = ", ".join(verticesStringList)

    thresholdsStringList = []
    for threshold in microscopeImage.thresholds:
        thresholdsStringList.append(str(threshold))
    thresholdsString = ", ".join(thresholdsStringList)

    return LIFETIME_OUTPUT_FILE_HEADER_TEMPLATE.format(
        header=outputFileTopHeader(ProgramType.LIFETIME),
        verticesString=verticesString,
        thresholdsString=thresholdsString,
        lowerContrast=userSettings.lowerContrast,
        upperContrast=userSettings.upperContrast,
        dotSize=userSettings.dotSize,
        blobSize=userSettings.blobSize,
        removeEdgeFrames=userSettings.removeEdgeFrames,
        saveFigures=userSettings.saveFigures,
        skipsAllowed=userSettings.skipsAllowed,
        startImageHeaderText=getLifetimeStartImageHeaderText(
            userSettings.startImage)
    )


def getLifetimeStartImageHeaderText(startImage):
    return f" | Start image: {startImage.split('/')[-1]}" if startImage != "" else ""


DEFAULT_CONFIG_FILE_CONTENTS = '''# Default selections run by the software (can be changed by the user):

FILEPATH = ""
# Path to the file or directory of files that should be used. The default value is an empty string: ""

PROGRAM = "density"
# Whether a "density" program or "lifetime" program should be run

SCALE = None
# Linear scale of the image (width of a single pixel in nanometers per pixel). Default value is None. If None is entered, the final density output will be in dots per pixel^2. If a numerical value is entered, the final density output will be in dots per micron^2.

############################################
############ THRESHOLD SETTINGS ############
############################################

LOWER_DOT_THRESH_SCALE = 1.5
# Scaling for the lower threshold defining the brightness of the dots. The default is 1.5,which corresponds to 1.5 standard deviations above the mean. Lower this value to increase the number of faint dots detected, or raise it to reduce the number.

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

NOISE_STATISTIC = 2.5
# Used to remove noisy data from detected lifetime dots. The default value is 2.5. Increase to include less noise (and remove shorter lifetimes), and decrease for the opposite.

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

WINDOW_HEIGHT = 650
WINDOW_WIDTH = 750
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

FIGURE_FILETYPES = ["pdf"]
# The filetypes for the output figures. Multiple types can also be selected, e.g., ["png", "pdf", "tif"]. Only use the supported filetypes ("eps", "tif", "ps", "tiff", "rgba", "svg", "png", "jpg", "raw", "pdf", "svgz", "pgf", and "jpeg").

FIGURE_RESOLUTION = 300
# Resolution (DPI) of the output figures. This is for images only; PDF outputs are unaffected by this value.
'''
