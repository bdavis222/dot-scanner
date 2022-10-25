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
	
	filenames = getSortedFilenames(directory, startImage)
	
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
	while index > 0:
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
	return "." + mostCommonExtension

def getRightEdgeOfTrailingNumber(string):
	for index, char in enumerate(reversed(string)):
		if char.isdigit():
			return len(string) - index - 1
	raise Exception(strings.fileNumberingException)

def getSortedFilenames(directory, startImage):
	fileExtension = getMostCommonFileExtension(directory)
	filenames = getFilenamesWithExtension(directory, fileExtension)
	filenames.sort(key=lambda filename: getTrailingNumber(filename))
	
	if startImage != "":
		filenames = removeImagesBeforeStartingImage(filenames, startImage)
	
	return filenames

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

def getTargetPath(directory, program):
	figurePath = f"{directory}{cfg.FIGURE_DIRECTORY_NAME}"
	if not figurePath.endswith("/"):
		figurePath += "/"
	
	if not os.path.exists(figurePath):
	    os.mkdir(figurePath)
	
	targetPath = figurePath + f"{program}/"
	if not os.path.exists(targetPath):
	    os.mkdir(targetPath)
	
	return targetPath
