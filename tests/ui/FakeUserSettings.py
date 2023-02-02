class FakeUserSettings:
    def __init__(self, filepath="test/directory/", dotSize=2, blobSize=5, saveFigures=False, 
        startImage="", skipsAllowed=0, removeEdgeFrames=True, thresholds=(1.5, 5.0, 2.0), 
        lowerContrast=0.0, upperContrast=5.0, lowerDotThresh=1.5, upperDotThresh=5.0, 
        lowerBlobThresh=2.0, program="density"):
        self.filepath = filepath
        self.dotSize = dotSize
        self.blobSize = blobSize
        self.saveFigures = saveFigures
        self.startImage = startImage
        self.skipsAllowed = skipsAllowed
        self.removeEdgeFrames = removeEdgeFrames
        self.thresholds = thresholds
        self.lowerContrast = lowerContrast
        self.upperContrast = upperContrast
        self.lowerDotThresh = lowerDotThresh
        self.upperDotThresh = upperDotThresh
        self.lowerBlobThresh = lowerBlobThresh
        self.program = program