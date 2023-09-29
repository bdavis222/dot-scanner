import matplotlib.pyplot as pl
import numpy as np
import os

import dotscanner.files as files
import dotscanner.dataprocessing as dp
import dotscanner.strings as strings
import dotscanner.ui.window as ui
from dotscanner.ui.MicroscopeImage import MicroscopeImage
import settings.config as cfg


def addToPlotCoords(coordsToPlot, y, x, imageNumber, lifetime):
    for frame in range(imageNumber, imageNumber + lifetime):
        if frame not in coordsToPlot:
            coordsToPlot[frame] = set()
        if (x, y) not in coordsToPlot[frame]:
            coordsToPlot[frame].add((x, y))


def checkEnoughFramesForLifetimes(filenames, userSettings):
    if len(filenames) <= 2 * (userSettings.skipsAllowed + 1):
        raise Exception(strings.TOO_FEW_FRAMES_EXCEPTION)


def coordExistsInPrevFrame(y, x, imageNumber, imageNumberToCoordMap, dotSize, skipsAllowed):
    firstFrameNumber = max(0, imageNumber - skipsAllowed - 1)
    frameNumbers = range(firstFrameNumber, imageNumber)
    for frameNumber in reversed(frameNumbers):
        frameCoords = imageNumberToCoordMap[frameNumber]
        if dp.coordExistsWithinRadius(y, x, frameCoords, dotSize):
            return True
    return False


def getCoordLifetimeAndDisplacement(y, x, imageNumber, edgeFrameNumbers, imageNumberToCoordMap,
                                    dotSize, skipsAllowed, removeEdgeFrames):
    startingY, startingX = y, x
    skipsRemaining = skipsAllowed
    nextImageNumber = imageNumber + 1

    if nextImageNumber not in imageNumberToCoordMap and skipsAllowed > 0:
        return None, None

    while nextImageNumber in imageNumberToCoordMap:
        nextCoords = imageNumberToCoordMap[nextImageNumber]

        closestDotCoords = dp.getClosestCoordWithinRadius(
            y, x, nextCoords, dotSize)
        if closestDotCoords is None:
            if skipsRemaining == 0:
                break
            skipsRemaining -= 1

        else:
            if removeEdgeFrames and nextImageNumber in edgeFrameNumbers:
                return None, None

            if skipsRemaining < skipsAllowed:
                skipsRemaining = skipsAllowed

            y, x = closestDotCoords

        nextImageNumber += 1

    lifetime = nextImageNumber - imageNumber - (skipsAllowed - skipsRemaining)
    displacement = (y - startingY)**2 + (x - startingX)**2

    return lifetime, displacement


def getEdgeFrameNumbers(imageNumberToCoordMap, skipsAllowed):
    firstFrame = 0
    lastFrameOfFrontEdge = skipsAllowed + 1
    firstFrameOfBackEdge = list(
        imageNumberToCoordMap.keys())[-1] - skipsAllowed
    lastFrame = list(imageNumberToCoordMap.keys())[-1] + 1

    firstFrames = range(firstFrame, lastFrameOfFrontEdge)
    lastFrames = range(firstFrameOfBackEdge, lastFrame)
    return set(list(firstFrames) + list(lastFrames))


def measureLifetime(directory, filenames, middleMicroscopeImage, userSettings, testing=False):
    if len(middleMicroscopeImage.polygon) < 3:
        return

    blobSize = userSettings.blobSize
    dotSize = userSettings.dotSize
    skipsAllowed = userSettings.skipsAllowed
    removeEdgeFrames = userSettings.removeEdgeFrames

    lowerDotThresh, upperDotThresh, lowerBlobThresh = dp.getThresholds(
        middleMicroscopeImage)
    middleImagePolygonCoordMap = dp.getInPolygonCoordMap(middleMicroscopeImage)
    xMin, xMax, yMin, yMax = dp.getPolygonLimits(middleMicroscopeImage.polygon)

    imageNumberToCoordMap = {}
    imageNumberToBlobCoordMap = {}
    imageNumberToFilenameMap = {}

    numberOfFiles = len(filenames)
    if not testing:
        print("Getting coordinates of all dots...")
        ui.printProgressBar(0, numberOfFiles)

    for index, filename in enumerate(filenames):
        microscopeImage = MicroscopeImage(directory, filename, userSettings)

        dotCoords, blobCoords = dp.getCoordMapsWithinPolygon(microscopeImage.data,
                                                             microscopeImage.sums, lowerDotThresh,
                                                             upperDotThresh, lowerBlobThresh,
                                                             middleImagePolygonCoordMap, xMin, xMax,
                                                             yMin, yMax)
        dp.cleanDotCoords(microscopeImage.data, dotCoords,
                          blobCoords, blobSize, dotSize)

        imageNumberToCoordMap[index] = dotCoords
        imageNumberToFilenameMap[index] = filename
        if cfg.PLOT_BLOBS:
            imageNumberToBlobCoordMap[index] = blobCoords

        if not testing:
            ui.printProgressBar(index + 1, numberOfFiles)

    lifetimes, resultCoords, startImages, displacements = [], [], [], []
    edgeFrameNumbers = getEdgeFrameNumbers(imageNumberToCoordMap, skipsAllowed)
    coordsToPlot = {}  # Maps image numbers to coordinate maps for plotting

    for imageNumber, coordMap in imageNumberToCoordMap.items():
        if removeEdgeFrames and imageNumber in edgeFrameNumbers:
            continue

        for y, xSet in coordMap.items():
            for x in xSet:
                updateLifetimeResults(imageNumber, y, x, lifetimes, resultCoords, startImages,
                                      displacements, imageNumberToCoordMap, edgeFrameNumbers,
                                      dotSize, skipsAllowed, removeEdgeFrames,
                                      userSettings.saveFigures, coordsToPlot)

    if not len(lifetimes):
        print(strings.NO_LIFETIMES_FOUND_ERROR)
        quit()

    filteredLifetimeIndices = getFilteredLifetimeIndices(lifetimes)

    saveLifetimeDataFiles(directory, lifetimes, resultCoords, startImages, displacements,
                          filteredLifetimeIndices, imageNumberToBlobCoordMap,
                          imageNumberToFilenameMap, middleMicroscopeImage, userSettings,
                          coordsToPlot, middleMicroscopeImage.polygon, testing=testing)


