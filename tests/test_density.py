import mock
import numpy as np
import os
import unittest

import dotscanner.dataprocessing as dp
import dotscanner.density as density
from tests.ui.FakeMicroscopeImage import FakeMicroscopeImage
from tests.ui.FakeUserSettings import FakeUserSettings


class TestDensity(unittest.TestCase):
    def getTestCoordsInPolygon(self):
        data = np.zeros([10, 10])

        points = []
        for y in range(10):
            for x in range(10):
                points.append((y, x))

        polygonVertices = [
            [1, 1],
            [6, 1],
            [6, 3],
            [1, 3],
            [1, 1]
        ]

        return dp.getCoordsInPolygon(data, points, polygonVertices)

    @mock.patch("settings.config.DENSITY_OUTPUT_FILENAME", "data/fakeData.txt")
    def test_getAlreadyMeasured(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        directory = dir_path if dir_path.endswith("/") else dir_path + "/"
        alreadyMeasured = density.getAlreadyMeasured(directory)

        self.assertEqual(len(alreadyMeasured), 3)
        self.assertIn("108.TIF", alreadyMeasured)

    def test_getCoordsInPolygon(self):
        coordsInPolygon = self.getTestCoordsInPolygon()
        coordTuples = []
        for coordPair in coordsInPolygon:
            y, x = coordPair
            coordTuples.append((y, x))

        self.assertNotIn((1, 1), coordTuples)
        self.assertIn((6, 3), coordTuples)
        self.assertIn((5, 2), coordTuples)
        self.assertIn((2, 2), coordTuples)
        self.assertNotIn((2, 5), coordTuples)
        self.assertNotIn((7, 3), coordTuples)
        self.assertNotIn((0, 0), coordTuples)

    def test_getTotalsAndCoords(self):
        coordsInPolygon = self.getTestCoordsInPolygon()
        dotCoords = {
            0: {0, 3},
            3: {2, 5},
            6: {3}
        }
        blobCoords = {
            8: {8}
        }

        dotTotal, blobTotal, _, _ = density.getTotalsAndCoords(coordsInPolygon, dotCoords,
                                                               blobCoords, blobSize=5)

        self.assertEqual(dotTotal, 1)
        self.assertEqual(blobTotal, 4)

        dotCoords = {
            0: {0, 3},
            3: {2, 5},
            6: {3}
        }
        blobCoords = {
            0: {8}
        }

        dotTotal, blobTotal, _, _ = density.getTotalsAndCoords(coordsInPolygon, dotCoords,
                                                               blobCoords, blobSize=5)

        self.assertEqual(dotTotal, 2)
        self.assertEqual(blobTotal, 5)

    def test_setReanalysisAdjustments_doesNothingWithNoChanges(self):
        lowerDotThresh, upperDotThresh, lowerBlobThresh = 1.5, 5.0, 2.0
        blobSize, dotSize = 5, 2
        lowerContrast, upperContrast = 0.0, 6.0
        polygon = [[1, 1], [5, 5], [10, 5], [5, 10], [1, 1]]
        data = [
            lowerDotThresh,
            upperDotThresh,
            lowerBlobThresh,
            blobSize,
            dotSize,
            lowerContrast,
            upperContrast,
            polygon
        ]
        microscopeImage = FakeMicroscopeImage(
            polygon=polygon,
            lowerDotThreshScale=1.5,
            upperDotThreshScale=5.0,
            lowerBlobThreshScale=2.0
        )
        newUserSettings = FakeUserSettings(
            dotSize=2,
            blobSize=5,
            lowerContrast=0.0,
            upperContrast=6.0,
            polygon=polygon
        )
        adjustments = density.getReanalysisAdjustments(
            data, newUserSettings, microscopeImage)

        for element in adjustments:
            self.assertEqual(element, None)

    def test_setReanalysisAdjustments_identifiesChangesCorrectly(self):
        lowerDotThresh, upperDotThresh, lowerBlobThresh = 1.5, 5.0, 2.0
        blobSize, dotSize = 5, 2
        lowerContrast, upperContrast = 0.0, 6.0
        polygon = [[1, 1], [5, 5], [10, 5], [5, 10], [1, 1]]
        data = [
            lowerDotThresh,
            upperDotThresh,
            lowerBlobThresh,
            blobSize,
            dotSize,
            lowerContrast,
            upperContrast,
            polygon
        ]
        newUserSettings = FakeUserSettings(
            dotSize=2,
            blobSize=6,
            lowerContrast=0.0,
            upperContrast=5.5,
            polygon=polygon
        )
        microscopeImage = FakeMicroscopeImage(
            polygon=polygon,
            lowerDotThreshScale=1.7,
            upperDotThreshScale=4.8,
            lowerBlobThreshScale=2.0
        )
        adjustments = density.getReanalysisAdjustments(
            data, newUserSettings, microscopeImage)

        self.assertEqual(adjustments[0], 1.7)
        self.assertEqual(adjustments[1], 4.8)
        self.assertEqual(adjustments[2], None)
        self.assertEqual(adjustments[3], 6)
        self.assertEqual(adjustments[4], None)
        self.assertEqual(adjustments[5], None)
        self.assertEqual(adjustments[6], 5.5)
        self.assertEqual(adjustments[7], None)

    def test_setReanalysisDataValues(self):
        adjustments = [1.7, None, None, None, None, None,
                       None, [[1, 1], [5, 5], [10, 8], [1, 1]]]
        lowerDotThresh, upperDotThresh, lowerBlobThresh = 1.5, 5.0, 2.0
        blobSize, dotSize = 5, 2
        lowerContrast, upperContrast = 0.0, 6.0
        polygon = [[1, 1], [5, 5], [10, 5], [5, 10], [1, 1]]
        data = [
            lowerDotThresh,
            upperDotThresh,
            lowerBlobThresh,
            blobSize,
            dotSize,
            lowerContrast,
            upperContrast,
            polygon
        ]
        microscopeImage = FakeMicroscopeImage(
            lowerDotThreshScale=1.5,
            upperDotThreshScale=5.0,
            lowerBlobThreshScale=2.0
        )
        userSettings = FakeUserSettings(
            dotSize=2,
            blobSize=5,
            lowerContrast=0.0,
            upperContrast=6.0,
            polygon=polygon
        )
        density.setReanalysisDataValues(
            adjustments, userSettings, microscopeImage, data)

        self.assertEqual(microscopeImage.lowerDotThreshScale, 1.7)
        self.assertEqual(microscopeImage.upperDotThreshScale, 5.0)
        self.assertEqual(microscopeImage.lowerBlobThreshScale, 2.0)
        self.assertEqual(microscopeImage.thresholds, (1.7, 5.0, 2.0))
        self.assertEqual(userSettings.dotSize, 2)
        self.assertEqual(userSettings.blobSize, 5)
        self.assertEqual(userSettings.lowerContrast, 0.0)
        self.assertEqual(userSettings.upperContrast, 6.0)
        self.assertEqual(microscopeImage.polygon, [
                         [1, 1], [5, 5], [10, 8], [1, 1]])


if __name__ == '__main__':
    unittest.main()
