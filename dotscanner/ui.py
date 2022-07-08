import dotscanner.config as cfg
import dotscanner.dataprocessing as dp
import dotscanner.files as files
import dotscanner.strings as strings
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as pl
import matplotlib.widgets as wdgts
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog

matplotlib.rcParams["toolbar"] = "None"
matplotlib.rcParams["figure.facecolor"] = "gray"
matplotlib.rcParams["figure.subplot.left"] = 0.01
matplotlib.rcParams["figure.subplot.bottom"] = 0.01
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
		value = round(value, 1)
		if value < 0:
			value = 0
		self.lowerDotThreshScale = value
		self.updateThresholds()
		self.dotCoords, self.blobCoords = self.getCoords()
	
	def decreaseUpperDotThreshScale(self):
		value = self.upperDotThreshScale - cfg.THRESHOLD_DELTA
		value = round(value, 1)
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
			dp.cleanDotCoords(self.data, dotCoords, blobCoords, self.blobSize, self.dotSize)
			self.memoizedCoords[self.thresholds] = (dotCoords, blobCoords)
		return dotCoords, blobCoords
	
	def increaseLowerDotThreshScale(self):
		value = self.lowerDotThreshScale + cfg.THRESHOLD_DELTA
		value = round(value, 1)
		if value > self.upperDotThreshScale:
			value = self.upperDotThreshScale
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
		self.dotSize = userSettings.dotSize
		self.blobSize = userSettings.blobSize
		self.data = image.data
		
		self.window = createWindow("Dot Scanner - Region Selection (click the plot to add polygon vertices)")
		
		self.figure, self.axes, _, self.dotScatter, self.blobScatter = createPlots(self.data, 
																					userSettings)
		
		self.clickMarkerBackdrop = self.axes.scatter([None], [None], s=100, marker='x', color="k", 
														linewidth=4)
		self.underLine, = self.axes.plot([None], [None], linestyle="-", color="k", linewidth=5)
		self.line, = self.axes.plot([None], [None], linestyle="-", color="C1", linewidth=1.5)
		self.dottedLine, = self.axes.plot([None], [None], linestyle=":", color="C1", linewidth=1.5)
		self.clickMarker = self.axes.scatter([None], [None], s=100, marker='x', color="C1", 
												linewidth=1.5)
		
		self.connectId = self.line.figure.canvas.mpl_connect("button_press_event", self)
		
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		
		self.canvas = FigureCanvasTkAgg(self.figure, master=self.window)
		self.canvas.draw()
		
		self.buttonBar = tk.Frame(self.window)
		self.buttonBar.pack(side=tk.LEFT)
		self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		
		if skipButton:
			self.skipButton = tk.Button(self.window, text="Skip", command=self.skip, 
										fg="darkgoldenrod")
			self.skipButton.pack(in_=self.buttonBar, side=tk.TOP)
			
			self.firstSpacer = tk.Label(self.window, text="                       ")
			self.firstSpacer.pack(in_=self.buttonBar, side=tk.TOP)
		
		self.resetButton = tk.Button(self.window, text="Reset", command=self.reset, fg="red")
		self.resetButton.pack(in_=self.buttonBar, side=tk.TOP)
		
		self.secondSpacer = tk.Label(self.window, text="                       ")
		self.secondSpacer.pack(in_=self.buttonBar, side=tk.TOP)
		
		self.doneButton = tk.Button(self.window, text="Done", command=self.finish, fg="blue")
		self.doneButton.pack(in_=self.buttonBar, side=tk.TOP)
		
		self.window.protocol("WM_DELETE_WINDOW", quit)
		self.window.bind("<Return>", self.finishWithReturnKey)
		self.window.bind("<BackSpace>", self.resetWithDeleteKey)
		
		self.window.mainloop()

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
	
	def finish(self):
		if len(self.xList) > 2: # If a valid enclosed polygon was drawn
			self.xList.append(self.xList[0]) # Enclose the polygon to the beginning vertex
			self.yList.append(self.yList[0])
			for y, x in zip(self.yList, self.xList):
				self.image.polygon.append([int(round(y, 0)), int(round(x, 0))])
		
		else: # An invalid polygon was drawn
			print(strings.invalidPolygonWarning)
		
		self.line.figure.canvas.mpl_disconnect(self.connectId)
		self.window.destroy()
		self.window.quit()
	
	def finishWithReturnKey(self, event):
		self.finish()
		
	def reset(self):
		self.xList = []
		self.yList = []
		self.line.set_data(self.xList, self.yList)
		self.underLine.set_data(self.xList, self.yList)
		self.dottedLine.set_data(self.xList, self.yList)
		self.underLine.figure.canvas.draw_idle()
		self.line.figure.canvas.draw_idle()
		self.restartclickMarker()
	
	def resetWithDeleteKey(self, event):
		self.reset()
	
	def restartclickMarker(self):
		self.clickMarkerBackdrop.set_offsets([float("nan"), float("nan")])
		self.clickMarker.set_offsets([float("nan"), float("nan")])
		self.clickMarkerBackdrop.figure.canvas.draw_idle()
		self.clickMarker.figure.canvas.draw_idle()
	
	def skip(self):
		self.image.skipped = True
		self.window.destroy()
		self.window.quit()

