import dotscanner.config as cfg
import dotscanner.dataprocessing as dp
import dotscanner.files as files
import dotscanner.strings as strings
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as pl
import matplotlib.widgets as wdgts
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog

matplotlib.rcParams["toolbar"] = "None"
matplotlib.rcParams["figure.facecolor"] = "gray"
matplotlib.rcParams["figure.subplot.left"] = 0.01
matplotlib.rcParams["figure.subplot.bottom"] = 0.07
matplotlib.rcParams["figure.subplot.right"] = 0.99
matplotlib.rcParams["figure.subplot.top"] = 0.99
matplotlib.rcParams["xtick.bottom"] = False
matplotlib.rcParams["xtick.labelbottom"] = False
matplotlib.rcParams["ytick.left"] = False
matplotlib.rcParams["ytick.labelleft"] = False

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
		value = round(value, 2)
		if value < 0:
			value = 0
		self.lowerDotThreshScale = value
		self.updateThresholds()
		self.dotCoords, self.blobCoords = self.getCoords()
	
	def decreaseUpperDotThreshScale(self):
		value = self.upperDotThreshScale - cfg.THRESHOLD_DELTA
		value = round(value, 2)
		if value < self.lowerDotThreshScale:
			value = self.lowerDotThreshScale
		self.upperDotThreshScale = value
		self.updateThresholds()
		self.dotCoords, self.blobCoords = self.getCoords()
	
	def getCoords(self):
		if self.thresholds in self.memoizedCoords:
			dotCoords, blobCoords = self.memoizedCoords[self.thresholds]
		else:
			dotCoords, blobCoords = dp.getCoords(self.data, self.sums, self.thresholds, 
								self.dotSize)
			dp.cleanDotCoords(self.sums, dotCoords, blobCoords, self.blobSize, self.dotSize)
			self.memoizedCoords[self.thresholds] = (dotCoords, blobCoords)
		return dotCoords, blobCoords
	
	def increaseLowerDotThreshScale(self):
		value = self.lowerDotThreshScale + cfg.THRESHOLD_DELTA
		value = round(value, 2)
		if value > self.upperDotThreshScale:
			value = self.upperDotThreshScale
		self.lowerDotThreshScale = value
		self.updateThresholds()
		self.dotCoords, self.blobCoords = self.getCoords()
	
	def increaseUpperDotThreshScale(self):
		value = self.upperDotThreshScale + cfg.THRESHOLD_DELTA
		value = round(value, 2)
		self.upperDotThreshScale = value
		self.updateThresholds()
		self.dotCoords, self.blobCoords = self.getCoords()
	
	def setThresholds(self, newThresholds):
		self.lowerDotThreshScale = round(newThresholds[0], 1)
		self.upperDotThreshScale = round(newThresholds[1], 1)
		self.lowerBlobThreshScale = round(newThresholds[2], 1)
		
		if self.lowerDotThreshScale < 0:
			print(strings.lowerDotThreshScaleWarning)
			self.lowerDotThreshScale = 0
		
		if self.upperDotThreshScale < self.lowerDotThreshScale:
			print(strings.upperDotThreshScaleWarning)
			self.upperDotThreshScale = self.lowerDotThreshScale
		
		if self.lowerBlobThreshScale < 1:
			print(strings.lowerBlobThreshScaleWarning)
			self.lowerBlobThreshScale = 1
		
		self.updateThresholds()
	
	def updateThresholds(self):
		self.thresholds = (self.lowerDotThreshScale, self.upperDotThreshScale, 
					self.lowerBlobThreshScale)

