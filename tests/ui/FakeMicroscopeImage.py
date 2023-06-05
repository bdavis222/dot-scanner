class FakeMicroscopeImage:
    def __init__(self, polygon=[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]], 
        thresholds=(1.5, 5.0, 2.0), lowerDotThreshScale=1.5, upperDotThreshScale=5.0, 
        lowerBlobThreshScale=2.0):
        self.polygon = polygon
        self.thresholds = thresholds
        self.lowerDotThreshScale = lowerDotThreshScale
        self.upperDotThreshScale = upperDotThreshScale
        self.lowerBlobThreshScale = lowerBlobThreshScale
