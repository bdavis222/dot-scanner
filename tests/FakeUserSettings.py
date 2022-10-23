class FakeUserSettings:
    def __init__(self, dotSize=2, blobSize=5, skipsAllowed=0, thresholds=(1.5, 5.0, 2.0), 
                    removeEdgeFrames=True):
        self.filepath = "test/directory/"
        self.startImage = ""
        self.dotSize = dotSize
        self.blobSize = blobSize
        self.skipsAllowed = skipsAllowed
        self.thresholds = thresholds
        self.removeEdgeFrames = removeEdgeFrames