def getFilteredLifetimeIndices(lifetimes):
    statistic = np.mean(lifetimes) / np.std(lifetimes)
    indices = list(range(len(lifetimes)))
    while statistic < cfg.NOISE_STATISTIC:
        lifetimes, indices = getLifetimesAndIndicesWithoutMin(
            lifetimes, indices)
        statistic = np.mean(lifetimes) / np.std(lifetimes)
    return set(indices)


def getLifetimesAndIndicesWithoutMin(lifetimes, indices):
    minLifetime = min(lifetimes)
    filteredLifetimes = []
    filteredIndices = []
    for lifetime, index in zip(lifetimes, indices):
        if lifetime != minLifetime:
            filteredLifetimes.append(lifetime)
            filteredIndices.append(index)
    return filteredLifetimes, filteredIndices


def saveLifetimeDataFiles(directory, lifetimes, resultCoords, startImages, displacements,
                          filteredIndices, imageNumberToBlobCoordMap, imageNumberToFilenameMap,
                          microscopeImage, userSettings, coordsToPlot, polygon, testing=False):
    if userSettings.reanalysis:
        targetPath = files.getReanalysisTargetPath(
            directory, cfg.LIFETIME_OUTPUT_FILENAME)
    else:
        targetPath = files.getAnalysisTargetPath(
            directory, cfg.LIFETIME_OUTPUT_FILENAME)
        if os.path.exists(targetPath):
            os.remove(targetPath)

    with open(targetPath, "a") as file:
        file.write(strings.lifetimeOutputFileHeader(
            microscopeImage, userSettings))
        for index, lifetime, resultCoord, startImage, displacement in zip(range(len(lifetimes)),
                                                                          lifetimes, resultCoords,
                                                                          startImages,
                                                                          displacements):
            y, x = resultCoord
            filename = imageNumberToFilenameMap[startImage]
            note = "" if index in filteredIndices else " y"
            output = f"{x} {y} {lifetime} {filename} {displacement}{note}\n"
            file.write(output)

    outputFilename = targetPath.split("/")[-1]
    if not testing:
        print(f"{outputFilename} saved.")

    saveHistogram(directory, outputFilename, lifetimes)
    saveNoiseStatisticHistogram(
        directory, outputFilename, lifetimes, filteredIndices)

    if userSettings.saveFigures:
        saveLifetimeFigures(directory, outputFilename, coordsToPlot, imageNumberToBlobCoordMap,
                            imageNumberToFilenameMap, userSettings, polygon)


