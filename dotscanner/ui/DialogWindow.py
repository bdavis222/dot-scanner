import tkinter as tk

class DialogWindow:
	def __init__(self, title, message, positiveButtonText, negativeButtonText, positiveButtonAction, 
					negativeButtonAction=None, windowWidth=300, windowHeight=140, windowX=50, 
					windowY=70, positiveButtonColor="red"):		
		self.window = tk.Tk()
		self.window.title(title)
		self.window.geometry(f"{windowWidth}x{windowHeight}+{windowX}+{windowY}")
		
		self.positiveButtonAction = positiveButtonAction
				
		self.spacer = tk.Label(self.window, text=" ")
		
		self.messageText = tk.Label(self.window, text=message)
		
		self.spacer2 = tk.Label(self.window, text=" ")
		
		self.buttonsFrame = tk.Frame(self.window)
		
		self.positiveButton = tk.Button(self.window, text=positiveButtonText, 
										fg=positiveButtonColor, command=positiveButtonAction)
		
		if negativeButtonAction is None:
			self.negativeButton = tk.Button(self.window, text=negativeButtonText, 
											command=self.window.destroy)
			self.window.bind("<Escape>", self.closeWindowWithEscapeKey)
		else:
			self.negativeButton = tk.Button(self.window, text=negativeButtonText, 
											command=negativeButtonAction)
		
		self.negativeButton.pack(in_=self.buttonsFrame, side=tk.LEFT)
		self.positiveButton.pack(in_=self.buttonsFrame, side=tk.LEFT)
		
		self.spacer.pack()
		self.messageText.pack()
		self.spacer2.pack()
		self.buttonsFrame.pack()
		
		self.window.bind("<q>", self.quitWithQKey)
		self.window.bind("<w>", self.closeWindowWithWKey)
		self.window.bind("<Return>", self.positiveButtonWithReturnKey)
		
		
		self.window.mainloop()
	
	def closeWindowWithEscapeKey(self, event):
		self.window.destroy()
	
	def closeWindowWithWKey(self, event):
		self.window.destroy()
	
	def positiveButtonWithReturnKey(self, event):
		self.positiveButtonAction()
	
	def quitWithQKey(self, event):
		quit()
