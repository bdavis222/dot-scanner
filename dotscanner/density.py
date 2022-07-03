import dotscanner.config as cfg
import dotscanner.dataprocessing as dp
import dotscanner.files as files
import dotscanner.strings as strings
import matplotlib.pyplot as pl
import numpy as np
import os

if cfg.SCALE is None:
	PIXELS_TO_MICRONS = 1
	UNITS = "pix"
else:
	PIXELS_TO_MICRONS = 1e6 / (cfg.SCALE**2)
	UNITS = "um"

def checkUnitsConsistent(directory):
	if os.path.exists(directory + cfg.DENSITY_OUTPUT_FILENAME):
		with open(directory + cfg.DENSITY_OUTPUT_FILENAME, "r") as file:
			firstLine = file.readline().rstrip()
			if firstLine.split()[6][:-1] != UNITS:
				raise Exception(strings.unitsInconsistentException)

def getAlreadyMeasured(directory):
	alreadyMeasured = set()
	if os.path.exists(directory + cfg.DENSITY_OUTPUT_FILENAME):
		with open(directory + cfg.DENSITY_OUTPUT_FILENAME, "r") as file:
			for line in file:
				filename = line.split()[0]
				alreadyMeasured.add(filename)
	return alreadyMeasured

def getCoordTotals(coordsInPolygon, dotCoords, blobCoords, blobSize):
	dotTotal, blobTotal = 0, 0
	for coordPair in coordsInPolygon:
		y, x = coordPair
		if dp.coordExistsWithinRadius(y, x, blobCoords, blobSize):
			blobTotal += 1
		elif dp.coordExists(y, x, dotCoords):
			dotTotal += 1
	return dotTotal, blobTotal

def getDensityAndError(microscopeImage, dotCoords, blobCoords, blobSize):
	points = []
	data = microscopeImage.data
	for y in range(len(data)):
		for x in range(len(data[0])):
			points.append((y, x))
	
	coordsInPolygon = dp.getCoordsInPolygon(data, points, microscopeImage.polygon)
	dotTotal, blobTotal = getCoordTotals(coordsInPolygon, dotCoords, blobCoords, blobSize)

	surveyedArea = len(coordsInPolygon) - blobTotal
	density = dotTotal / surveyedArea * PIXELS_TO_MICRONS
	error = np.sqrt(dotTotal) / surveyedArea * PIXELS_TO_MICRONS
	
	return density, error

def measureDensity(directory, filename, microscopeImage, userSettings):
	saveFigures = userSettings.saveFigures
	blobSize = userSettings.blobSize
	dotSize = userSettings.dotSize
	
	if not len(microscopeImage.polygon):
		return
	
	dotCoords, blobCoords = dp.getCoordMapsWithinPolygonFromImage(microscopeImage, userSettings)
	dp.cleanDotCoords(microscopeImage.data, dotCoords, blobCoords, blobSize, dotSize)
	
	density, error = getDensityAndError(microscopeImage, dotCoords, blobCoords, blobSize)
	
	saveDensityDataFiles(directory, filename, density, error, microscopeImage, userSettings, 
							dotCoords, blobCoords)

def saveDensityDataFiles(directory, filename, density, error, microscopeImage, userSettings, 
							dotCoords, blobCoords, skipped=False):
	saveFigures = userSettings.saveFigures
	blobSize = userSettings.blobSize
	dotSize = userSettings.dotSize
	
	targetPath = directory + cfg.DENSITY_OUTPUT_FILENAME
	if not os.path.exists(targetPath):
		with open(targetPath, "a") as file:
			file.write(strings.densityOutputFileHeader)
			
	if skipped:
		output = f"{filename} skipped - - - - - - - -\n"
		
	else:
		density = np.round(density, 7)
		error = np.round(error, 7)
		output = strings.densityOutput(filename, density, error, microscopeImage.thresholds, 
										dotSize, blobSize, microscopeImage.polygon)
	
	with open(targetPath, "a") as file:
		file.write(output)
	
	if not skipped and saveFigures:
		saveDensityFigure(directory, filename, microscopeImage, userSettings, dotCoords, blobCoords)

def saveDensityFigure(directory, filename, microscopeImage, userSettings, dotCoords, blobCoords):
	dotSize = userSettings.dotSize
	program = userSettings.program
	
	data = microscopeImage.data
	# dotCoords = microscopeImage.dotCoords
	polygon = microscopeImage.polygon
	
	figure, axes = pl.subplots()
	axes.imshow(data, origin="lower", cmap="gray", vmin=userSettings.lowerContrast, 
					vmax=userSettings.upperContrast * np.std(data))
	dotScatter = axes.scatter([None], [None], s=5 * dotSize, facecolors="none", 
								edgecolors=cfg.DOT_COLOR, linewidths=0.25)
	dp.setScatterOffset(dotCoords, dotScatter)
	
	if cfg.PLOT_BLOBS:
		blobSize = userSettings.blobSize
		# blobCoords = microscopeImage.blobCoords
		blobScatter = axes.scatter([None], [None], s=0.1 * blobSize, facecolors="none", 
									edgecolors=cfg.BLOB_COLOR, linewidths=0.5)
		dp.setScatterOffset(blobCoords, blobScatter)
	
	if cfg.PLOT_POLYGON:
		polygonY, polygonX = dp.getYAndXFromCoordList(polygon)
		underLine, = axes.plot(polygonX, polygonY, linestyle="-", color="k", linewidth=0.75)
		line, = axes.plot(polygonX, polygonY, linestyle="-", color=cfg.POLYGON_COLOR, 
							linewidth=cfg.POLYGON_THICKNESS)
	
	targetPath = files.getTargetPath(directory, program)
	
	truncatedFilename = ".".join(filename.split(".")[:-1])
	figure.savefig(f"{targetPath}{truncatedFilename}.pdf", 
		bbox_inches="tight", pad_inches=0)
	figure.clf()
	pl.close(figure)

def skipFile(directory, filename, userSettings):
	saveDensityDataFiles(directory, filename, None, None, None, userSettings, skipped=True)
	print("File skipped")