class ThresholdAdjuster:
	def __init__(self, image, userSettings, skipButton=True):
		self.index = 0
		self.editingThresholds = False
		
		self.image = image
		self.dotSize = userSettings.dotSize
		self.blobSize = userSettings.blobSize
		self.defaultThresholds = userSettings.thresholds
		self.userSettings = userSettings
		self.data = image.data
		
		self.xBounds = [
			(0,                     len(self.data[0]) - 1),
			(0,                     len(self.data[0]) / 2),
			(len(self.data[0]) / 2, len(self.data[0]) - 1),
			(0,                     len(self.data[0]) / 2),
			(len(self.data[0]) / 2, len(self.data[0]) - 1),
		]

		self.yBounds = [
			(0,                     len(self.data) - 1),
			(len(self.data) / 2,    len(self.data) - 1),
			(len(self.data) / 2,    len(self.data) - 1),
			(0,                     len(self.data) / 2),
			(0,                     len(self.data) / 2),
		]
		
		self.window = createWindow("Dot Scanner - Threshold Adjustment")
		
		self.figure, self.axes, self.dataPlot, self.dotScatter, self.blobScatter = createPlots(
																					self.data, 
																					userSettings)

		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		
		self.displayCorrectMarkerSize(self.index)
		
		self.canvas = FigureCanvasTkAgg(self.figure, master=self.window)
		self.canvas.draw()
		
		self.buttonBar = tk.Frame(self.window)
		
		self.viewItem = tk.Frame(self.window)
		self.viewButtons = tk.Frame(self.window)
		self.leftViewButtons = tk.Frame(self.window)
		self.rightViewButtons = tk.Frame(self.window)
		self.fourViewButtons = tk.Frame(self.window)
		
		self.contrastItem = tk.Frame(self.window)
		self.contrastButtons = tk.Frame(self.window)
		
		self.dotsItem = tk.Frame(self.window)
		self.dotsButtons = tk.Frame(self.window)
		
		self.blobsItem = tk.Frame(self.window)
		self.blobsButtons = tk.Frame(self.window)
		
		self.thresholdEditItem = tk.Frame(self.window)
		
		if skipButton:
			self.skipButton = tk.Button(self.window, text="Skip", command=self.skip, 
										fg="darkgoldenrod")
			self.skipButton.pack(in_=self.buttonBar, side=tk.TOP, pady=12)
		
		self.viewLabel = tk.Label(self.window, text="View: ")
		self.viewTopLeftButton = tk.Button(self.window, text="⌜", command=self.showTopLeftRegion)
		self.viewBottomLeftButton = tk.Button(self.window, text="⌞", 
												command=self.showBottomLeftRegion)
		self.viewTopRightButton = tk.Button(self.window, text="⌝", command=self.showTopRightRegion)
		self.viewBottomRightButton = tk.Button(self.window, text="⌟", 
												command=self.showBottomRightRegion)
		self.viewFullButton = tk.Button(self.window, text="Full", command=self.showWholeImage)
		
		self.contrastLabel = tk.Label(self.window, text="Contrast: ")
		self.contrastUpButton = tk.Button(self.window, text="ʌ", command=self.upperContrastDown)
		self.contrastDownButton = tk.Button(self.window, text="v", command=self.upperContrastUp)
		
		self.dotsLabel = tk.Label(self.window, text="Dots: ")
		self.dotsUpButton = tk.Button(self.window, text="ʌ", command=self.lowerDotThresholdScaleDown)
		self.dotsDownButton = tk.Button(self.window, text="v", command=self.lowerDotThresholdScaleUp)
		
		self.blobsLabel = tk.Label(self.window, text="Blobs: ")
		self.blobsUpButton = tk.Button(self.window, text="ʌ", command=self.upperDotThresholdScaleDown)
		self.blobsDownButton = tk.Button(self.window, text="v", command=self.upperDotThresholdScaleUp)
		
		self.thresholdsLabel = tk.Label(self.window, text="Thresholds: ")
		
		self.editButton = tk.Button(self.window, text="Edit", command=self.edit)
		
		self.resetButton = tk.Button(self.window, text="Reset", 
										command=self.resetThreshScalesToDefaultValues)
		
		self.nextButton = tk.Button(self.window, text="Next", command=self.finish, fg="blue")
		
		self.buttonBar.pack(side=tk.LEFT)
		self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		
		self.viewItem.pack(in_=self.buttonBar, side=tk.TOP, pady=12)
		self.contrastItem.pack(in_=self.buttonBar, side=tk.TOP, pady=12)
		self.dotsItem.pack(in_=self.buttonBar, side=tk.TOP, pady=12)
		self.blobsItem.pack(in_=self.buttonBar, side=tk.TOP, pady=12)
		self.thresholdEditItem.pack(in_=self.buttonBar, side=tk.TOP, pady=12)
		self.nextButton.pack(in_=self.buttonBar, side=tk.TOP, pady=12)
		
		self.viewTopLeftButton.pack(in_=self.leftViewButtons, side=tk.TOP)
		self.viewBottomLeftButton.pack(in_=self.leftViewButtons, side=tk.TOP)
		self.viewTopRightButton.pack(in_=self.rightViewButtons, side=tk.TOP)
		self.viewBottomRightButton.pack(in_=self.rightViewButtons, side=tk.TOP)
		
		self.leftViewButtons.pack(in_=self.fourViewButtons, side=tk.LEFT)
		self.rightViewButtons.pack(in_=self.fourViewButtons, side=tk.LEFT)
		
		self.viewLabel.pack(in_=self.viewItem, side=tk.TOP)
		self.fourViewButtons.pack(in_=self.viewItem, side=tk.TOP)
		self.viewFullButton.pack(in_=self.viewItem, side=tk.TOP)
		
		self.contrastUpButton.pack(in_=self.contrastButtons, side=tk.TOP)
		self.contrastDownButton.pack(in_=self.contrastButtons, side=tk.TOP)
		
		self.contrastLabel.pack(in_=self.contrastItem, side=tk.TOP)
		self.contrastButtons.pack(in_=self.contrastItem, side=tk.TOP)
		
		self.dotsUpButton.pack(in_=self.dotsButtons, side=tk.TOP)
		self.dotsDownButton.pack(in_=self.dotsButtons, side=tk.TOP)
		
		self.dotsLabel.pack(in_=self.dotsItem, side=tk.TOP)
		self.dotsButtons.pack(in_=self.dotsItem, side=tk.TOP)
		
		self.blobsUpButton.pack(in_=self.blobsButtons, side=tk.TOP)
		self.blobsDownButton.pack(in_=self.blobsButtons, side=tk.TOP)
		
		self.blobsLabel.pack(in_=self.blobsItem, side=tk.TOP)
		self.blobsButtons.pack(in_=self.blobsItem, side=tk.TOP)
		
		self.thresholdsLabel.pack(in_=self.thresholdEditItem, side=tk.TOP)
		self.editButton.pack(in_=self.thresholdEditItem, side=tk.TOP)
		self.resetButton.pack(in_=self.thresholdEditItem, side=tk.TOP)
		
		self.window.protocol("WM_DELETE_WINDOW", quit)
		self.window.bind("<Return>", self.finishWithReturnKey)
		self.window.bind("<space>", self.cycleViews)
		self.window.bind("<Up>", self.lowerDotThresholdScaleDownWithUpKey)
		self.window.bind("<Down>", self.lowerDotThresholdScaleUpWithDownKey)
		self.window.bind("<Left>", self.upperDotThresholdScaleUpWithLeftKey)
		self.window.bind("<Right>", self.upperDotThresholdScaleDownWithRightKey)
		
		self.window.mainloop()
	
	def cycleViews(self, event):
		self.index += 1
		self.index %= 5
		self.showCorrectImage(self.index)
	
	def displayCorrectMarkerSize(self, index):
		if self.index == 0:
			self.dotScatter.set_sizes([5 * self.dotSize])
		else:
			self.dotScatter.set_sizes([50 * self.dotSize])
	
	def edit(self):
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
		self.canvas.draw()
	
	def finish(self):
		self.window.destroy()
		self.window.quit()
	
	def finishWithReturnKey(self, event):
		self.finish()
	
	def lowerDotThresholdScaleDown(self):
		self.image.decreaseLowerDotThreshScale()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		self.canvas.draw()
	
	def lowerDotThresholdScaleDownWithUpKey(self, event):
		self.lowerDotThresholdScaleDown()

	def lowerDotThresholdScaleUp(self):
		self.image.increaseLowerDotThreshScale()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		self.canvas.draw()
	
	def lowerDotThresholdScaleUpWithDownKey(self, event):
		self.lowerDotThresholdScaleUp()
	
	def showCorrectImage(self, index):
		self.displayCorrectMarkerSize(index)
		self.axes.set_xbound(self.xBounds[index])
		self.axes.set_ybound(self.yBounds[index])
		self.canvas.draw()

	def showWholeImage(self):
		self.index = 0
		self.showCorrectImage(self.index)

	def showTopLeftRegion(self):
		self.index = 1
		self.showCorrectImage(self.index)

	def showTopRightRegion(self):
		self.index = 2
		self.showCorrectImage(self.index)

	def showBottomLeftRegion(self):
		self.index = 3
		self.showCorrectImage(self.index)

	def showBottomRightRegion(self):
		self.index = 4
		self.showCorrectImage(self.index)
	
	def skip(self):
		self.image.skipped = True
		self.finish()

	def resetThreshScalesToDefaultValues(self):
		self.image.setThresholds(self.defaultThresholds)
		self.image.dotCoords, self.image.blobCoords = self.image.getCoords()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		self.canvas.draw()
	
	def upperContrastDown(self):
		value = self.userSettings.upperContrast - cfg.CONTRAST_DELTA
		value = round(value, 1)
		self.userSettings.upperContrast = value
		self.dataPlot.set_clim(self.userSettings.lowerContrast, 
								self.userSettings.upperContrast * np.std(self.data))
		self.canvas.draw()
	
	def upperContrastUp(self):
		value = self.userSettings.upperContrast + cfg.CONTRAST_DELTA
		value = round(value, 1)
		self.userSettings.upperContrast = value
		self.dataPlot.set_clim(self.userSettings.lowerContrast, 
								self.userSettings.upperContrast * np.std(self.data))
		self.canvas.draw()
	
	def upperDotThresholdScaleDown(self):
		self.image.decreaseUpperDotThreshScale()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		self.canvas.draw()
	
	def upperDotThresholdScaleDownWithRightKey(self, event):
		self.upperDotThresholdScaleDown()

	def upperDotThresholdScaleUp(self):
		self.image.increaseUpperDotThreshScale()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		self.canvas.draw()
	
	def upperDotThresholdScaleUpWithLeftKey(self, event):
		self.upperDotThresholdScaleUp()

