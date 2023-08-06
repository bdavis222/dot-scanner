from PIL import Image
import os

from dotscanner.programtype import ProgramType
import dotscanner.strings as strings
import settings.config as cfg


def fixDirectory(string):
    return string if string.endswith("/") else string + "/"


def getDirectoryAndFilenames(userSettings, testing=False):
    filepath = userSettings.filepath
    startImage = userSettings.startImage

    if os.path.isfile(filepath):
        directory = fixDirectory(os.path.dirname(filepath))
        filename = os.path.basename(filepath)
        return directory, [filename]

    elif os.path.isdir(filepath):
        directory = fixDirectory(filepath)

    else:
        raise Exception(strings.FILEPATH_EXCEPTION)

    filenames = getSortedFilenames(
        directory, startImage, userSettings.program, testing=testing)

    if not len(filenames):
        raise Exception(strings.NO_FILES_EXCEPTION)

    return directory, filenames


def getFilenamesWithExtension(directory, fileExtension, testing=False):
    filenames = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(fileExtension.lower()):
            filenames.append(filename)

    if not testing:
        verifyImageExtension(directory, filenames[0])

    return filenames


def verifyImageExtension(directory, filename):
    try:
        Image.open(directory + filename)
    except:
        extension = filename.split(".")[-1]
        print(strings.INVALID_IMAGE_EXTENSION.format(extension=extension))
        quit()


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
        raise Exception(strings.NO_FILES_EXCEPTION)

    extensionFrequencies = {}  # Maps the extension string to the number of times it appears
    for filename in filenames:
        if filename.startswith(".") or filename.endswith(".txt"):
            continue

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
        raise Exception(strings.NO_FILES_EXCEPTION)

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

    raise Exception(strings.FILE_NUMBERING_EXCEPTION)


def getSortedFilenames(directory, startImage, programSelected, testing=False):
    if hasNoValidFiles(directory):
        return []

    fileExtension = getMostCommonFileExtension(directory)
    filenames = getFilenamesWithExtension(
        directory, fileExtension, testing=testing)

    allFilesNumbered = allFilesAreNumbered(filenames)
    if programSelected == ProgramType.LIFETIME and not allFilesNumbered:
        raise Exception(strings.FILE_NUMBERING_EXCEPTION)

    if allFilesNumbered:
        filenames.sort(key=lambda filename: getTrailingNumber(filename))
    else:
        filenames.sort()

    if programSelected == ProgramType.LIFETIME and startImage != "":
        filenames = removeImagesBeforeStartingImage(filenames, startImage)

    return filenames


def hasNoValidFiles(directory):
    for file in os.listdir(directory):
        if file.startswith("."):
            continue

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


def getAnalysisTargetPath(directory, filename):
    return directory + filename


def getReanalysisTargetPath(directory, filename):
    targetPath = directory + filename
    while os.path.exists(targetPath):
        targetPath = incrementTargetPathName(targetPath)
    return targetPath


def incrementTargetPathName(targetPath):
    filename = os.path.basename(targetPath)
    if not filenameIsNumbered(filename):
        filenameArray = filename.split(".")
        filename = filenameArray[0] + "1." + filenameArray[1]
    trailingNumber = getTrailingNumber(filename)
    trailingNumber += 1
    newFilename = getFilenameWithNewTrailingNumber(filename, trailingNumber)
    directory = fixDirectory(os.path.dirname(targetPath))
    return directory + newFilename


def getFilenameWithNewTrailingNumber(filename, trailingNumber):
    rightIndex = getRightEdgeOfTrailingNumber(filename)
    leftIndex = getLeftEdgeOfTrailingNumber(filename, rightIndex)
    return f"{filename[:leftIndex]}{trailingNumber}{filename[rightIndex + 1:]}"


def filenameIsNumbered(filename):
    periodReached = False
    for index, char in enumerate(reversed(filename)):
        if char == ".":
            periodReached = True
            continue

        if not periodReached:
            continue

        return char.isdigit()


def getFigureTargetPath(directory, outputFilename, fileExtension):
    figureDirectoryName = cfg.FIGURE_DIRECTORY_NAME
    if not figureDirectoryName.endswith("/"):
        figureDirectoryName += "/"

    figurePathWithoutExtension = f"{directory}{figureDirectoryName}"

    if not os.path.exists(figurePathWithoutExtension):
        os.mkdir(figurePathWithoutExtension)

    figurePath = f"{directory}{figureDirectoryName}{fileExtension}/"

    if not os.path.exists(figurePath):
        os.mkdir(figurePath)

    outputFilenameWithoutExtension = outputFilename.split(".")[0]
    targetPath = figurePath + f"{outputFilenameWithoutExtension}/"
    if not os.path.exists(targetPath):
        os.mkdir(targetPath)

    return targetPath


def getLifetimeHistogramTargetPath(directory):
    figureDirectoryName = cfg.FIGURE_DIRECTORY_NAME
    if not figureDirectoryName.endswith("/"):
        figureDirectoryName += "/"

    figurePath = f"{directory}{figureDirectoryName}/"

    if not os.path.exists(figurePath):
        os.mkdir(figurePath)

    return figurePath


def getExtensionIndexFromDensityAnalysisFileLineArray(lineArray):
    for index, element in enumerate(lineArray):
        if "." in element:
            periodIndex = element.find(".")
            if not element[periodIndex + 1].isdigit():
                return index
    return -1
