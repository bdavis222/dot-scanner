import settings.config as cfg

import dotscanner.dataprocessing as dp
import dotscanner.strings as strings


class MicroscopeImage:
    def __init__(self, directory, filename, userSettings):
        self.memoizedCoords = {}
        self.polygon = self.getPolygon(filename, userSettings)
        self.skipped = False  # Whether analysis should be skipped for this image

        self.userSettings = userSettings
        self.thresholds = userSettings.thresholds
        self.lowerDotThreshScale = self.thresholds[0]
        self.upperDotThreshScale = self.thresholds[1]
        self.lowerBlobThreshScale = self.thresholds[2]

        self.data = dp.getData(directory, filename)
        self.sums = dp.getFullDataSquareSum(self.data)
        self.dotCoords, self.blobCoords = self.getCoords()

    def decreaseLowerDotThreshScale(self):
        value = self.lowerDotThreshScale - cfg.THRESHOLD_DELTA
        value = round(value, 1)
        self.lowerDotThreshScale = value
        self.updateThresholds()
        self.dotCoords, self.blobCoords = self.getCoords()

    def decreaseUpperDotThreshScale(self):
        value = self.upperDotThreshScale - cfg.THRESHOLD_DELTA
        value = round(value, 1)
        if value < self.lowerDotThreshScale:
            print(strings.UPPER_DOT_THRESH_SCALE_WARNING)
            return
        self.upperDotThreshScale = value
        self.updateThresholds()
        self.dotCoords, self.blobCoords = self.getCoords()

    def getCoords(self):
        combination = (self.thresholds,
                       (self.userSettings.dotSize, self.userSettings.blobSize))
        if combination in self.memoizedCoords:
            dotCoords, blobCoords = self.memoizedCoords[combination]
        else:
            dotCoords, blobCoords = dp.getCoords(
                self.data, self.sums, self.thresholds)
            dp.cleanDotCoords(self.data, dotCoords, blobCoords, self.userSettings.blobSize,
                              self.userSettings.dotSize)
            self.memoizedCoords[combination] = (dotCoords, blobCoords)
        return dotCoords, blobCoords

    def getPolygon(self, filename, userSettings):
        if userSettings.polygon:
            return userSettings.polygon
        elif userSettings.densityData:
            return userSettings.densityData[filename][7]
        else:
            return []

    def increaseLowerDotThreshScale(self):
        value = self.lowerDotThreshScale + cfg.THRESHOLD_DELTA
        value = round(value, 1)
        if value > self.upperDotThreshScale:
            print(strings.UPPER_DOT_THRESH_SCALE_WARNING)
            return
        self.lowerDotThreshScale = value
        self.updateThresholds()
        self.dotCoords, self.blobCoords = self.getCoords()

    def increaseUpperDotThreshScale(self):
        value = self.upperDotThreshScale + cfg.THRESHOLD_DELTA
        value = round(value, 1)
        self.upperDotThreshScale = value
        self.updateThresholds()
        self.dotCoords, self.blobCoords = self.getCoords()

    def setThresholds(self, newThresholds):
        newLowerDotThreshScale = round(newThresholds[0], 1)
        newUpperDotThreshScale = round(newThresholds[1], 1)
        newLowerBlobThreshScale = round(newThresholds[2], 1)

        if newUpperDotThreshScale < newLowerDotThreshScale:
            print(strings.UPPER_DOT_THRESH_SCALE_WARNING)
            return

        if newLowerBlobThreshScale < 1:
            print(strings.LOWER_BLOB_THRESH_SCALE_WARNING)
            newLowerBlobThreshScale = 1.0

        self.lowerDotThreshScale = newLowerDotThreshScale
        self.upperDotThreshScale = newUpperDotThreshScale
        self.lowerBlobThreshScale = newLowerBlobThreshScale

        self.updateThresholds()

    def updateThresholds(self):
        self.thresholds = (self.lowerDotThreshScale, self.upperDotThreshScale,
                           self.lowerBlobThreshScale)