class RegionSelector:
	def __init__(self, image, userSettings, skipButton=True):
		self.xList = []
		self.yList = []
		
		self.image = image
		self.program = userSettings.program
		self.dotSize = userSettings.dotSize
		self.blobSize = userSettings.blobSize
		self.data = image.data
		
		self.figure, self.axes = pl.subplots()
		manager = pl.get_current_fig_manager()
		geometry = f"{cfg.WINDOW_WIDTH}x{cfg.WINDOW_HEIGHT}+{cfg.WINDOW_X}+{cfg.WINDOW_Y}"
		manager.window.geometry(geometry)
		manager.window.title(f"Dot Scanner - Region Selection ({self.program})")
		
		self.axes.imshow(self.data, origin="lower", cmap="gray", vmin=0, vmax=2 * np.std(self.data))
		self.dotScatter = self.axes.scatter([None], [None], s=5 * self.dotSize, facecolors="none", 
							edgecolors=cfg.DOT_COLOR, linewidths=1)
		self.blobScatter = self.axes.scatter([None], [None], s=2 * self.blobSize, facecolors="none",
							edgecolor=cfg.BLOB_COLOR, linewidths=1)
		
		self.clickMarkerBackdrop = self.axes.scatter([None], [None], s=100, marker='x', color="k", 
								linewidth=4)
		self.underLine, = self.axes.plot([None], [None], linestyle="-", color="k", linewidth=5)
		self.line, = self.axes.plot([None], [None], linestyle="-", color="C1", linewidth=1.5)
		self.dottedLine, = self.axes.plot([None], [None], linestyle=":", color="C1", linewidth=1.5)
		self.clickMarker = self.axes.scatter([None], [None], s=100, marker='x', color="C1", 
							linewidth=1.5)
		
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
					self.blobScatter)
		self.figure.canvas.draw_idle()
		
		self.cid = self.line.figure.canvas.mpl_connect("button_press_event", self)
		
		quitButton = createButton(name="Quit", position=0, action=self.quit, 
						color="orangered")
		
		if skipButton:
			skipButton = createButton(name="Skip", position=0.095, action=self.skip, 
							color="gold")
		
		instructionsTextBox = createInactiveTextBox("Click the plot to add polygon vertices", 
								position=0.69)

		resetButton = createButton(name="Reset", position=0.735, action=self.reset, 
						color="lightgray")

		doneButton = createButton(name="Done", position=0.83, action=self.finish, 
						color="cornflowerblue")
		
		pl.show()

	def __call__(self, event):
		if event.inaxes != self.line.axes:
			return
		self.drawLine(event)
		self.drawclickMarker(event)
	
	def drawclickMarker(self, event):
		self.clickMarkerBackdrop.set_offsets([event.xdata, event.ydata])
		self.clickMarker.set_offsets([event.xdata, event.ydata])
		self.clickMarkerBackdrop.figure.canvas.draw_idle()
		self.clickMarker.figure.canvas.draw_idle()
	
	def drawLine(self, event):
		self.xList.append(event.xdata)
		self.yList.append(event.ydata)
		self.underLine.set_data(self.xList, self.yList)
		self.line.set_data(self.xList, self.yList)
		if len(self.xList) > 2:
			self.underLine.set_data([self.xList + [self.xList[0]], self.yList + [self.yList[0]]])
			self.dottedLine.set_data([[self.xList[0], self.xList[-1]], [self.yList[0], 
							self.yList[-1]]])
		self.underLine.figure.canvas.draw_idle()
		self.line.figure.canvas.draw_idle()
	
	def finish(self, _event):
		if len(self.xList) > 2: # If a valid enclosed polygon was drawn
			self.xList.append(self.xList[0]) # Enclose the polygon to the beginning vertex
			self.yList.append(self.yList[0])
			for y, x in zip(self.yList, self.xList):
				self.image.polygon.append([y, x])
		
		else: # An invalid polygon was drawn
			print(strings.invalidPolygonWarning)
			
		pl.close("all")
	
	def quit(self, event):
		quit()
	
	def reset(self, _event):
		self.xList = []
		self.yList = []
		self.line.set_data(self.xList, self.yList)
		self.underLine.set_data(self.xList, self.yList)
		self.dottedLine.set_data(self.xList, self.yList)
		self.underLine.figure.canvas.draw_idle()
		self.line.figure.canvas.draw_idle()
		self.restartclickMarker()
	
	def restartclickMarker(self):
		self.clickMarkerBackdrop.set_offsets([float("nan"), float("nan")])
		self.clickMarker.set_offsets([float("nan"), float("nan")])
		self.clickMarkerBackdrop.figure.canvas.draw_idle()
		self.clickMarker.figure.canvas.draw_idle()
	
	def skip(self, event):
		self.image.skipped = True
		pl.close("all")