def saveLifetimeFigures(directory, outputFilename, coordsToPlot, imageNumberToBlobCoordMap,
                        imageNumberToFilenameMap, userSettings, polygon):
    print("Saving figures...")
    coordsToPlotSize = len(list(coordsToPlot.keys()))
    count = 0
    totalCount = coordsToPlotSize * len(cfg.FIGURE_FILETYPES)
    ui.printProgressBar(count, totalCount)

    for fileExtension in cfg.FIGURE_FILETYPES:
        for imageNumber, dotCoordSet in coordsToPlot.items():
            filename = imageNumberToFilenameMap[imageNumber]
            microscopeImage = MicroscopeImage(
                directory, filename, userSettings)
            data = microscopeImage.data

            figure, axes = pl.subplots()
            axes.imshow(data, cmap="gray", vmin=userSettings.lowerContrast,
                        vmax=userSettings.upperContrast * np.std(data), zorder=0)
            dotScatter = axes.scatter([None], [None], s=5 * userSettings.dotSize, facecolors="none",
                                      edgecolors=cfg.DOT_COLOR,
                                      linewidths=cfg.DOT_THICKNESS/2, zorder=4)
            dotScatter.set_offsets(list(dotCoordSet))

            if cfg.PLOT_BLOBS:
                blobSize = userSettings.blobSize
                blobCoordMap = imageNumberToBlobCoordMap[imageNumber]
                blobScatter = axes.scatter([None], [None], s=0.1 * blobSize, facecolors="none",
                                           edgecolors=cfg.BLOB_COLOR,
                                           linewidths=cfg.BLOB_THICKNESS/2, zorder=3)
                dp.setScatterOffset(blobCoordMap, blobScatter)

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

            count += 1
            ui.printProgressBar(count, totalCount)


def saveHistogram(directory, outputFilename, lifetimes):
    figure = pl.figure()
    axes = figure.add_subplot(111)

    plotBins = max(lifetimes) + 1
    histData = axes.hist(lifetimes, bins=np.arange(
        plotBins)+0.5, rwidth=0.9, color="C1")
    yOffset = max(histData[0]) * 0.005

    for i in range(plotBins - 1):
        if plotBins < 25 or (i+1) % 5 == 0:
            axes.text(i+1, yOffset, i+1, fontsize=6,
                      horizontalalignment="center")

    if plotBins < 25:
        for i in range(plotBins - 1):
            if histData[0][i] > 5 * yOffset:
                axes.text(i+1, histData[0][i] + yOffset, int(histData[0][i]),
                          fontsize=6, color="C1", horizontalalignment="center")
    else:
        maxCounts = max(histData[0])
        for i in range(plotBins - 1):
            if histData[0][i] == maxCounts:
                axes.text(i+1, histData[0][i] + yOffset, int(histData[0][i]),
                          fontsize=6, color="C1", horizontalalignment="center")
                break

    targetPath = files.getLifetimeHistogramTargetPath(directory)
    outputFilenameWithoutExtension = outputFilename.split(".")[0]
    figure.savefig(f"{targetPath}{outputFilenameWithoutExtension}_hist.pdf")

    figure.clf()
    pl.close(figure)


def saveNoiseStatisticHistogram(directory, outputFilename, lifetimes, filteredIndices):
    figure = pl.figure()
    axes = figure.add_subplot(111)

    filteredLifetimes = []
    for index in filteredIndices:
        filteredLifetimes.append(lifetimes[index])

    plotBins = max(lifetimes) + 1
    filteredHistData = axes.hist(filteredLifetimes, bins=np.arange(plotBins)+0.5,
                                 rwidth=0.9, color="C0", density=True, label="Filtered data")

    histData = axes.hist(lifetimes, bins=np.arange(
        plotBins)+0.5, rwidth=0.9, color="C1", density=True, label="All data")
    yOffset = max(histData[0]) * 0.005

    for i in range(plotBins - 1):
        if plotBins < 25 or (i+1) % 5 == 0:
            axes.text(i+1, yOffset, i+1, fontsize=6,
                      horizontalalignment="center")

    axes.legend()

    targetPath = files.getLifetimeHistogramTargetPath(directory)
    outputFilenameWithoutExtension = outputFilename.split(".")[0]
    figure.savefig(
        f"{targetPath}{outputFilenameWithoutExtension}_noise_hist.pdf")

    figure.clf()
    pl.close(figure)


def updateLifetimeResults(imageNumber, y, x, lifetimes, resultCoords, startImages, displacements,
                          imageNumberToCoordMap, edgeFrameNumbers, dotSize, skipsAllowed,
                          removeEdgeFrames, saveFigures, coordsToPlot):
    if removeEdgeFrames and imageNumber <= skipsAllowed:
        return

    if coordExistsInPrevFrame(y, x, imageNumber, imageNumberToCoordMap, dotSize, skipsAllowed):
        return

    coordLifetime, coordDisplacement = getCoordLifetimeAndDisplacement(y, x, imageNumber,
                                                                       edgeFrameNumbers,
                                                                       imageNumberToCoordMap,
                                                                       dotSize, skipsAllowed,
                                                                       removeEdgeFrames)

    if coordLifetime is None:
        return

    lifetimes.append(coordLifetime)
    resultCoords.append((y, x))
    startImages.append(imageNumber)
    displacements.append(coordDisplacement)

    if saveFigures and coordLifetime >= cfg.LIFETIME_MIN_FOR_PLOT:
        addToPlotCoords(coordsToPlot, y, x, imageNumber, coordLifetime)
