class FakeUserSettings:
    def __init__(self, filepath="test/directory/", dotSize=2, blobSize=5, saveFigures=False,
                 startImage="", skipsAllowed=0, removeEdgeFrames=True, lowerContrast=0.0,
                 upperContrast=5.0, lowerDotThresh=1.5, upperDotThresh=5.0, lowerBlobThresh=2.0,
                 program="density", polygon=None, densityData={}, reanalysis=False):
        self.filepath = filepath
        self.dotSize = dotSize
        self.blobSize = blobSize
        self.saveFigures = saveFigures
        self.startImage = startImage
        self.skipsAllowed = skipsAllowed
        self.removeEdgeFrames = removeEdgeFrames
        self.lowerContrast = lowerContrast
        self.upperContrast = upperContrast
        self.lowerDotThresh = lowerDotThresh
        self.upperDotThresh = upperDotThresh
        self.lowerBlobThresh = lowerBlobThresh
        self.thresholds = (lowerDotThresh, upperDotThresh, lowerBlobThresh)
        self.program = program
        self.polygon = polygon
        self.densityData = densityData
        self.reanalysis = reanalysis
