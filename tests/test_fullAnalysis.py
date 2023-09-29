import mock
import os
import unittest
from unittest.mock import MagicMock

import dotscanner.density as density
import dotscanner.files as files
import dotscanner.lifetime as lifetime
from dotscanner.ui.MicroscopeImage import MicroscopeImage
from tests.ui.FakeUserSettings import FakeUserSettings


class TestFullAnalysis(unittest.TestCase):
    def getPathFromBase(self, filename):
        return "/".join(__file__.split("/")[:-2]) + "/" + filename

    def removeFileAndAssertNonexistent(self, filepath):
        if os.path.exists(filepath):
            os.remove(filepath)

        self.assertFalse(os.path.exists(filepath))

    def assertTestDataFilesEquivalent(self, fileOneName, fileTwoName):
        targetPath = self.getPathFromBase(f"tests/data/{fileOneName}")
        expectedTargetPath = self.getPathFromBase(f"tests/data/{fileTwoName}")

        self.assertFilesEquivalent(targetPath, expectedTargetPath)

    def assertFilesEquivalent(self, pathOne, pathTwo):
        self.assertTrue(os.path.exists(pathOne))

        fileOneArray = []
        with open(pathOne, "r") as file:
            for line in file:
                fileOneArray.append(line)

        fileTwoArray = []
        with open(pathTwo, "r") as file:
            for line in file:
                fileTwoArray.append(line)

        for index in range(len(fileOneArray)):
            self.assertEqual(fileOneArray[index], fileTwoArray[index])

    def test_getPathFromBase(self):
        filename1 = self.getPathFromBase("filename1.txt")
        filename2 = self.getPathFromBase("folder/filename2.txt")
        filename3 = self.getPathFromBase("two/folders/filename3.txt")

        self.assertTrue(filename1.endswith("dot-scanner/filename1.txt"))
        self.assertTrue(filename2.endswith("dot-scanner/folder/filename2.txt"))
        self.assertTrue(filename3.endswith(
            "dot-scanner/two/folders/filename3.txt"))

    def test_removeFileAndAssertNonexistent(self):
        # Test first without a real file
        targetPath = self.getPathFromBase("tests/data/fakeData2.txt")

        self.assertFalse(os.path.exists(targetPath))
        self.removeFileAndAssertNonexistent(targetPath)

        # Now create a real file and test
        with open(targetPath, "w") as file:
            file.write("test\ndata\nhere")

        self.assertTrue(os.path.exists(targetPath))
        self.removeFileAndAssertNonexistent(targetPath)

    def test_assertTestDataFilesEquivalent(self):
        targetPath3 = self.getPathFromBase("tests/data/fakeData3.txt")
        targetPath4 = self.getPathFromBase("tests/data/fakeData4.txt")

        with open(targetPath3, "w") as file:
            file.write("test\ndata\nhere")

        with open(targetPath4, "w") as file:
            file.write("test\ndata\nhere")

        self.assertTestDataFilesEquivalent("fakeData3.txt", "fakeData4.txt")
        self.removeFileAndAssertNonexistent(targetPath3)
        self.removeFileAndAssertNonexistent(targetPath4)

    def test_assertFilesEquivalent(self):
        filepath = self.getPathFromBase("tests/data/fakeData.txt")

        self.assertFilesEquivalent(filepath, filepath)

    def test_mainHasNotChanged(self):
        mainPath = self.getPathFromBase("dotscanner/__main__.py")
        mainExpectedPath = self.getPathFromBase("tests/data/mainExpected.txt")

        self.assertFilesEquivalent(mainPath, mainExpectedPath)

    def test_densityAnalysis(self):
        filepath = self.getPathFromBase("images/demo/demo_image1.TIF")
        userSettings = FakeUserSettings(filepath=filepath, dotSize=2, blobSize=5,
                                        saveFigures=False, startImage="", skipsAllowed=0, removeEdgeFrames=True,
                                        lowerContrast=0.0, upperContrast=5.0, lowerDotThresh=1.5, upperDotThresh=5.0,
                                        lowerBlobThresh=2.0, program="density",
                                        polygon=[[469, 62], [413, 15], [299, 166], [362, 212], [469, 62]], densityData={},
                                        reanalysis=False)

        directory, filenames = files.getDirectoryAndFilenames(
            userSettings, testing=True)
        filename = filenames[0]

        targetPath = self.getPathFromBase("tests/data/densityTestOutput.txt")

        self.removeFileAndAssertNonexistent(targetPath)

        microscopeImage = MicroscopeImage(directory, filename, userSettings)
        density.measureDensity(directory, filename,
                               targetPath, microscopeImage, userSettings)

        self.assertTestDataFilesEquivalent(
            "densityTestOutput.txt", "densityExpectedOutput.txt")

    def test_densityAnalysis2(self):
        filepath = self.getPathFromBase("images/demo/demo_image1.TIF")
        userSettings = FakeUserSettings(filepath=filepath, dotSize=3, blobSize=6,
                                        saveFigures=False, startImage="", skipsAllowed=0, removeEdgeFrames=True,
                                        lowerContrast=0.0, upperContrast=5.5, lowerDotThresh=1.8, upperDotThresh=4.8,
                                        lowerBlobThresh=2.0, program="density",
                                        polygon=[[469, 62], [413, 15], [299, 166], [362, 212], [469, 62]], densityData={},
                                        reanalysis=False)

        directory, filenames = files.getDirectoryAndFilenames(
            userSettings, testing=True)
        filename = filenames[0]

        targetPath = self.getPathFromBase("tests/data/densityTestOutput.txt")

        self.removeFileAndAssertNonexistent(targetPath)

        microscopeImage = MicroscopeImage(directory, filename, userSettings)
        density.measureDensity(directory, filename,
                               targetPath, microscopeImage, userSettings)

        self.assertTestDataFilesEquivalent(
            "densityTestOutput.txt", "densityExpectedOutput2.txt")

    @mock.patch("settings.config.NOISE_STATISTIC", 2.5)
    def test_lifetimeAnalysis(self):
        filepath = self.getPathFromBase("images/demo/")
        userSettings = FakeUserSettings(filepath=filepath, dotSize=2, blobSize=5,
                                        saveFigures=False, startImage="", skipsAllowed=1, removeEdgeFrames=True,
                                        lowerContrast=0.0, upperContrast=5.0, lowerDotThresh=1.5, upperDotThresh=5.0,
                                        lowerBlobThresh=2.0, program="density",
                                        polygon=[[469, 58], [420, 14], [303, 161], [361, 205], [469, 58]], densityData={},
                                        reanalysis=False)

        directory, filenames = files.getDirectoryAndFilenames(
            userSettings, testing=True)
        middleIndex = len(filenames) // 2
        middleMicroscopeImage = MicroscopeImage(
            directory, filenames[middleIndex], userSettings)

        targetPath = self.getPathFromBase("tests/data/lifetimeTestOutput.txt")
        files.getAnalysisTargetPath = MagicMock(return_value=targetPath)
        lifetime.saveHistogram = MagicMock(return_value=None)
        lifetime.saveNoiseStatisticHistogram = MagicMock(return_value=None)
        lifetime.measureLifetime(directory, filenames, middleMicroscopeImage, userSettings,
                                 testing=True)

        self.assertTestDataFilesEquivalent(
            "lifetimeTestOutput.txt", "lifetimeExpectedOutput.txt")

    @mock.patch("settings.config.NOISE_STATISTIC", 2.5)
    def test_lifetimeAnalysis2(self):
        filepath = self.getPathFromBase("images/demo/")
        userSettings = FakeUserSettings(filepath=filepath, dotSize=2, blobSize=5,
                                        saveFigures=False, startImage="", skipsAllowed=1, removeEdgeFrames=True,
                                        lowerContrast=0.0, upperContrast=5.5, lowerDotThresh=1.7, upperDotThresh=4.7,
                                        lowerBlobThresh=2.0, program="density",
                                        polygon=[[469, 58], [420, 14], [303, 161], [361, 205], [469, 58]], densityData={},
                                        reanalysis=False)

        directory, filenames = files.getDirectoryAndFilenames(
            userSettings, testing=True)
        middleIndex = len(filenames) // 2
        middleMicroscopeImage = MicroscopeImage(
            directory, filenames[middleIndex], userSettings)

        targetPath = self.getPathFromBase("tests/data/lifetimeTestOutput.txt")
        files.getAnalysisTargetPath = MagicMock(return_value=targetPath)
        lifetime.saveHistogram = MagicMock(return_value=None)
        lifetime.saveNoiseStatisticHistogram = MagicMock(return_value=None)
        lifetime.measureLifetime(directory, filenames, middleMicroscopeImage, userSettings,
                                 testing=True)

        self.assertTestDataFilesEquivalent(
            "lifetimeTestOutput.txt", "lifetimeExpectedOutput2.txt")


if __name__ == '__main__':
    unittest.main()
