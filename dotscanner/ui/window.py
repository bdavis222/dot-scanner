import dotscanner.strings as strings
import settings.config as cfg
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as pl
import numpy as np
import os
import tkinter as tk

def createPlots(data, userSettings):
	windowScaling = getWindowScaling()
	figure, axes = pl.subplots()
	dataPlot = axes.imshow(data, origin="lower", cmap="gray", vmin=userSettings.lowerContrast, 
							vmax=userSettings.upperContrast * np.std(data))
	dotScatter = axes.scatter([None], [None], s=5 * userSettings.dotSize * windowScaling, 
								facecolors="none", edgecolors=cfg.DOT_COLOR, 
								linewidths=cfg.DOT_THICKNESS)
	blobScatter = axes.scatter([None], [None], s=2 * userSettings.blobSize * windowScaling, 
								facecolors="none", edgecolor=cfg.BLOB_COLOR, 
								linewidths=cfg.BLOB_THICKNESS)
	return figure, axes, dataPlot, dotScatter, blobScatter

def createConfigurationsWindow():
	window = tk.Tk()
	window.title(strings.configurationsWindowTitle)
	width, _ = getWindowDimensions()
	if width > 650:
		width = 650
	window.geometry(f"{width}x170+{cfg.WINDOW_X}+{cfg.WINDOW_Y}")
	return window

def createDefaultConfigurationsEditorWindow():
	window = tk.Tk()
	window.title(strings.defaultConfigurationsEditorWindowTitle)
	width, _ = getWindowDimensions()
	if width > 650:
		width = 650
	window.geometry(f"{width}x170+{cfg.WINDOW_X + 20}+{cfg.WINDOW_Y + 20}")
	return window

def createPlotWindow(title):
	window = tk.Tk()
	window.title(title)
	width, height = getWindowDimensions()
	geometry = f"{height + 88}x{height}+{cfg.WINDOW_X}+{cfg.WINDOW_Y}" # buttonBar width = 88
	window.geometry(geometry)
	return window

def getWindowDimensions():
	if cfg.DYNAMIC_WINDOW:
		window = tk.Tk()
		height = window.winfo_screenheight() - 180
		detectedWidth = window.winfo_screenwidth() - 180
		
		if height + 88 < detectedWidth: # buttonBar width = 88
			width = height + 88
		else:
			width = detectedWidth
		
		window.destroy()
	
	else:
		height = cfg.WINDOW_HEIGHT
		width = cfg.WINDOW_WIDTH
	
	return width, height

def getWindowScaling():
	_, height = getWindowDimensions()
	return height / 550

def printProgressBar (iteration, total, prefix = "", suffix = "", decimals = 1, 
						barLength = 50, fill = "█", printEnd = "\r"):
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(barLength * iteration // total)
	bar = fill * filledLength + "-" * (barLength - filledLength)
	print(f"\r{prefix} |{bar}| {percent}% {suffix}", end = printEnd)
	
	if iteration == total: 
		print()

def setupWindow():
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