class ThresholdAdjuster:
	def __init__(self, image, userSettings, skipButton=True):
		self.index = 0
		self.editingThresholds = False
		
		self.image = image
		self.program = userSettings.program
		self.dotSize = userSettings.dotSize
		self.blobSize = userSettings.blobSize
		self.defaultThresholds = userSettings.thresholds
		self.data = image.data
		
		self.xBounds = [
			(0,                     len(self.data[0])    ),
			(0,                     len(self.data[0]) / 2),
			(len(self.data[0]) / 2, len(self.data[0])    ),
			(0,                     len(self.data[0]) / 2),
			(len(self.data[0]) / 2, len(self.data[0])),
		]

		self.yBounds = [
			(0,                     len(self.data)),
			(len(self.data) / 2,    len(self.data)),
			(len(self.data) / 2,    len(self.data)),
			(0,                     len(self.data) / 2),
			(0,                     len(self.data) / 2),
		]
		
		self.figure, self.axes = pl.subplots()
		manager = pl.get_current_fig_manager()
		geometry = f"{cfg.WINDOW_WIDTH}x{cfg.WINDOW_HEIGHT}+{cfg.WINDOW_X}+{cfg.WINDOW_Y}"
		manager.window.geometry(geometry)
		manager.window.title(f"Dot Scanner - Threshold Adjustment ({self.program})")
		
		self.axes.imshow(self.data, origin="lower", cmap="gray", vmin=0, vmax=2 * np.std(self.data))
		self.dotScatter = self.axes.scatter([None], [None], s=50 * self.dotSize, facecolors="none", 
							edgecolors=cfg.DOT_COLOR, linewidths=1)
		self.blobScatter = self.axes.scatter([None], [None], s=2 * self.blobSize, facecolors="none",
							edgecolor=cfg.BLOB_COLOR, linewidths=1)

		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
					self.blobScatter)
		self.displayCorrectMarkerSize(self.index)
		self.figure.canvas.draw_idle()

		quitButton = createButton(name="Quit", position=0, action=self.quit, 
						color="orangered")
		
		if skipButton:
			skipButton = createButton(name="Skip", position=0.095, action=self.skip, 
							color="gold")

		viewTextBox = createInactiveTextBox("View: ", position=0.265)
		topLeftButton, bottomLeftButton = createSmallStackedButtons(topText="", 
										bottomText="", position=0.275, 
										topAction=self.showTopLeftRegion, 
										bottomAction=self.showBottomLeftRegion, 
										color="lightgray")
		topRightButton, bottomRightButton = createSmallStackedButtons(topText="", 
										bottomText="", position=0.305, 
										topAction=self.showTopRightRegion, 
										bottomAction=self.showBottomRightRegion,
										color="lightgray")
		fullButton = createFullViewButton(name="", position=0.335, action=self.showWholeImage, 
											color="lightgray")

		dotsTextBox = createInactiveTextBox("Dots: ", position=0.47)
		dotLowerThreshScaleUpButton, dotLowerThreshScaleDownButton = createSmallStackedButtons(
										topText="ʌ", bottomText="v", position=0.48, 
										topAction=self.lowerDotThresholdScaleDown, 
										bottomAction=self.lowerDotThresholdScaleUp, 
										color="lightgray")
		blobsTextBox = createInactiveTextBox("Blobs: ", position=0.6)
		dotUpperThreshScaleUpButton, dotUpperThreshScaleDownButton = createSmallStackedButtons(
										topText="ʌ", bottomText="v", position=0.61, 
										topAction=self.upperDotThresholdScaleDown, 
										bottomAction=self.upperDotThresholdScaleUp, 
										color="lightgray")

		editButton = createButton(name="Edit", position=0.64, action=self.edit, 
						color="lightgray")
		resetButton = createButton(name="Reset", position=0.735, 
						action=self.resetThreshScalesToDefaultValues, color="lightgray")

		nextButton = createButton(name="Next", position=0.83, action=self.finish, 
						color="cornflowerblue")

		pl.show()
	
	def displayCorrectMarkerSize(self, index):
		if self.index == 0:
			self.dotScatter.set_sizes([5 * self.dotSize])
		else:
			self.dotScatter.set_sizes([50 * self.dotSize])
	
	def edit(self, event):
		if self.editingThresholds:
			return
			
		self.editingThresholds = True
		userInput = "empty"
		while len(userInput.split()) != 3:
			inputString = strings.editThresholds(self.image.thresholds)
			userInput = input(inputString)
			if userInput == "":
				print(f"Edit canceled")
				break
			else:
				try:
					numberIn1 = round(float(userInput.split()[0]), 1)
					numberIn2 = round(float(userInput.split()[1]), 1)
					numberIn3 = round(float(userInput.split()[2]), 1)
					newThresholds = (round(numberIn1, 2), round(numberIn2, 2), 
								round(numberIn3, 2))
					self.image.setThresholds(newThresholds)
				except:
					print("\nInvalid input.")
					userInput = "empty"
		
		self.editingThresholds = False
		self.image.dotCoords, self.image.blobCoords = self.image.getCoords()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
					self.blobScatter)
		self.figure.canvas.draw_idle()
		pl.pause(0.01)
	
	def finish(self, event):
		pl.close("all")
	
	def lowerDotThresholdScaleDown(self, event):
		self.image.decreaseLowerDotThreshScale()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
					self.blobScatter)
		self.figure.canvas.draw_idle()
		pl.pause(0.01)

	def lowerDotThresholdScaleUp(self, event):
		self.image.increaseLowerDotThreshScale()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
					self.blobScatter)
		self.figure.canvas.draw_idle()
		pl.pause(0.01)

	def quit(self, event):
		quit()

	def showWholeImage(self, event):
		self.index = 0
		self.displayCorrectMarkerSize(self.index)
		self.axes.set_xbound(self.xBounds[self.index])
		self.axes.set_ybound(self.yBounds[self.index])
		self.figure.canvas.draw_idle()
		pl.pause(0.01)

	def showTopLeftRegion(self, event):
		self.index = 1
		self.displayCorrectMarkerSize(self.index)
		self.axes.set_xbound(self.xBounds[self.index])
		self.axes.set_ybound(self.yBounds[self.index])
		self.figure.canvas.draw_idle()
		pl.pause(0.01)

	def showTopRightRegion(self, event):
		self.index = 2
		self.displayCorrectMarkerSize(self.index)
		self.axes.set_xbound(self.xBounds[self.index])
		self.axes.set_ybound(self.yBounds[self.index])
		self.figure.canvas.draw_idle()
		pl.pause(0.01)

	def showBottomLeftRegion(self, event):
		self.index = 3
		self.displayCorrectMarkerSize(self.index)
		self.axes.set_xbound(self.xBounds[self.index])
		self.axes.set_ybound(self.yBounds[self.index])
		self.figure.canvas.draw_idle()
		pl.pause(0.01)

	def showBottomRightRegion(self, event):
		self.index = 4
		self.displayCorrectMarkerSize(self.index)
		self.axes.set_xbound(self.xBounds[self.index])
		self.axes.set_ybound(self.yBounds[self.index])
		self.figure.canvas.draw_idle()
		pl.pause(0.01)
	
	def skip(self, event):
		self.image.skipped = True
		pl.close("all")

	def resetThreshScalesToDefaultValues(self, event):
		self.image.setThresholds(self.defaultThresholds)
		self.image.dotCoords, self.image.blobCoords = self.image.getCoords()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
					self.blobScatter)
		self.figure.canvas.draw_idle()
		pl.pause(0.01)
	
	def upperDotThresholdScaleDown(self, event):
		self.image.decreaseUpperDotThreshScale()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
					self.blobScatter)
		self.figure.canvas.draw_idle()
		pl.pause(0.01)

	def upperDotThresholdScaleUp(self, event):
		self.image.increaseUpperDotThreshScale()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
					self.blobScatter)
		self.figure.canvas.draw_idle()
		pl.pause(0.01)

