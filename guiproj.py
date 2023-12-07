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

months_dict: dict = {index: month for index, month in enumerate(calendar.month_name) if month}

class MyGUI:
   def __init__(self):
      self.root = tk.Tk(className="Expenses Tracker")
      self.root.geometry("600x800")
      self.root.resizable(width=False, height=False)
      self.root.columnconfigure(0, weight=1)
      self.root.rowconfigure(0, weight=1)

      # Main Menu Bar
      self.menu_bar = Menu(self.root)
      self.menu_files = Menu(self.menu_bar, tearoff=0)
      self.menu_bar.add_cascade(label="Files", menu=self.menu_files)
      self.menu_bar.add_command(label="Save", state="disabled", command= lambda: [self.saveFile(), self.load_entries(), self.updateSubmenu(self.submenu_open)])
   
      # Files Menu
      self.menu_files.add_command(label="New", command=self.newFile)

      self.submenu_open = tk.Menu(self.menu_files, tearoff=0)
      self.updateSubmenu(self.submenu_open)
      self.menu_files.add_cascade(label="Open", menu=self.submenu_open)

      self.root.config(menu=self.menu_bar)

      self.tab_control = ttk.Notebook(self.root, padding="12")

      self.file_name: str = ""
      self.data_json: dict = {}
      self.details_dropdown: dict = {}

      self.curr_year: int = 0
      self.curr_month: int = 0
      self.curr_data_lists: list = []

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
      fn_entry.grid(row=0, column=1, sticky='ew')

      month_label = tk.Label(new_file_window, text="Starting Month: ")
      month_label.grid(row=1, column=0, sticky='w', pady=12)

      month_selection = ttk.Combobox(new_file_window, state="readonly", values=tuple(months_dict.values()))
      month_selection.current(datetime.datetime.now().month - 1)
      month_value: int = datetime.datetime.now().month
      month_selection.grid(row=1, column=1, sticky='ew')

      def on_month_change(event: tk.Event):
         nonlocal month_value
         widget = event.widget
         month_value = widget['values'].index(widget.get()) + 1
      month_selection.bind("<<ComboboxSelected>>", on_month_change)

      year_label = tk.Label(new_file_window, text="Starting Year: ")
      year_label.grid(row=2, column=0, sticky='w', pady=12)

      curr_year = datetime.datetime.now().year
      year_selection = ttk.Combobox(new_file_window, state="readonly", values=tuple(i for i in range(2020, curr_year + 1)))
      year_selection.current(curr_year - 2020)
      year_value: int = curr_year
      year_selection.grid(row=2, column=1, sticky='ew')

      def on_year_change(event: tk.Event):
         nonlocal year_value
         year_value = int(year_selection.get())
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
            self.data_json = { year_value: { month_value: {} } }
            file_path = data_path / (fn_entry.get() + '.json')
            self.loadFile(file_path)
            new_file_window.destroy()

      submit_button = tk.Button(new_file_window, text="Create", command=on_submit)
      submit_button.grid(row=3, column=0, columnspan=2, pady=12, sticky='ew')

   def loadFile(self, file_path: Path):
      self.file_name = os.path.splitext(os.path.basename(file_path))[0]
      def keystoint(x): return {int(k): v for k, v in x.items()}

      if os.path.exists(file_path):
         with open(file_path, 'r') as read_file:
            self.data_json = json.load(read_file, object_hook=keystoint)

      self.root.title(f"Expenses Tracker - {file_path.stem}")
      self.create_tab_control()

   def saveFile(self):
      self.pack_lists_to_json()
      file_path = data_path / (self.file_name + '.json')

      with open(file_path, 'w') as write_file:
         json.dump(self.data_json, write_file)
      self.updateSubmenu(self.submenu_open)
      self.menu_bar.entryconfig("Save", state="disabled")

   def pack_lists_to_json(self):
      self.curr_data_lists = [ v for v in self.curr_data_lists if len(v) > 0 ]
      def getkey(lst): return int(lst[0])
      self.curr_data_lists.sort(key=getkey)

      data_field = self.data_json[self.curr_year][self.curr_month]
      data_field.clear()
      for data in self.curr_data_lists:
         date = int(data[0])
         amount = float(data[1])

         if date in data_field:
            data_field[date].append([ amount, data[2], data[3] ])
         else:
            data_field[date]  = [[ amount, data[2], data[3] ]]

   def unpack_json_to_lists(self):
         data_field = self.data_json[self.curr_year][self.curr_month]
         self.curr_data_lists.clear()
         for day, entries in data_field.items():
            for entry in entries:
               self.curr_data_lists.append([ day, entry[0], entry[1], entry[2] ])
   
   def create_tab_control(self):
      if self.tab_control.winfo_ismapped(): 
         self.data_analysis_tab.destroy()
         self.data_entry_tab.destroy()

      self.data_entry_tab = ttk.Frame(self.tab_control)
      self.data_analysis_tab = ttk.Frame(self.tab_control)

      self.data_entry_tab.columnconfigure(0, weight=1)
      self.data_analysis_tab.columnconfigure(0, weight=1)

      self.tab_control.add(self.data_entry_tab, text="Data Entry")
      self.tab_control.add(self.data_analysis_tab, text="Data Analysis")
      self.tab_control.grid(row=0, column=0, sticky='nsew')
      
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
      top_frame.grid(row=0, column=0, sticky='nsew')

      m_label = tk.Label(top_frame, text="Month: ")
      y_label = tk.Label(top_frame, text="Year: ")

      m_label.grid(row=0, column=0, sticky='e')
      y_label.grid(row=0, column=2, sticky='e')

      y_var = tk.StringVar()
      m_var = tk.StringVar()

      self.curr_year = list(self.data_json)[-1]
      self.curr_month = list(self.data_json[self.curr_year])[-1]

      y_selection = ttk.Combobox(top_frame, state="readonly", width=10, textvariable=y_var)
      y_selection['values'] = tuple(self.data_json)
      y_selection.current(len(self.data_json) - 1)

      m_selection = ttk.Combobox(top_frame, state="readonly", width=10, textvariable=m_var)
      m_selection['values'] = tuple(months_dict[m] for m in self.data_json[self.curr_year])
      m_selection.current(len(self.data_json[self.curr_year]) - 1)

      m_selection.grid(row=0, column=1, sticky='w')
      y_selection.grid(row=0, column=3, sticky='w')
         
      def on_y_change(*args):
         self.pack_lists_to_json()
         y_var.set(y_selection.get())
         self.curr_year = int(y_var.get())
         m_selection['values'] = tuple(months_dict[m] for m in self.data_json[self.curr_year])
         if self.curr_month not in self.data_json[self.curr_year]:
            self.curr_month = list(self.data_json[self.curr_year])[-1]
            m_selection.current(len(self.data_json[self.curr_year]) - 1)
         
         self.unpack_json_to_lists()
         self.load_entries()

      def on_m_change(*args):
         self.pack_lists_to_json()
         m_var.set(m_selection.get())
         def get_key(dict_: dict, val_search):
            for key, val in dict_.items():
               if val == val_search: return key
         self.curr_month = get_key(months_dict, m_var.get())

         self.unpack_json_to_lists()
         self.load_entries()

      def fn_new_month():
         self.pack_lists_to_json()
         final_year = list(self.data_json)[-1]
         final_month = list(self.data_json[final_year])[-1]
         if final_month + 1 <= 12:
            self.data_json[final_year][final_month + 1] = {}
            self.curr_month = final_month + 1
         else:
            self.data_json[final_year + 1] = { 1: {} }
            final_year += 1
            self.curr_month = 1

         self.curr_year = final_year
         y_selection['values'] = tuple(self.data_json)
         y_selection.current(len(self.data_json) - 1)

         m_selection['values'] = tuple(months_dict[m] for m in self.data_json[final_year])
         m_selection.current(len(self.data_json[final_year]) - 1)

         self.unpack_json_to_lists()
         self.load_entries()

      y_selection.bind("<<ComboboxSelected>>", on_y_change)
      m_selection.bind("<<ComboboxSelected>>", on_m_change)
      new_month_btn = tk.Button(top_frame, text="New Month", width=15, command=fn_new_month)
      new_month_btn.grid(row=0, column=4, columnspan=2, sticky='n')

      self.unpack_json_to_lists()
      self.load_entries()

   def details_dropdown_val(self):
      for year in self.data_json.values():
         for month in year.values():
            for day in month.values():
               for entries in day:
                  if entries[1] in self.details_dropdown:
                     if entries[2] in self.details_dropdown[entries[1]]: continue
                     self.details_dropdown[entries[1]].append(entries[2])
                  else:
                     self.details_dropdown[entries[1]] = [entries[2]]
      
      sorted_key = sorted(list(self.details_dropdown.keys()))
      for key, val in self.details_dropdown.items():
         val.sort()
      self.details_dropdown = { i: self.details_dropdown[i] for i in sorted_key }

   def load_entries(self):
      def frame_grid_config(frame: tk.Frame):
         frame.columnconfigure(2, weight=1)
         frame.columnconfigure(3, weight=1)

      # Labels
      bottom_frame = tk.Frame(self.data_entry_tab, padx=40, pady=10)
      bottom_frame.columnconfigure(0, weight=1)
      bottom_frame.grid(row=1, column=0, sticky='nsew')

      label_frame = tk.Frame(bottom_frame, pady=10)
      label_frame.grid(row=0, column=0, sticky='ew')
      frame_grid_config(label_frame)

      date_label = tk.Label(label_frame, text="Date", anchor='w', width=7)
      amount_label = tk.Label(label_frame, text="Amount", anchor='w', width=15)
      title_label = tk.Label(label_frame, text="Title")
      details_label = tk.Label(label_frame, text="Details")

      date_label.grid(row=0, column=0, sticky='w')
      amount_label.grid(row=0, column=1, sticky='w')
      title_label.grid(row=0, column=2, sticky='w')
      details_label.grid(row=0, column=3, sticky='w')

      #Entries
      num_of_days = calendar.monthrange(self.curr_year, self.curr_month)[1]
      self.details_dropdown_val()

      entry_amount = 24
      for i in range(entry_amount):
         input_frame = tk.Frame(bottom_frame)
         input_frame.grid(row=(i + 1), column=0, sticky="we")
         frame_grid_config(input_frame)

         date_input = ttk.Combobox(input_frame, width=5, values=tuple(i for i in range(1, num_of_days + 1)))
         amount_input = tk.Entry(input_frame, width=15)
         title_input = ttk.Combobox(input_frame, values=tuple(self.details_dropdown))
         details_input = ttk.Combobox(input_frame)

         date_input.grid(row=0, column=0, sticky='ew')
         amount_input.grid(row=0, column=1, sticky='ew')
         title_input.grid(row=0, column=2, sticky='ew')
         details_input.grid(row=0, column=3, sticky='ew')

      def frame_focus_out(event: tk.Event, current_data: list):
         frame = event.widget
         self.menu_bar.entryconfig("Save", state="normal")

         current_data.clear()
         for i, child in enumerate(frame.winfo_children()):
            child_input = child.get()
            if child_input == "" and i == 3: 
               current_data.append(current_data[2])
               return 
            if child_input == "": 
               current_data.clear()
               return
            if i == 0: current_data.append(child_input)
            elif i == 1: current_data.append(child_input)
            elif i in (2, 3): current_data.append(child_input)

      def get_inputframe_by_row(row) -> tk.Frame:
         slaves = bottom_frame.grid_slaves()
         slaves.reverse()
         input_frame: tk.Frame = slaves[row]
         return input_frame

      def get_widget_by_col(col, container: tk.Frame):
         for child in container.winfo_children():
            if child.grid_info()['column'] == col:
               return child

      def date_focus_out(event: tk.Event):
         widget: ttk.Combobox = event.widget
         val = widget.get()
         if not val.isdigit() or val.startswith('0'):
            widget.set("")
         elif int(val) not in range(1, num_of_days + 1):
            widget.set(num_of_days)
         
      def amount_focus_out(event: tk.Event):
         widget: tk.Entry = event.widget
         try:
            float_val = round(float(widget.get()), 2)
            float_val = format(float_val, '.2f')
            widget.delete(0, tk.END)
            widget.insert(0, float_val)
         except ValueError:
            widget.delete(0, tk.END)
      
      def capitalize_entry(event: tk.Event):
         widget: ttk.Combobox = event.widget
         string = widget.get().capitalize()
         widget.set(string)

      def update_detail_dropdown(update_title_dropdown = False):
         for i in range(1, 25):
            input_frame = get_inputframe_by_row(i)
            title_input = get_widget_by_col(2, input_frame)
            details_input = get_widget_by_col(3, input_frame)

            title_val = title_input.get()
            if update_title_dropdown:
               title_input['values'] = tuple(self.details_dropdown)
            if title_val == '':
               details_input['values'] = []
               continue
            details_input['values'] = tuple(self.details_dropdown[title_val])

      def details_focus_out(event: tk.Event, title_input: ttk.Combobox):
         capitalize_entry(event)
         widget = event.widget
         deet_val = widget.get()
         title_val = title_input.get()

         if deet_val and title_val and deet_val not in self.details_dropdown[title_val]:
            self.details_dropdown[title_val].append(deet_val)
         update_detail_dropdown()

      def title_focus_out(event: tk.Event):
         capitalize_entry(event)
         widget = event.widget
         title_val = widget.get()

         if title_val and title_val not in self.details_dropdown:
            self.details_dropdown[title_val] = [ title_val ]
         update_detail_dropdown(True)

      def page(page_no: int):
         nonlocal entry_amount

         for i in range(entry_amount):
            current_data = []
            if (i + (page_no - 1) * entry_amount) + 1 > len(self.curr_data_lists):
               self.curr_data_lists.append(current_data)
            else:
               current_data = self.curr_data_lists[i + (page_no - 1) * entry_amount]

            row = i + 1
            get_input_frame = lambda r=row: get_inputframe_by_row(r)
            input_frame = get_input_frame()

            date_input: ttk.Combobox = get_widget_by_col(0, input_frame)
            amount_input: tk.Entry = get_widget_by_col(1, input_frame)
            title_input: ttk.Combobox = get_widget_by_col(2, input_frame)
            details_input: ttk.Combobox = get_widget_by_col(3, input_frame)

            date_input.set("")
            amount_input.delete(0, tk.END)
            title_input.set("")
            details_input.set("")

            input_frame.bind("<FocusOut>", lambda event, data = current_data: frame_focus_out(event, data))
            date_input.bind("<FocusOut>", lambda event: date_focus_out(event))
            amount_input.bind("<FocusOut>", lambda event: amount_focus_out(event))
            title_input.bind("<FocusOut>", lambda event: title_focus_out(event))
            details_input.bind("<FocusOut>", lambda event, tE = title_input: details_focus_out(event, tE))

            if len(current_data) > 0:
               date_input.set(current_data[0])
               amount_input.insert(0, format(float(current_data[1]), '.2f'))
               title_input.set(current_data[2])
               details_input.set(current_data[3])

            title_val = title_input.get()
            if title_val: details_input['values'] = tuple(self.details_dropdown[title_val])


      total_pages = len(self.curr_data_lists) // (entry_amount + 1) + 1
      curr_page = total_pages
      page_navi_frame = tk.Frame(bottom_frame)
      page_navi_frame.grid(row=entry_amount + 2, column=0, sticky='ew', padx=20, pady=30)
      page_navi_frame.grid_columnconfigure(3, weight=1)

      page_label = tk.Label(page_navi_frame, text="Page: ")
      page_entry = tk.Entry(page_navi_frame, width=3)
      page_total = tk.Label(page_navi_frame, text=f" /  {total_pages} ")
      page_entry.insert(0, curr_page)

      def new_page_fn():
         nonlocal total_pages, curr_page
         total_pages += 1
         curr_page = total_pages

         page_entry.delete(0, tk.END)
         page_entry.insert(0, curr_page)
         page(curr_page)
         page_total.config(text=f" /  {total_pages} ")

      def page_event(event: tk.Event):
         widget: tk.Entry = event.widget
         try:
            if widget.get() == "": return
            page_val = int(widget.get())
            if page_val > total_pages: 
               page_val = total_pages
               widget.delete(0, tk.END)
               widget.insert(0, page_val)
            page(page_val)
         except ValueError:
            widget.delete(0, tk.END)
            widget.insert(0, curr_page)

      new_page_btn = tk.Button(page_navi_frame, text="New Page", width=15, command=new_page_fn)
      page_entry.bind('<KeyRelease>', page_event)

      page_label.grid(row=0, column=0)
      page_entry.grid(row=0, column=1)
      page_total.grid(row=0, column=2)
      new_page_btn.grid(row=0, column=3, sticky='e')
      
      page(curr_page)

   def create_data_analysis_content(self):
      top_frame = tk.Frame(self.data_analysis_tab, padx=25, pady=20)
      top_frame.grid(row=0, column=0, sticky='nsew')
      top_frame.grid_columnconfigure(0, weight=1)
      top_frame.grid_columnconfigure(1, weight=1)
      top_frame.grid_columnconfigure(2, weight=1)

      duration_frame = tk.Frame(top_frame)
      period_frame = tk.Frame(top_frame)
      sortby_frame = tk.Frame(top_frame)
      duration_frame.grid(row=0, column=0, sticky='w')
      period_frame.grid(row=0, column=1, sticky='w')
      sortby_frame.grid(row=0, column=2, sticky='w')

      duration_label = tk.Label(duration_frame, text="Duration: ")
      period_label = tk.Label(period_frame, text="Period: ")
      sortby_label = tk.Label(sortby_frame, text="Sort By: ")

      duration_label.grid(row=0, column=0)
      period_label.grid(row=0, column=0)
      sortby_label.grid(row=0, column=0)
   
      period_values = ["ALLTIME"]
      for year in self.data_json:
         for month in self.data_json[year]:
            period_values.append(f"{month} / {year}")

      duration_dropdown = ttk.Combobox(duration_frame, state='readonly', width=7, values=("Month", "ALLTIME"))
      period_dropdown = ttk.Combobox(period_frame, state='readonly', width=10, values=period_values)
      sortby_dropdown = ttk.Combobox(sortby_frame, state='readonly', width=7, values=("Title", "Details"))

      duration_dropdown.current(0)
      period_dropdown.current(0)
      sortby_dropdown.current(0)
      duration_dropdown.grid(row=0, column=1)
      period_dropdown.grid(row=0, column=1)
      sortby_dropdown.grid(row=0, column=1)

      def duration_event(event: tk.Event):
         widget = event.widget
         if widget.get() == "ALLTIME":
            period_dropdown['values'] = period_values[0]
            period_dropdown.set(period_values[0])
         else:
            period_dropdown['values'] = period_values
            period_dropdown.current(0)
         
         self.render_analysis_content(duration_dropdown.get(), period_dropdown.get(), sortby_dropdown.get())

      def period_event(event: tk.Event):
         self.render_analysis_content(duration_dropdown.get(), period_dropdown.get(), sortby_dropdown.get())

      def sortby_event(event: tk.Event):
         self.render_analysis_content(duration_dropdown.get(), period_dropdown.get(), sortby_dropdown.get())

      duration_dropdown.bind("<<ComboboxSelected>>", duration_event)
      period_dropdown.bind("<<ComboboxSelected>>", period_event)
      sortby_dropdown.bind("<<ComboboxSelected>>", sortby_event)

      self.render_analysis_content(duration_dropdown.get(), period_dropdown.get(), sortby_dropdown.get())

   def render_analysis_content(self, duration: str, period: str, sort: str):
      frame = tk.Frame(self.data_analysis_tab, padx=35)
      frame.grid(row=1, column=0, sticky='nsew')

      print(f"{duration}, {period}, {sort}")
      def get_entries(func):
         for year in self.data_json.values():
            for month in year.values():
               for entries in month.values():
                  for entry in entries:
                     func(entry)

      all_titles = []
      def update_title(entry: list): 
         if sort == "Title" and entry[1] not in all_titles: 
            all_titles.append(entry[1])
         if sort == "Details" and entry[2] not in all_titles:
            all_titles.append(entry[2])
      get_entries(update_title)

      for i, title in enumerate(all_titles):
         label_title = tk.Label(frame, text=title)
         label_title.grid(row=i + 1, column=0, sticky='w')



MyGUI()