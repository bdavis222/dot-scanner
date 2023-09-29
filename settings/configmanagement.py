import matplotlib.colors as colors
import traceback

from dotscanner import strings
from dotscanner.ui.DialogWindow import DialogWindow


def runChecks():
    try:
        scanConfigFileForErrors()
    except Exception as exception:
        print("\n", traceback.format_exc())
        showStartupErrorDialog()
        quit()


def scanConfigFileForErrors():
    import settings.config as cfg

    matplotlibColors = set(colors.BASE_COLORS.keys())
    for color in colors.TABLEAU_COLORS.keys():
        matplotlibColors.add(color)
    for color in colors.CSS4_COLORS.keys():
        matplotlibColors.add(color)

    assert type(cfg.FILEPATH) == str
    assert cfg.PROGRAM in ["density", "lifetime"]
    assert cfg.SCALE is None or type(cfg.SCALE) in [int, float]

    assert type(cfg.LOWER_DOT_THRESH_SCALE) in [int, float]
    assert type(cfg.UPPER_DOT_THRESH_SCALE) in [int, float]
    assert cfg.LOWER_DOT_THRESH_SCALE <= cfg.UPPER_DOT_THRESH_SCALE
    assert type(cfg.LOWER_BLOB_THRESH_SCALE) in [int, float]
    assert cfg.LOWER_BLOB_THRESH_SCALE >= 1
    assert type(cfg.THRESHOLD_DELTA) in [int, float]

    assert type(cfg.LOWER_CONTRAST) in [int, float]
    assert type(cfg.UPPER_CONTRAST) in [int, float]
    assert cfg.LOWER_CONTRAST < cfg.UPPER_CONTRAST
    assert type(cfg.CONTRAST_DELTA) in [int, float]

    assert type(cfg.SKIPS_ALLOWED) == int
    assert cfg.SKIPS_ALLOWED >= 0
    assert type(cfg.REMOVE_EDGE_FRAMES) == bool
    assert type(cfg.LIFETIME_MIN_FOR_PLOT) == int
    assert type(cfg.NOISE_STATISTIC) in [int, float]

    assert type(cfg.DOT_SIZE) == int
    assert cfg.DOT_COLOR in matplotlibColors
    assert type(cfg.DOT_THICKNESS) in [int, float]

    assert type(cfg.BLOB_SIZE) == int
    assert type(cfg.PLOT_BLOBS) == bool
    assert cfg.BLOB_COLOR in matplotlibColors
    assert type(cfg.BLOB_THICKNESS) in [int, float]

    assert type(cfg.PLOT_POLYGON) == bool
    assert cfg.POLYGON_COLOR in matplotlibColors
    assert type(cfg.POLYGON_THICKNESS) in [int, float]

    assert type(cfg.DYNAMIC_WINDOW) == bool
    assert type(cfg.WINDOW_HEIGHT) in [int, float]
    assert type(cfg.WINDOW_WIDTH) in [int, float]
    assert type(cfg.WINDOW_X) in [int, float]
    assert type(cfg.WINDOW_Y) in [int, float]

    assert type(cfg.SAVE_FIGURES) == bool
    assert type(cfg.DENSITY_OUTPUT_FILENAME) == str
    assert type(cfg.LIFETIME_OUTPUT_FILENAME) == str
    assert type(cfg.FIGURE_DIRECTORY_NAME) == str
    assert type(cfg.FIGURE_FILETYPES) == list
    assert type(cfg.FIGURE_FILETYPES[0]) == str
    assert type(cfg.FIGURE_RESOLUTION) in [int, float]

    supportedPlotOutputTypes = {"eps", "tif", "ps", "tiff", "rgba",
                                "svg", "png", "jpg", "raw", "pdf", "svgz", "pgf", "jpeg"}
    for fileExtension in cfg.FIGURE_FILETYPES:
        assert fileExtension in supportedPlotOutputTypes


def showEditConfigFileDialog():
    DialogWindow(
        title="Edit config file?",
        message="\
Are you sure you want to edit this file? \n\
Dot scanner will close during editing. \n\
The edited file must be saved to retain any changes.",
        positiveButtonText="Edit file",
        negativeButtonText="Cancel",
        positiveButtonAction=editConfigFile,
        windowWidth=400
    )


def showResetConfigFileDialog():
    DialogWindow(
        title="Reset config file?",
        message="\
Are you sure you want to reset this file? \n\
Doing so will close Dot Scanner and restore the default values.",
        positiveButtonText="Reset file",
        negativeButtonText="Cancel",
        positiveButtonAction=resetConfigFile,
        windowWidth=420,
        windowHeight=125
    )


def showStartupErrorDialog():
    DialogWindow(
        title="Config file error",
        message="\
Errors found in config file. \n\
Fix the errors manually or reset the file.\n\
See terminal output for details.",
        positiveButtonText="Reset",
        negativeButtonText="Edit",
        positiveButtonAction=showResetConfigFileDialog,
        negativeButtonAction=showEditConfigFileDialog,
        windowWidth=400,
        windowX=10,
        windowY=30
    )


def getConfigFilePath():
    pathArray = __file__.split("/")
    completePathArray = []
    for directory in pathArray[:-2]:
        completePathArray.append(directory)
        completePathArray.append("/")
    completePathArray.append("settings")
    completePathArray.append("/")
    completePathArray.append("config.py")
    return "".join(completePathArray)


def editConfigFile():
    import os
    import subprocess

    configFilePath = getConfigFilePath()

    if os.name == 'nt':  # Windows operating system
        commandArray = ["Notepad", configFilePath]
    else:
        commandArray = ["open", "-a", "TextEdit", configFilePath]

    subprocess.call(commandArray)

    quit()


def resetConfigFile():
    configFilePath = getConfigFilePath()

    with open(configFilePath, "w") as file:
        file.write(strings.DEFAULT_CONFIG_FILE_CONTENTS)

    quit()