class UserSettings:
	def __init__(self):
		self.window = tk.Tk()
		self.window.title("Dot Scanner - Configurations")
		self.window.geometry(f"{cfg.WINDOW_WIDTH}x170+{cfg.WINDOW_X}+{cfg.WINDOW_Y}")

		self.filepath = cfg.FILEPATH
		if self.filepath in ["", " ", "/"]:
			self.filepathSet = False
		else:
			self.filepathSet = True
		
		self.startImage = ""
		self.program = cfg.PROGRAM
		self.blobSize = round(cfg.BLOB_SIZE, 0)
		self.dotSize = round(cfg.DOT_SIZE, 0)
		self.lowerDotThresh = round(cfg.LOWER_DOT_THRESH_SCALE, 1)
		self.upperDotThresh = round(cfg.UPPER_DOT_THRESH_SCALE, 1)
		self.lowerBlobThresh = round(cfg.LOWER_BLOB_THRESH_SCALE, 1)
		self.saveFigures = cfg.SAVE_FIGURES
		self.removeEdgeFrames = cfg.REMOVE_EDGE_FRAMES
		self.skipsAllowed = round(cfg.SKIPS_ALLOWED, 0)
		self.completed = False
		
		self.labelSelectedPath = tk.Label(self.window, text="Select a file or folder for analysis", 
							fg="red")
		if self.filepathSet:
			self.labelSelectedPath.configure(text=self.filepath, bg="white", fg="black")
		self.labelSelectedPath.pack()
		
		self.navigation = tk.Frame(self.window)
		self.navigation.pack()
		
		self.labelBrowse = tk.Label(self.window, text="Browse:")
		
		self.buttonSelectFile = tk.Button(self.window,
							text="File",
							command=self.browseFiles)

		self.buttonSelectFolder = tk.Button(self.window,
							text="Folder",
							command=self.browseFolders)
		
		self.labelProgram = tk.Label(self.window, text="Program:")

		self.menuProgramSelectVar = tk.StringVar(self.window)
		self.menuProgramSelectVar.set("Density") # default value
		self.menuProgramSelect = tk.OptionMenu(self.window, self.menuProgramSelectVar, "Density", 
							"Lifetime", command=self.show)
		
		self.checkboxSaveFigsVar = tk.BooleanVar()
		self.checkboxSaveFigs = tk.Checkbutton(self.window, 
							text='Save figures',
							variable=self.checkboxSaveFigsVar, 
							onvalue=True, offvalue=False, 
							command=self.setSaveFigs)
		self.checkboxSaveFigsVar.set(self.saveFigures)
		
		self.labelBrowse.pack(in_=self.navigation, side=tk.LEFT)
		self.buttonSelectFile.pack(in_=self.navigation, side=tk.LEFT)
		self.buttonSelectFolder.pack(in_=self.navigation, side=tk.LEFT)
		self.labelProgram.pack(in_=self.navigation, side=tk.LEFT)
		self.menuProgramSelect.pack(in_=self.navigation, side=tk.LEFT)
		self.checkboxSaveFigs.pack(in_=self.navigation, side=tk.LEFT)
		
		self.entries = tk.Frame(self.window)
		self.entries.pack()

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
		self.buttonSelectStartingImage = tk.Button(self.window,
								text="Browse...",
								command=self.browseStartingImage)

		self.labelSkipsAllowed = tk.Label(self.window, text="Skips allowed:")
		self.entrySkipsAllowed = tk.Entry(self.window, width=5)
		self.entrySkipsAllowed.insert(0, self.skipsAllowed)

		self.checkboxRemoveEdgeVar = tk.BooleanVar()
		self.checkboxRemoveEdge = tk.Checkbutton(self.window, 
								text='Remove edge frames',
								variable=self.checkboxRemoveEdgeVar, 
								onvalue=True, offvalue=False, 
								command=self.setRemoveEdge)
		self.checkboxRemoveEdgeVar.set(self.removeEdgeFrames)
		
		self.labelStartImage.pack(in_=self.lifetimeOptions, side=tk.LEFT)
		self.buttonSelectStartingImage.pack(in_=self.lifetimeOptions, side=tk.LEFT)
		self.labelSkipsAllowed.pack(in_=self.lifetimeOptions, side=tk.LEFT)
		self.entrySkipsAllowed.pack(in_=self.lifetimeOptions, side=tk.LEFT)
		self.checkboxRemoveEdge.pack(in_=self.lifetimeOptions, side=tk.LEFT)

		self.buttonDone = tk.Button(self.window, text="Done", command=self.done, 
									bg="cornflowerblue")
		self.buttonDone.pack()
		
		self.labelStartImageWarning = tk.Label(self.window, 
							text=f"WARNING: {strings.fileNumberingException}", 
							fg="red")

		self.window.mainloop()

	def browseFiles(self):
		chosenFile = filedialog.askopenfilename(title="Select a file to analyze")
		if chosenFile != "":
			self.filepath = chosenFile
			displayedFilename = chosenFile
			if len(chosenFile) > 50:
				displayedFilename = "..." + chosenFile[-50:]
			self.labelSelectedPath.configure(text=displayedFilename, bg="white", fg="black")

	def browseFolders(self):
		chosenFolder = filedialog.askdirectory(title="Select a folder with images to analyze")
		if chosenFolder != "":
			self.filepath = chosenFolder
			displayedFolder = chosenFolder
			if len(chosenFolder) > 50:
				displayedFolder = "..." + chosenFolder[-50:]
			self.labelSelectedPath.configure(text=displayedFolder, bg="white", fg="black")

	def browseStartingImage(self):
		chosenImage = filedialog.askopenfilename(initialdir=self.filepath, 
			title="Select the starting image for the lifetime measurement")
		if chosenImage != "":
			try:
				trailingNumberString = str(files.getTrailingNumber(chosenImage))
				if len(trailingNumberString) > 10:
					trailingNumberString = "..." + trailingNumberString[-10:]
				self.buttonSelectStartingImage.config(text=trailingNumberString, fg="darkgreen")
				self.startImage = chosenImage
				self.lifetimeOptions.pack_forget()
				self.buttonDone.pack_forget()
				self.labelStartImageWarning.pack_forget()
				self.lifetimeOptions.pack()
				self.buttonDone.pack()
			except:
				self.buttonSelectStartingImage.config(text="Browse...", fg="black")
				self.startImage = ""
				self.labelStartImageWarning.pack()

	def setRemoveEdge(self):
		if self.checkboxRemoveEdgeVar.get():
			self.removeEdgeFrames = True
		else:
			self.removeEdgeFrames = False

	def setSaveFigs(self):
		if self.checkboxSaveFigsVar.get():
			self.saveFigures = True
		else:
			self.saveFigures = False

	def show(self, click):
		if click == "Lifetime":
			self.program = "lifetime"
			self.buttonDone.pack_forget()
			self.lifetimeOptions.pack()
			self.buttonDone.pack()
		else:
			self.program = "density"
			self.lifetimeOptions.pack_forget()
			self.buttonDone.pack_forget()
			self.buttonDone.pack()

	def done(self):        
		self.dotSize = int(self.entryDotSize.get())
		self.blobSize = int(self.entryBlobSize.get())
		self.lowerDotThresh = round(float(self.entryThreshold1.get()), 1)
		self.upperDotThresh = round(float(self.entryThreshold2.get()), 1)
		self.lowerBlobThresh = round(float(self.entryThreshold3.get()), 1)
		self.skipsAllowed = int(self.entrySkipsAllowed.get())
		self.thresholds = (self.lowerDotThresh, self.upperDotThresh, self.lowerBlobThresh)
		self.completed = True
		self.window.destroy()

