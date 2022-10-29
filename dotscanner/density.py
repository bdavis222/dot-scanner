import dotscanner.dataprocessing as dp
import dotscanner.files as files
import dotscanner.strings as strings
import settings.config as cfg
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
			unitsInFile = firstLine.split("per sq ")[1].split(")")[0]
			if unitsInFile != UNITS:
				raise Exception(strings.unitsInconsistentException)

def getAlreadyMeasured(directory):
	alreadyMeasured = set()
	if os.path.exists(directory + cfg.DENSITY_OUTPUT_FILENAME):
		with open(directory + cfg.DENSITY_OUTPUT_FILENAME, "r") as file:
			for line in file:
				filename = line.split()[0]
				alreadyMeasured.add(filename)
	return alreadyMeasured

def getTotalsAndCoords(coordsInPolygon, dotCoords, blobCoords, blobSize):
	dotTotal, blobTotal = 0, 0
	dotsInPoly, blobsInPoly = [], []
	for coordPair in coordsInPolygon:
		y, x = coordPair
		if dp.coordExistsWithinRadius(y, x, blobCoords, blobSize):
			blobTotal += 1
			if dp.coordExists(y, x, blobCoords):
				blobsInPoly.append((x, y)) # For use with set_offsets(), which expects (x, y)
		elif dp.coordExists(y, x, dotCoords):
			dotTotal += 1
			dotsInPoly.append((x, y)) # For use with set_offsets(), which expects (x, y)
	return dotTotal, blobTotal, dotsInPoly, blobsInPoly

def getDensityErrorAndCoords(microscopeImage, blobSize):
	dotCoords = microscopeImage.dotCoords
	blobCoords = microscopeImage.blobCoords
	data = microscopeImage.data
	
	points = []
	for y in range(len(data)):
		for x in range(len(data[0])):
			points.append((y, x))
	
	coordsInPolygon = dp.getCoordsInPolygon(data, points, microscopeImage.polygon)
	
	dotTotal, blobTotal, dotsInPoly, blobsInPoly = getTotalsAndCoords(coordsInPolygon, dotCoords, 
																		blobCoords, blobSize)
	
	surveyedArea = len(coordsInPolygon) - blobTotal
	density = dotTotal / surveyedArea * PIXELS_TO_MICRONS
	error = np.sqrt(dotTotal) / surveyedArea * PIXELS_TO_MICRONS
	
	return density, error, dotsInPoly, blobsInPoly

def measureDensity(directory, filename, microscopeImage, userSettings):
	if len(microscopeImage.polygon) < 3:
		return
	
	blobSize = userSettings.blobSize
	
	density, error, dotsInPoly, blobsInPoly = getDensityErrorAndCoords(microscopeImage, blobSize)
	
	saveDensityDataFiles(directory, filename, density, error, microscopeImage, userSettings, 
							dotsInPoly, blobsInPoly)

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
	
	if not skipped and saveFigures:
		saveDensityFigure(directory, filename, microscopeImage, userSettings, dotCoords, blobCoords)
	
	with open(targetPath, "a") as file:
		file.write(output)

def saveDensityFigure(directory, filename, microscopeImage, userSettings, dotCoords, blobCoords):
	dotSize = userSettings.dotSize
	program = userSettings.program
	
	data = microscopeImage.data
	polygon = microscopeImage.polygon
	
	figure, axes = pl.subplots()
	axes.imshow(data, origin="lower", cmap="gray", vmin=userSettings.lowerContrast, 
					vmax=userSettings.upperContrast * np.std(data), zorder=0)
	dotScatter = axes.scatter([None], [None], s=5 * dotSize, facecolors="none", 
								edgecolors=cfg.DOT_COLOR, linewidths=cfg.DOT_THICKNESS/2, zorder=4)
	dotScatter.set_offsets(dotCoords)
	
	if cfg.PLOT_BLOBS:
		blobSize = userSettings.blobSize
		blobScatter = axes.scatter([None], [None], s=0.1 * blobSize, facecolors="none", 
									edgecolors=cfg.BLOB_COLOR, linewidths=cfg.BLOB_THICKNESS/2, 
									zorder=3)
		blobScatter.set_offsets(blobCoords)
	
	if cfg.PLOT_POLYGON:
		polygonY, polygonX = dp.getYAndXFromCoordList(polygon)
		underLine, = axes.plot(polygonX, polygonY, linestyle="-", color="k", linewidth=0.75, 
								zorder=1)
		line, = axes.plot(polygonX, polygonY, linestyle="-", color=cfg.POLYGON_COLOR, 
							linewidth=cfg.POLYGON_THICKNESS, zorder=2)
	
	targetPath = files.getTargetPath(directory, program)
	
	truncatedFilename = ".".join(filename.split(".")[:-1])
	figure.savefig(f"{targetPath}{truncatedFilename}.pdf", 
		bbox_inches="tight", pad_inches=0)
	figure.clf()
	pl.close(figure)

def skipFile(directory, filename, userSettings):
	saveDensityDataFiles(directory, filename, None, None, None, userSettings, None, None, 
							skipped=True)
	print(strings.fileSkippedNotification(filename))
