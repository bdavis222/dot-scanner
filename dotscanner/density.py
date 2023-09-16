import matplotlib.pyplot as pl
import numpy as np
import os

import dotscanner.dataprocessing as dp
import dotscanner.files as files
import dotscanner.strings as strings
from dotscanner.ui.DialogWindow import DialogWindow
from dotscanner.ui.MicroscopeImage import MicroscopeImage
from dotscanner.ui.ThresholdAdjuster import ThresholdAdjuster
import dotscanner.ui.window as ui
import settings.config as cfg
import settings.configmanagement as cm

if cfg.SCALE is None:
    PIXELS_TO_MICRONS = 1
    UNITS = "pix"
else:
    PIXELS_TO_MICRONS = 1e6 / (cfg.SCALE**2)
    UNITS = "um"


def checkUnitsConsistent(directory):
    if os.path.exists(directory + cfg.DENSITY_OUTPUT_FILENAME):
        with open(directory + cfg.DENSITY_OUTPUT_FILENAME, "r") as file:
            for line in file:
                splitLine = line.split()
                if len(splitLine) > 1 and splitLine[0] == "#" and splitLine[1] == "filename":
                    unitsInFile = line.split("per sq ")[1].split(")")[0]
                    if unitsInFile != UNITS:
                        showMismatchedUnitsErrorDialog()
                        quit()
                    return


def showMismatchedUnitsErrorDialog():
    DialogWindow(
        title="Inconsistent units error",
        message="\
Other measurements already recorded in output file \n\
have different units than those selected.\n\
This must be reconciled before proceeding.",
        positiveButtonText="Edit configurations",
        negativeButtonText="Cancel",
        positiveButtonAction=cm.showEditConfigFileDialog,
        windowWidth=400,
        windowX=10,
        windowY=30
    )


def getAlreadyMeasured(directory):
    alreadyMeasured = set()
    if os.path.exists(directory + cfg.DENSITY_OUTPUT_FILENAME):
        with open(directory + cfg.DENSITY_OUTPUT_FILENAME, "r") as file:
            for line in file:
                lineList = line.split()
                if len(lineList) and lineList[0] != "#":
                    filename = lineList[0]
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
                # For use with set_offsets(), which expects (x, y)
                blobsInPoly.append((x, y))
        elif dp.coordExists(y, x, dotCoords):
            dotTotal += 1
            # For use with set_offsets(), which expects (x, y)
            dotsInPoly.append((x, y))
    return dotTotal, blobTotal, dotsInPoly, blobsInPoly


def getDensityErrorAndCoords(microscopeImage, blobSize):
    dotCoords = microscopeImage.dotCoords
    blobCoords = microscopeImage.blobCoords
    data = microscopeImage.data

    points = []
    for y in range(len(data)):
        for x in range(len(data[0])):
            points.append((y, x))

    coordsInPolygon = dp.getCoordsInPolygon(
        data, points, microscopeImage.polygon)

    dotTotal, blobTotal, dotsInPoly, blobsInPoly = getTotalsAndCoords(
        coordsInPolygon, dotCoords, blobCoords, blobSize)

    surveyedArea = len(coordsInPolygon) - blobTotal
    density = dotTotal / surveyedArea * PIXELS_TO_MICRONS
    error = np.sqrt(dotTotal) / surveyedArea * PIXELS_TO_MICRONS

    return dotTotal, surveyedArea, density, error, dotsInPoly, blobsInPoly


def measureDensity(directory, filename, targetPath, microscopeImage, userSettings):
    if len(microscopeImage.polygon) < 3:
        return

    blobSize = userSettings.blobSize

    dotTotal, surveyedArea, density, error, dotsInPoly, blobsInPoly = getDensityErrorAndCoords(
        microscopeImage, blobSize)

    microscopeImage.dotCoords, microscopeImage.blobCoords = dotsInPoly, blobsInPoly
    saveDensityDataFiles(directory, filename, targetPath, dotTotal,
                         surveyedArea, density, error, microscopeImage, userSettings)


