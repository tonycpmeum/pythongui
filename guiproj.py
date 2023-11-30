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

def keystoint(x):
   return {int(k): v for k, v in x.items()}

months_dict: dict = {index: month for index, month in enumerate(calendar.month_name) if month}

class MyGUI:
   def __init__(self):
      self.root = tk.Tk(className="Expenses Tracker")
      self.root.geometry("800x800")

      # Main Menu Bar
      self.menu_bar = Menu(self.root)
      self.menu_files = Menu(self.menu_bar, tearoff=0)
      self.menu_bar.add_cascade(label="Files", menu=self.menu_files)
      self.menu_bar.add_command(label="Save", state="disabled", command= lambda: [self.saveFile(), self.updateSubmenu(self.submenu_open)])
   
      # Files Menu
      self.menu_files.add_command(label="New", command=self.newFile)

      self.submenu_open = tk.Menu(self.menu_files, tearoff=0)
      self.updateSubmenu(self.submenu_open)
      self.menu_files.add_cascade(label="Open", menu=self.submenu_open)

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
      month_selection = ttk.Combobox(new_file_window, textvariable=n, state="readonly", values=tuple(months_dict.values()))
      month_selection.current(datetime.datetime.now().month - 1)
      month_value: int = datetime.datetime.now().month
      month_selection.grid(row=1, column=1, sticky='we')

      def on_month_change(*args):
         nonlocal month_value
         n.set(month_selection.get())
         month_value = month_selection['values'].index(n.get()) + 1
      month_selection.bind("<<ComboboxSelected>>", on_month_change)

      year_label = tk.Label(new_file_window, text="Starting Year: ")
      year_label.grid(row=2, column=0, sticky='w', pady=12)

      m = tk.StringVar()
      curr_year = datetime.datetime.now().year
      year_selection = ttk.Combobox(new_file_window, textvariable=m, state="readonly", values=tuple(i for i in range(2020, curr_year + 1)))
      year_selection.current(curr_year - 2020)
      year_value: int = curr_year
      year_selection.grid(row=2, column=1, sticky='we')

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
            self.root.title(f"Expenses Tracker - {self.file_name}")
            self.data_json = { year_value: { month_value: { } } }
            
            self.create_tab_control()
            self.menu_bar.entryconfig("Save", state="normal")
            new_file_window.destroy()

      submit_button = tk.Button(new_file_window, text="Create", command=on_submit)
      submit_button.grid(row=3, column=0, columnspan=2, pady=12, sticky='we')

   def loadFile(self, file_path: Path):
      with open(file_path, 'r') as read_file:
         self.data_json = json.load(read_file, object_hook=keystoint)

      file_stem = file_path.stem
      self.root.title(f"Expenses Tracker - {file_stem}")

      self.create_tab_control()

   def saveFile(self):
      file_path = data_path / (self.file_name + '.json')
      with open(file_path, 'w') as write_file:
         json.dump(self.data_json, write_file)
      self.updateSubmenu(self.submenu_open)
   
   def create_tab_control(self):
      if self.tab_control.winfo_ismapped(): 
         self.data_analysis_tab.destroy()
         self.data_entry_tab.destroy()

      self.data_entry_tab = ttk.Frame(self.tab_control)
      self.data_analysis_tab = ttk.Frame(self.tab_control)
      
      self.tab_control.add(self.data_entry_tab, text="Data Entry")
      self.tab_control.add(self.data_analysis_tab, text="Data Analysis")
      self.tab_control.pack(expand=1, fill="both")
      
      self.create_data_entry_content()
      self.create_data_analysis_content()
      
   def create_data_entry_content(self):
      top_frame = tk.Frame(self.data_entry_tab, padx=20, pady=10)
      top_frame.columnconfigure(0, weight=1)
      top_frame.columnconfigure(1, weight=1)
      top_frame.columnconfigure(2, weight=1)
      top_frame.columnconfigure(3, weight=1)
      top_frame.columnconfigure(4, weight=5)
      top_frame.columnconfigure(5, weight=5)

      m_label = tk.Label(top_frame, text="Month: ")
      y_label = tk.Label(top_frame, text="Year: ")

      m_label.grid(row=0, column=0, sticky='e')
      y_label.grid(row=0, column=2, sticky='e')

      y_var = tk.StringVar()
      m_var = tk.StringVar()

      curr_y: int = list(self.data_json)[-1]
      curr_m: int = list(self.data_json[curr_y])[-1]

      y_selection = ttk.Combobox(top_frame, state="readonly", width=10, textvariable=y_var)
      y_selection['values'] = tuple(self.data_json)
      y_selection.current(len(self.data_json) - 1)

      m_selection = ttk.Combobox(top_frame, state="readonly", width=10, textvariable=m_var)
      m_selection['values'] = tuple(months_dict[m] for m in self.data_json[curr_y])
      m_selection.current(len(self.data_json[curr_y]) - 1)

      def on_y_change(*args):
         nonlocal curr_y, curr_m
         y_var.set(y_selection.get())
         curr_y = int(y_var.get())
         m_selection['values'] = tuple(months_dict[m] for m in self.data_json[curr_y])
         if curr_m not in self.data_json[curr_y]:
            curr_m = list(self.data_json[curr_y])[-1]
            m_selection.current(len(self.data_json[curr_y]) - 1)
      y_selection.bind("<<ComboboxSelected>>", on_y_change)

      def on_m_change(*args):
         nonlocal curr_m
         m_var.set(m_selection.get())
         def get_key(dict_: dict, val_search):
            for key, val in dict_.items():
               if val == val_search: return key
         curr_m = get_key(months_dict, m_var.get())
      m_selection.bind("<<ComboboxSelected>>", on_m_change)

      m_selection.grid(row=0, column=1, sticky='w')
      y_selection.grid(row=0, column=3, sticky='w')

      def fn_new_month():
         nonlocal curr_m, curr_y
         final_year = list(self.data_json)[-1]
         final_month = list(self.data_json[final_year])[-1]
         if final_month + 1 <= 12:
            self.data_json[final_year][final_month + 1] = {}
            curr_m = final_month + 1
         else:
            self.data_json[final_year + 1] = { 1: {} }
            final_year += 1
            curr_m = 1

         curr_y = final_year
         y_selection['values'] = tuple(self.data_json)
         y_selection.current(len(self.data_json) - 1)

         m_selection['values'] = tuple(months_dict[m] for m in self.data_json[final_year])
         m_selection.current(len(self.data_json[final_year]) - 1)

         print(f"curr_m: {type(curr_m)}, curr_y: {type(curr_y)}")
         print(self.data_json)

      new_month_btn = tk.Button(top_frame, text="New Month", width=15, command=fn_new_month)
      new_month_btn.grid(row=0, column=4, columnspan=2, sticky='n')
      
      self.data_entry_tab.columnconfigure(0, weight=1)
      top_frame.grid(row=0, column=0, sticky='we')


   def create_data_analysis_content(self):
      entry = tk.Entry(self.data_analysis_tab)
      entry.pack(padx=10, pady=10)

MyGUI()