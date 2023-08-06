import mock
import numpy as np
import unittest

from dotscanner.ui.MicroscopeImage import MicroscopeImage
from tests.ui.FakeUserSettings import FakeUserSettings


class TestMicroscopeImage(unittest.TestCase):
    @mock.patch("dotscanner.dataprocessing.getData")
    def getMicroscopeImageAndUserSettings(self, mock_getData):
        mock_getData.return_value = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 5, 8, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 10, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 7, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ])
        userSettings = FakeUserSettings(
            filepath="test/directory/", dotSize=2, blobSize=5, saveFigures=False,
            startImage="fakeImage01.png", skipsAllowed=3, removeEdgeFrames=True, lowerContrast=0.0,
            upperContrast=5.0, lowerDotThresh=1.5, upperDotThresh=5.0, lowerBlobThresh=2.0,
            program="density", polygon=None)

        return MicroscopeImage("test/directory/", "filename.png", userSettings), userSettings

    def test_properLoading_whenClassInitializes(self):
        microscopeImage, userSettings = self.getMicroscopeImageAndUserSettings()

        self.assertEqual(userSettings.dotSize, 2)
        self.assertEqual(userSettings.blobSize, 5)
        self.assertEqual(userSettings.saveFigures, False)
        self.assertEqual(userSettings.startImage, "fakeImage01.png")
        self.assertEqual(userSettings.skipsAllowed, 3)
        self.assertEqual(userSettings.removeEdgeFrames, True)
        self.assertEqual(microscopeImage.thresholds, (1.5, 5.0, 2.0))
        self.assertIn(3, microscopeImage.dotCoords)
        self.assertIn(1, microscopeImage.dotCoords[3])
        self.assertEqual(microscopeImage.blobCoords, {})

    @mock.patch('settings.config.THRESHOLD_DELTA', 0.1)
    @mock.patch('settings.config.LOWER_DOT_THRESH_SCALE', 1.5)
    def test_decreaseLowerDotThreshScale(self):
        microscopeImage, _ = self.getMicroscopeImageAndUserSettings()

        microscopeImage.decreaseLowerDotThreshScale()

        self.assertEqual(microscopeImage.lowerDotThreshScale, 1.4)

        microscopeImage.decreaseLowerDotThreshScale()

        self.assertEqual(microscopeImage.lowerDotThreshScale, 1.3)

    @mock.patch('settings.config.THRESHOLD_DELTA', 0.1)
    @mock.patch('settings.config.LOWER_DOT_THRESH_SCALE', 1.5)
    def test_increaseLowerDotThreshScale(self):
        microscopeImage, _ = self.getMicroscopeImageAndUserSettings()

        microscopeImage.increaseLowerDotThreshScale()

        self.assertEqual(microscopeImage.lowerDotThreshScale, 1.6)

        microscopeImage.increaseLowerDotThreshScale()

        self.assertEqual(microscopeImage.lowerDotThreshScale, 1.7)

    @mock.patch('settings.config.THRESHOLD_DELTA', 0.1)
    @mock.patch('settings.config.UPPER_DOT_THRESH_SCALE', 5.0)
    def test_decreaseUpperDotThreshScale(self):
        microscopeImage, _ = self.getMicroscopeImageAndUserSettings()

        microscopeImage.decreaseUpperDotThreshScale()

        self.assertEqual(microscopeImage.upperDotThreshScale, 4.9)

        microscopeImage.decreaseUpperDotThreshScale()

        self.assertEqual(microscopeImage.upperDotThreshScale, 4.8)

    @mock.patch('settings.config.THRESHOLD_DELTA', 0.1)
    @mock.patch('settings.config.UPPER_DOT_THRESH_SCALE', 5.0)
    def test_increaseUpperDotThreshScale(self):
        microscopeImage, _ = self.getMicroscopeImageAndUserSettings()

        microscopeImage.increaseUpperDotThreshScale()

        self.assertEqual(microscopeImage.upperDotThreshScale, 5.1)

        microscopeImage.increaseUpperDotThreshScale()

        self.assertEqual(microscopeImage.upperDotThreshScale, 5.2)

    def test_setThresholds(self):
        microscopeImage, _ = self.getMicroscopeImageAndUserSettings()

        microscopeImage.setThresholds((1.26, 5.2, 3))

        self.assertEqual(microscopeImage.thresholds, (1.3, 5.2, 3.0))

    def test_updateThresholds(self):
        microscopeImage, _ = self.getMicroscopeImageAndUserSettings()

        microscopeImage.lowerDotThreshScale = 1.2
        microscopeImage.lowerBlobThreshScale = 2.2
        microscopeImage.updateThresholds()

        self.assertEqual(microscopeImage.thresholds, (1.2, 5.0, 2.2))


if __name__ == '__main__':
    unittest.main()
