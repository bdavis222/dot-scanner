import dotscanner.files as files
import unittest

class TestFiles(unittest.TestCase):
    def test_fixDirectory(self):
        string = "test"
        self.assertTrue(files.fixDirectory(string).endswith("/"))
    
    def test_getTrailingNumber(self):
        self.assertEqual(files.getTrailingNumber("test123.file"), 123)
        self.assertEqual(files.getTrailingNumber("test123gjw.file"), 123)
        self.assertEqual(files.getTrailingNumber("test123lj010.file"), 10)

if __name__ == '__main__':
    unittest.main()
