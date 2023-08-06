import dotscanner.density as density
import dotscanner.files as files
import dotscanner.lifetime as lifetime
from dotscanner.programtype import ProgramType
import dotscanner.strings as strings
from dotscanner.ui.UserSettings import UserSettings
from dotscanner.ui.ThresholdAdjuster import ThresholdAdjuster
from dotscanner.ui.RegionSelector import RegionSelector
from dotscanner.ui.MicroscopeImage import MicroscopeImage
import settings.config as cfg
import settings.configmanagement as cm

cm.runChecks()


def main():
    while True:
        userSettings = UserSettings()
        directory, filenames = files.getDirectoryAndFilenames(userSettings)
        if userSettings.program == ProgramType.DENSITY:
            getDensityData(directory, filenames, userSettings)
        elif userSettings.program == ProgramType.LIFETIME:
            getLifetimeData(directory, filenames, userSettings)
        else:
            raise Exception(strings.PROGRAM_NAME_EXCEPTION)


def getDensityData(directory, filenames, userSettings):
    if userSettings.reanalysis:
        if len(filenames) == 1:
            density.reanalyzeSingleDensityFile(
                directory, filenames[0], userSettings
            )
        else:
            density.reanalyzeDensityData(directory, userSettings)
        return

    density.checkUnitsConsistent(directory)
    alreadyMeasured = density.getAlreadyMeasured(directory)
    targetPath = files.getAnalysisTargetPath(
        directory, cfg.DENSITY_OUTPUT_FILENAME)
    for filename in filenames:
        if filename in alreadyMeasured:
            print(strings.alreadyMeasuredNotification(filename))
            continue

        print(f"\n----------\nDisplaying {filename}\n----------")
        microscopeImage = MicroscopeImage(directory, filename, userSettings)

        thresholdAdjuster = ThresholdAdjuster(microscopeImage, userSettings)
        # Updating with the threshold adjustments
        userSettings = thresholdAdjuster.userSettings
        if microscopeImage.skipped:
            density.skipFile(directory, filename, targetPath,
                             userSettings, microscopeImage)
            continue

        RegionSelector(microscopeImage, userSettings)
        if microscopeImage.skipped:
            density.skipFile(directory, filename, targetPath,
                             userSettings, microscopeImage)
            continue

        density.measureDensity(directory, filename,
                               targetPath, microscopeImage, userSettings)


def getLifetimeData(directory, filenames, userSettings):
    lifetime.checkEnoughFramesForLifetimes(filenames, userSettings)

    middleIndex = len(filenames) // 2
    middleMicroscopeImage = MicroscopeImage(
        directory, filenames[middleIndex], userSettings)

    thresholdAdjuster = ThresholdAdjuster(
        middleMicroscopeImage, userSettings, skipButton=False)
    # Updating with the threshold adjustments
    userSettings = thresholdAdjuster.userSettings
    RegionSelector(middleMicroscopeImage, userSettings, skipButton=False)

    lifetime.measureLifetime(directory, filenames,
                             middleMicroscopeImage, userSettings)


if __name__ == '__main__':
    main()
