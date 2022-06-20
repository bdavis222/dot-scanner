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

def checkEnoughFramesForLifetimes(filenames, userSettings):
	if len(filenames) <= 2 * (userSettings.skipsAllowed + 1):
		raise Exception(strings.tooFewFramesException)

def getCoordsWithinPolygon(data, sums, thresholds, dotSize, polygonCoordMap):
	dotCoords = {}
	blobCoords = {}
	# Hashmaps mapping each y coordinate to a set of corresponding x coordinates
	# e.g., the coordinates (y1, x1) and (y1, x2) would be the following key-value pair:
	# {y1 : {x1, x2}}
	lowerDotThreshScale, upperDotThreshScale, lowerBlobThreshScale = thresholds
	lowerDotThresh = lowerDotThreshScale * np.std(sums)
	upperDotThresh = upperDotThreshScale * np.std(sums)
	lowerBlobThresh = lowerBlobThreshScale * upperDotThresh
	
	for y in range(len(sums)):
		if y in polygonCoordMap:
			for x in range(len(sums[0])):
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

def measureLifetime(directory, filenames, middleMicroscopeImage, userSettings):
	blobSize = userSettings.blobSize
	dotSize = userSettings.dotSize
	skipsAllowed = userSettings.skipsAllowed
	saveFigures = userSettings.saveFigures
	
	middleImageThresholds = middleMicroscopeImage.thresholds
	middleImagePolygonCoordMap = getInPolygonCoordMap(middleMicroscopeImage)
	
	imageNumberToCoordMap = {}
	imageNumberToFilenameMap = {}
	numberOfFiles = len(filenames)
	
	print("Getting coordinates of all dots...")
	ui.printProgressBar(0, numberOfFiles)
	for index, filename in enumerate(filenames):
		microscopeImage = MicroscopeImage(directory, filename, userSettings)
		
		dotCoords, blobCoords = getCoordsWithinPolygon(microscopeImage.data, microscopeImage.sums, 
														middleImageThresholds, dotSize, 
														middleImagePolygonCoordMap)
		dp.cleanDotCoords(microscopeImage.sums, dotCoords, blobCoords, blobSize, dotSize)
		
		imageNumberToCoordMap[index] = dotCoords
		imageNumberToFilenameMap[index] = filename
		ui.printProgressBar(index + 1, numberOfFiles)
	
	lifetimes, resultCoords, startImages = [], [], []
	coordsInPrevFrames = {}
	
	imageNumberToCoordMapSize = len(list(imageNumberToCoordMap.keys()))
	print("Measuring lifetimes...")
	ui.printProgressBar(0, imageNumberToCoordMapSize)
	for imageNumber, coordMap in imageNumberToCoordMap.items():
		for y, xSet in coordMap.items():
			for x in xSet:
				updateLifetimeResults(imageNumber, y, x, lifetimes, resultCoords, startImages, 
										imageNumberToCoordMap, coordsInPrevFrames, userSettings)
		ui.printProgressBar(imageNumber + 1, imageNumberToCoordMapSize)
	
	if userSettings.removeEdgeFrames:
		print("Removing dots in edge frames...")
		lifetimesCleaned, resultCoordsCleaned, startImagesCleaned = removeDotsInEdgeFrames(
																		imageNumberToCoordMap, 
																		coordsInPrevFrames, 
																		lifetimes, resultCoords, 
																		startImages, skipsAllowed)
		saveLifetimeDataFiles(directory, lifetimesCleaned, resultCoordsCleaned, startImagesCleaned,
								imageNumberToCoordMap, imageNumberToFilenameMap, userSettings)
	else:
		saveLifetimeDataFiles(directory, lifetimes, resultCoords, startImages, 
								imageNumberToCoordMap, imageNumberToFilenameMap, userSettings)

def removeDotsInEdgeFrames(imageNumberToCoordMap, coordsInPrevFrames, lifetimes, resultCoords, 
							startImages, skipsAllowed):
	lifetimesCleaned, resultCoordsCleaned, startImagesCleaned = [], [], []
	edgeFrameNumbers = getEdgeFrameNumbers(imageNumberToCoordMap, skipsAllowed)
	resultCoordsLength = len(resultCoords)
	ui.printProgressBar(0, resultCoordsLength)
	for index, coordPair in enumerate(resultCoords):
		y, x = coordPair
		if not coordExistsInSpecificFrames(y, x, imageNumberToCoordMap, edgeFrameNumbers):
			lifetimesCleaned.append(lifetimes[index])
			resultCoordsCleaned.append(resultCoords[index])
			startImagesCleaned.append(startImages[index])
		ui.printProgressBar(index + 1, resultCoordsLength)
	return lifetimesCleaned, resultCoordsCleaned, startImagesCleaned

