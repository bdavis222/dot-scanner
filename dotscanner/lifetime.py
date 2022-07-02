import dotscanner.config as cfg
import dotscanner.files as files
import dotscanner.dataprocessing as dp
import dotscanner.strings as strings
import dotscanner.ui as ui
from dotscanner.ui import MicroscopeImage
import matplotlib
import matplotlib.pyplot as pl
import numpy as np
import os

def addToPlotCoords(coordsToPlot, y, x, imageNumber, lifetime):
	for frame in range(imageNumber, imageNumber + lifetime):
		if frame not in coordsToPlot:
			coordsToPlot[frame] = set()
		if (x, y) not in coordsToPlot[frame]:
			coordsToPlot[frame].add((x, y))

def checkEnoughFramesForLifetimes(filenames, userSettings):
	if len(filenames) <= 2 * (userSettings.skipsAllowed + 1):
		raise Exception(strings.tooFewFramesException)

def coordExistsInPrevFrame(y, x, imageNumber, edgeFrameNumbers, imageNumberToCoordMap, dotSize, 
							skipsAllowed):
	firstFrameNumber = max(0, imageNumber - skipsAllowed - 1)
	frameNumbers = range(firstFrameNumber, imageNumber)
	for frameNumber in frameNumbers:
		frameCoords = imageNumberToCoordMap[frameNumber]
		if dp.coordExistsWithinRadius(y, x, frameCoords, dotSize):
			return True
	return False

def getCoordLifetime(y, x, imageNumber, edgeFrameNumbers, imageNumberToCoordMap, dotSize, 
						skipsAllowed, removeEdgeFrames):
	skipsRemaining = skipsAllowed
	nextImageNumber = imageNumber + 1
	while nextImageNumber in imageNumberToCoordMap:
		nextCoords = imageNumberToCoordMap[nextImageNumber]
		
		if dp.coordExistsWithinRadius(y, x, nextCoords, dotSize):
			if removeEdgeFrames and nextImageNumber in edgeFrameNumbers:
				return None
			
			if skipsRemaining < skipsAllowed:
				skipsRemaining = skipsAllowed
				
		else:
			if skipsRemaining == 0:
				break
			skipsRemaining -= 1
		nextImageNumber += 1
			
	return nextImageNumber - imageNumber - (skipsAllowed - skipsRemaining)

def getCoordsWithinPolygon(data, sums, lowerDotThresh, upperDotThresh, lowerBlobThresh, dotSize, polygonCoordMap, xMin, xMax, yMin, yMax):
	dotCoords = {}
	blobCoords = {}
	# Hashmaps mapping each y coordinate to a set of corresponding x coordinates
	# e.g., the coordinates (y1, x1) and (y1, x2) would be the following key-value pair:
	# {y1 : {x1, x2}}
	
	for y in range(yMin, yMax + 1):
		if y in polygonCoordMap:
			for x in range(xMin, xMax + 1):
				if x in polygonCoordMap[y]:
					if sums[y, x] > lowerDotThresh:
						if sums[y, x] < upperDotThresh:
							dp.addCoordinate(y, x, dotCoords)
						else:
							if dp.squareSum(data, y, x, dotSize + 1) > lowerBlobThresh:
								dp.addCoordinate(y, x, blobCoords)
							else:
								dp.addCoordinate(y, x, dotCoords)
	return dotCoords, blobCoords

def getEdgeFrameNumbers(imageNumberToCoordMap, skipsAllowed):
	firstFrame = 0
	lastFrameOfFrontEdge = skipsAllowed + 1
	firstFrameOfBackEdge = list(imageNumberToCoordMap.keys())[-1] - skipsAllowed
	lastFrame = list(imageNumberToCoordMap.keys())[-1] + 1
	
	firstFrames = range(firstFrame, lastFrameOfFrontEdge)
	lastFrames = range(firstFrameOfBackEdge, lastFrame)
	return set(list(firstFrames) + list(lastFrames))

