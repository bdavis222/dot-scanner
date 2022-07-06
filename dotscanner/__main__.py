import dotscanner.density as density
import dotscanner.files as files
import dotscanner.lifetime as lifetime
import dotscanner.strings as strings
from dotscanner.ui import MicroscopeImage, RegionSelector, ThresholdAdjuster, UserSettings

def main():
	userSettings = UserSettings()
	if userSettings.completed:		
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
			continue
		
		print(filename)
		microscopeImage = MicroscopeImage(directory, filename, userSettings)
		
		ThresholdAdjuster(microscopeImage, userSettings)
		if microscopeImage.skipped:
			density.skipFile(directory, filename, userSettings)
			continue
		
		RegionSelector(microscopeImage, userSettings)
		if microscopeImage.skipped:
			density.skipFile(directory, filename, userSettings)
			continue
		
		density.measureDensity(directory, filename, microscopeImage, userSettings)

def getLifetimeData(directory, filenames, userSettings):
	lifetime.checkEnoughFramesForLifetimes(filenames, userSettings)
	
	middleIndex = len(filenames) // 2
	middleMicroscopeImage = MicroscopeImage(directory, filenames[middleIndex], userSettings)
	
	ThresholdAdjuster(middleMicroscopeImage, userSettings, skipButton=False)
	if middleMicroscopeImage.skipped:
		quit()
	
	RegionSelector(middleMicroscopeImage, userSettings, skipButton=False)
	if middleMicroscopeImage.skipped:
		quit()
	
	lifetime.measureLifetime(directory, filenames, middleMicroscopeImage, userSettings)

if __name__ == '__main__':
	main()
