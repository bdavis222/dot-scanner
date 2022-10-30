import dotscanner.dataprocessing as dp
import dotscanner.strings as strings
import dotscanner.ui.window as ui
import settings.config as cfg

class MicroscopeImage:
	def __init__(self, directory, filename, userSettings):
		self.memoizedCoords = {}
		self.polygon = [] # Vertices of the region selected for analysis (mutated by other classes)
		self.skipped = False # Whether the image should be skipped (mutated by other classes)
		
		self.dotSize = userSettings.dotSize
		self.blobSize = userSettings.blobSize
		self.saveFigures = userSettings.saveFigures
		self.startImage = userSettings.startImage
		self.skipsAllowed = userSettings.skipsAllowed
		self.removeEdgeFrames = userSettings.removeEdgeFrames
		
		self.thresholds = userSettings.thresholds
		self.lowerDotThreshScale = self.thresholds[0]
		self.upperDotThreshScale = self.thresholds[1]
		self.lowerBlobThreshScale = self.thresholds[2]
		
		self.data = dp.getData(directory, filename)
		self.sums = dp.getFullDataSquareSum(self.data)
		self.dotCoords, self.blobCoords = self.getCoords()
		
	def decreaseLowerDotThreshScale(self):
		value = self.lowerDotThreshScale - cfg.THRESHOLD_DELTA
		value = round(value, 1)
		self.lowerDotThreshScale = value
		self.updateThresholds()
		self.dotCoords, self.blobCoords = self.getCoords()
	
	def decreaseUpperDotThreshScale(self):
		value = self.upperDotThreshScale - cfg.THRESHOLD_DELTA
		value = round(value, 1)
		if value < self.lowerDotThreshScale:
			print(strings.upperDotThreshScaleWarning)
			return
		self.upperDotThreshScale = value
		self.updateThresholds()
		self.dotCoords, self.blobCoords = self.getCoords()
	
	def getCoords(self):
		if self.thresholds in self.memoizedCoords:
			dotCoords, blobCoords = self.memoizedCoords[self.thresholds]
		else:
			dotCoords, blobCoords = dp.getCoords(self.data, self.sums, self.thresholds, 
													self.dotSize)
			dp.cleanDotCoords(self.data, dotCoords, blobCoords, self.blobSize, self.dotSize)
			self.memoizedCoords[self.thresholds] = (dotCoords, blobCoords)
		return dotCoords, blobCoords
	
	def increaseLowerDotThreshScale(self):
		value = self.lowerDotThreshScale + cfg.THRESHOLD_DELTA
		value = round(value, 1)
		if value > self.upperDotThreshScale:
			print(strings.upperDotThreshScaleWarning)
			return
		self.lowerDotThreshScale = value
		self.updateThresholds()
		self.dotCoords, self.blobCoords = self.getCoords()
	
	def increaseUpperDotThreshScale(self):
		value = self.upperDotThreshScale + cfg.THRESHOLD_DELTA
		value = round(value, 1)
		self.upperDotThreshScale = value
		self.updateThresholds()
		self.dotCoords, self.blobCoords = self.getCoords()
	
	def setThresholds(self, newThresholds):
		newLowerDotThreshScale = round(newThresholds[0], 1)
		newUpperDotThreshScale = round(newThresholds[1], 1)
		newLowerBlobThreshScale = round(newThresholds[2], 1)
		
		if newUpperDotThreshScale < newLowerDotThreshScale:
			print(strings.upperDotThreshScaleWarning)
			return
		
		if newLowerBlobThreshScale < 1:
			print(strings.lowerBlobThreshScaleWarning)
			newLowerBlobThreshScale = 1.0
		
		self.lowerDotThreshScale = newLowerDotThreshScale
		self.upperDotThreshScale = newUpperDotThreshScale
		self.lowerBlobThreshScale = newLowerBlobThreshScale
		
		self.updateThresholds()
	
	def updateThresholds(self):
		self.thresholds = (self.lowerDotThreshScale, self.upperDotThreshScale, 
							self.lowerBlobThreshScale)