def createButton(name, position, action, color="whitesmoke", clickedColor="darkgray"):
	buttonWidth = 45 / 500
	buttonHeight = 5 / 100
	buttonSpacing = 5 / 1000
	buttonXStart = 0.01 * 5 - (2 * buttonSpacing)
	buttonYStart = 0.007 * 5 - buttonHeight / 2

	axes = pl.axes([
		buttonXStart + position, 
		buttonYStart, 
		buttonWidth, 
		buttonHeight])
	
	fontSize = min(13, int(round(cfg.WINDOW_WIDTH * 0.01875, 0)))
	
	button = wdgts.Button(axes, name, color=color, hovercolor=color)
	button.label.set_fontsize(fontSize)
	# matplotlib lags a little with hovercolor, so leaving it the same to not confuse users
	button.on_clicked(action)
	
	return button

def createFullViewButton(name, position, action, color="whitesmoke", clickedColor="darkgray"):
	buttonHeight = 5 / 100
	buttonSpacing = 5 / 1000
	buttonWidth = 5 / 100 + buttonSpacing
	buttonXStart = 0.01 * 5 - (2 * buttonSpacing)
	buttonYStart = 0.007 * 5 - buttonHeight / 2

	axes = pl.axes([
		buttonXStart + position, 
		buttonYStart, 
		buttonWidth, 
		buttonHeight])
	button = wdgts.Button(axes, name, color=color, hovercolor=color)
	# matplotlib lags a little with hovercolor, so leaving it the same to not confuse users
	button.on_clicked(action)
	
	return button