def reanalyzeDensityData(directory, userSettings):
    targetPath = files.getReanalysisTargetPath(
        directory, cfg.DENSITY_OUTPUT_FILENAME)
    adjustmentsMade = False

    numberOfFiles = len(list(userSettings.densityData.keys()))
    count = 0
    for filename, data in userSettings.densityData.items():
        microscopeImage = getMicroscopeImageFromReanalysisFile(
            directory, filename, userSettings, singleFile=False)

        if not adjustmentsMade:
            thresholdAdjuster = ThresholdAdjuster(
                microscopeImage, userSettings)

            print("Re-analyzing images...")
            ui.printProgressBar(0, numberOfFiles)

            # Updating with the threshold adjustments
            userSettings = thresholdAdjuster.userSettings
            adjustments = getReanalysisAdjustments(
                data, userSettings, microscopeImage)
            setReanalysisDataValues(
                adjustments, userSettings, microscopeImage, data)
            adjustmentsMade = not microscopeImage.skipped

        else:
            setReanalysisDataValues(
                adjustments, userSettings, microscopeImage, data)

        measureDensity(directory, filename, targetPath,
                       microscopeImage, userSettings)

        ui.printProgressBar(count + 1, numberOfFiles)
        count += 1


def reanalyzeSingleDensityFile(directory, filename, userSettings):
    targetPath = files.getReanalysisTargetPath(
        directory, cfg.DENSITY_OUTPUT_FILENAME)

    microscopeImage = getMicroscopeImageFromReanalysisFile(
        directory, filename, userSettings, singleFile=True)

    thresholdAdjuster = ThresholdAdjuster(
        microscopeImage, userSettings)

    # Updating with the threshold adjustments
    userSettings = thresholdAdjuster.userSettings
    data = userSettings.densityData[filename]
    adjustments = getReanalysisAdjustments(
        data, userSettings, microscopeImage)
    setReanalysisDataValues(
        adjustments, userSettings, microscopeImage, data)

    measureDensity(directory, filename, targetPath,
                   microscopeImage, userSettings)


def getMicroscopeImageFromReanalysisFile(directory, filename, userSettings, singleFile):
    microscopeImage = None
    try:
        microscopeImage = MicroscopeImage(directory, filename, userSettings)
    except:
        displayFilename = filename if len(
            filename) < 25 else f"{filename[:12]}...{filename[-12:]}"
        message = strings.REANALYSIS_NOT_IN_FILE if singleFile else strings.REANALYSIS_NOT_IN_FOLDER
        DialogWindow("File not found", message.format(filename=displayFilename),
                     "Ok", "Cancel", positiveButtonAction=quit, positiveButtonColor="blue")
        quit()
    return microscopeImage


def getReanalysisAdjustments(densityData, newUserSettings, microscopeImage):
    adjustments = [None for _ in range(8)]
    if densityData[0] != microscopeImage.lowerDotThreshScale:
        adjustments[0] = microscopeImage.lowerDotThreshScale
    if densityData[1] != microscopeImage.upperDotThreshScale:
        adjustments[1] = microscopeImage.upperDotThreshScale
    if densityData[2] != microscopeImage.lowerBlobThreshScale:
        adjustments[2] = microscopeImage.lowerBlobThreshScale
    if densityData[3] != newUserSettings.blobSize:
        adjustments[3] = newUserSettings.blobSize
    if densityData[4] != newUserSettings.dotSize:
        adjustments[4] = newUserSettings.dotSize
    if densityData[5] != newUserSettings.lowerContrast:
        adjustments[5] = newUserSettings.lowerContrast
    if densityData[6] != newUserSettings.upperContrast:
        adjustments[6] = newUserSettings.upperContrast
    if densityData[7] != microscopeImage.polygon:
        adjustments[7] = microscopeImage.polygon
    return adjustments


