import dotscanner.lifetime as lifetime
import unittest

class UserSettingsMock:
    def __init__(self, skipsAllowed):
        self.skipsAllowed = skipsAllowed

class TestLifetime(unittest.TestCase):
    def test_checkEnoughFramesForLifetimes(self):
        filenames = ["file1.tif", "file2.tif", "file3.tif", "file4.tif", "file5.tif"]
        userSettings = UserSettingsMock(skipsAllowed=2)
        with self.assertRaises(Exception):
            lifetime.checkEnoughFramesForLifetimes(filenames, userSettings)
    
    def test_getEdgeFrameNumbers(self):
        testImageNumberToCoordMap = {
            0: {11: {2, 3, 4}, 21: {5, 6, 7}},
            1: {11: {2, 7, 4}, 21: {5, 6, 8}},
            2: {11: {2, 0, 4}, 21: {5, 2, 7}},
            3: {11: {3}, 21: {7}},
            4: {11: {2, 3, 4}, 21: {5, 6, 7}},
            5: {11: {2, 7, 4}, 21: {5, 6, 8}},
            6: {11: {2, 0, 4}, 21: {5, 2, 7}},
            7: {11: {3}, 21: {7}}
        }
        edgeFrameNumbers = lifetime.getEdgeFrameNumbers(testImageNumberToCoordMap, 0)
        self.assertIn(0, edgeFrameNumbers)
        self.assertIn(7, edgeFrameNumbers)
        self.assertNotIn(1, edgeFrameNumbers)
        self.assertNotIn(2, edgeFrameNumbers)
        self.assertNotIn(3, edgeFrameNumbers)
        self.assertNotIn(4, edgeFrameNumbers)
        self.assertNotIn(5, edgeFrameNumbers)
        self.assertNotIn(6, edgeFrameNumbers)
        
        edgeFrameNumbers = lifetime.getEdgeFrameNumbers(testImageNumberToCoordMap, 2)
        self.assertIn(0, edgeFrameNumbers)
        self.assertIn(1, edgeFrameNumbers)
        self.assertIn(2, edgeFrameNumbers)
        self.assertIn(5, edgeFrameNumbers)
        self.assertIn(6, edgeFrameNumbers)
        self.assertIn(7, edgeFrameNumbers)
        self.assertNotIn(3, edgeFrameNumbers)
        self.assertNotIn(4, edgeFrameNumbers)

if __name__ == '__main__':
    unittest.main()
