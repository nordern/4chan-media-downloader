import os, time, urllib, threading, subprocess
import bs4, requests
from tkinter import *
import tkinter.ttk as ttk

# specify preferred download location here
media_dl_location = "D:\\Downloads\\"

root = Tk()
root.title("4chan Media Downloader")
root.iconbitmap("favicon.ico")
root.geometry("500x200")
root.grid_propagate(False)
root.resizable(0,0)

# url entry field
label_url = Label(root, text="URL ", fg="#696969")
label_url.place(x=10, y=50)

entry_url = Entry(root, bd=0, width=73, bg="#FAFAFA")
entry_url.config(highlightbackground="#C8C8C8", highlightcolor="#C8C8C8", highlightthickness=1)
entry_url.place(x=48, y=50)
entry_url.focus()

# title entry field
label_title = Label(root, text="Title ", fg="#696969")
label_title.place(x=10, y=80)

entry_title = Entry(root, bd=0, width=73, bg="#FAFAFA")
entry_title.config(highlightbackground="#C8C8C8", highlightcolor="#C8C8C8", highlightthickness=1)
entry_title.place(x=48, y=80)

# dest entry field
label_destination = Label(root, text="Dest. ", fg="#696969", height=1)
label_destination.place(x=10, y=110)

entry_dest = Entry(root, bd=0, width=73, bg="#FAFAFA", fg="black")
entry_dest.config(highlightbackground="#C8C8C8", highlightcolor="#C8C8C8", highlightthickness=1)
entry_dest.place(x=48, y=110)
entry_dest.insert(INSERT, media_dl_location)

# context menu
context_menu = Menu(root, tearoff=0)
context_menu.add_command(label="Cut")
context_menu.add_command(label="Copy")
context_menu.add_command(label="Paste")

def show_menu(e):
    w = e.widget
    context_menu.entryconfigure("Cut", command=lambda: w.event_generate("<<Cut>>"))
    context_menu.entryconfigure("Copy", command=lambda: w.event_generate("<<Copy>>"))
    context_menu.entryconfigure("Paste", command=lambda: w.event_generate("<<Paste>>"))
    context_menu.tk.call("tk_popup", context_menu, e.x_root, e.y_root)

root.bind_class("Entry", "<Button-3><ButtonRelease-3>", show_menu)

def grab_media_links(chan_url):
    file_links = []
    res = requests.get(chan_url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    elems = soup.findAll("div", attrs={'class': 'fileText'})
    for div in elems:
        file_links.append(div.a["href"].replace("//",""))
    return file_links

def media_loc():    
    if os.path.exists(str(entry_dest.get()) + str(entry_title.get())):
        folder_exists_message = Label(root, font=("Ebrima", 9), text="Folder already exists                                                                                     ", fg="#696969")
        folder_exists_message.place(x=10, y=140)        
        pass
    else:
    	os.makedirs(str(entry_dest.get()) + str(entry_title.get()))
    
    media_links = grab_media_links(str(entry_url.get()))

    media_links_formatted = ["http://" + x for x in media_links]
    media_files_number_found = Label(root, font=("Ebrima", 9), text="Found " + str(len(media_links_formatted)) + " media files                                                                                             ", fg="#696969")
    media_files_number_found.place(x=10, y=140)    
    
    file = open(entry_dest.get() + entry_title.get() + "\donwloads.txt", "w")
    file.write('\n'.join(media_links_formatted))
    file.close()

decorative_progress_bar = ttk.Progressbar(root, orient="horizontal", length=480, mode="determinate")
decorative_progress_bar.place(x=10, y=170)

label_destination = Label(root, font=("Ebrima", 9), text="Hit Search to find any media files, then Download to grab them ", fg="#696969", height=1)
label_destination.place(x=10, y=140)

def dl_media_files():    
    max_progress = sum(1 for line in open(entry_dest.get() + entry_title.get() + "\donwloads.txt", "r", encoding='utf-8')) + 1
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=480, mode="determinate", maximum=max_progress)
    progress_bar.place(x=10, y=170)

    entry_url.config(state=DISABLED)
    entry_title.config(state=DISABLED)
    entry_dest.config(state=DISABLED)
    
    links = open(entry_dest.get() + entry_title.get() + "\donwloads.txt", "r", encoding='utf-8')

    for link in links:
        link = link.strip()
        name = link.rsplit('/', 1)[-1]
        filename = os.path.join(entry_dest.get() + entry_title.get(), name)
        if not os.path.isfile(filename):
            progress_bar.step(1)                
            try:
                urllib.request.urlretrieve(link, filename)   	
            except Exception as inst:
                print(inst)
                unknown_error_message = Label(root, font=("Ebrima", 9), text="Encountered unknown error. Continuing.               ", fg="#696969")
                unknown_error_message.place(x=10, y=140)    
    
    progress_bar.stop()
    entry_url.config(state=NORMAL)
    entry_title.config(state=NORMAL)
    entry_dest.config(state=NORMAL)

    if links:
        downloading_done_message = Label(root, font=("Ebrima", 9), text="Done                                                                                             ", fg="#696969")
        downloading_done_message.place(x=10, y=140)    

        done_download_img.lower()
        done_status_img.place(x=465, y=135)

    if os.path.exists(entry_dest.get() + entry_title.get() + "\donwloads.txt"):
    	links.close()
    	os.remove(entry_dest.get() + entry_title.get() + "\donwloads.txt")
    else:
    	pass

def start_dl_thread():
    download = threading.Thread(target=dl_media_files)
    downloding_message = Label(root, font=("Ebrima", 9), text="Downloading...                                                                                             ", fg="#696969")
    downloding_message.place(x=10, y=140)
    download.start()

    done_status_img.lower()
    done_download_img.place(x=465, y=135)

def get_media_links():
	media_links = threading.Thread(target=media_loc)
	media_links.start()

def open_media_dl_loc():
    subprocess.Popen(["explorer", "/select,", entry_dest.get() + entry_title.get()])

search_img = PhotoImage(file="magnifying-glass-search-button.png")
display_search_img = search_img.subsample(1, 1)
search_button = Button(root, image=display_search_img, text="  Search", bd=0, compound="left", padx=4, pady=4, command=get_media_links)
search_button.place(x=10, y=11)

dl_img = PhotoImage(file="download-arrow.png")
display_dl_img = dl_img.subsample(1, 1)
dl_button = Button(root, image=display_dl_img, text="  Download", bd=0, compound="left", padx=4, pady=4, command=start_dl_thread)
dl_button.place(x=90, y=11)

open_dest_img = PhotoImage(file="file-folder.png")
display_open_dest_img = open_dest_img.subsample(1, 1)
open_dest_button = Button(root, image=display_open_dest_img, text="  Open", bd=0, compound="left", padx=4, pady=4, command=open_media_dl_loc)
open_dest_button.place(x=190, y=11)

# status img
done_img = PhotoImage(file="done.png")
display_done_img = done_img.subsample(1, 1)
done_status_img = Label(root, image=display_done_img)

download_img = PhotoImage(file="downloading.png")
display_download_img = download_img.subsample(1, 1)
done_download_img = Label(root, image=display_download_img)

root.mainloop()