class UserSettings:
	def __init__(self):
		self.window = tk.Tk()
		self.window.title("Dot Scanner - Configurations")
		windowWidth, _ = getWindowDimensions()
		self.window.geometry(f"{windowWidth}x170+{cfg.WINDOW_X}+{cfg.WINDOW_Y}")

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
		self.lowerContrast = round(cfg.LOWER_CONTRAST, 1)
		self.upperContrast = round(cfg.UPPER_CONTRAST, 1)
		self.saveFigures = cfg.SAVE_FIGURES
		self.removeEdgeFrames = cfg.REMOVE_EDGE_FRAMES
		self.skipsAllowed = round(cfg.SKIPS_ALLOWED, 0)
		
		self.labelSelectedPath = tk.Label(self.window, text="Select a file or folder for analysis", 
											fg="red")
		if self.filepathSet:
			self.labelSelectedPath.configure(text=self.filepath, bg="white", fg="black")
		self.labelSelectedPath.pack()
		
		self.navigation = tk.Frame(self.window)
		self.navigation.pack()
		
		self.labelBrowse = tk.Label(self.window, text="Browse:")
		
		self.buttonSelectFile = tk.Button(self.window, text="File", command=self.browseFiles)

		self.buttonSelectFolder = tk.Button(self.window, text="Folder", command=self.browseFolders)
		
		self.labelProgram = tk.Label(self.window, text="Program:")

		self.menuProgramSelectVar = tk.StringVar(self.window)
		self.menuProgramSelectVar.set(self.program.capitalize()) # default value
		self.menuProgramSelect = tk.OptionMenu(self.window, self.menuProgramSelectVar, "Density", 
												"Lifetime", command=self.show)
		
		self.checkboxSaveFigsVar = tk.BooleanVar()
		self.checkboxSaveFigs = tk.Checkbutton(self.window, text='Save figures', 
												variable=self.checkboxSaveFigsVar, onvalue=True, 
												offvalue=False, command=self.setSaveFigs)
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
		self.buttonSelectStartingImage = tk.Button(self.window, text="Browse...", 
													command=self.browseStartingImage)

		self.labelSkipsAllowed = tk.Label(self.window, text="Skips allowed:")
		self.entrySkipsAllowed = tk.Entry(self.window, width=5)
		self.entrySkipsAllowed.insert(0, self.skipsAllowed)

		self.checkboxRemoveEdgeVar = tk.BooleanVar()
		self.checkboxRemoveEdge = tk.Checkbutton(self.window, text='Remove edge frames', 
													variable=self.checkboxRemoveEdgeVar, 
													onvalue=True, offvalue=False, 
													command=self.setRemoveEdge)
		self.checkboxRemoveEdgeVar.set(self.removeEdgeFrames)
		
		self.labelStartImage.pack(in_=self.lifetimeOptions, side=tk.LEFT)
		self.buttonSelectStartingImage.pack(in_=self.lifetimeOptions, side=tk.LEFT)
		self.labelSkipsAllowed.pack(in_=self.lifetimeOptions, side=tk.LEFT)
		self.entrySkipsAllowed.pack(in_=self.lifetimeOptions, side=tk.LEFT)
		self.checkboxRemoveEdge.pack(in_=self.lifetimeOptions, side=tk.LEFT)

		self.buttonNext = tk.Button(self.window, text="Next", command=self.done, fg="blue")
		self.buttonNext.pack()
		
		self.labelStartImageWarning = tk.Label(self.window, 
												text=f"WARNING: {strings.fileNumberingException}", 
												fg="red")
		
		self.show(click=self.program.capitalize())
		
		self.window.protocol("WM_DELETE_WINDOW", quit)
		self.window.bind("<Return>", self.doneWithReturnKey)
		
		self.window.mainloop()

	def browseFiles(self):
		chosenFile = filedialog.askopenfilename(initialdir=self.filepath, 
												title="Select a file to analyze")
		if chosenFile != "":
			self.filepath = chosenFile
			displayedFilename = chosenFile
			if len(chosenFile) > 50:
				displayedFilename = "..." + chosenFile[-50:]
			self.labelSelectedPath.configure(text=displayedFilename, bg="white", fg="black")
		self.window.focus_force()

	def browseFolders(self):
		chosenFolder = filedialog.askdirectory(initialdir=self.filepath, 
												title="Select a folder with images to analyze")
		if chosenFolder != "":
			self.filepath = chosenFolder
			displayedFolder = chosenFolder
			if len(chosenFolder) > 50:
				displayedFolder = "..." + chosenFolder[-50:]
			self.labelSelectedPath.configure(text=displayedFolder, bg="white", fg="black")
		self.window.focus_force()

	def browseStartingImage(self):
		chosenFilepath = filedialog.askopenfilename(initialdir=self.filepath, 
									title="Select the starting image for the lifetime measurement")
		chosenImage = os.path.basename(chosenFilepath)
		if chosenImage != "":
			try:
				trailingNumberString = str(files.getTrailingNumber(chosenImage))
				if len(trailingNumberString) > 10:
					trailingNumberString = "..." + trailingNumberString[-10:]
				self.buttonSelectStartingImage.config(text=trailingNumberString, fg="darkgreen")
				self.startImage = chosenImage
				self.lifetimeOptions.pack_forget()
				self.buttonNext.pack_forget()
				self.labelStartImageWarning.pack_forget()
				self.lifetimeOptions.pack()
				self.buttonNext.pack()
			except:
				self.buttonSelectStartingImage.config(text="Browse...", fg="black")
				self.startImage = ""
				self.labelStartImageWarning.pack()
		self.window.focus_force()
	
	def done(self):        
		self.dotSize = int(self.entryDotSize.get())
		self.blobSize = int(self.entryBlobSize.get())
		self.lowerDotThresh = round(float(self.entryThreshold1.get()), 1)
		self.upperDotThresh = round(float(self.entryThreshold2.get()), 1)
		self.lowerBlobThresh = round(float(self.entryThreshold3.get()), 1)
		self.skipsAllowed = int(self.entrySkipsAllowed.get())
		self.thresholds = (self.lowerDotThresh, self.upperDotThresh, self.lowerBlobThresh)
		self.window.destroy()
	
	def doneWithReturnKey(self, event):        
		self.done()

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
			self.buttonNext.pack_forget()
			self.lifetimeOptions.pack()
			self.buttonNext.pack()
		else:
			self.program = "density"
			self.lifetimeOptions.pack_forget()
			self.buttonNext.pack_forget()
			self.buttonNext.pack()

