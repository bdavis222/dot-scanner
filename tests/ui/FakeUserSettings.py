class FakeUserSettings:
    def __init__(self, filepath="test/directory/", dotSize=2, blobSize=5, saveFigures=False, 
                    startImage="", skipsAllowed=0, removeEdgeFrames=True, 
                    thresholds=(1.5, 5.0, 2.0)):
        self.filepath = filepath
        self.dotSize = dotSize
        self.blobSize = blobSize
        self.saveFigures = saveFigures
        self.startImage = startImage
        self.skipsAllowed = skipsAllowed
        self.removeEdgeFrames = removeEdgeFrames
        self.thresholds = thresholds
