import dotscanner.files as files
import dotscanner.dataprocessing as dp
import dotscanner.strings as strings
import dotscanner.ui.window as ui
from dotscanner.ui.MicroscopeImage import MicroscopeImage
import settings.config as cfg
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
	
	if nextImageNumber not in imageNumberToCoordMap and skipsAllowed > 0:
		return None
	
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

def getEdgeFrameNumbers(imageNumberToCoordMap, skipsAllowed):
	firstFrame = 0
	lastFrameOfFrontEdge = skipsAllowed + 1
	firstFrameOfBackEdge = list(imageNumberToCoordMap.keys())[-1] - skipsAllowed
	lastFrame = list(imageNumberToCoordMap.keys())[-1] + 1
	
	firstFrames = range(firstFrame, lastFrameOfFrontEdge)
	lastFrames = range(firstFrameOfBackEdge, lastFrame)
	return set(list(firstFrames) + list(lastFrames))

def measureLifetime(directory, filenames, middleMicroscopeImage, userSettings):
	if len(middleMicroscopeImage.polygon) < 3:
		return
	
	blobSize = userSettings.blobSize
	dotSize = userSettings.dotSize
	skipsAllowed = userSettings.skipsAllowed
	removeEdgeFrames = userSettings.removeEdgeFrames
	
	lowerDotThresh, upperDotThresh, lowerBlobThresh = dp.getThresholds(middleMicroscopeImage)
	middleImagePolygonCoordMap = dp.getInPolygonCoordMap(middleMicroscopeImage)
	xMin, xMax, yMin, yMax = dp.getPolygonLimits(middleMicroscopeImage.polygon)
	
	imageNumberToCoordMap = {}
	imageNumberToBlobCoordMap = {}
	imageNumberToFilenameMap = {}
	
	numberOfFiles = len(filenames)
	print("Getting coordinates of all dots...")
	ui.printProgressBar(0, numberOfFiles)
	for index, filename in enumerate(filenames):
		microscopeImage = MicroscopeImage(directory, filename, userSettings)
		
		dotCoords, blobCoords = dp.getCoordMapsWithinPolygon(
														microscopeImage.data, microscopeImage.sums, 
														lowerDotThresh, upperDotThresh, 
														lowerBlobThresh, dotSize, 
														middleImagePolygonCoordMap, xMin, xMax, 
														yMin, yMax)
		dp.cleanDotCoords(microscopeImage.data, dotCoords, blobCoords, blobSize, dotSize)
		
		imageNumberToCoordMap[index] = dotCoords
		imageNumberToFilenameMap[index] = filename
		if cfg.PLOT_BLOBS:
			imageNumberToBlobCoordMap[index] = blobCoords
		
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
										imageNumberToCoordMap, edgeFrameNumbers, dotSize, 
										skipsAllowed, removeEdgeFrames, userSettings.saveFigures, 
										coordsToPlot)
	
	saveLifetimeDataFiles(directory, lifetimes, resultCoords, startImages, imageNumberToCoordMap, 
							imageNumberToBlobCoordMap, imageNumberToFilenameMap, 
							middleMicroscopeImage, userSettings, coordsToPlot, 
							middleMicroscopeImage.polygon)

def saveLifetimeDataFiles(directory, lifetimes, resultCoords, startImages, 
							imageNumberToCoordMap, imageNumberToBlobCoordMap, 
							imageNumberToFilenameMap, microscopeImage, userSettings, coordsToPlot, 
							polygon):
	targetPath = directory + cfg.LIFETIME_OUTPUT_FILENAME
	if os.path.exists(targetPath):
		os.remove(targetPath)
	
	with open(targetPath, "a") as file:
		file.write(strings.lifetimeOutputFileHeader(microscopeImage, userSettings))
		for lifetime, resultCoord, startImage in zip(lifetimes, resultCoords, startImages):
			y, x = resultCoord
			filename = imageNumberToFilenameMap[startImage]
			output = f"{x} {y} {lifetime} {filename}\n"
			file.write(output)
	
	print(f"{cfg.LIFETIME_OUTPUT_FILENAME} saved.")
	
	if userSettings.saveFigures:
		saveLifetimeFigures(directory, coordsToPlot, imageNumberToBlobCoordMap, 
							imageNumberToFilenameMap, userSettings, polygon)

def saveLifetimeFigures(directory, coordsToPlot, imageNumberToBlobCoordMap, 
						imageNumberToFilenameMap, userSettings, polygon):
	print("Saving figures...")
	coordsToPlotSize = len(list(coordsToPlot.keys()))
	count = 0
	ui.printProgressBar(count, coordsToPlotSize)
	for imageNumber, dotCoordSet in coordsToPlot.items():
		filename = imageNumberToFilenameMap[imageNumber]
		microscopeImage = MicroscopeImage(directory, filename, userSettings)
		data = microscopeImage.data
	
		figure, axes = pl.subplots()
		axes.imshow(data, origin="lower", cmap="gray", vmin=userSettings.lowerContrast, 
					vmax=userSettings.upperContrast * np.std(data), zorder=0)
		dotScatter = axes.scatter([None], [None], s=5 * userSettings.dotSize, facecolors="none", 
									edgecolors=cfg.DOT_COLOR, linewidths=cfg.DOT_THICKNESS/2, 
									zorder=4)
		dotScatter.set_offsets(list(dotCoordSet))
		
		if cfg.PLOT_BLOBS:
			blobSize = userSettings.blobSize
			blobCoordMap = imageNumberToBlobCoordMap[imageNumber]
			blobScatter = axes.scatter([None], [None], s=0.1 * blobSize, facecolors="none", 
										edgecolors=cfg.BLOB_COLOR, linewidths=cfg.BLOB_THICKNESS/2, 
										zorder=3)
			dp.setScatterOffset(blobCoordMap, blobScatter)
		
		if cfg.PLOT_POLYGON:
			polygonY, polygonX = dp.getYAndXFromCoordList(polygon)
			underLine, = axes.plot(polygonX, polygonY, linestyle="-", color="k", linewidth=0.75, 
									zorder=1)
			line, = axes.plot(polygonX, polygonY, linestyle="-", color=cfg.POLYGON_COLOR, 
								linewidth=cfg.POLYGON_THICKNESS, zorder=2)
		
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
	if removeEdgeFrames and imageNumber <= skipsAllowed:
		return
	
	if coordExistsInPrevFrame(y, x, imageNumber, edgeFrameNumbers, imageNumberToCoordMap, 
								dotSize, skipsAllowed):
		return
		
	coordLifetime = getCoordLifetime(y, x, imageNumber, edgeFrameNumbers, 
										imageNumberToCoordMap, dotSize, skipsAllowed, 
										removeEdgeFrames)
	
	if coordLifetime is None:
		return
	
	lifetimes.append(coordLifetime)
	resultCoords.append((y, x))
	startImages.append(imageNumber)
	
	if saveFigures and coordLifetime >= cfg.LIFETIME_MIN_FOR_PLOT:
		addToPlotCoords(coordsToPlot, y, x, imageNumber, coordLifetime)
