import dotscanner.strings as strings
import settings.config as cfg
import os

def fixDirectory(string):
	return string if string.endswith("/") else string + "/"

def getDirectoryAndFilenames(userSettings):
	filepath = userSettings.filepath
	startImage = userSettings.startImage
	
	if os.path.isfile(filepath):
		directory = fixDirectory(os.path.dirname(filepath))
		filename = os.path.basename(filepath)
		return directory, [filename]
	
	elif os.path.isdir(filepath):
		directory = fixDirectory(filepath)
	
	else:
		raise Exception(strings.filepathException)
	
	filenames = getSortedFilenames(directory, startImage, userSettings.program)
	
	if not len(filenames):
		raise Exception(strings.noFilesException)
	
	return directory, filenames

def getFilenamesWithExtension(directory, fileExtension):
	filenames = []
	for filename in os.listdir(directory):
		if filename.lower().endswith(fileExtension.lower()):
			filenames.append(filename)
	return filenames

def getLeftEdgeOfTrailingNumber(string, index):
	if index == 0:
		return 0
	
	while index >= 0:
		if string[index].isdigit():
			index -= 1
		else:
			return index + 1
	return index + 1

def getMostCommonFileExtension(directory):
	filenames = os.listdir(directory)
	if not len(filenames):
		raise Exception(strings.noFilesException)
	
	extensionFrequencies = {} # Maps the extension string to the number of times it appears
	for filename in filenames:
		if len(filename.split(".")) > 1:
			extension = filename.split(".")[-1]
			if extension not in extensionFrequencies:
				extensionFrequencies[extension] = 0
			extensionFrequencies[extension] += 1
	
	mostCommonExtension = None
	highestFrequency = 0
	for extension, frequency in extensionFrequencies.items():
		if frequency > highestFrequency:
			highestFrequency = frequency
			mostCommonExtension = extension
	
	if mostCommonExtension is None:
		raise Exception(strings.noFilesException)
	
	return "." + mostCommonExtension

def getRightEdgeOfTrailingNumber(string):
	periodReached = False
	for index, char in enumerate(reversed(string)):
		if char == ".":
			periodReached = True
		
		if not periodReached:
			continue
		
		if char.isdigit():
			return len(string) - index - 1
	
	raise Exception(strings.fileNumberingException)

def getSortedFilenames(directory, startImage, programSelected):
	if hasNoValidFiles(directory):
		return []
	
	fileExtension = getMostCommonFileExtension(directory)
	filenames = getFilenamesWithExtension(directory, fileExtension)
	
	allFilesNumbered = allFilesAreNumbered(filenames)
	if programSelected == "lifetime" and not allFilesNumbered:
		raise Exception(strings.fileNumberingException)
	
	if allFilesNumbered:
		filenames.sort(key=lambda filename: getTrailingNumber(filename))
	else:
		filenames.sort()
	
	if startImage != "":
		filenames = removeImagesBeforeStartingImage(filenames, startImage)
	
	return filenames

def hasNoValidFiles(directory):
	for file in os.listdir(directory):
		if "." in file:
			return False
	return True

def allFilesAreNumbered(filenames):
	for filename in filenames:
		digitFound = False
		
		for char in reversed(filename):
			if char.isdigit():
				digitFound = True
				break
				
		if not digitFound:
			return False
	
	return True

def getTrailingNumber(string):
	rightIndex = getRightEdgeOfTrailingNumber(string)
	leftIndex = getLeftEdgeOfTrailingNumber(string, rightIndex)
	return int(string[leftIndex:rightIndex + 1])

def removeImagesBeforeStartingImage(filenames, startImage):
	startImageNumber = getTrailingNumber(startImage)
	filenamesFromStartingImage = []
	for filename in filenames:
		if getTrailingNumber(filename) >= startImageNumber:
			filenamesFromStartingImage.append(filename)
	return filenamesFromStartingImage

def getTargetPath(directory, program, fileExtension):
	figureDirectoryName = cfg.FIGURE_DIRECTORY_NAME
	if not figureDirectoryName.endswith("/"):
		figureDirectoryName += "/"
	
	figurePathWithoutExtension = f"{directory}{figureDirectoryName}"
	
	if not os.path.exists(figurePathWithoutExtension):
	    os.mkdir(figurePathWithoutExtension)
	
	figurePath = f"{directory}{figureDirectoryName}{fileExtension}/"
	
	if not os.path.exists(figurePath):
	    os.mkdir(figurePath)
	
	targetPath = figurePath + f"{program}/"
	if not os.path.exists(targetPath):
	    os.mkdir(targetPath)
	
	return targetPath
