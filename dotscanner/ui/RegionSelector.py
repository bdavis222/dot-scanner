import dotscanner.dataprocessing as dp
import dotscanner.strings as strings
import dotscanner.ui.window as ui
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class RegionSelector:
	def __init__(self, image, userSettings, skipButton=True):
		ui.setupWindow()
		
		self.xList = []
		self.yList = []
		
		self.image = image
		self.dotSize = userSettings.dotSize
		self.blobSize = userSettings.blobSize
		self.data = image.data
		
		self.window = ui.createPlotWindow(strings.regionSelectorWindowTitle)
		
		self.figure, self.axes, _, self.dotScatter, self.blobScatter = ui.createPlots(self.data, 
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
		self.buttonBar.pack(side=tk.LEFT, expand=False)
		self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		
		self.polygonLabel = tk.Label(self.window, text="Polygon:")
		self.polygonLabel.pack(in_=self.buttonBar, side=tk.TOP)
		
		self.resetButton = tk.Button(self.window, text="Reset", command=self.reset, fg="red")
		self.resetButton.pack(in_=self.buttonBar, side=tk.TOP)
		
		self.spacer = tk.Label(self.window, text="    ---------    ", fg="lightgray")
		self.spacer.pack(in_=self.buttonBar, side=tk.TOP)
		
		if skipButton:
			self.window.bind("<Escape>", self.skipWithEscapeKey)
			self.skipButton = tk.Button(self.window, text="Skip", command=self.skip, 
										fg="darkgoldenrod")
			self.skipButton.pack(in_=self.buttonBar, side=tk.TOP)
		
		self.doneButton = tk.Button(self.window, text="Done", command=self.finish, fg="blue", 
									font=tk.font.Font(weight="bold"))
		self.doneButton.pack(in_=self.buttonBar, side=tk.TOP)
		
		self.window.protocol("WM_DELETE_WINDOW", quit)
		self.window.bind("<q>", self.quitWithQKey)
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
		self.window.after(100, self.window.quit)
	
	def finishWithReturnKey(self, event):
		self.finish()
	
	def quitWithQKey(self, event):
		quit()
		
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
		self.clickMarkerBackdrop.set_offsets([None, None])
		self.clickMarker.set_offsets([None, None])
		self.clickMarkerBackdrop.figure.canvas.draw_idle()
		self.clickMarker.figure.canvas.draw_idle()
	
	def skip(self):
		self.image.skipped = True
		self.window.destroy()
		self.window.quit()
	
	def skipWithEscapeKey(self, event):
		self.skip()
