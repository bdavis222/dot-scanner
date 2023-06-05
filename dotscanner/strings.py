import settings.config as cfg

class ProgramType:
	DENSITY = "Density"
	LIFETIME = "Lifetime"

configurationsWindowTitle = "Dot Scanner - Configurations"

defaultConfigurationsEditorWindowTitle = "Dot Scanner - Default Configurations"

def outputFileTopHeader(programType):
	return f"\
# Dot Scanner (https://github.com/bdavis222/dotscanner)\n\
# Generated output file for {programType.lower()} measurement\n#"

densityOutputFileHeader = f"{outputFileTopHeader(ProgramType.DENSITY)}\n\
# If this file is selected for re-analysis, the following settings will be read in and used unless \
changed in the threshold adjustment window. The re-analyzed data will then be given in a new \
output file in this same directory.\n\
#\n\
# lowerDotThreshScale | upperDotThreshScale | lowerBlobThreshScale | blob size | dot size | \
upper contrast | polygon vertices\n\
#\n\
# Any values changed in the threshold adjustment window during re-analysis will be changed for \
all files listed in the data output below. Other settings can be adjusted in the config file \
using the \"Edit defaults\" button in the main configuration window.\n\
#\n\
# The data columns are organized as follows:\n\
# filename | number of dots | number of pixels surveyed | \
density (per sq {'pix' if cfg.SCALE is None else 'um'}) | error | lowerDotThreshScale | \
upperDotThreshScale | lowerBlobThreshScale | blobSize | dotSize | lowerContrast | upperContrast | \
polygon vertices (x, y)\n#\n"

fileNumberingException = "Filenames must contain sequentially-ordered numbers with no gaps and \
have valid file extensions to calculate lifetimes."

fileNumberingWarning = "WARNING: Filenames must contain sequentially-ordered numbers to calculate \
lifetimes."

filepathException = "Filepath must point to a file or directory."

invalidPolygonWarning = "\nNo valid, enclosed polygon drawn. No measurements made."

invalidDotAndBlobSizeEdit = "\nInvalid input. Previous dot and blob size values will be retained."

invalidThresholdEdit = "\nInvalid input. Previous threshold values will be retained."

lifetimeSingleFileException = "Lifetimes must be calculated using a directory of images, \
not a single image."

lifetimeSingleFileWarning = "WARNING: Lifetimes must be calculated using a directory of images, \
not a single image."

lowerBlobThreshScaleWarning = "\nWARNING: Lower blob threshold scale set below 1.0, which means \
blobs can be dimmer than the brightest dots, which shouldn't happen. Setting to 1.0."

maxContrastWarning = "\nWARNING: Max contrast reached. Previous contrast values will be retained."

noFilesException = "No valid files selected. Does the folder you've selected contain files with \
valid file extensions (e.g., .tiff)? Subfolders within the selected folder will not be scanned for \
files. Check the values of 'FILEPATH' and 'START_IMAGE' in the configurations file."

programNameException = "Invalid program name selected in configurations file."

regionSelectorWindowTitle = "Dot Scanner - Region Selection (click the plot to add polygon \
vertices)"

startImageDirectoryWarning = "WARNING: Start image must be in the same directory as the other \
lifetime files."

thresholdAdjusterWindowTitle = "Dot Scanner - Threshold Adjustment"

tooFewFramesException = "There are not enough images to get meaningful lifetimes."

upperDotThreshScaleWarning = "\nWARNING: Upper dot threshold scale set below lower dot threshold \
scale. Previous threshold values will be retained."

windowSizeWarning = "\nWARNING: The current window height is smaller than 550 pixels, potentially \
resulting in some buttons not being visible. However, the Return key will still allow confirmation \
in each window, and the Escape key will allow for skipping files, when the option is available."

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
	
	return f"{outputFileTopHeader(ProgramType.LIFETIME)}\n\
# If this file is selected for re-analysis, the following settings will be read in and used unless \
changed in the threshold adjustment window. The re-analyzed data will then be given in a new \
output file in this same directory.\n\
#\n\
# Polygon vertices (x, y): {verticesString}\n\
# Threshold scales: {thresholdsString}\n\
# Contrast settings: {userSettings.lowerContrast}, {userSettings.upperContrast}\n\
# Dot size: {userSettings.dotSize} | Blob size: {userSettings.blobSize}\n\
#\n\
# The following settings were used in this analysis, but will not be read in during re-analysis \
(these and other settings can be adjusted in the config file using the \"Edit defaults\" button \
in the main configuration window):\n\
#\n\
# Remove edge frames: \
{userSettings.removeEdgeFrames} | Save figures: {userSettings.saveFigures} | Skips allowed: \
{userSettings.skipsAllowed}{getLifetimeStartImageHeaderText(userSettings.startImage)}\n#\n\
# The data columns are organized as follows:\n\
# x | y | lifetime | starting image | displacement squared (sq px)\n#\n"

def getLifetimeStartImageHeaderText(startImage):
	return f" | Start image: {startImage.split('/')[-1]}" if startImage != "" else ""
