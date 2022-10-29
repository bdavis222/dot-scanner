import dotscanner.files as files
from tests.FakeUserSettings import FakeUserSettings
import mock
import unittest

class TestFiles(unittest.TestCase):
    def getTestFilenames(self):
        return ["file03.png", "file02.png", "file01.png", "file05.PNG", "file04.png", "file11.png", 
                "readme.md", "test", "directory2/"]
    
    def test_fixDirectory(self):
        string = "test"
        
        self.assertEqual(files.fixDirectory(string), "test/")
        
        string2 = "testString/"
        
        self.assertEqual(files.fixDirectory(string2), "testString/")
    
    def test_getTrailingNumber(self):
        self.assertEqual(files.getTrailingNumber("test123.file"), 123)
        self.assertEqual(files.getTrailingNumber("test123gjw.file"), 123)
        self.assertEqual(files.getTrailingNumber("test123lj010.file"), 10)
    
    @mock.patch("dotscanner.files.os.listdir")
    def test_getMostCommonFileExtension(self, mock_listdir):
        mock_listdir.return_value = self.getTestFilenames()
        
        extension = files.getMostCommonFileExtension("test/directory/")
        
        self.assertEqual(extension, ".png")
    
    @mock.patch("dotscanner.files.os.listdir")
    def test_getFilenamesWithExtension(self, mock_listdir):
        mock_listdir.return_value = self.getTestFilenames()
        
        unsortedFilenames = files.getFilenamesWithExtension("test/directory/", ".png")
        
        self.assertIn("file03.png", unsortedFilenames)
        self.assertIn("file02.png", unsortedFilenames)
        self.assertIn("file01.png", unsortedFilenames)
        self.assertIn("file05.PNG", unsortedFilenames)
        self.assertIn("file04.png", unsortedFilenames)
        self.assertIn("file11.png", unsortedFilenames)
        self.assertNotIn("readme.md", unsortedFilenames)
        self.assertNotIn("test", unsortedFilenames)
        self.assertNotIn("directory2/", unsortedFilenames)
        
        unsortedFilenames2 = files.getFilenamesWithExtension("test/directory/", ".md")
        
        self.assertIn("readme.md", unsortedFilenames2)
        self.assertNotIn("file02.png", unsortedFilenames2)
        self.assertNotIn("file01.png", unsortedFilenames2)
        self.assertNotIn("file05.PNG", unsortedFilenames2)
        self.assertNotIn("file04.png", unsortedFilenames2)
        self.assertNotIn("file11.png", unsortedFilenames2)
        self.assertNotIn("file03.png", unsortedFilenames2)
        self.assertNotIn("test", unsortedFilenames2)
        self.assertNotIn("directory2/", unsortedFilenames2)
    
    @mock.patch("dotscanner.files.os.listdir")
    def test_getSortedFilenames(self, mock_listdir):
        mock_listdir.return_value = self.getTestFilenames()
        
        sortedFilenames = files.getSortedFilenames("test/directory/", startImage="file01.png")
        
        self.assertEqual(
            sortedFilenames, 
            ["file01.png", "file02.png", "file03.png", "file04.png", "file05.PNG", "file11.png"]
        )
        
        sortedFilenames = files.getSortedFilenames("test/directory/", startImage="file04.png")
        
        self.assertEqual(
            sortedFilenames, 
            ["file04.png", "file05.PNG", "file11.png"]
        )
    
    @mock.patch("dotscanner.files.os.path.basename")
    @mock.patch("dotscanner.files.os.path.dirname")
    @mock.patch("dotscanner.files.os.path.isfile")
    def test_getDirectoryAndFilenames_forFile(self, mock_isfile, mock_dirname, mock_basename):
        fakeUserSettings = FakeUserSettings()
        mock_isfile.return_value = True
        mock_dirname.return_value = "test/directory/"
        mock_basename.return_value = "testFile.png"
        
        directory, filenames = files.getDirectoryAndFilenames(fakeUserSettings)
        
        self.assertEqual(directory, "test/directory/")
        self.assertEqual(filenames, ["testFile.png"])
    
    @mock.patch("dotscanner.files.os.listdir")
    @mock.patch("dotscanner.files.os.path.isdir")
    @mock.patch("dotscanner.files.os.path.isfile")
    def test_getDirectoryAndFilenames_forDirectory(self, mock_isfile, mock_isdir, mock_listdir):
        fakeUserSettings = FakeUserSettings()
        mock_isfile.return_value = False
        mock_isdir.return_value = True
        mock_listdir.return_value = self.getTestFilenames()
        
        directory, filenames = files.getDirectoryAndFilenames(fakeUserSettings)
        
        self.assertEqual(directory, fakeUserSettings.filepath)
        self.assertEqual(
            filenames, 
            ["file01.png", "file02.png", "file03.png", "file04.png", "file05.PNG", "file11.png"]
        )

if __name__ == '__main__':
    unittest.main()
