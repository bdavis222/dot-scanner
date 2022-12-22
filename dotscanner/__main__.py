import settings.configmanagement as cm
cm.runChecks()
import dotscanner.density as density
import dotscanner.files as files
import dotscanner.lifetime as lifetime
import dotscanner.strings as strings
from dotscanner.ui.MicroscopeImage import MicroscopeImage
from dotscanner.ui.RegionSelector import RegionSelector
from dotscanner.ui.ThresholdAdjuster import ThresholdAdjuster
from dotscanner.ui.UserSettings import UserSettings

def main():	
	while True:
		userSettings = UserSettings()
		directory, filenames = files.getDirectoryAndFilenames(userSettings)
		if userSettings.program == "density":
			getDensityData(directory, filenames, userSettings)
		elif userSettings.program == "lifetime":
			getLifetimeData(directory, filenames, userSettings)
		else:
			raise Exception(strings.programNameException)
	
def getDensityData(directory, filenames, userSettings):
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
			density.skipFile(directory, filename, thresholdAdjuster.userSettings)
			continue
		
		RegionSelector(microscopeImage, thresholdAdjuster.userSettings)
		if microscopeImage.skipped:
			density.skipFile(directory, filename, thresholdAdjuster.userSettings)
			continue
		
		density.measureDensity(directory, filename, microscopeImage, userSettings)

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
