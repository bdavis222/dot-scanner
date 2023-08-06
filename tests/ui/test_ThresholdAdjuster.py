import mock
import numpy as np
import unittest
from unittest.mock import MagicMock

from dotscanner.ui.MicroscopeImage import MicroscopeImage
from dotscanner.ui.ThresholdAdjuster import ThresholdAdjuster
from tests.ui.FakeUserSettings import FakeUserSettings


class TestThresholdAdjuster(unittest.TestCase):
    @mock.patch("dotscanner.dataprocessing.getData")
    def getMicroscopeImageAndUserSettings(self, mock_getData):
        testData = np.array([
            [2,  0,  0,  0,  0,  0, -2,  0,  0,  0,  0,  0,  0],
            [2,  2,  0,  0,  0,  1,  0, -1, -1,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0, -2,  0,  2,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
            [-1,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  5,  4,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  2,  0, -1,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0, -1, -1,  0,  0,  0,  0],
            [0,  7,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0],
            [0,  5,  9,  0,  0,  0,  0,  1,  0,  0,  0,  8,  0],
            [-1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0],
        ])
        mock_getData.return_value = testData
        fakeUserSettings = FakeUserSettings(
            filepath="test/directory/", dotSize=2, blobSize=3, saveFigures=False,
            startImage="", skipsAllowed=0, removeEdgeFrames=True, lowerContrast=0.0,
            upperContrast=5.0, lowerDotThresh=1.2, upperDotThresh=1.8, lowerBlobThresh=1.3,
            program="density", polygon=None, densityData={})
        microscopeImage = MicroscopeImage(
            "test/directory/", "filename.png", fakeUserSettings)
        return microscopeImage, fakeUserSettings

    def test_upperDotThresholdScaleDown(self):
        '''getFullDataSquareSum generates the following from the given test data:
        [[ 6  6  2  0  1 -1 -2 -4 -2 -1  0  0  0]
         [ 6  6  2  0  1 -1 -2 -6 -4 -1  2  2  0]
         [ 4  4  2  0  1  1  0 -4 -4 -1  2  2  0]
         [-1 -1  0  0  0  1  1 -1 -2  0  2  2  0]
         [-1 -1  0  0  0  6 10 10  4  0  0  0  0]
         [-1 -1  0  0  0  8 12 11  3 -1  0  0  0]
         [ 0  0  0  0  0  7 10  8  1 -2  0  0  0]
         [ 7  7  7  0  0  2  1 -1 -3 -2  1  1  1]
         [12 21 21  9  0  0  0 -1 -1 -1  9  9  9]
         [11 20 21  9  0  0  1  1  1  0 10 10 10]
         [ 4 13 14  9  0  0  1  1  1  0  9  9  9]]

        Given the threshold scales of 1.2, 1.8, and 1.3, the thresholds are:
        6.151707193431039, 9.227560790146558, and 11.995829027190528

        Decreasing the upper dot thresh scale by 0.1 results in the following:
        6.151707193431039, 8.714918524027306, and 11.995829027190528

        This means that getFullDataSquareSum values of 9 will be evaluated as potential blobs now,
        resulting in the previous dot with testData value 8 detected at (x, y) = (11, 9) no
        longer being detected as a dot.

        Also, because of the getFullDataSquareSum values of 9 at (x, y) = (3, 8) and (10, 8), and 
        the blob size of 3, the testData values of 5, 4, and 2 near the middle of the image are
        no longer considered, and the testData value of 1 at (x, y) = (6, 4) is the new dot.'''

        microscopeImage, fakeUserSettings = self.getMicroscopeImageAndUserSettings()
        thresholdAdjuster = ThresholdAdjuster(
            microscopeImage, fakeUserSettings, drawUi=False)
        thresholdAdjuster.setThresholdEntries = MagicMock(return_value=None)
        thresholdAdjuster.canvas.draw = MagicMock(return_value=None)

        # Expected offsets = [[6, 5], [11, 9]]
        dotOffsets = thresholdAdjuster.dotScatter.get_offsets()

        self.assertEqual(microscopeImage.thresholds, (1.2, 1.8, 1.3))
        self.assertEqual(len(dotOffsets), 2)
        self.assertIn([6, 5], dotOffsets)
        self.assertIn([11, 9], dotOffsets)
        self.assertEqual(len(dotOffsets), 2)

        thresholdAdjuster.upperDotThresholdScaleDown()

        # Expected offsets = [[6, 4]]
        dotOffsets2 = thresholdAdjuster.dotScatter.get_offsets()

        self.assertEqual(microscopeImage.thresholds, (1.2, 1.7, 1.3))
        self.assertEqual(len(dotOffsets2), 1)
        self.assertIn([6, 4], dotOffsets2)

    def test_upperDotThresholdScaleUp(self):
        # This is the inverse of the previous test, scaling down first, and then back up

        microscopeImage, fakeUserSettings = self.getMicroscopeImageAndUserSettings()
        thresholdAdjuster = ThresholdAdjuster(
            microscopeImage, fakeUserSettings, drawUi=False)
        thresholdAdjuster.setThresholdEntries = MagicMock(return_value=None)
        thresholdAdjuster.canvas.draw = MagicMock(return_value=None)

        thresholdAdjuster.upperDotThresholdScaleDown()

        # Expected offsets = [[6, 4]]
        dotOffsets = thresholdAdjuster.dotScatter.get_offsets()

        self.assertEqual(microscopeImage.thresholds, (1.2, 1.7, 1.3))
        self.assertEqual(len(dotOffsets), 1)
        self.assertIn([6, 4], dotOffsets)

        thresholdAdjuster.upperDotThresholdScaleUp()

        # Expected offsets = [[6, 5], [11, 9]]
        dotOffsets2 = thresholdAdjuster.dotScatter.get_offsets()

        self.assertEqual(microscopeImage.thresholds, (1.2, 1.8, 1.3))
        self.assertEqual(len(dotOffsets2), 2)
        self.assertIn([6, 5], dotOffsets2)
        self.assertIn([11, 9], dotOffsets2)

    def test_lowerDotThresholdScaleDown(self):
        '''getFullDataSquareSum generates the following from the given test data:
        [[ 6  6  2  0  1 -1 -2 -4 -2 -1  0  0  0]
         [ 6  6  2  0  1 -1 -2 -6 -4 -1  2  2  0]
         [ 4  4  2  0  1  1  0 -4 -4 -1  2  2  0]
         [-1 -1  0  0  0  1  1 -1 -2  0  2  2  0]
         [-1 -1  0  0  0  6 10 10  4  0  0  0  0]
         [-1 -1  0  0  0  8 12 11  3 -1  0  0  0]
         [ 0  0  0  0  0  7 10  8  1 -2  0  0  0]
         [ 7  7  7  0  0  2  1 -1 -3 -2  1  1  1]
         [12 21 21  9  0  0  0 -1 -1 -1  9  9  9]
         [11 20 21  9  0  0  1  1  1  0 10 10 10]
         [ 4 13 14  9  0  0  1  1  1  0  9  9  9]]

        Given the threshold scales of 1.2, 1.8, and 1.3, the thresholds are:
        6.151707193431039, 9.227560790146558, and 11.995829027190528

        Decreasing the lower dot thresh scale by 0.1 results in the following:
        5.639064927311785, 8.714918524027306, and 11.995829027190528

        This means that getFullDataSquareSum values of 6 will be bright enough to be dots now,
        resulting in a new dot at (0, 0).'''

        microscopeImage, fakeUserSettings = self.getMicroscopeImageAndUserSettings()
        thresholdAdjuster = ThresholdAdjuster(
            microscopeImage, fakeUserSettings, drawUi=False)
        thresholdAdjuster.setThresholdEntries = MagicMock(return_value=None)
        thresholdAdjuster.canvas.draw = MagicMock(return_value=None)

        # Expected offsets = [[6, 5], [11, 9]]
        dotOffsets = thresholdAdjuster.dotScatter.get_offsets()

        self.assertEqual(microscopeImage.thresholds, (1.2, 1.8, 1.3))
        self.assertEqual(len(dotOffsets), 2)
        self.assertIn([6, 5], dotOffsets)
        self.assertIn([11, 9], dotOffsets)

        thresholdAdjuster.lowerDotThresholdScaleDown()

        # Expected offsets = [[0, 0], [6, 5], [11, 9]]
        dotOffsets2 = thresholdAdjuster.dotScatter.get_offsets()

        self.assertEqual(microscopeImage.thresholds, (1.1, 1.8, 1.3))
        self.assertEqual(len(dotOffsets2), 3)
        self.assertIn([0, 0], dotOffsets2)
        self.assertIn([6, 5], dotOffsets2)
        self.assertIn([11, 9], dotOffsets2)

    def test_lowerDotThresholdScaleUp(self):
        # This is the inverse of the previous test, scaling down first, and then back up

        microscopeImage, fakeUserSettings = self.getMicroscopeImageAndUserSettings()
        thresholdAdjuster = ThresholdAdjuster(
            microscopeImage, fakeUserSettings, drawUi=False)
        thresholdAdjuster.setThresholdEntries = MagicMock(return_value=None)
        thresholdAdjuster.canvas.draw = MagicMock(return_value=None)

        thresholdAdjuster.lowerDotThresholdScaleDown()

        # Expected offsets = [[0, 0], [6, 5], [11, 9]]
        dotOffsets = thresholdAdjuster.dotScatter.get_offsets()

        self.assertEqual(microscopeImage.thresholds, (1.1, 1.8, 1.3))
        self.assertEqual(len(dotOffsets), 3)
        self.assertIn([0, 0], dotOffsets)
        self.assertIn([6, 5], dotOffsets)
        self.assertIn([11, 9], dotOffsets)

        thresholdAdjuster.lowerDotThresholdScaleUp()

        # Expected offsets = [[6, 5], [11, 9]]
        dotOffsets2 = thresholdAdjuster.dotScatter.get_offsets()

        self.assertEqual(microscopeImage.thresholds, (1.2, 1.8, 1.3))
        self.assertEqual(len(dotOffsets2), 2)
        self.assertIn([6, 5], dotOffsets2)
        self.assertIn([11, 9], dotOffsets2)


if __name__ == '__main__':
    unittest.main()