def getInPolygonCoordMap(microscopeImage):
	data = microscopeImage.data
	points = []
	for y in range(len(data)):
		for x in range(len(data[0])):
			points.append((y, x))

	path = matplotlib.path.Path(microscopeImage.polygon)
	flattenedMask = path.contains_points(points)
	mask = flattenedMask.reshape(len(data), len(data[0]))
	coordsInPolygon = np.argwhere(mask)
	
	polygonCoordMap = {}
	for coordPair in coordsInPolygon:
		y, x = coordPair
		dp.addCoordinate(y, x, polygonCoordMap)
	
	return polygonCoordMap

def getPolygonLimits(polygon):
	polygonXMin, polygonXMax = float("inf"), float("-inf")
	polygonYMin, polygonYMax = float("inf"), float("-inf")
	
	for coordPair in polygon:
		y, x = coordPair
		polygonYMin = min(y, polygonYMin)
		polygonYMax = max(y, polygonYMax)
		polygonXMin = min(x, polygonXMin)
		polygonXMax = max(x, polygonXMax)
	
	polygonYMin = int(round(polygonYMin, 0))
	polygonYMax = int(round(polygonYMax, 0))
	polygonXMin = int(round(polygonXMin, 0))
	polygonXMax = int(round(polygonXMax, 0))
	
	return polygonXMin, polygonXMax, polygonYMin, polygonYMax

def getThresholds(microscopeImage):
	sums = microscopeImage.sums
	lowerDotThreshScale, upperDotThreshScale, lowerBlobThreshScale = microscopeImage.thresholds
	lowerDotThresh = lowerDotThreshScale * np.std(sums)
	upperDotThresh = upperDotThreshScale * np.std(sums)
	lowerBlobThresh = lowerBlobThreshScale * upperDotThresh
	return lowerDotThresh, upperDotThresh, lowerBlobThresh

def measureLifetime(directory, filenames, middleMicroscopeImage, userSettings):
	blobSize = userSettings.blobSize
	dotSize = userSettings.dotSize
	skipsAllowed = userSettings.skipsAllowed
	removeEdgeFrames = userSettings.removeEdgeFrames
	
	lowerDotThresh, upperDotThresh, lowerBlobThresh = getThresholds(middleMicroscopeImage)
	middleImagePolygonCoordMap = getInPolygonCoordMap(middleMicroscopeImage)
	xMin, xMax, yMin, yMax = getPolygonLimits(middleMicroscopeImage.polygon)
	
	imageNumberToCoordMap = {}
	imageNumberToFilenameMap = {}
	
	numberOfFiles = len(filenames)
	print("Getting coordinates of all dots...")
	ui.printProgressBar(0, numberOfFiles)
	for index, filename in enumerate(filenames):
		microscopeImage = MicroscopeImage(directory, filename, userSettings)
		
		dotCoords, blobCoords = getCoordsWithinPolygon(microscopeImage.data, microscopeImage.sums, 
								lowerDotThresh, upperDotThresh, lowerBlobThresh, dotSize, 
								middleImagePolygonCoordMap, xMin, xMax, yMin, yMax)
		dp.cleanDotCoords(microscopeImage.data, dotCoords, blobCoords, blobSize, dotSize)
		
		imageNumberToCoordMap[index] = dotCoords
		imageNumberToFilenameMap[index] = filename
		ui.printProgressBar(index + 1, numberOfFiles)
	
	lifetimes, resultCoords, startImages = [], [], []
	edgeFrameNumbers = getEdgeFrameNumbers(imageNumberToCoordMap, skipsAllowed)
	coordsToPlot = {} # Maps image numbers to coordinate maps for plotting
	
	for imageNumber, coordMap in imageNumberToCoordMap.items():
		if removeEdgeFrames and imageNumber in edgeFrameNumbers:
			continue
		
		for y, xSet in coordMap.items():
			for x in xSet:
				updateLifetimeResults(imageNumber, y, x, lifetimes, resultCoords, startImages, 
							imageNumberToCoordMap, edgeFrameNumbers, dotSize, skipsAllowed, 
							removeEdgeFrames, userSettings.saveFigures, coordsToPlot)
	
	saveLifetimeDataFiles(directory, lifetimes, resultCoords, startImages, imageNumberToCoordMap, 
							imageNumberToFilenameMap, middleMicroscopeImage, userSettings, 
							coordsToPlot)

