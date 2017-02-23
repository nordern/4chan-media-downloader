#!/usr/bin/env python3

"""
Interesting comments about this code
"""

# per PEP8, all imports go on separate lines -NYT
import os
import threading
import subprocess
import platform
from functools import partial

# try python2 tkinter imports, if that fails try python3 -NYT
try:
	import Tkinter as tk
	import ttk
	from tkMessageBox import showerror
	from urllib import urlretrieve
except ImportError:
	import tkinter as tk
	from tkinter import ttk
	from tkinter.messagebox import showerror
	from urllib.request import urlretrieve
try:
	import bs4
	import requests
except:
	# rather than an error message, you could add the code to install these modules
	# remember to install to user space to allow for systems that require admin for system installation
	# -NYT
	tk.Tk().withdraw()
	showerror("Modules Missing", "This program requires the requests and beautifulsoup modules to run.\n\nRun this command from the command line to install them:\n\n  pip install --user requests bs4")
	raise


# specify preferred download location here
# Windows filenames must be raw strings -NYT
media_dl_location = r"D:\Downloads"

# single source of truth - if you want to make a change to your program you should only need to change one place
# one way to do that is to store the values in a dictionary: -NYT
entry_style = dict(
	bd=0,
	width=55,
	bg="#FAFAFA",
	highlightbackground="#C8C8C8",
	highlightcolor="#C8C8C8",
	highlightthickness=1
	)

label_style = dict(fg="#696969")

def open_file(path):
	"""cross platform file explorer opener"""
	if platform.system() == "Windows":
		os.startfile(path)
	elif platform.system() == "Darwin":
		subprocess.Popen(["open", path])
	else:
		subprocess.Popen(["xdg-open", path])

# another way to ssot is to make a subclass that bakes in the defaults -NYT
class ImageButton(tk.Button):
	"""a version of a button that includes an icon"""
	def __init__(self, master, file, **kwargs):
		self.img = tk.PhotoImage(file=file)
		self.img = self.img.subsample(1,1)
		tk.Button.__init__(self, master,
			image=self.img,
			bd=0,
			compound="left",
			padx=4,
			pady=4,
			**kwargs)

class StatusLabel(tk.Label):
	"""we can move the configuration code to the widget itself"""
	def __init__(self, master=None, **kwargs):
		tk.Label.__init__(self, master, **kwargs)

	def normal(self, text):
		self.config(text=text, font=("Ebrima", 9), **label_style)

	def error(self, text):
		self.config(text=text, font=("Ebrima", 9, 'bold'), fg="red")

class ButtonFrame(tk.Frame):
	def __init__(self, master=None, **kwargs):
		tk.Frame.__init__(self, master, **kwargs)

		# we will use the pack layout to automatically stack the buttons in -NYT

		search_button = ImageButton(self,
			file="imgs/magnifying-glass-search-button.png",
			text="  Search",
			command=master.start_search_thread)
		search_button.pack(side=tk.LEFT)

		dl_button = ImageButton(self,
			file="imgs/download-arrow.png",
			text="  Download",
			command=master.start_dl_thread)
		dl_button.pack(side=tk.LEFT)

		open_dest_button = ImageButton(self,
			file="imgs/file-folder.png",
			text="  Open",
			command=master.open_media_dl_loc)
		open_dest_button.pack(side=tk.LEFT)

class EntryFrame(tk.Frame):
	def __init__(self, master=None, **kwargs):
		tk.Frame.__init__(self, master, padx=5, pady=5, **kwargs)

		# We will lay this frame out on a grid, using the grid layout -NYT

		# url entry field
		label_url = tk.Label(self, text="URL ", **label_style)
		label_url.grid(row=0, column=0)
		self.url = tk.Entry(self, **entry_style)
		self.url.grid(row=0, column=1, pady=5)
		self.url.focus()

		# title entry field
		label_title = tk.Label(self, text="Title ", **label_style)
		label_title.grid(row=1, column=0)
		self.title = tk.Entry(self, **entry_style)
		self.title.grid(row=1, column=1, pady=5)

		# dest entry field
		label_destination = tk.Label(self, text="Dest. ", **label_style)
		label_destination.grid(row=2, column=0)
		self.dest = tk.Entry(self, **entry_style)
		self.dest.grid(row=2, column=1, pady=5)
		self.dest.insert(tk.INSERT, media_dl_location)

	def state(self, state):
		"""update the state of all the Entry widgets at once"""
		for entry in (self.url, self.title, self.dest):
			entry.config(state=state)