def getEdgeFrameNumbers(coordMap, skipsAllowed):
	firstFrame = 0
	lastFrameOfFrontEdge = skipsAllowed + 1
	firstFrameOfBackEdge = list(coordMap.keys())[-1] - skipsAllowed
	lastFrame = list(coordMap.keys())[-1] + 1
	
	firstFrames = range(firstFrame, lastFrameOfFrontEdge)
	lastFrames = range(firstFrameOfBackEdge, lastFrame)
	return list(firstFrames) + list(lastFrames)

def coordExistsInSpecificFrames(y, x, coordMap, listOfFrameNumbers):
	for frameNumber in listOfFrameNumbers:
		frameCoords = coordMap[frameNumber]
		if dp.coordExists(y, x, frameCoords):
			return True
	return False

def updateLifetimeResults(imageNumber, y, x, lifetimes, resultCoords, startImages, 
							imageNumberToCoordMap, coordsInPrevFrames, userSettings):
	skipsAllowed = userSettings.skipsAllowed
	dotSize = userSettings.dotSize
	
	if coordExistsInPrevFrame(y, x, coordsInPrevFrames, dotSize):
		return
	
	coordLifetime = getCoordLifetime(y, x, imageNumber, imageNumberToCoordMap, skipsAllowed)
	
	lifetimes.append(coordLifetime)
	resultCoords.append((y,x))
	startImages.append(imageNumber)

def coordExistsInPrevFrame(y, x, coordsInPrevFrames, dotSize):
	yRange = range(y - dotSize, y + dotSize + 1)
	xRange = range(x - dotSize, x + dotSize + 1)
	for currentY in yRange:
		if currentY in coordsInPrevFrames:
			for currentX in xRange:
				if currentX in coordsInPrevFrames[currentY]:
					return True
	dp.addCoordinate(y, x, coordsInPrevFrames)
	return False

def getCoordLifetime(y, x, imageNumber, imageNumberToCoordMap, skipsAllowed):
	skipsRemaining = skipsAllowed
	nextImageNumber = imageNumber + 1
	while nextImageNumber in imageNumberToCoordMap:
		nextCoords = imageNumberToCoordMap[nextImageNumber]
		
		if dp.coordExists(y, x, nextCoords):
			if skipsRemaining < skipsAllowed:
				skipsRemaining = skipsAllowed
				
		else:
			if skipsRemaining == 0:
				break
			skipsRemaining -= 1
		nextImageNumber += 1
			
	return nextImageNumber - imageNumber - (skipsAllowed - skipsRemaining)

def saveLifetimeDataFiles(directory, lifetimes, resultCoords, startImages, 
							imageNumberToCoordMap, imageNumberToFilenameMap, userSettings):
	dotSize = userSettings.dotSize
	saveFigures = userSettings.saveFigures
	
	targetPath = directory + cfg.LIFETIME_OUTPUT_FILENAME
	if not os.path.exists(targetPath):
		with open(targetPath, "a") as file:
			file.write(strings.lifetimeOutputFileHeader)
	
	else:
		os.remove(targetPath)
	
	with open(targetPath, "a") as file:
		for lifetime, resultCoord, startImage in zip(lifetimes, resultCoords, startImages):
			y, x = resultCoord
			filename = imageNumberToFilenameMap[startImage]
			output = f"{x} {y} {lifetime} {filename}\n"
			file.write(output)
	
	print(f"{cfg.LIFETIME_OUTPUT_FILENAME} saved.")
	
	if saveFigures:
		saveLifetimeFigures(directory, dotSize, imageNumberToCoordMap, imageNumberToFilenameMap, 
							userSettings)

def saveLifetimeFigures(directory, dotSize, imageNumberToCoordMap, imageNumberToFilenameMap, 
						userSettings):
	print("Saving figures...")
	imageNumberToCoordMapSize = len(list(imageNumberToCoordMap.keys()))
	ui.printProgressBar(0, imageNumberToCoordMapSize)
	for imageNumber in imageNumberToCoordMap.keys():
		filename = imageNumberToFilenameMap[imageNumber]
		filepath = directory + filename
		
		microscopeImage = MicroscopeImage(directory, filename, userSettings)
		data = microscopeImage.data
		dotCoords = imageNumberToCoordMap[imageNumber]
	
		figure, axes = pl.subplots()
		axes.imshow(data, origin="lower", cmap="gray", vmin=0, vmax=2 * np.std(data))
		dotScatter = axes.scatter([None], [None], s=5 * dotSize, facecolors="none", 
			edgecolors=cfg.DOT_COLOR, linewidths=1)
		
		dp.setScatterOffset(dotCoords, dotScatter)
		
		targetPath = files.getTargetPath(directory, userSettings.program)
		
		truncatedFilename = ".".join(filename.split(".")[:-1])
		figure.savefig(f"{targetPath}{truncatedFilename}.pdf", 
			bbox_inches="tight", pad_inches=0)
		figure.clf()
		pl.close(figure)
		ui.printProgressBar(imageNumber + 1, imageNumberToCoordMapSize)
	print("All files saved.")