import dotscanner.dataprocessing as dp
import dotscanner.strings as strings
import dotscanner.ui.window as ui
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import tkinter as tk

class ThresholdAdjuster:
	def __init__(self, image, userSettings, skipButton=True):
		ui.setupWindow()
		
		self.index = 0
		self.skipButtonExists = skipButton
		
		
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
		
		self.window = ui.createPlotWindow(strings.thresholdAdjusterWindowTitle)
		self.windowScaling = ui.getWindowScaling()
		
		self.figure, self.axes, self.dataPlot, self.dotScatter, self.blobScatter = ui.createPlots(
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
		
		self.viewLabel = tk.Label(self.window, text="View:")
		self.viewTopLeftButton = tk.Button(self.window, text="⌜", command=self.showTopLeftRegion)
		self.viewBottomLeftButton = tk.Button(self.window, text="⌞", 
												command=self.showBottomLeftRegion)
		self.viewTopRightButton = tk.Button(self.window, text="⌝", command=self.showTopRightRegion)
		self.viewBottomRightButton = tk.Button(self.window, text="⌟", 
												command=self.showBottomRightRegion)
		self.viewFullButton = tk.Button(self.window, text="Full", command=self.showWholeImage)
		
		self.contrastLabel = tk.Label(self.window, text="Contrast:")
		self.contrastUpButton = tk.Button(self.window, text="ʌ", command=self.upperContrastDown)
		self.contrastDownButton = tk.Button(self.window, text="v", command=self.upperContrastUp)
		
		self.dotsLabel = tk.Label(self.window, text="Dots:")
		self.dotsUpButton = tk.Button(self.window, text="ʌ", command=self.lowerDotThresholdScaleDown)
		self.dotsDownButton = tk.Button(self.window, text="v", command=self.lowerDotThresholdScaleUp)
		
		self.blobsLabel = tk.Label(self.window, text="Blobs:")
		self.blobsUpButton = tk.Button(self.window, text="ʌ", command=self.upperDotThresholdScaleDown)
		self.blobsDownButton = tk.Button(self.window, text="v", command=self.upperDotThresholdScaleUp)
		
		self.thresholdsLabel = tk.Label(self.window, text="Thresholds:")
		
		self.editButton = tk.Button(self.window, text="Edit", command=self.edit)
		
		self.resetButton = tk.Button(self.window, text="Reset", 
										command=self.resetThreshScalesToDefaultValues)
		
		self.doneButton = tk.Button(self.window, text="Done", command=self.finish, fg="blue", 
									font=tk.font.Font(weight="bold"))
		
		self.buttonBar.pack(side=tk.LEFT, expand=False)
		self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		self.viewItem.pack(in_=self.buttonBar, side=tk.TOP, pady=(0, 5))
		self.contrastItem.pack(in_=self.buttonBar, side=tk.TOP, pady=5)
		self.dotsItem.pack(in_=self.buttonBar, side=tk.TOP, pady=5)
		self.blobsItem.pack(in_=self.buttonBar, side=tk.TOP, pady=5)
		self.thresholdEditItem.pack(in_=self.buttonBar, side=tk.TOP, pady=(5, 0))
		self.spacer = tk.Label(self.window, text="---------", fg="lightgray")
		self.spacer.pack(in_=self.buttonBar, side=tk.TOP)
		if self.skipButtonExists:
			self.window.bind("<Escape>", self.skipWithEscapeKey)
			self.skipButton = tk.Button(self.window, text="Skip", command=self.skip, 
										fg="darkgoldenrod")
			self.skipButton.pack(in_=self.buttonBar, side=tk.TOP)
		self.doneButton.pack(in_=self.buttonBar, side=tk.TOP)
		
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
		
		self.editSpacer = tk.Label(self.window, text="---------", fg="lightgray")
		
		self.entryThresholdLabel1 = tk.Label(self.window, text="Dot lower:")
		self.entryThreshold1 = tk.Entry(self.window, width=5)
		self.entryThreshold1.insert(0, userSettings.lowerDotThresh)
		
		self.entryThresholdLabel2 = tk.Label(self.window, text="Dot upper:")
		self.entryThreshold2 = tk.Entry(self.window, width=5)
		self.entryThreshold2.insert(0, userSettings.upperDotThresh)
		
		self.entryThresholdLabel3 = tk.Label(self.window, text="Blob lower:")
		self.entryThreshold3 = tk.Entry(self.window, width=5)
		self.entryThreshold3.insert(0, userSettings.lowerBlobThresh)
		
		self.editDoneButton = tk.Button(self.window, text="Done", command=self.editFinish, 
										fg="blue", font=tk.font.Font(weight="bold"))
		
		self.window.protocol("WM_DELETE_WINDOW", quit)
		self.window.bind("<q>", self.quitWithQKey)
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
			self.dotScatter.set_sizes([5 * self.dotSize * self.windowScaling])
		else:
			self.dotScatter.set_sizes([50 * self.dotSize * self.windowScaling])
	
	def edit(self):
		self.window.unbind("<Up>")
		self.window.unbind("<Down>")
		self.window.unbind("<Left>")
		self.window.unbind("<Right>")
		self.window.unbind("<Return>")
		self.window.bind("<Return>", self.editFinishWithReturnKey)
		
		self.dotsItem.pack_forget()
		self.blobsItem.pack_forget()
		self.thresholdEditItem.pack_forget()
		self.spacer.pack_forget()
		if self.skipButtonExists:
			self.skipButton.pack_forget()
		self.doneButton.pack_forget()
		
		self.editSpacer.pack(in_=self.buttonBar, side=tk.TOP)
		self.entryThresholdLabel1.pack(in_=self.buttonBar, side=tk.TOP, pady=(0, 5))
		self.entryThreshold1.pack(in_=self.buttonBar, side=tk.TOP, pady=5)
		self.entryThresholdLabel2.pack(in_=self.buttonBar, side=tk.TOP, pady=5)
		self.entryThreshold2.pack(in_=self.buttonBar, side=tk.TOP, pady=5)
		self.entryThresholdLabel3.pack(in_=self.buttonBar, side=tk.TOP, pady=5)
		self.entryThreshold3.pack(in_=self.buttonBar, side=tk.TOP, pady=5)
		self.editDoneButton.pack(in_=self.buttonBar, side=tk.TOP, pady=(5, 0))
		
		self.window.update()
	
	def editFinish(self):
		self.window.unbind("<Return>")
		self.window.bind("<Up>", self.lowerDotThresholdScaleDownWithUpKey)
		self.window.bind("<Down>", self.lowerDotThresholdScaleUpWithDownKey)
		self.window.bind("<Left>", self.upperDotThresholdScaleUpWithLeftKey)
		self.window.bind("<Right>", self.upperDotThresholdScaleDownWithRightKey)
		self.window.bind("<Return>", self.finishWithReturnKey)
		
		self.editSpacer.pack_forget()
		self.entryThresholdLabel1.pack_forget()
		self.entryThreshold1.pack_forget()
		self.entryThresholdLabel2.pack_forget()
		self.entryThreshold2.pack_forget()
		self.entryThresholdLabel3.pack_forget()
		self.entryThreshold3.pack_forget()
		self.editDoneButton.pack_forget()
		
		self.dotsItem.pack(in_=self.buttonBar, side=tk.TOP, pady=5)
		self.blobsItem.pack(in_=self.buttonBar, side=tk.TOP, pady=5)
		self.thresholdEditItem.pack(in_=self.buttonBar, side=tk.TOP, pady=(5, 0))
		self.spacer.pack(in_=self.buttonBar, side=tk.TOP)
		if self.skipButtonExists:
			self.skipButton.pack(in_=self.buttonBar, side=tk.TOP)
		self.doneButton.pack(in_=self.buttonBar, side=tk.TOP)
		
		try:
			numberIn1 = round(float(self.entryThreshold1.get()), 1)
			numberIn2 = round(float(self.entryThreshold2.get()), 1)
			numberIn3 = round(float(self.entryThreshold3.get()), 1)
			newThresholds = (numberIn1, numberIn2, numberIn3)
		
		except:
			self.setThresholdEntries(self.image.thresholds)
			print(strings.invalidThresholdEdit)
			return
		
		self.image.setThresholds(newThresholds)
		self.setThresholdEntries(self.image.thresholds)
		
		self.image.dotCoords, self.image.blobCoords = self.image.getCoords()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		self.canvas.draw()
	
	def editFinishWithReturnKey(self, event):
		self.editFinish()
	
	def finish(self):
		self.window.destroy()
		self.window.quit()
	
	def finishWithReturnKey(self, event):
		self.finish()
	
	def lowerDotThresholdScaleDown(self):
		self.image.decreaseLowerDotThreshScale()
		self.setThresholdEntries(self.image.thresholds)
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		self.canvas.draw()
	
	def lowerDotThresholdScaleDownWithUpKey(self, event):
		self.lowerDotThresholdScaleDown()

	def lowerDotThresholdScaleUp(self):
		self.image.increaseLowerDotThreshScale()
		self.setThresholdEntries(self.image.thresholds)
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		self.canvas.draw()
	
	def lowerDotThresholdScaleUpWithDownKey(self, event):
		self.lowerDotThresholdScaleUp()
	
	def setThresholdEntries(self, thresholds):
		thresh1, thresh2, thresh3 = thresholds
		self.entryThreshold1.delete(0, tk.END)
		self.entryThreshold2.delete(0, tk.END)
		self.entryThreshold3.delete(0, tk.END)
		self.entryThreshold1.insert(0, thresh1)
		self.entryThreshold2.insert(0, thresh2)
		self.entryThreshold3.insert(0, thresh3)
	
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
	
	def skipWithEscapeKey(self, event):
		self.skip()
	
	def quitWithQKey(self, event):
		quit()

	def resetThreshScalesToDefaultValues(self):
		self.image.setThresholds(self.defaultThresholds)
		self.setThresholdEntries(self.defaultThresholds)
		
		self.image.dotCoords, self.image.blobCoords = self.image.getCoords()
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		self.canvas.draw()
	
	def upperContrastDown(self):
		self.userSettings.decreaseUpperContrast()
		self.dataPlot.set_clim(self.userSettings.lowerContrast, 
								self.userSettings.upperContrast * np.std(self.data))
		self.canvas.draw()
	
	def upperContrastUp(self):
		self.userSettings.increaseUpperContrast()
		self.dataPlot.set_clim(self.userSettings.lowerContrast, 
								self.userSettings.upperContrast * np.std(self.data))
		self.canvas.draw()
	
	def upperDotThresholdScaleDown(self):
		self.image.decreaseUpperDotThreshScale()
		self.setThresholdEntries(self.image.thresholds)
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		self.canvas.draw()
	
	def upperDotThresholdScaleDownWithRightKey(self, event):
		self.upperDotThresholdScaleDown()

	def upperDotThresholdScaleUp(self):
		self.image.increaseUpperDotThreshScale()
		self.setThresholdEntries(self.image.thresholds)
		dp.setScatterData(self.image.dotCoords, self.image.blobCoords, self.dotScatter, 
							self.blobScatter)
		self.canvas.draw()
	
	def upperDotThresholdScaleUpWithLeftKey(self, event):
		self.upperDotThresholdScaleUp()