def createPlots(data, userSettings):
	figure, axes = pl.subplots()
	dataPlot = axes.imshow(data, origin="lower", cmap="gray", vmin=userSettings.lowerContrast, 
							vmax=userSettings.upperContrast * np.std(data))
	dotScatter = axes.scatter([None], [None], s=5 * userSettings.dotSize, facecolors="none", 
								edgecolors=cfg.DOT_COLOR, linewidths=cfg.DOT_THICKNESS)
	blobScatter = axes.scatter([None], [None], s=2 * userSettings.blobSize, facecolors="none",
								edgecolor=cfg.BLOB_COLOR, linewidths=cfg.BLOB_THICKNESS)
	return figure, axes, dataPlot, dotScatter, blobScatter

def createWindow(title):
	window = tk.Tk()
	window.title(title)
	
	width, height = getWindowDimensions()
	geometry = f"{width}x{height}+{cfg.WINDOW_X}+{cfg.WINDOW_Y}"
	window.geometry(geometry)
	return window

def getWindowDimensions():
	if cfg.DYNAMIC_WINDOW:
		window = tk.Tk()
		height = window.winfo_screenheight() - 180
		width = height + 100
		window.destroy()
	else:
		height = cfg.WINDOW_HEIGHT
		width = cfg.WINDOW_WIDTH
	return width, height

def printProgressBar (iteration, total, prefix = "", suffix = "", decimals = 1, 
						barLength = 50, fill = "█", printEnd = "\r"):
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(barLength * iteration // total)
	bar = fill * filledLength + "-" * (barLength - filledLength)
	print(f"\r{prefix} |{bar}| {percent}% {suffix}", end = printEnd)
	
	if iteration == total: 
		print()
