import os, json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import Menu

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
      # End Main Menu Bar

      #spinbox
      # combobox

      self.label = tk.Label(self.root, text="type something", font=("Helvatica", 18))
      self.label.pack(padx=10, pady=10)

      self.input_filename = tk.Entry(self.root, font=("Monospace", 14), width=10)
      self.input_filename.pack(padx=10, pady=10)

      self.input_content = tk.Entry(self.root, font=("Monospace", 14), width=10)
      self.input_content.pack(padx=10, pady=10)

      self.button_save = tk.Button(self.root, text="Save", font=("Monospace", 14), command=lambda: [self.saveFile(), self.updateSubmenu(submenu_open)], activebackground="orange", activeforeground="purple", bg="grey")
      self.button_save.pack(padx=10, pady=10)

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
         self.label.config(text=text)
         
         self.input_content.delete(0, 'end')
         self.input_filename.delete(0, 'end')
         self.input_content.insert(0, text)
         self.input_filename.insert(0, file_stem)

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
      

MyGUI()