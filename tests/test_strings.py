import dotscanner.strings as strings
import settings.config as cfg
from tests.ui.FakeMicroscopeImage import FakeMicroscopeImage
from tests.ui.FakeUserSettings import FakeUserSettings
import mock
import unittest

class TestStrings(unittest.TestCase):
    @mock.patch("settings.config.DENSITY_OUTPUT_FILENAME", "density.txt")
    def test_alreadyMeasuredNotification(self):
        output = strings.alreadyMeasuredNotification(filename="test.png")
        
        self.assertEqual(
            output, 
            f"\nFile test.png already measured in density.txt file. Skipping."
        )
    
    def test_densityOutput(self):
        polygon = [[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]
        
        output = strings.densityOutput(
            filename="test.png", 
            dotTotal=6,
            surveyedArea=600,
            density=0.01,
            error=0.0001,
            thresholds=(1.5, 5.0, 2.0),
            dotSize=2,
            blobSize=5,
            polygon=[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]
        )
        
        self.assertEqual(
            output,
            "test.png 6 600 0.01 0.0001 1.5 5.0 2.0 5 2 (1, 1), (1, 10), (10, 10), (10, 1)\n"
        )
    
    def test_fileSkippedNotification(self):
        output = strings.fileSkippedNotification("test.png")
        
        self.assertEqual(output, "\nFile test.png skipped")
    
    def test_lifetimeOutputFileHeader(self):
        polygon = [[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]
        thresholds = (1.5, 5.0, 2.0)
        fakeMicroscopeImage = FakeMicroscopeImage(polygon, thresholds)
        fakeUserSettings = FakeUserSettings(
                                dotSize=2, 
                                blobSize=5, 
                                skipsAllowed=1, 
                                thresholds=(1.5, 5.0, 2.0), 
                                removeEdgeFrames=True)
        
        output = strings.lifetimeOutputFileHeader(fakeMicroscopeImage, fakeUserSettings)
        
        self.assertEqual(
            output,
"# Polygon vertices (x, y): (1, 1), (1, 10), (10, 10), (10, 1)\n\
# Threshold scales: 1.5, 5.0, 2.0\n\
# Dot size: 2 | Blob size: 5 | Remove edge frames: True | Skips allowed: 1\n\
#\n\
# x | y | lifetime | starting image\n"
        )

if __name__ == "__main__":
    unittest.main()