def setReanalysisDataValues(adjustments, userSettings, microscopeImage, data):
    # Set the data to what is read from the file
    microscopeImage.lowerDotThreshScale = data[0]
    microscopeImage.upperDotThreshScale = data[1]
    microscopeImage.lowerBlobThreshScale = data[2]
    microscopeImage.thresholds = (data[0], data[1], data[2])
    microscopeImage.blobSize = data[3]
    microscopeImage.dotSize = data[4]
    userSettings.lowerContrast = data[5]
    userSettings.upperContrast = data[6]
    microscopeImage.polygon = data[7]

    # Adjust the data that was adjusted to be different from the previous analysis
    threshAdjusted = False
    for index, adjustment in enumerate(adjustments):
        if adjustment is not None:
            if index == 0:
                microscopeImage.lowerDotThreshScale = adjustment
                threshAdjusted = True
            elif index == 1:
                microscopeImage.upperDotThreshScale = adjustment
                threshAdjusted = True
            elif index == 2:
                microscopeImage.lowerBlobThreshScale = adjustment
                threshAdjusted = True
            elif index == 3:
                userSettings.blobSize = adjustment
            elif index == 4:
                userSettings.dotSize = adjustment
            elif index == 5:
                userSettings.lowerContrast = adjustment
            elif index == 6:
                userSettings.upperContrast = adjustment
            elif index == 7:
                microscopeImage.polygon = adjustment
    if threshAdjusted:
        microscopeImage.thresholds = (microscopeImage.lowerDotThreshScale,
                                      microscopeImage.upperDotThreshScale,
                                      microscopeImage.lowerBlobThreshScale)


def saveDensityDataFiles(directory, filename, targetPath, dotTotal, surveyedArea, density, error,
                         microscopeImage, userSettings, skipped=False):
    if not os.path.exists(targetPath):
        with open(targetPath, "a") as file:
            file.write(strings.DENSITY_OUTPUT_FILE_HEADER)

    if skipped:
        output = f"{filename} skipped - - - - - - - - - - - -\n"

    else:
        density = np.round(density, 7)
        error = np.round(error, 7)
        output = strings.densityOutput(filename, dotTotal, surveyedArea, density, error,
                                       microscopeImage, userSettings)

    if not skipped and userSettings.saveFigures:
        outputFilename = targetPath.split("/")[-1]
        saveDensityFigure(directory, filename, outputFilename,
                          microscopeImage, userSettings)

    with open(targetPath, "a") as file:
        file.write(output)


def saveDensityFigure(directory, filename, outputFilename, microscopeImage, userSettings):
    data = microscopeImage.data
    polygon = microscopeImage.polygon
    dotCoords = microscopeImage.dotCoords
    blobCoords = microscopeImage.blobCoords

    for fileExtension in cfg.FIGURE_FILETYPES:
        figure, axes = pl.subplots()
        axes.imshow(data, cmap="gray", vmin=userSettings.lowerContrast,
                    vmax=userSettings.upperContrast * np.std(data), zorder=0)
        dotScatter = axes.scatter([None], [None], s=5 * userSettings.dotSize, facecolors="none",
                                  edgecolors=cfg.DOT_COLOR, linewidths=cfg.DOT_THICKNESS/2,
                                  zorder=4)
        dotScatter.set_offsets(dotCoords)

        if cfg.PLOT_BLOBS and blobCoords:
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

        targetPath = files.getFigureTargetPath(
            directory, outputFilename, fileExtension)

        truncatedFilename = ".".join(filename.split(".")[:-1])

        if fileExtension == "pdf":
            figure.savefig(f"{targetPath}{truncatedFilename}.{fileExtension}",
                           bbox_inches="tight", pad_inches=0)
        else:
            figure.savefig(f"{targetPath}{truncatedFilename}.{fileExtension}",
                           bbox_inches="tight", pad_inches=0, dpi=cfg.FIGURE_RESOLUTION)

        figure.clf()
        pl.close(figure)


def skipFile(directory, filename, targetPath, userSettings, microscopeImage):
    saveDensityDataFiles(directory, filename, targetPath, None,
                         None, None, None, microscopeImage, userSettings, skipped=True)
    print(strings.fileSkippedNotification(filename))
