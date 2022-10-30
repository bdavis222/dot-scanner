from dotscanner.ui.MicroscopeImage import MicroscopeImage
from tests.FakeUserSettings import FakeUserSettings
import mock
import numpy as np
import unittest

class TestMicroscopeImage(unittest.TestCase):
	@mock.patch("dotscanner.dataprocessing.getData")
	def getMicroscopeImage(self, mock_getData):
		mock_getData.return_value = np.array([
			[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 5, 8, 0, 0, 1, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 10, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 7, 0, 0, 0, 0, 1],
			[0, 0, 0, 0, 0, 0, 0, 0, 0]
		])
		fakeUserSettings = FakeUserSettings(
							dotSize=2,
							blobSize=5,
							saveFigures=False,
							startImage="fakeImage01.png",
							skipsAllowed=3,
							removeEdgeFrames=True,
							thresholds=(1.5, 5.0, 2.0))
		return MicroscopeImage("test/directory/", "filename.png", fakeUserSettings)
	
	def test_properLoading_whenClassInitializes(self):
		microscopeImage = self.getMicroscopeImage()
		
		self.assertEqual(microscopeImage.dotSize, 2)
		self.assertEqual(microscopeImage.blobSize, 5)
		self.assertEqual(microscopeImage.saveFigures, False)
		self.assertEqual(microscopeImage.startImage, "fakeImage01.png")
		self.assertEqual(microscopeImage.skipsAllowed, 3)
		self.assertEqual(microscopeImage.removeEdgeFrames, True)
		self.assertEqual(microscopeImage.thresholds, (1.5, 5.0, 2.0))
		self.assertIn(3, microscopeImage.dotCoords)
		self.assertIn(1, microscopeImage.dotCoords[3])
		self.assertEqual(microscopeImage.blobCoords, {})
	
	@mock.patch('settings.config.THRESHOLD_DELTA', 0.1)
	@mock.patch('settings.config.LOWER_DOT_THRESH_SCALE', 1.5)
	def test_decreaseLowerDotThreshScale(self):
		microscopeImage = self.getMicroscopeImage()
		
		microscopeImage.decreaseLowerDotThreshScale()
		
		self.assertEqual(microscopeImage.lowerDotThreshScale, 1.4)
		
		microscopeImage.decreaseLowerDotThreshScale()
		
		self.assertEqual(microscopeImage.lowerDotThreshScale, 1.3)
	
	@mock.patch('settings.config.THRESHOLD_DELTA', 0.1)
	@mock.patch('settings.config.LOWER_DOT_THRESH_SCALE', 1.5)
	def test_increaseLowerDotThreshScale(self):
		microscopeImage = self.getMicroscopeImage()
		
		microscopeImage.increaseLowerDotThreshScale()
		
		self.assertEqual(microscopeImage.lowerDotThreshScale, 1.6)
		
		microscopeImage.increaseLowerDotThreshScale()
		
		self.assertEqual(microscopeImage.lowerDotThreshScale, 1.7)
	
	@mock.patch('settings.config.THRESHOLD_DELTA', 0.1)
	@mock.patch('settings.config.UPPER_DOT_THRESH_SCALE', 5.0)
	def test_decreaseUpperDotThreshScale(self):
		microscopeImage = self.getMicroscopeImage()
		
		microscopeImage.decreaseUpperDotThreshScale()
		
		self.assertEqual(microscopeImage.upperDotThreshScale, 4.9)
		
		microscopeImage.decreaseUpperDotThreshScale()
		
		self.assertEqual(microscopeImage.upperDotThreshScale, 4.8)
	
	@mock.patch('settings.config.THRESHOLD_DELTA', 0.1)
	@mock.patch('settings.config.UPPER_DOT_THRESH_SCALE', 5.0)
	def test_increaseUpperDotThreshScale(self):
		microscopeImage = self.getMicroscopeImage()
		
		microscopeImage.increaseUpperDotThreshScale()
		
		self.assertEqual(microscopeImage.upperDotThreshScale, 5.1)
		
		microscopeImage.increaseUpperDotThreshScale()
		
		self.assertEqual(microscopeImage.upperDotThreshScale, 5.2)
	
	def test_setThresholds(self):
		microscopeImage = self.getMicroscopeImage()
		
		microscopeImage.setThresholds((1.26, 5.2, 3))
		
		self.assertEqual(microscopeImage.thresholds, (1.3, 5.2, 3.0))
	
	def test_updateThresholds(self):
		microscopeImage = self.getMicroscopeImage()
		
		microscopeImage.lowerDotThreshScale = 1.2
		microscopeImage.lowerBlobThreshScale = 2.2
		microscopeImage.updateThresholds()
		
		self.assertEqual(microscopeImage.thresholds, (1.2, 5.0, 2.2))

if __name__ == '__main__':
	unittest.main()