def createInactiveTextBox(text, position):
	textBoxWidth = 0.0
	textBoxHeight = 0.0
	textBoxSpacing = 0.0
	textBoxXStart = 0.05
	textBoxYStart = 0.035

	axes = pl.axes([
		textBoxXStart + position, 
		textBoxYStart, 
		textBoxWidth, 
		textBoxHeight])
	
	fontSize = min(13, int(round(cfg.WINDOW_WIDTH * 0.01875, 0)))
	
	textBox = wdgts.TextBox(axes, text, initial="")
	textBox.label.set_fontsize(fontSize)
	return textBox

def createSmallStackedButtons(topText, bottomText, position, topAction, bottomAction, 
				color="whitesmoke", clickedColor="darkgray"):
	buttonWidth = 5 / 200
	buttonSpacing = 5 / 1000
	buttonHeight = 5 / 200 - (buttonSpacing / 2)
	buttonXStart = 0.01 * 5 - (2 * buttonSpacing)
	buttonYStart = 0.007 * 5 - 5 / 200

	topAxes = pl.axes([
		buttonXStart + position, 
		buttonYStart + buttonHeight + buttonSpacing, 
		buttonWidth, 
		buttonHeight])
	bottomAxes = pl.axes([
		buttonXStart + position, 
		buttonYStart, 
		buttonWidth, 
		buttonHeight])
	
	fontSize = min(13, int(round(cfg.WINDOW_WIDTH * 0.015, 0)))
	
	topButton = wdgts.Button(topAxes, topText, color=color, hovercolor=color)
	topButton.label.set_fontsize(fontSize)
	topButton.on_clicked(topAction)
	bottomButton = wdgts.Button(bottomAxes, bottomText, color=color, hovercolor=color)
	bottomButton.label.set_fontsize(fontSize)
	bottomButton.on_clicked(bottomAction)
	
	return topButton, bottomButton

def printProgressBar (iteration, total, prefix = "", suffix = "", decimals = 1, 
						barLength = 50, fill = "█", printEnd = "\r"):
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(barLength * iteration // total)
	bar = fill * filledLength + "-" * (barLength - filledLength)
	print(f"\r{prefix} |{bar}| {percent}% {suffix}", end = printEnd)
	
	if iteration == total: 
		print()
