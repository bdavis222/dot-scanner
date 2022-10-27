import dotscanner.ui.window as ui
import settings.config as cfg
import settings.configmanagement as cm
import tkinter as tk
from tkinter import filedialog

class DefaultUserSettingsEditor:
	def __init__(self, userSettings):
		self.window = ui.createDefaultConfigurationsEditorWindow()
		
		self.userSettings = userSettings
		self.filepath = cfg.FILEPATH
		
		self.filepathFrame = tk.Frame(self.window)
		
		self.labelFilepath = tk.Label(self.window, text="Filepath:")
		self.labelSelectedPath = tk.Label(self.window, text="No default filepath selected", 
											bg="white", fg="lightgray")
		self.labelSaved = tk.Label(self.window, text="Saved!", fg="green")
		if self.filepath not in ["", " ", "/"]:
			self.labelSelectedPath.configure(text=self.filepath, bg="white", fg="black")
		
		self.labelFilepath.pack(in_=self.filepathFrame, side=tk.LEFT)
		self.labelSelectedPath.pack(in_=self.filepathFrame, side=tk.LEFT)
		
		self.navigation = tk.Frame(self.window)
		
		self.labelBrowse = tk.Label(self.window, text="Default filepath:")

		self.buttonSelectFolder = tk.Button(self.window, text="Browse...", 
											command=self.browseFolders)
		self.buttonClearDefaultPath = tk.Button(self.window, text="Clear", fg="red", 
											command=self.clearDefaultPath)
		self.buttonSaveDefaultPath = tk.Button(self.window, text="Save", fg="blue", 
											command=self.saveDefaultPath)
		
		self.labelBrowse.pack(in_=self.navigation, side=tk.LEFT)
		self.buttonSelectFolder.pack(in_=self.navigation, side=tk.LEFT)
		self.buttonClearDefaultPath.pack(in_=self.navigation, side=tk.LEFT)
		self.buttonSaveDefaultPath.pack(in_=self.navigation, side=tk.LEFT)
		
		self.spacer = tk.Label(self.window, text=" ")
		
		self.configFileButtons = tk.Frame(self.window)
		
		self.configFileLabel = tk.Label(self.window, text="Config file:")
		self.buttonEdit = tk.Button(self.window, text="Edit...", 
									command=cm.showEditConfigFileDialog)
		self.buttonReset = tk.Button(self.window, text="Reset", fg="red", 
									command=cm.showResetConfigFileDialog)
		
		self.configFileLabel.pack(in_=self.configFileButtons, side=tk.LEFT)
		self.buttonEdit.pack(in_=self.configFileButtons, side=tk.LEFT)
		self.buttonReset.pack(in_=self.configFileButtons, side=tk.LEFT)
				
		self.filepathFrame.pack()
		self.navigation.pack()
		self.spacer.pack()
		self.configFileButtons.pack()
		
		self.window.mainloop()

	def browseFolders(self):
		chosenFolder = filedialog.askdirectory(initialdir=self.filepath, 
												title="Select a default starting folder")
		if chosenFolder not in ["", " ", "/"]:
			self.filepath = chosenFolder
			displayedFolder = chosenFolder
			if len(chosenFolder) > 50:
				displayedFolder = "..." + chosenFolder[-50:]
			self.labelSelectedPath.configure(text=displayedFolder, bg="white", fg="black")
		self.unshowSavedText()
		self.window.focus_force()
	
	def clearDefaultPath(self):
		self.unshowSavedText()
		if self.filepath in ["", " ", "/"]:
			return
		self.filepath = "/"
		self.labelSelectedPath.configure(text="No default filepath selected", bg="white", 
											fg="lightgray")
	
	def saveDefaultPath(self):
		import settings.configmanagement as cm
		
		configFilePath = cm.getConfigFilePath()
		
		with open(configFilePath, "r") as file:
			data = file.readlines()
		
		data[2] = f'FILEPATH = "{self.filepath}"\n'
		
		with open(configFilePath, "w") as file:
			file.writelines(data)
		
		self.showSavedText()
		self.userSettings.filepath = self.filepath
		self.userSettings.showFilepath()
	
	def showSavedText(self):
		self.labelFilepath.pack_forget()
		self.labelSelectedPath.pack_forget()
		self.labelSaved.pack_forget()
		
		self.filepathFrame.pack_forget()
		self.navigation.pack_forget()
		self.spacer.pack_forget()
		self.configFileButtons.pack_forget()
		
		self.labelFilepath.pack(in_=self.filepathFrame, side=tk.LEFT)
		self.labelSelectedPath.pack(in_=self.filepathFrame, side=tk.LEFT)
		self.labelSaved.pack(in_=self.filepathFrame, side=tk.LEFT)
		
		self.filepathFrame.pack()
		self.navigation.pack()
		self.spacer.pack()
		self.configFileButtons.pack()
	
	def unshowSavedText(self):
		self.labelFilepath.pack_forget()
		self.labelSelectedPath.pack_forget()
		self.labelSaved.pack_forget()
		
		self.filepathFrame.pack_forget()
		self.navigation.pack_forget()
		self.spacer.pack_forget()
		self.configFileButtons.pack_forget()
		
		self.labelFilepath.pack(in_=self.filepathFrame, side=tk.LEFT)
		self.labelSelectedPath.pack(in_=self.filepathFrame, side=tk.LEFT)
		
		self.filepathFrame.pack()
		self.navigation.pack()
		self.spacer.pack()
		self.configFileButtons.pack()
