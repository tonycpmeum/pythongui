import os, json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import Menu
from tkinter import ttk

data_path = Path("./data/")
if not os.path.exists(data_path):
   os.makedirs(data_path)

class MyGUI:
   def __init__(self):
      self.root = tk.Tk(className="Poo")
      self.root.geometry("1000x400")

      # Main Menu Bar
      self.menu_bar = Menu(self.root)
      self.menu_files = Menu(self.menu_bar, tearoff=0)
      self.menu_bar.add_cascade(label="Files", menu=self.menu_files)
      self.menu_bar.add_command(label="Save")

      # Files Menu
      self.menu_files.add_command(label="New")

      submenu_open = tk.Menu(self.menu_files, tearoff=0)
      self.updateSubmenu(submenu_open)
      self.menu_files.add_cascade(label="Open", menu=submenu_open)

      self.root.config(menu=self.menu_bar)

      # tabs
      self.create_tab_control()
      self.create_data_entry_content()
      self.create_data_analysis_content()

      self.tab_control.pack(expand=1, fill="both")
      #spinbox
      # combobox


      self.root.mainloop()

   def updateSubmenu(self, submenu_open: Menu):
      submenu_open.delete(0, 'end')
      for file_name in os.listdir(data_path):
         if file_name.endswith(".json"):
            file_path = Path(data_path) / file_name
            file_stem = file_path.stem
            submenu_open.add_command(label=file_stem, command=lambda path=file_path: self.loadFile(path))

   def loadFile(self, file_path: Path):
      with open(file_path, 'r') as read_file:
         text = json.load(read_file)
         file_stem = file_path.stem

         self.root.title(f"Something - {file_stem}")

   def saveFile(self):
      input_msg = self.input_content.get()
      file_name = self.input_filename.get()

      if file_name == "" or input_msg == "":
         messagebox.showerror("You Noob.", "File Name / input is empty")
      else:
         file_path = data_path / (file_name + '.json')
         with open(file_path, 'w') as write_file:
            json.dump(input_msg, write_file)

      self.root.title(f"Something - {file_name}")
   
   def create_tab_control(self):
      self.tab_control = ttk.Notebook(self.root, padding="12") 
      self.data_entry_tab = ttk.Frame(self.tab_control)
      self.data_analysis_tab = ttk.Frame(self.tab_control)
      
      self.tab_control.add(self.data_entry_tab, text="Data Entry")
      self.tab_control.add(self.data_analysis_tab, text="Data Analysis")
      
   def create_data_entry_content(self):
      label_one = tk.Label(self.data_entry_tab, text="Content for Data Entry")
      label_two = tk.Label(self.data_entry_tab, text="Content Two for Data Entry")
      self.data_entry_tab.grid_columnconfigure(0, weight=1)
      self.data_entry_tab.grid_columnconfigure(1, weight=1)
      label_one.grid(row=0, column=0, pady=10)
      label_two.grid(row=0, column=1, pady=10)

   def create_data_analysis_content(self):
      entry = tk.Entry(self.data_analysis_tab)
      entry.pack(padx=10, pady=10)

MyGUI()