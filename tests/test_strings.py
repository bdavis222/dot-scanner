import mock
import unittest

from dotscanner.programtype import ProgramType
import dotscanner.strings as strings
from tests.ui.FakeMicroscopeImage import FakeMicroscopeImage
from tests.ui.FakeUserSettings import FakeUserSettings


class TestStrings(unittest.TestCase):
    @mock.patch("settings.config.DENSITY_OUTPUT_FILENAME", "density.txt")
    def test_alreadyMeasuredNotification(self):
        output = strings.alreadyMeasuredNotification(filename="test.png")

        self.assertEqual(
            output,
            f"\nFile test.png already measured in density.txt file. Skipping."
        )

    def test_densityOutput(self):
        fakeUserSettings = FakeUserSettings(dotSize=2, blobSize=5)
        fakeMicroscopeImage = FakeMicroscopeImage(
            polygon=[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]], lowerDotThreshScale=1.5,
            upperDotThreshScale=5.0, lowerBlobThreshScale=2.0)
        output = strings.densityOutput(
            filename="test.png",
            dotTotal=6,
            surveyedArea=600,
            density=0.01,
            error=0.0001,
            microscopeImage=fakeMicroscopeImage,
            userSettings=fakeUserSettings
        )

        self.assertEqual(
            output,
            "test.png 6 600 0.01 0.0001 1.5 5.0 2.0 5 2 0.0 5.0 (1, 1), (1, 10), (10, 10), (10, 1)\n"
        )

    def test_fileSkippedNotification(self):
        output = strings.fileSkippedNotification("test.png")

        self.assertEqual(output, "\nFile test.png skipped")

    def test_invalidAnalysisFileWarning(self):
        self.assertEqual(
            strings.invalidAnalysisFileWarning("test_file.png"),
            f'\nInvalid analysis file selected: "test_file.png". A valid file has a .txt extension \
and contains density or lifetime data.'
        )

    def test_invalidFilenameInDensityAnalysisFile(self):
        self.assertEqual(
            strings.invalidFilenameInDensityAnalysisFile(
                ["file", "array", "example"]),
            f"Filename with valid extension not found in the following line in densities file:\n\
file array example"
        )

    def test_outputFileTopHeader(self):
        self.assertEqual(
            strings.outputFileTopHeader(ProgramType.DENSITY),
            f"# Dot Scanner (https://github.com/bdavis222/dotscanner)\n\
# Generated output file for density measurement\n#"
        )
        self.assertEqual(
            strings.outputFileTopHeader(ProgramType.LIFETIME),
            f"# Dot Scanner (https://github.com/bdavis222/dotscanner)\n\
# Generated output file for lifetime measurement\n#"
        )

    def test_lifetimeOutputFileHeader(self):
        fakeMicroscopeImage = FakeMicroscopeImage(
            polygon=[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]], lowerDotThreshScale=1.5,
            upperDotThreshScale=5.0, lowerBlobThreshScale=2.0)
        fakeUserSettings = FakeUserSettings(
            dotSize=2, blobSize=5, skipsAllowed=1, lowerDotThresh=1.5, upperDotThresh=5.0,
            lowerBlobThresh=2.0, removeEdgeFrames=True)

        output = strings.lifetimeOutputFileHeader(
            fakeMicroscopeImage, fakeUserSettings)

        self.assertEqual(
            output,
            "# Dot Scanner (https://github.com/bdavis222/dotscanner)\n\
# Generated output file for lifetime measurement\n\
#\n\
# If this file is selected for re-analysis, the following settings will be read in and used unless \
changed in the threshold adjustment window. The re-analyzed data will then be given in a new \
output file in this same directory.\n\
#\n\
# Polygon vertices (x, y): (1, 1), (1, 10), (10, 10), (10, 1)\n\
# Threshold scales: 1.5, 5.0, 2.0\n\
# Contrast settings: 0.0, 5.0\n\
# Dot size: 2 | Blob size: 5\n\
#\n\
# The following settings were used in this analysis, but will not be read in during re-analysis \
(these and other settings can be adjusted in the config file using the \"Edit defaults\" button \
in the main configuration window):\n\
#\n\
# Remove edge frames: True | Save figures: False | Skips allowed: 1\n\
#\n\
# The data columns are organized as follows:\n\
# x | y | lifetime | starting image | displacement squared (sq px) | potentially unreliable?\n#\n"
        )

    def test_lifetimeOutputFileHeaderWithStartImage(self):
        fakeMicroscopeImage = FakeMicroscopeImage(
            polygon=[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]], lowerDotThreshScale=1.5,
            upperDotThreshScale=5.0, lowerBlobThreshScale=2.0)
        fakeUserSettings = FakeUserSettings(
            dotSize=2, blobSize=5, startImage="path/to/image.png", skipsAllowed=1,
            lowerDotThresh=1.5, upperDotThresh=5.0, lowerBlobThresh=2.0, removeEdgeFrames=True)

        output = strings.lifetimeOutputFileHeader(
            fakeMicroscopeImage, fakeUserSettings)

        self.assertEqual(
            output,
            "# Dot Scanner (https://github.com/bdavis222/dotscanner)\n\
# Generated output file for lifetime measurement\n\
#\n\
# If this file is selected for re-analysis, the following settings will be read in and used unless \
changed in the threshold adjustment window. The re-analyzed data will then be given in a new \
output file in this same directory.\n\
#\n\
# Polygon vertices (x, y): (1, 1), (1, 10), (10, 10), (10, 1)\n\
# Threshold scales: 1.5, 5.0, 2.0\n\
# Contrast settings: 0.0, 5.0\n\
# Dot size: 2 | Blob size: 5\n\
#\n\
# The following settings were used in this analysis, but will not be read in during re-analysis \
(these and other settings can be adjusted in the config file using the \"Edit defaults\" button \
in the main configuration window):\n\
#\n\
# Remove edge frames: True | Save figures: False | \
Skips allowed: 1 | Start image: image.png\n\
#\n\
# The data columns are organized as follows:\n\
# x | y | lifetime | starting image | displacement squared (sq px) | potentially unreliable?\n#\n"
        )


if __name__ == "__main__":
    unittest.main()
