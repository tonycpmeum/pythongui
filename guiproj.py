import os, json
import calendar
import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import Menu
from tkinter import ttk

data_path = Path("./data/")
if not os.path.exists(data_path):
   os.makedirs(data_path)

months_dict: dict = {month: index for index, month in enumerate(calendar.month_name) if month}

class MyGUI:
   def __init__(self):
      self.root = tk.Tk(className="Poo")
      self.root.geometry("1000x400")

      # Main Menu Bar
      self.menu_bar = Menu(self.root)
      self.menu_files = Menu(self.menu_bar, tearoff=0)
      self.menu_bar.add_cascade(label="Files", menu=self.menu_files)
      self.menu_bar.add_command(label="Save", state="disabled", command= lambda: [self.saveFile(), self.updateSubmenu(submenu_open)])
   
      # Files Menu
      self.menu_files.add_command(label="New", command=self.newFile)

      submenu_open = tk.Menu(self.menu_files, tearoff=0)
      self.updateSubmenu(submenu_open)
      self.menu_files.add_cascade(label="Open", menu=submenu_open)

      self.root.config(menu=self.menu_bar)

      self.tab_control = ttk.Notebook(self.root, padding="12")

      self.file_name: str = ""
      self.data_json: dict = {}

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

   def newFile(self):
      new_file_window = tk.Toplevel(self.root)
      new_file_window.geometry("360x200")
      new_file_window.title("New File")
      new_file_window.config(padx=20, pady=10)
      new_file_window.grid_columnconfigure(0, weight=1)
      new_file_window.grid_columnconfigure(1, weight=1)

      fn_label = tk.Label(new_file_window, text="File name: ")
      fn_label.grid(row=0, column=0, sticky='w', pady=12)

      fn_entry = tk.Entry(new_file_window)
      fn_entry.grid(row=0, column=1, sticky='we')

      month_label = tk.Label(new_file_window, text="Starting Month: ")
      month_label.grid(row=1, column=0, sticky='w', pady=12)

      n = tk.StringVar()
      month_selection = ttk.Combobox(new_file_window, textvariable=n, state="readonly", values=tuple(months_dict.keys()))
      month_selection.current(datetime.datetime.now().month - 1)
      month_value: int = datetime.datetime.now().month
      month_selection.grid(row=1, column=1, sticky='we')

      year_label = tk.Label(new_file_window, text="Starting Year: ")
      year_label.grid(row=2, column=0, sticky='w', pady=12)

      m = tk.StringVar()
      curr_year = datetime.datetime.now().year
      year_value: int = curr_year
      year_selection = ttk.Combobox(new_file_window, textvariable=m, state="readonly", values=tuple(i for i in range(2020, curr_year + 1)))
      year_selection.current(curr_year - 2020)
      year_selection.grid(row=2, column=1, sticky='we')

      def on_month_change(*args):
         nonlocal month_value
         n.set(month_selection.get())
         month_value = months_dict[n.get()]
      month_selection.bind("<<ComboboxSelected>>", on_month_change)
      
      def on_year_change(*args):
         nonlocal year_value
         m.set(year_selection.get())
         year_value = int(m.get())
      year_selection.bind("<<ComboboxSelected>>", on_year_change)

      def valid_filename(file_name: str):
         allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
         if file_name == "": return False
         return all(char in allowed_chars for char in file_name)

      def on_submit():
         nonlocal year_value, month_value
         if not valid_filename(fn_entry.get()):
            messagebox.showerror("New File Error!", "File name must not contain space or special characters.")
         else:
            self.file_name = fn_entry.get()
            self.root.title(f"Record - {self.file_name}")
            self.create_tab_control()
            self.data_json = { year_value: { month_value: { } } }
            self.menu_bar.entryconfig("Save", state="normal")
            new_file_window.destroy()

      submit_button = tk.Button(new_file_window, text="Create", command=on_submit)
      submit_button.grid(row=3, column=0, columnspan=2, pady=12, sticky='we')

   def loadFile(self, file_path: Path):
      with open(file_path, 'r') as read_file:
         self.data_json = json.load(read_file)

      print(self.data_json)
      file_stem = file_path.stem
      self.root.title(f"Record - {file_stem}")
      self.create_tab_control()

   def saveFile(self):
      file_path = data_path / (self.file_name + '.json')
      with open(file_path, 'w') as write_file:
         json.dump(self.data_json, write_file)
   
   def create_tab_control(self):
      if self.tab_control.winfo_ismapped(): 
         print("Exist")
         return

      self.data_entry_tab = ttk.Frame(self.tab_control)
      self.data_analysis_tab = ttk.Frame(self.tab_control)
      
      self.tab_control.add(self.data_entry_tab, text="Data Entry")
      self.tab_control.add(self.data_analysis_tab, text="Data Analysis")
      self.tab_control.pack(expand=1, fill="both")
      
      self.create_data_entry_content()
      self.create_data_analysis_content()
      
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