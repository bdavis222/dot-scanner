import dotscanner.__main__ as main
import dotscanner.density as density
import dotscanner.files as files
import dotscanner.lifetime as lifetime
from dotscanner.ui.MicroscopeImage import MicroscopeImage
from dotscanner.ui.ThresholdAdjuster import ThresholdAdjuster
from tests.ui.FakeUserSettings import FakeUserSettings
import os
import unittest
from unittest.mock import MagicMock

class TestFullAnalysis(unittest.TestCase):
	def test_densityAnalysis(self):
		filepath = "/".join(__file__.split("/")[:-2]) + "/images/demo/demo_image1.TIF"
		userSettings = FakeUserSettings(filepath=filepath, dotSize=2, blobSize=5, 
			saveFigures=False, startImage="", skipsAllowed=0, removeEdgeFrames=True, 
			lowerContrast=0.0, upperContrast=5.0, lowerDotThresh=1.5, upperDotThresh=5.0, 
			lowerBlobThresh=2.0, program="density", 
			polygon=[[469, 62], [413, 15], [299, 166], [362, 212], [469, 62]], densityData={}, 
			reanalysis=False)
		
		directory, filenames = files.getDirectoryAndFilenames(userSettings)
		filename = filenames[0]
		targetPath = "/".join(__file__.split("/")[:-1]) + "/data/densityTestOutput.txt"
		if os.path.exists(targetPath):
			os.remove(targetPath)
		
		microscopeImage = MicroscopeImage(directory, filename, userSettings)
		density.measureDensity(directory, filename, targetPath, microscopeImage, userSettings)
		
		self.assertTrue(os.path.exists(targetPath))
		
		testFileArray = []
		with open(targetPath, "r") as file:
			for line in file:
				testFileArray.append(line)
		
		expectedTargetPath = "/".join(__file__.split("/")[:-1]) + "/data/densityExpectedOutput.txt"
		expectedFileArray = []
		with open(expectedTargetPath, "r") as file:
			for line in file:
				expectedFileArray.append(line)
		
		for index in range(len(testFileArray)):
			self.assertEqual(testFileArray[index], expectedFileArray[index])
	
	def test_densityAnalysis2(self):
		filepath = "/".join(__file__.split("/")[:-2]) + "/images/demo/demo_image1.TIF"
		userSettings = FakeUserSettings(filepath=filepath, dotSize=3, blobSize=6, 
			saveFigures=False, startImage="", skipsAllowed=0, removeEdgeFrames=True, 
			lowerContrast=0.0, upperContrast=5.5, lowerDotThresh=1.8, upperDotThresh=4.8, 
			lowerBlobThresh=2.0, program="density", 
			polygon=[[469, 62], [413, 15], [299, 166], [362, 212], [469, 62]], densityData={}, 
			reanalysis=False)
		
		directory, filenames = files.getDirectoryAndFilenames(userSettings)
		filename = filenames[0]
		targetPath = "/".join(__file__.split("/")[:-1]) + "/data/densityTestOutput.txt"
		if os.path.exists(targetPath):
			os.remove(targetPath)
		
		microscopeImage = MicroscopeImage(directory, filename, userSettings)
		density.measureDensity(directory, filename, targetPath, microscopeImage, userSettings)
		
		self.assertTrue(os.path.exists(targetPath))
		
		testFileArray = []
		with open(targetPath, "r") as file:
			for line in file:
				testFileArray.append(line)
		
		expectedTargetPath = "/".join(__file__.split("/")[:-1]) + "/data/densityExpectedOutput2.txt"
		expectedFileArray = []
		with open(expectedTargetPath, "r") as file:
			for line in file:
				expectedFileArray.append(line)
		
		for index in range(len(testFileArray)):
			self.assertEqual(testFileArray[index], expectedFileArray[index])
	
	def test_lifetimeAnalysis(self):
		filepath = "/".join(__file__.split("/")[:-2]) + "/images/demo/"
		userSettings = FakeUserSettings(filepath=filepath, dotSize=2, blobSize=5, 
			saveFigures=False, startImage="", skipsAllowed=1, removeEdgeFrames=True, 
			lowerContrast=0.0, upperContrast=5.0, lowerDotThresh=1.5, upperDotThresh=5.0, 
			lowerBlobThresh=2.0, program="density", 
			polygon=[[469, 58], [420, 14], [303, 161], [361, 205], [469, 58]], densityData={}, 
			reanalysis=False)
		
		directory, filenames = files.getDirectoryAndFilenames(userSettings)
		middleIndex = len(filenames) // 2
		middleMicroscopeImage = MicroscopeImage(directory, filenames[middleIndex], userSettings)
		
		targetPath = "/".join(__file__.split("/")[:-1]) + "/data/lifetimeTestOutput.txt"
		files.getAnalysisTargetPath = MagicMock(return_value=targetPath)
		lifetime.saveHistogram = MagicMock(return_value=None)
		lifetime.measureLifetime(directory, filenames, middleMicroscopeImage, userSettings, 
			testing=True)
		
		testFileArray = []
		with open(targetPath, "r") as file:
			for line in file:
				testFileArray.append(line)
		
		expectedTargetPath = "/".join(__file__.split("/")[:-1]) + "/data/lifetimeExpectedOutput.txt"
		expectedFileArray = []
		with open(expectedTargetPath, "r") as file:
			for line in file:
				expectedFileArray.append(line)
		
		for index in range(len(testFileArray)):
			self.assertEqual(testFileArray[index], expectedFileArray[index])
	
	def test_lifetimeAnalysis(self):
		filepath = "/".join(__file__.split("/")[:-2]) + "/images/demo/"
		userSettings = FakeUserSettings(filepath=filepath, dotSize=2, blobSize=5, 
			saveFigures=False, startImage="", skipsAllowed=1, removeEdgeFrames=True, 
			lowerContrast=0.0, upperContrast=5.5, lowerDotThresh=1.7, upperDotThresh=4.7, 
			lowerBlobThresh=2.0, program="density", 
			polygon=[[469, 58], [420, 14], [303, 161], [361, 205], [469, 58]], densityData={}, 
			reanalysis=False)
		
		directory, filenames = files.getDirectoryAndFilenames(userSettings)
		middleIndex = len(filenames) // 2
		middleMicroscopeImage = MicroscopeImage(directory, filenames[middleIndex], userSettings)
		
		targetPath = "/".join(__file__.split("/")[:-1]) + "/data/lifetimeTestOutput.txt"
		files.getAnalysisTargetPath = MagicMock(return_value=targetPath)
		lifetime.saveHistogram = MagicMock(return_value=None)
		lifetime.measureLifetime(directory, filenames, middleMicroscopeImage, userSettings, 
			testing=True)
		
		testFileArray = []
		with open(targetPath, "r") as file:
			for line in file:
				testFileArray.append(line)
		
		expectedTargetPath = "/".join(__file__.split("/")[:-1]) + "/data/lifetimeExpectedOutput2.txt"
		expectedFileArray = []
		with open(expectedTargetPath, "r") as file:
			for line in file:
				expectedFileArray.append(line)
		
		for index in range(len(testFileArray)):
			self.assertEqual(testFileArray[index], expectedFileArray[index])

if __name__ == '__main__':
	unittest.main()
