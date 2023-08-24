import os
import tkinter as tk
from tkinter import filedialog

import dotscanner.files as files
from dotscanner.programtype import ProgramType
import dotscanner.strings as strings
import dotscanner.ui.window as ui
from dotscanner.ui.DefaultUserSettingsEditor import DefaultUserSettingsEditor
import settings.config as cfg

EMPTY_DIRECTORY_SET = set(["", " ", "/"])


class UserSettings:
    def __init__(self):
        self.window = ui.createConfigurationsWindow()

        self.filepath = cfg.FILEPATH
        self.startImage = ""
        self.program = self.getProgramType(cfg.PROGRAM)
        self.blobSize = round(cfg.BLOB_SIZE, 0)
        self.dotSize = round(cfg.DOT_SIZE, 0)
        self.lowerDotThresh = round(cfg.LOWER_DOT_THRESH_SCALE, 1)
        self.upperDotThresh = round(cfg.UPPER_DOT_THRESH_SCALE, 1)
        self.lowerBlobThresh = round(cfg.LOWER_BLOB_THRESH_SCALE, 1)
        self.thresholds = (self.lowerDotThresh,
                           self.upperDotThresh, self.lowerBlobThresh)
        self.lowerContrast = round(cfg.LOWER_CONTRAST, 1)
        self.upperContrast = round(cfg.UPPER_CONTRAST, 1)
        self.saveFigures = cfg.SAVE_FIGURES
        self.removeEdgeFrames = cfg.REMOVE_EDGE_FRAMES
        self.skipsAllowed = round(cfg.SKIPS_ALLOWED, 0)
        self.reanalysis = False
        self.polygon = None
        self.densityData = {}

        self.filepathFrame = tk.Frame(self.window)

        self.labelFilepath = tk.Label(self.window, text="Filepath:")
        self.labelSelectedPath = tk.Label(
            self.window, text="Select a file or folder for analysis", fg="red", bg="white")
        self.showFilepath()

        self.labelFilepath.pack(in_=self.filepathFrame, side=tk.LEFT)
        self.labelSelectedPath.pack(in_=self.filepathFrame, side=tk.LEFT)

        self.navigation = tk.Frame(self.window)

        self.labelBrowse = tk.Label(self.window, text="Browse:")

        self.buttonSelectFile = tk.Button(
            self.window, text="File", command=self.browseFiles)

        self.buttonSelectFolder = tk.Button(
            self.window, text="Folder", command=self.browseFolders)

        self.labelProgram = tk.Label(self.window, text="Program:")

        self.menuProgramSelectVar = tk.StringVar(self.window)
        self.menuProgramSelectVar.set(self.program)  # default value
        self.menuProgramSelect = tk.OptionMenu(
            self.window,
            self.menuProgramSelectVar,
            ProgramType.DENSITY,
            ProgramType.LIFETIME,
            command=self.toggleExtraOptions
        )

        self.checkboxSaveFigsVar = tk.BooleanVar()
        self.checkboxSaveFigs = tk.Checkbutton(
            self.window, text="Save figures", variable=self.checkboxSaveFigsVar, onvalue=True,
            offvalue=False, command=self.setSaveFigs)
        self.checkboxSaveFigsVar.set(self.saveFigures)

        self.labelBrowse.pack(in_=self.navigation, side=tk.LEFT)
        self.buttonSelectFile.pack(in_=self.navigation, side=tk.LEFT)
        self.buttonSelectFolder.pack(in_=self.navigation, side=tk.LEFT)
        self.labelProgram.pack(in_=self.navigation, side=tk.LEFT)
        self.menuProgramSelect.pack(in_=self.navigation, side=tk.LEFT)
        self.checkboxSaveFigs.pack(in_=self.navigation, side=tk.LEFT)

        self.entries = tk.Frame(self.window)

        self.labelDotSize = tk.Label(self.window, text="Dot size:")
        self.entryDotSize = tk.Entry(self.window, width=5)
        self.entryDotSize.insert(0, self.dotSize)

        self.labelBlobSize = tk.Label(self.window, text="Blob size:")
        self.entryBlobSize = tk.Entry(self.window, width=5)
        self.entryBlobSize.insert(0, self.blobSize)

        self.labelThresholds = tk.Label(self.window, text="Thresholds:")

        self.entryThreshold1 = tk.Entry(self.window, width=5)
        self.entryThreshold1.insert(0, self.lowerDotThresh)

        self.entryThreshold2 = tk.Entry(self.window, width=5)
        self.entryThreshold2.insert(0, self.upperDotThresh)

        self.entryThreshold3 = tk.Entry(self.window, width=5)
        self.entryThreshold3.insert(0, self.lowerBlobThresh)

        self.labelDotSize.pack(in_=self.entries, side=tk.LEFT)
        self.entryDotSize.pack(in_=self.entries, side=tk.LEFT)
        self.labelBlobSize.pack(in_=self.entries, side=tk.LEFT)
        self.entryBlobSize.pack(in_=self.entries, side=tk.LEFT)
        self.labelThresholds.pack(in_=self.entries, side=tk.LEFT)
        self.entryThreshold1.pack(in_=self.entries, side=tk.LEFT)
        self.entryThreshold2.pack(in_=self.entries, side=tk.LEFT)
        self.entryThreshold3.pack(in_=self.entries, side=tk.LEFT)

        self.lifetimeOptions = tk.Frame(self.window)

        self.labelStartImage = tk.Label(self.window, text="Start image:")
        self.buttonSelectStartingImage = tk.Button(
            self.window, text="Browse...", command=self.browseStartingImage)

        self.labelSkipsAllowed = tk.Label(self.window, text="Skips allowed:")
        self.entrySkipsAllowed = tk.Entry(self.window, width=5)
        self.entrySkipsAllowed.insert(0, self.skipsAllowed)

        self.checkboxRemoveEdgeVar = tk.BooleanVar()
        self.checkboxRemoveEdge = tk.Checkbutton(
            self.window, text="Remove edge frames", variable=self.checkboxRemoveEdgeVar,
            onvalue=True, offvalue=False, command=self.setRemoveEdge)
        self.checkboxRemoveEdgeVar.set(self.removeEdgeFrames)

        self.labelStartImage.pack(in_=self.lifetimeOptions, side=tk.LEFT)
        self.buttonSelectStartingImage.pack(
            in_=self.lifetimeOptions, side=tk.LEFT)
        self.labelSkipsAllowed.pack(in_=self.lifetimeOptions, side=tk.LEFT)
        self.entrySkipsAllowed.pack(in_=self.lifetimeOptions, side=tk.LEFT)
        self.checkboxRemoveEdge.pack(in_=self.lifetimeOptions, side=tk.LEFT)

        self.bottomButtons = tk.Frame(self.window)

        self.buttonEditDefaults = tk.Button(
            self.window, text="Edit defaults...", command=self.editDefaults)
        self.buttonUsePreviousAnalysis = tk.Button(
            self.window, text="Use previous settings...", command=self.usePreviousAnalysis)
        self.buttonNext = tk.Button(
            self.window, text="Next", command=self.done, fg="blue",
            font=tk.font.Font(weight="bold"))

        self.buttonEditDefaults.pack(in_=self.bottomButtons, side=tk.LEFT)
        self.buttonUsePreviousAnalysis.pack(
            in_=self.bottomButtons, side=tk.LEFT)
        self.buttonNext.pack(in_=self.bottomButtons, side=tk.LEFT)

        self.labelWarning = tk.Label(self.window, text="", fg="red")

        self.filepathFrame.pack()
        self.navigation.pack()
        self.entries.pack()
        self.lifetimeOptions.pack()
        self.bottomButtons.pack()
        self.labelWarning.pack()

        self.toggleExtraOptions(click=self.program.capitalize())

        self.window.protocol("WM_DELETE_WINDOW", quit)
        self.window.bind("<q>", self.quitWithQKey)
        self.window.bind("<Return>", self.doneWithReturnKey)

        self.window.mainloop()

    def browseFiles(self):
        chosenFile = filedialog.askopenfilename(
            initialdir=self.filepath, title="Select a file to analyze")
        if chosenFile not in EMPTY_DIRECTORY_SET:
            self.filepath = chosenFile
            self.showFilepath()
        self.window.focus_force()
        self.checkForWarning()

    def browseFolders(self):
        chosenFolder = filedialog.askdirectory(
            initialdir=self.filepath, title="Select a folder with images to analyze")
        if chosenFolder not in EMPTY_DIRECTORY_SET:
            self.filepath = chosenFolder
            self.showFilepath()
        self.window.focus_force()
        self.checkForWarning()

    def browseStartingImage(self):
        chosenFilepath = filedialog.askopenfilename(
            initialdir=self.filepath,
            title="Select the starting image for the lifetime measurement")
        chosenImage = os.path.basename(chosenFilepath)
        if chosenImage != "":
            if os.path.isfile(self.filepath):
                self.buttonSelectStartingImage.config(
                    text="Browse...", fg="black")
                self.startImage = ""
                self.labelWarning.configure(
                    text=strings.LIFETIME_SINGLE_FILE_WARNING)
            elif os.path.dirname(chosenFilepath) != self.filepath:
                self.buttonSelectStartingImage.config(
                    text="Browse...", fg="black")
                self.startImage = ""
                self.labelWarning.configure(
                    text=strings.START_IMAGE_DIRECTORY_WARNING)

            else:
                try:
                    trailingNumberString = str(
                        files.getTrailingNumber(chosenImage))
                    if len(trailingNumberString) > 10:
                        trailingNumberString = "..." + \
                            trailingNumberString[-10:]
                    self.buttonSelectStartingImage.config(
                        text=trailingNumberString, fg="darkgreen")
                    self.startImage = chosenImage

                except:
                    self.buttonSelectStartingImage.config(
                        text="Browse...", fg="black")
                    self.startImage = ""
                    self.labelWarning.configure(
                        text=strings.FILE_NUMBERING_WARNING)

        self.window.update()
        self.window.focus_force()

    def checkForWarning(self):
        if os.path.isfile(self.filepath) and self.program == ProgramType.LIFETIME:
            self.labelWarning.configure(
                text=strings.LIFETIME_SINGLE_FILE_WARNING)
        else:
            self.labelWarning.configure(text="")

    def decreaseUpperContrast(self):
        value = self.upperContrast - cfg.CONTRAST_DELTA
        value = round(value, 1)
        if value <= self.lowerContrast:
            print(strings.MAX_CONTRAST_WARNING)
            return
        self.upperContrast = value

    def done(self):
        if self.filepathNotSet():
            return
        self.dotSize = int(self.entryDotSize.get())
        self.blobSize = int(self.entryBlobSize.get())
        self.lowerDotThresh = round(float(self.entryThreshold1.get()), 1)
        self.upperDotThresh = round(float(self.entryThreshold2.get()), 1)
        self.lowerBlobThresh = round(float(self.entryThreshold3.get()), 1)
        self.skipsAllowed = int(self.entrySkipsAllowed.get())
        self.thresholds = (self.lowerDotThresh,
                           self.upperDotThresh, self.lowerBlobThresh)

        self.window.destroy()
        self.window.quit()

    def doneWithReturnKey(self, _):
        self.done()

    def editDefaults(self):
        DefaultUserSettingsEditor(self)

    def getProgramType(self, programString):
        if programString.lower() == "density":
            return ProgramType.DENSITY
        elif programString.lower() == "lifetime":
            return ProgramType.LIFETIME
        else:
            raise Exception(strings.PROGRAM_NAME_EXCEPTION)

    def filepathNotSet(self):
        return self.filepath in EMPTY_DIRECTORY_SET

    def increaseUpperContrast(self):
        value = self.upperContrast + cfg.CONTRAST_DELTA
        value = round(value, 1)
        self.upperContrast = value

    def quitWithQKey(self, _):
        quit()

    def setRemoveEdge(self):
        if self.checkboxRemoveEdgeVar.get():
            self.removeEdgeFrames = True
        else:
            self.removeEdgeFrames = False
        self.checkForWarning()

    def setSaveFigs(self):
        if self.checkboxSaveFigsVar.get():
            self.saveFigures = True
        else:
            self.saveFigures = False
        self.checkForWarning()

    def showFilepath(self):
        if self.filepathNotSet():
            self.labelSelectedPath.configure(
                text="Select a file or folder for analysis", fg="red", bg="white")
        else:
            displayedFilepath = self.filepath
            if len(displayedFilepath) > 50:
                displayedFilepath = "..." + displayedFilepath[-50:]
            self.labelSelectedPath.configure(
                text=displayedFilepath, bg="white", fg="black")

    def toggleExtraOptions(self, click):
        if click == ProgramType.LIFETIME:
            self.program = ProgramType.LIFETIME
            self.bottomButtons.pack_forget()
            self.labelWarning.pack_forget()
            self.lifetimeOptions.pack()
            self.bottomButtons.pack()
            self.labelWarning.pack()
        else:
            self.program = ProgramType.DENSITY
            self.lifetimeOptions.pack_forget()
            self.bottomButtons.pack_forget()
            self.labelWarning.pack_forget()
            self.bottomButtons.pack()
            self.labelWarning.pack()
        self.checkForWarning()

    def usePreviousAnalysis(self):
        if self.filepathNotSet():
            return

        chosenFile = filedialog.askopenfilename(
            initialdir=self.filepath,
            title="Select a .txt file generated by a previous analysis with the desired settings",
            filetypes=[("text files", ".txt")])
        if chosenFile not in EMPTY_DIRECTORY_SET:
            extension = chosenFile.split(".")[-1]
            if extension != "txt":
                print(strings.invalidAnalysisFileWarning(chosenFile))
                return

            self.parseAnalysisFile(chosenFile)

    def parseAnalysisFile(self, chosenFile):
        with open(chosenFile, "r") as file:
            for line in file:
                if not line.startswith("#"):
                    break

                lineArray = line.split()
                if len(lineArray) < 2:
                    continue

                if lineArray[1] == "Generated":
                    programString = lineArray[5]
                    if programString == "density":
                        self.program = ProgramType.DENSITY
                        self.parseDensityFile(chosenFile)
                        return
                    else:
                        self.program = ProgramType.LIFETIME
                        self.parseLifetimeFile(chosenFile)
                        return

        print(strings.invalidAnalysisFileWarning(chosenFile))
        return

    def parseDensityFile(self, chosenFile):
        with open(chosenFile, "r") as file:
            for line in file:
                if line.startswith("#"):
                    continue

                splitLine = line.split()
                if splitLine[1] == "skipped":
                    continue

                # Handle filenames with spaces in them
                extensionIndex = files.getExtensionIndexFromDensityAnalysisFileLineArray(
                    splitLine)
                if extensionIndex == -1:
                    print(strings.invalidFilenameInDensityAnalysisFile(splitLine))
                    return
                filename = " ".join(splitLine[:extensionIndex + 1])

                lowerDotThreshScale = round(
                    float(splitLine[extensionIndex + 5]), 1)
                upperDotThreshScale = round(
                    float(splitLine[extensionIndex + 6]), 1)
                lowerBlobThreshScale = round(
                    float(splitLine[extensionIndex + 7]), 1)
                blobSize = int(splitLine[extensionIndex + 8])
                dotSize = int(splitLine[extensionIndex + 9])
                lowerContrast = round(float(splitLine[extensionIndex + 10]), 1)
                upperContrast = round(float(splitLine[extensionIndex + 11]), 1)
                polygonString = line.split("(")[1:]
                polygonPairsStringArray = [item.split(
                    ")")[0] for item in polygonString]
                polygon = []
                for pair in polygonPairsStringArray:
                    x, y = pair.split(",")
                    polygon.append([int(y), int(x)])
                polygon.append([polygon[0][0], polygon[0][1]])

                self.densityData[filename] = [
                    lowerDotThreshScale,
                    upperDotThreshScale,
                    lowerBlobThreshScale,
                    blobSize,
                    dotSize,
                    lowerContrast,
                    upperContrast,
                    polygon
                ]

        self.reanalysis = True
        self.window.destroy()
        self.window.quit()

    def parseLifetimeFile(self, chosenFile):
        with open(chosenFile, "r") as file:
            for line in file:
                if not line.startswith("#"):  # Only read the header
                    break

                lineArray = line.split()
                if len(lineArray) < 3:
                    continue

                if lineArray[1] == "Polygon":
                    self.polygon = []
                    polygonData = line.split(":")[1].split(")")
                    for item in polygonData:
                        polygonDataArray = item.split("(")
                        if len(polygonDataArray) > 1:
                            x, y = polygonDataArray[1].split(",")
                            self.polygon.append([int(y), int(x)])
                    self.polygon.append(
                        [self.polygon[0][0], self.polygon[0][1]])

                elif lineArray[1] == "Threshold":
                    parsedThresholds = [
                        float(value) for value in line.split(":")[1].split(",")
                    ]
                    self.lowerDotThresh = round(parsedThresholds[0], 1)
                    self.upperDotThresh = round(parsedThresholds[1], 1)
                    self.lowerBlobThresh = round(parsedThresholds[2], 1)
                    self.thresholds = (
                        self.lowerDotThresh,
                        self.upperDotThresh,
                        self.lowerBlobThresh
                    )

                elif lineArray[1] == "Contrast":
                    parsedContrasts = [
                        float(value) for value in line.split(":")[1].split(",")
                    ]
                    self.lowerContrast = round(parsedContrasts[0], 1)
                    self.upperContrast = round(parsedContrasts[1], 1)

                elif lineArray[1] == "Dot" and lineArray[2] == "size:":
                    valueArray = [
                        item.split(":")[1] for item in line.split("|")
                    ]
                    self.dotSize = int(valueArray[0])
                    self.blobSize = int(valueArray[1])

        self.reanalysis = True
        self.window.destroy()
        self.window.quit()