class ContextMenu(tk.Menu):
	def __init__(self, master=None, **kwargs):
		tk.Menu.__init__(self, master, tearoff=0, **kwargs)
		# partial is better than lambda. -NYT
		self.add_command(label="Cut", command=partial(self.run, "<<Cut>>"))
		self.add_command(label="Copy", command=partial(self.run, "<<Copy>>"))
		self.add_command(label="Paste", command=partial(self.run, "<<Paste>>"))

	def run(self, event):
		self.widget.event_generate(event)

	def show(self, event):
		self.widget = event.widget
		self.tk.call("tk_popup", self, event.x_root, event.y_root)

class GUI(tk.Frame):
	def __init__(self, master=None, **kwargs):
		tk.Frame.__init__(self, master, padx=5, pady=5, **kwargs)

		context_menu = ContextMenu(self)
		master.bind_class("Entry", "<Button-3><ButtonRelease-3>", context_menu.show)

		self.file_links = None

		self.make_ui() # separating this from __init__ sometimes helps to keep things neat -NYT

	def make_ui(self):
		self.buttons = ButtonFrame(self)
		self.buttons.pack(anchor=tk.W)

		self.entries = EntryFrame(self)
		self.entries.pack()

		self.status = StatusLabel(self)
		self.status.normal("Hit Search to find any media files, then Download to grab them ")
		self.status.pack(anchor=tk.W)

		self.progress = ttk.Progressbar(self,
			orient="horizontal",
			length=480,
			mode="determinate")
		self.progress.pack()

	def start_search_thread(self):
		media_links = threading.Thread(target=self.grab_media_links)
		media_links.start()

	def grab_media_links(self):
		chan_url = self.entries.url.get().strip()
		# we modify the exisitng Label, do not make a new one to cover the old one up -NYT
		self.status.normal("Searching "+chan_url)
		try:
			res = requests.get(chan_url)
			res.raise_for_status()
		except ValueError:
			self.status.error("ERROR: invalid URL")
			return # abort -NYT

		self.file_links = [] # use a self. name so that other methods can access this. -NYT
		schema = res.url.split('/')[0]
		soup = bs4.BeautifulSoup(res.text, "html.parser")
		elems = soup.findAll("div", attrs={'class': 'fileText'})
		for div in elems:
			self.file_links.append(schema+div.a["href"])
		self.status.normal("Found {} links".format(len(self.file_links)))

	def start_dl_thread(self):
		if self.file_links is None:
			self.status.error("ERROR: search for links first")
		elif not self.path():
			self.status.error("ERROR: No path defined")
		else:
			download = threading.Thread(target=self.dl_media_files)
			download.start()

	def path(self):
		# tiny little methods are very normal and good.
		# copy/pasting this snippet would be bad -NYT
		return os.path.join(self.entries.dest.get(), self.entries.title.get())

	def dl_media_files(self):
		self.status.normal("Downloading...")
		self.progress.config(maximum=len(self.file_links))
		self.progress.stop() # reset previous -NYT
		self.entries.state(tk.DISABLED)

		# make the dir if needed
		path = self.path()
		if not os.path.exists(path):
			os.makedirs(path)

		for link in self.file_links:
			name = os.path.split(link)[1]
			filename = os.path.join(path, name)

			if not os.path.isfile(filename):
				try:
					urlretrieve(link, filename)
				except Exception as inst:
					print(inst)
					self.status.normal("Encountered unknown error. Continuing.")
			self.progress.step(1)

		self.entries.state(tk.NORMAL)
		self.status.normal("Done")

	def open_media_dl_loc(self):
		# Since popen does not return an error, the exists check must be done here
		path = self.path()
		if not os.path.exists(path):
			self.status.error("ERROR: path does not exisit")
		else:
			open_file(path)

def main():
	root = tk.Tk()
	root.title("4chan Media Downloader")
	try:
		root.iconbitmap("imgs/favicon.ico")
	except:
		# loading an .ico file (Windows icon file) fails on Linux a lot
		print('icon load failed')
	window = GUI(root)
	window.pack()
	root.resizable(0,0)
	root.mainloop()

if __name__ == "__main__":
	main()
