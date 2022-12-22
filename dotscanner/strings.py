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

maxContrastWarning = "\nWARNING: Max contrast reached. Previous contrast values will be retained."

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
	
	return f"# Polygon vertices (x, y): {verticesString}\n\
# Threshold scales: {thresholdsString}\n\
# Dot size: {userSettings.dotSize} | Blob size: {userSettings.blobSize} | Remove edge frames: \
{userSettings.removeEdgeFrames} | Skips allowed: {userSettings.skipsAllowed}\n\
#\n# x | y | lifetime | starting image\n"