def saveLifetimeDataFiles(directory, lifetimes, resultCoords, startImages, 
							imageNumberToCoordMap, imageNumberToFilenameMap, microscopeImage, 
							userSettings, coordsToPlot):
	dotSize = userSettings.dotSize
	polygon = microscopeImage.polygon
	thresholds = microscopeImage.thresholds
	
	targetPath = directory + cfg.LIFETIME_OUTPUT_FILENAME
	if os.path.exists(targetPath):
		os.remove(targetPath)
	
	with open(targetPath, "a") as file:
		file.write(strings.lifetimeOutputFileHeader(polygon, thresholds))
		for lifetime, resultCoord, startImage in zip(lifetimes, resultCoords, startImages):
			y, x = resultCoord
			filename = imageNumberToFilenameMap[startImage]
			output = f"{x} {y} {lifetime} {filename}\n"
			file.write(output)
	
	print(f"{cfg.LIFETIME_OUTPUT_FILENAME} saved.")
	
	if userSettings.saveFigures:
		saveLifetimeFigures(directory, coordsToPlot, imageNumberToFilenameMap, userSettings)

def saveLifetimeFigures(directory, coordsToPlot, imageNumberToFilenameMap, userSettings):
	print("Saving figures...")
	coordsToPlotSize = len(list(coordsToPlot.keys()))
	count = 0
	ui.printProgressBar(count, coordsToPlotSize)
	for imageNumber, dotCoordSet in coordsToPlot.items():
		filename = imageNumberToFilenameMap[imageNumber]
		microscopeImage = MicroscopeImage(directory, filename, userSettings)
		data = microscopeImage.data
	
		figure, axes = pl.subplots()
		axes.imshow(data, origin="lower", cmap="gray", vmin=0, vmax=2 * np.std(data))
		dotScatter = axes.scatter([None], [None], s=5 * userSettings.dotSize, facecolors="none", 
									edgecolors=cfg.DOT_COLOR, linewidths=1)
		
		dotScatter.set_offsets(list(dotCoordSet))
		
		targetPath = files.getTargetPath(directory, userSettings.program)
		truncatedFilename = ".".join(filename.split(".")[:-1])
		
		figure.savefig(f"{targetPath}{truncatedFilename}.pdf", 
			bbox_inches="tight", pad_inches=0)
		figure.clf()
		pl.close(figure)
		
		count += 1
		ui.printProgressBar(count, coordsToPlotSize)

def updateLifetimeResults(imageNumber, y, x, lifetimes, resultCoords, startImages, 
							imageNumberToCoordMap, edgeFrameNumbers, dotSize, skipsAllowed, 
							removeEdgeFrames, saveFigures, coordsToPlot):
	if not removeEdgeFrames or imageNumber > skipsAllowed:
		if not coordExistsInPrevFrame(y, x, imageNumber, edgeFrameNumbers, imageNumberToCoordMap, 
										dotSize, skipsAllowed):
			
			coordLifetime = getCoordLifetime(y, x, imageNumber, edgeFrameNumbers, 
												imageNumberToCoordMap, dotSize, skipsAllowed, 
												removeEdgeFrames)
			
			if coordLifetime is not None:
				lifetimes.append(coordLifetime)
				resultCoords.append((y, x))
				startImages.append(imageNumber)
				
				if saveFigures:
					addToPlotCoords(coordsToPlot, y, x, imageNumber, coordLifetime)
