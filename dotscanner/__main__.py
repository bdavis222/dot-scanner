import settings.configmanagement as cm
cm.runChecks()
import dotscanner.density as density
import dotscanner.files as files
import dotscanner.lifetime as lifetime
import dotscanner.strings as strings
from dotscanner.strings import ProgramType
from dotscanner.ui.MicroscopeImage import MicroscopeImage
from dotscanner.ui.RegionSelector import RegionSelector
from dotscanner.ui.ThresholdAdjuster import ThresholdAdjuster
from dotscanner.ui.UserSettings import UserSettings
import settings.config as cfg

def main():	
	while True:
		userSettings = UserSettings()
		directory, filenames = files.getDirectoryAndFilenames(userSettings)
		if userSettings.program == ProgramType.DENSITY:
			getDensityData(directory, filenames, userSettings)
		elif userSettings.program == ProgramType.LIFETIME:
			getLifetimeData(directory, filenames, userSettings)
		else:
			raise Exception(strings.programNameException)
	
def getDensityData(directory, filenames, userSettings):
	if userSettings.reanalysis:
		reanalyzeDensityData(directory, userSettings)
		return
	
	density.checkUnitsConsistent(directory)
	alreadyMeasured = density.getAlreadyMeasured(directory)
	for filename in filenames:
		if filename in alreadyMeasured:
			print(strings.alreadyMeasuredNotification(filename))
			continue
		
		print(f"\n----------\nDisplaying {filename}\n----------")
		microscopeImage = MicroscopeImage(directory, filename, userSettings)
		
		thresholdAdjuster = ThresholdAdjuster(microscopeImage, userSettings)
		if microscopeImage.skipped:
			
			density.skipFile(directory, filename, thresholdAdjuster.userSettings, microscopeImage)
			continue
		
		RegionSelector(microscopeImage, thresholdAdjuster.userSettings)
		if microscopeImage.skipped:
			density.skipFile(directory, filename, thresholdAdjuster.userSettings, microscopeImage)
			continue
		
		density.measureDensity(directory, filename, microscopeImage, userSettings)

def reanalyzeDensityData(directory, userSettings):
	targetPath = files.getReanalysisTargetPath(directory, cfg.DENSITY_OUTPUT_FILENAME)
	adjustmentsMade = False
	for filename, data in userSettings.densityData.items():
		microscopeImage = MicroscopeImage(directory, filename, userSettings)
		setDensityDataValues(userSettings, microscopeImage, data)
		
		if not adjustmentsMade:
			thresholdAdjuster = ThresholdAdjuster(microscopeImage, userSettings)
			userSettings = thresholdAdjuster.userSettings
			adjustmentsMade = not microscopeImage.skipped
		
		density.measureDensity(directory, filename, targetPath, microscopeImage, userSettings)

def setDensityDataValues(userSettings, microscopeImage, data):
	userSettings.lowerDotThreshScale = data[0]
	userSettings.upperDotThreshScale = data[1]
	userSettings.lowerBlobThreshScale = data[2]
	userSettings.thresholds = (data[0], data[1], data[2])
	userSettings.blobSize = data[3]
	userSettings.dotSize = data[4]
	microscopeImage.blobSize = userSettings.blobSize
	microscopeImage.dotSize = userSettings.dotSize
	userSettings.lowerContrast = data[5]
	userSettings.upperContrast = data[6]
	microscopeImage.polygon = data[7]

def getLifetimeData(directory, filenames, userSettings):
	lifetime.checkEnoughFramesForLifetimes(filenames, userSettings)
	
	middleIndex = len(filenames) // 2
	middleMicroscopeImage = MicroscopeImage(directory, filenames[middleIndex], userSettings)
	
	thresholdAdjuster = ThresholdAdjuster(middleMicroscopeImage, userSettings, skipButton=False)
	RegionSelector(middleMicroscopeImage, thresholdAdjuster.userSettings, skipButton=False)
	
	lifetime.measureLifetime(directory, filenames, middleMicroscopeImage, 
		thresholdAdjuster.userSettings)

if __name__ == '__main__':
	main()
