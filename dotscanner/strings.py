import dotscanner.config as cfg

if cfg.SCALE is None:
	UNITS = "pix"
else:
	UNITS = "um"

densityOutputFileHeader = f"# filename | density (per sq {UNITS}) | error | \
lowerDotThreshScale | upperDotThreshScale | lowerBlobThreshScale | blobSize | dotSize\n"

fileNumberingException = "Filenames must contain sequentially-ordered numbers to calculate \
lifetimes"

filepathException = "Filepath must point to a file or directory."

invalidPolygonWarning = "No valid, enclosed polygon drawn. No measurements made."

lifetimeOutputFileHeader = "# x | y | lifetime | starting image\n"

lowerBlobThreshScaleWarning = "WARNING: lower blob threshold scale set below 1.0, which means \
blobs can be dimmer than the brightest dots, which shouldn't happen. Setting to 1.0."

lowerDotThreshScaleWarning = "WARNING: lower dot threshold scale set below zero. \
Setting to zero."

noFilesException = "No files selected. Check the values of 'FILEPATH' and 'START_IMAGE' in the \
configurations file."

programNameException = "Invalid program name selected in configurations file."

tooFewFramesException = "There are not enough images to get meaningful lifetimes."

unitsInconsistentException = f"Inconsistent units with other measurements already recorded in \
{cfg.DENSITY_OUTPUT_FILENAME}. To record measurements in units of per sq pix, set SCALE to None \
in configurations file. Otherwise, set the scale to the scale that was selected for the previous \
measurements."

upperDotThreshScaleWarning = "WARNING: upper dot threshold scale set below lower dot threshold \
scale. Setting to the value of lower dot threshold scale."

def densityOutput(filename, density, error, thresholds, dotSize, blobSize):
	return f"{filename} {density} {error} {thresholds[0]} {thresholds[1]} {thresholds[2]} \
{blobSize} {dotSize}\n"

def editThresholds(thresholds):
	return f"\nGive three threshold scales to set their new values (RETURN to cancel). \
\nThe current threshold scale values are: \
\nlowerDotThreshScale  upperDotThreshScale  lowerBlobThreshScale\n     \
{thresholds[0]}                   {thresholds[1]}                   {thresholds[2]}\n"
