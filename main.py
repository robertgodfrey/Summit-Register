"""

This app is a hiking tracker that uses an SQL database to store information about a number of different hiking trails
and their statistics such as distance, elevation gain, maximum elevation, prominence (in the case of peaks) and
difficulty rating. Implements the Tkinter GUI, where the user is able to see a list of hikes and sort them as they wish.
The user will also be able to mark a hike as completed and make their own notes about the hike.

Written by Robert Godfrey
Last updated 14 December 20


- TO DO -
[ ] fix treeview sort algorithm, not behaving properly with numbers (places 10 before 2, only looks at first digit)
[ ] add ability to add new hikes (and write to database)
[ ] add ability to save notes/completion status to database
[ ] use a loop to populate treeview headings instead of current sloppy code
[ ] *consider* adding photo and google maps link for each hike. this would take forever..
[ ] change 'complete' from radio button to checkbox
[ ] implement google maps to enable user to set their home location and use to determine actual distances to trailhead

"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from PIL import Image, ImageTk
import mysql.connector

# master list of hikes
hike_list = []

# connection to hikes database
try:
    hiking_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="***********",
        database="hikes"
    )
    cursor = hiking_db.cursor()
    cursor.execute("SELECT * FROM hikes")
    for hike in cursor:
        hike_list.append(hike)

except mysql.connector.Error:
    print("Unable to connect to database. Check your connection and try again.")
    quit()

class MainApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # create container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # create empty frames dictionary
        self.frames = {}
        # add frame objects to dictionary
        for f in (MainMenu, Search, SearchResults, MyHikes, AllHikes):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(column=0, row=0, sticky="nsew")

        self.show_frame(MainMenu)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def get_page(self, page_class):
        return self.frames[page_class]


# main menu
class MainMenu(tk.Frame):

    def __init__(self, parent, controller):
        self.main_background = ImageTk.PhotoImage(Image.open(r"peak_pro_main_bg.jpg"))
        self.main_title = ImageTk.PhotoImage(Image.open(r"main_title.png"))

        tk.Frame.__init__(self, parent)
        self.lbl_background = tk.Label(
            master=self,
            image=self.main_background,
            borderwidth=0,
            highlightthickness=0
        )
        self.lbl_background.place(x=0, y=0)

        self.lbl_main_text = tk.Label(
            master=self,
            image=self.main_title,
            borderwidth=0,
            highlightthickness=0
        )
        self.lbl_main_text.pack(pady=(135, 0))

        self.btn_find_a_hike = tk.Button(
            master=self,
            text="Find a Hike",
            font=("Comic Book", 23, "bold"),
            width=20,
            bg="#939bb0",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            pady=12,
            command=lambda: controller.show_frame(Search)
        )
        self.btn_find_a_hike.pack(pady=(40, 0))

        self.btn_view_all_hikes = tk.Button(
            master=self,
            text="View All Hikes",
            font=("Comic Book", 23, "bold"),
            width=20,
            bg="#939bb0",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            pady=12,
            command=lambda: controller.show_frame(AllHikes)
        )
        self.btn_view_all_hikes.pack(pady=(5, 0))

        self.btn_view_my_hikes = tk.Button(
            master=self,
            text="My Completed Hikes",
            font=("Comic Book", 23, "bold"),
            width=20,
            bg="#939bb0",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            pady=12,
            command=lambda: controller.show_frame(MyHikes)
        )
        self.btn_view_my_hikes.pack(pady=(5, 0))


# search class (find a hike)
class Search(tk.Frame):

    search_results = []

    def __init__(self, parent, controller):

        self.controller = controller

        tk.Frame.__init__(self, parent)

        self.main_background = ImageTk.PhotoImage(Image.open(r"peak_pro_main_bg.jpg"))
        self.search_title = ImageTk.PhotoImage(Image.open(r"search_title.png"))

        # setup for input validation: '%S' = text string being inserted/deleted
        val_cmd = (self.register(self.val_int_input), '%S')

        tk.Frame.__init__(self, parent)

        lbl_search_background = tk.Label(
            master=self,
            image=self.main_background,
            borderwidth=0,
            highlightthickness=0
        )
        lbl_search_background.place(x=0, y=0)

        lbl_search_text = tk.Label(
            master=self,
            image=self.search_title,
            borderwidth=0,
            highlightthickness=0
        )
        lbl_search_text.pack(pady=(30, 0))

        # create frame for search box
        frame_search_box = tk.Frame(
            master=self,
            bg="#6a96c6",
            highlightthickness=5,
            highlightbackground="#1b4760"
        )
        frame_search_box.pack(padx=175, pady=(14, 0), fill="x")

        lbl_search_instructions = tk.Label(
            master=frame_search_box,
            text="Enter one or more search parameters",
            font=("Comic Book", 11),
            bg="#6a96c6",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
        ).pack(pady=(15, 0))

        frame_search_columns = tk.Frame(
            master=frame_search_box,
            bg="#6a96c6",
        )
        frame_search_columns.pack()
        frame_search_columns.columnconfigure(0, weight=1, minsize=350)
        frame_search_columns.columnconfigure(1, weight=1, minsize=350)

        lbl_search_name = tk.Label(
            master=frame_search_columns,
            text="Name / Keyword:",
            font=("Comic Book", 16, "bold"),
            bg="#6a96c6",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
        )
        lbl_search_name.grid(column=0, row=0, sticky="w", padx=(30, 0), pady=(15, 0))

        lbl_search_distance = tk.Label(
            master=frame_search_columns,
            text="Distance (miles):",
            font=("Comic Book", 16, "bold"),
            bg="#6a96c6",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
        )
        lbl_search_distance.grid(column=0, row=1, sticky="w", padx=(30, 0), pady=(15, 0))

        lbl_search_elevation_gain = tk.Label(
            master=frame_search_columns,
            text="Elevation Gain (feet):",
            font=("Comic Book", 16),
            bg="#6a96c6",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
        )
        lbl_search_elevation_gain.grid(column=0, row=2, sticky="w", padx=(30, 0), pady=(15, 0))

        lbl_search_max_elevation = tk.Label(
            master=frame_search_columns,
            text="Max Elevation (feet):",
            font=("Comic Book", 16),
            bg="#6a96c6",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
        )
        lbl_search_max_elevation.grid(column=0, row=3, sticky="w", padx=(30, 0), pady=(15, 0))

        lbl_search_difficulty = tk.Label(
            master=frame_search_columns,
            text="Max Difficulty Rating:",
            font=("Comic Book", 16, "bold"),
            bg="#6a96c6",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
        )
        lbl_search_difficulty.grid(column=0, row=4, sticky="w", padx=(30, 0), pady=(15, 0))

        lbl_search_distance_from_home = tk.Label(
            master=frame_search_columns,
            text="Distance From Home:",
            font=("Comic Book", 16, "bold"),
            bg="#6a96c6",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
        )
        lbl_search_distance_from_home.grid(column=0, row=5, sticky="w", padx=(30, 0), pady=(15, 15))

        # assign string var to set up limiting character function
        self.name_val = tk.StringVar()
        self.name_val.trace('w', self.limit_name_chars)

        self.ent_name = tk.Entry(
            master=frame_search_columns,
            width=21,
            font=("Comic Book", 15),
            textvariable=self.name_val,
            borderwidth=4,
            relief=tk.FLAT,
        )
        self.ent_name.grid(column=1, row=0, padx=(0, 15), pady=(15, 0))

        frame_search_box_inputs1 = tk.Frame(
            master=frame_search_columns,
            bg="#6a96c6",
        )
        frame_search_box_inputs1.grid(column=1, row=1, padx=(0, 15))

        greater_or_less = ["Select ▼", "Greater than", "Less than"]
        self.drop1_string = tk.StringVar()
        self.drop1_string.set("Select ▼")
        drop1 = tk.OptionMenu(frame_search_box_inputs1, self.drop1_string, *greater_or_less, command=self.opt_update1)
        drop1.config(
            indicatoron=0,
            width=11,
            font=("Comic Book", 15),
            bg="#1b4760",
            fg="#ffffff",
            borderwidth=0,
            highlightthickness=0,
            padx=20,
            pady=6,
        )
        drop1.grid(column=0, row=0, sticky="w", padx=(0, 25), pady=(15, 0))

        # string var for char limit
        self.dist_val = tk.StringVar()
        self.dist_val.trace('w', self.limit_num_chars)

        self.ent_distance = tk.Entry(
            master=frame_search_box_inputs1,
            width=6,
            font=("Comic Book", 15),
            borderwidth=4,
            relief=tk.FLAT,
            validate="key",
            validatecommand=val_cmd,
            textvariable=self.dist_val,
            state=tk.DISABLED
        )
        self.ent_distance.grid(column=1, row=0, sticky="e", pady=(15, 0))

        frame_search_box_inputs2 = tk.Frame(
            master=frame_search_columns,
            bg="#6a96c6",
        )
        frame_search_box_inputs2.grid(column=1, row=2, padx=(0, 15))

        self.drop2_string = tk.StringVar()
        self.drop2_string.set("Select ▼")
        drop2 = tk.OptionMenu(frame_search_box_inputs2, self.drop2_string, *greater_or_less, command=self.opt_update2)
        drop2.config(
            indicatoron=0,
            width=11,
            font=("Comic Book", 15),
            bg="#1b4760",
            fg="#ffffff",
            borderwidth=0,
            highlightthickness=0,
            padx=20,
            pady=6
        )
        drop2.grid(column=0, row=1, sticky="w", padx=(0, 25), pady=(15, 0))

        # string var for char limit
        self.elev_change_val = tk.StringVar()
        self.elev_change_val.trace('w', self.limit_num_chars)

        self.ent_elevation_gain = tk.Entry(
            master=frame_search_box_inputs2,
            width=6,
            font=("Comic Book", 15),
            borderwidth=4,
            relief=tk.FLAT,
            textvariable=self.elev_change_val,
            state=tk.DISABLED
        )
        self.ent_elevation_gain.grid(column=1, row=1, sticky="e", pady=(15, 0))

        frame_search_box_inputs3 = tk.Frame(
            master=frame_search_columns,
            bg="#6a96c6",
        )
        frame_search_box_inputs3.grid(column=1, row=3, padx=(0, 15))

        self.drop3_string = tk.StringVar()
        self.drop3_string.set("Select ▼")
        drop3 = tk.OptionMenu(frame_search_box_inputs3, self.drop3_string, *greater_or_less, command=self.opt_update3)
        drop3.config(
            indicatoron=0,
            width=11,
            font=("Comic Book", 15),
            bg="#1b4760",
            fg="#ffffff",
            borderwidth=0,
            highlightthickness=0,
            padx=20,
            pady=6
        )
        drop3.grid(column=0, row=1, sticky="w", padx=(0, 25), pady=(15, 0))

        # string var for char limit
        self.max_elev_val = tk.StringVar()
        self.max_elev_val.trace('w', self.limit_num_chars)

        self.ent_max_elevation = tk.Entry(
            master=frame_search_box_inputs3,
            width=6,
            font=("Comic Book", 15),
            borderwidth=4,
            relief=tk.FLAT,
            textvariable=self.max_elev_val,
            state=tk.DISABLED
        )
        self.ent_max_elevation.grid(column=1, row=1, sticky="e", pady=(15, 0))

        self.drop4_string = tk.StringVar()
        self.drop4_string.set("Select Difficulty ▼")
        difficulty_ratings = ["Select Difficulty ▼", "Easy", "Moderate", "Hard", "Expert"]
        drop4 = tk.OptionMenu(frame_search_columns, self.drop4_string, *difficulty_ratings)
        drop4.config(
            indicatoron=0,
            width=24,
            font=("Comic Book", 15),
            bg="#1b4760",
            fg="#ffffff",
            borderwidth=0,
            highlightthickness=0,
            padx=20,
            pady=6
        )
        drop4.grid(column=1, row=4, padx=(15, 30), pady=(15, 0))

        self.drop5_string = tk.StringVar()
        self.drop5_string.set("Select Distance ▼")
        distances_lst = ["Select Distance ▼", "< 1 hour", "< 2 hours", "< 3 hours", "< 4 hours"]
        drop5 = tk.OptionMenu(frame_search_columns, self.drop5_string, *distances_lst)
        drop5.config(
            indicatoron=0,
            width=24,
            font=("Comic Book", 15),
            bg="#1b4760",
            fg="#ffffff",
            borderwidth=0,
            highlightthickness=0,
            padx=20,
            pady=6
        )
        drop5.grid(column=1, row=5, sticky="e", padx=(15, 30), pady=(15, 0))

        btn_search = tk.Button(
            master=frame_search_box,
            text=" Go!",
            font=("Comic Book", 17, "bold"),
            bg="#1b4760",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            width=15,
            pady=5,
            command=self.search
        )
        btn_search.pack(pady=(15, 20))

        btn_back = tk.Button(
            master=self,
            text="Return to Menu",
            font=("Comic Book", 15, "bold"),
            bg="#1b4760",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            width=18,
            height=2,
            command=lambda: controller.show_frame(MainMenu)
        )
        btn_back.pack(pady=25)

    # limit name entry box characters to 24
    def limit_name_chars(self, *args):
        value = self.name_val.get()
        if len(value) > 24:
            self.name_val.set(value[:24])
            self.bell()

    # limit mileage and elevation entry boxes to 5 chars
    def limit_num_chars(self, *args):
        value1 = self.dist_val.get()
        value2 = self.elev_change_val.get()
        value3 = self.max_elev_val.get()
        if len(value1) > 4 or len(value2) > 5 or len(value3) > 5:
            self.dist_val.set(value1[:4])
            self.elev_change_val.set(value2[:5])
            self.max_elev_val.set(value3[:5])
            self.bell()

    # validate input - only allows ints
    def val_int_input(self, s):
        if s:
            try:
                float(s)
                return True  # allows edits
            except ValueError:
                self.bell()  # alert bell
                return False  # does not allow edits
        else:
            self.bell()
            return False

    # make entry boxes usable when user selects "greater than" or "less than"
    def opt_update1(self, value):
        if value == "Select ▼":
            self.ent_distance.config(state=tk.DISABLED)
        else:
            self.ent_distance.config(state=tk.NORMAL)
        return

    def opt_update2(self, value):
        if value == "Select ▼":
            self.ent_elevation_gain.config(state=tk.DISABLED)
        else:
            self.ent_elevation_gain.config(state=tk.NORMAL)
        return

    def opt_update3(self, value):
        if value == "Select ▼":
            self.ent_max_elevation.config(state=tk.DISABLED)
        else:
            self.ent_max_elevation.config(state=tk.NORMAL)
        return

    # abstract data type (ICS 211 requirement)
    def is_empty(self):
        return self.search_results == []

    # search list from database
    def search(self):
        search_bool = False
        self.search_results.clear()  # resets list of previous search results, if any

        ''' to account for multiple parameters, a full list is initialized and items are deleted if they do not meet 
        search criteria. there is probably a better way to do this, but this works '''

        for hike in hike_list:
            self.search_results.append(hike)

        # search for name/keyword
        if len(self.ent_name.get()) > 0:
            search_bool = True
            length = len(self.search_results)
            i = 0
            name = self.ent_name.get().lower()
            while i < length:
                if name in self.search_results[i][1].lower() or name in self.search_results[i][7].lower() or \
                        name in self.search_results[i][11].lower():
                    i += 1
                else:
                    del self.search_results[i]
                    length -= 1

        # search list for distances
        if "▼" not in self.drop1_string.get():
            search_bool = True
            length = len(self.search_results)
            i = 0
            if "Greater" in self.drop1_string.get():
                while i < length:
                    if int(self.ent_distance.get()) <= self.search_results[i][2]:
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1
            else:
                while i < length:
                    if int(self.ent_distance.get()) >= self.search_results[i][2]:
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1

        # search list for elevation gain
        if "▼" not in self.drop2_string.get():
            search_bool = True
            length = len(self.search_results)
            i = 0
            if "Greater" in self.drop2_string.get():
                while i < length:
                    if int(self.ent_elevation_gain.get()) <= self.search_results[i][3]:
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1
            else:
                while i < length:
                    if int(self.ent_elevation_gain.get()) >= self.search_results[i][3]:
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1

        # search list for max elevation
        if "▼" not in self.drop3_string.get():
            search_bool = True
            length = len(self.search_results)
            i = 0
            if "Greater" in self.drop3_string.get():
                while i < length:
                    if int(self.ent_max_elevation.get()) <= self.search_results[i][4]:
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1
            else:
                while i < length:
                    if int(self.ent_max_elevation.get()) >= self.search_results[i][4]:
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1

        # search list for max difficulty rating
        if "▼" not in self.drop4_string.get():
            search_bool = True
            length = len(self.search_results)
            i = 0
            if "easy" in self.drop4_string.get().lower():
                while i < length:
                    if self.search_results[i][6].lower() == "easy":
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1
            elif "moderate" in self.drop4_string.get().lower():
                while i < length:
                    if "moderate" in self.search_results[i][6].lower() or "easy" in self.search_results[i][6].lower():
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1
            elif "hard" in self.drop4_string.get().lower():
                while i < length:
                    if "hard" in self.search_results[i][6].lower() or "moderate" in self.search_results[i][6].lower() \
                            or "easy" in self.search_results[i][6].lower():
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1
            else:
                pass

        # search list for max distance from home
        if "▼" not in self.drop5_string.get():
            search_bool = True
            length = len(self.search_results)
            i = 0
            if "1" in self.drop5_string.get():
                while i < length:
                    if self.search_results[i][8] <= 1:
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1
            elif "2" in self.drop5_string.get():
                while i < length:
                    if self.search_results[i][8] <= 2:
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1
            elif "3" in self.drop5_string.get():
                while i < length:
                    if self.search_results[i][8] <= 3:
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1
            else:
                while i < length:
                    if self.search_results[i][8] <= 4:
                        i += 1
                    else:
                        del self.search_results[i]
                        length -= 1

        # prevent search unless user selects at least one search parameter
        if not search_bool:
            messagebox.showinfo("Empty Values", "Please enter at least one search parameter.")
        # no matches
        elif self.is_empty():
            messagebox.showinfo("No Results", "The search yielded no results. Please try again.")
        else:
            self.controller.get_page(SearchResults).populate()
            self.controller.show_frame(SearchResults)


# search results class
class SearchResults(tk.Frame):

    def __init__(self, parent, controller):
        self.controller = controller
        self.main_background = ImageTk.PhotoImage(Image.open(r"peak_pro_main_bg.jpg"))
        self.search_results_title = ImageTk.PhotoImage(Image.open(r"search_results.png"))

        tk.Frame.__init__(self, parent)

        lbl_search_results_background = tk.Label(
            master=self,
            image=self.main_background,
            borderwidth=0,
            highlightthickness=0
        )
        lbl_search_results_background.place(x=0, y=0)

        lbl_search_results_text = tk.Label(
            master=self,
            image=self.search_results_title,
            borderwidth=0,
            highlightthickness=0
        )
        lbl_search_results_text.pack(pady=(23, 0))

        # create frame for search results box
        frame_search_results_box = tk.Frame(
            master=self,
            bg="#ffffff",
            highlightthickness=5,
            highlightbackground="black",
            height=475
        )
        frame_search_results_box.columnconfigure(0, weight=0)
        frame_search_results_box.pack_propagate(0)
        frame_search_results_box.pack(padx=25, pady=(25, 0), fill='x')

        ''' would like to figure out how to change table header height... '''

        # treeview style
        tview_heading_style = ttk.Style()
        tview_heading_style.configure("Treeview.Heading", font=("Comic Book", 10))
        tview_style = ttk.Style()
        tview_style.configure("Treeview", font=("Comic Book", 10), rowheight=55)

        # create treeview for search results
        self.tview_search_results = ttk.Treeview(frame_search_results_box, style="Custom.Treeview", selectmode="browse")
        self.tview_search_results['columns'] = ('complete', 'name', 'total_distance', 'elev_gain', 'max_elev',
                                                'prominence', 'diff_rating', 'gen_area', 'dist_from_home')
        self.tview_search_results.column("#0", width=0, minwidth=0)
        self.tview_search_results.column("complete", width=30, minwidth=30, anchor="c")
        self.tview_search_results.column("name", width=200, minwidth=200)
        self.tview_search_results.column("total_distance", width=100, minwidth=100)
        self.tview_search_results.column("elev_gain", width=100, minwidth=100)
        self.tview_search_results.column("max_elev", width=100, minwidth=100)
        self.tview_search_results.column("prominence", width=100, minwidth=100)
        self.tview_search_results.column("diff_rating", width=110, minwidth=110)
        self.tview_search_results.column("gen_area", width=150, minwidth=150)
        self.tview_search_results.column("dist_from_home", width=130, minwidth=130)

        ''' upon further reflection, i could have definitely combined these next few lines into a short loop. might fix 
        later '''

        self.tview_search_results.heading("#0", text="Label", anchor="w")
        self.tview_search_results.heading(
            "complete",
            text="✔",
            command=lambda _col="complete": self.treeview_sort(self.tview_search_results, _col, False)
        )
        self.tview_search_results.heading(
            "name",
            text="Name",
            command=lambda _col="name": self.treeview_sort(self.tview_search_results, _col, False)
        )
        self.tview_search_results.heading(
            "total_distance",
            text="Total Dist",
            command=lambda _col="total_distance": self.treeview_sort(self.tview_search_results, _col, False)
        )
        self.tview_search_results.heading(
            "elev_gain",
            text="Elev Gain",
            command=lambda _col="elev_gain": self.treeview_sort(self.tview_search_results, _col, False)
        )
        self.tview_search_results.heading(
            "max_elev",
            text="Max Elev",
            command=lambda _col="max_elev": self.treeview_sort(self.tview_search_results, _col, False)
        )
        self.tview_search_results.heading(
            "prominence",
            text="Prominence",
            command=lambda _col="prominence": self.treeview_sort(self.tview_search_results, _col, False)
        )
        self.tview_search_results.heading(
            "diff_rating",
            text="Diff Rating",
            command=lambda _col="diff_rating": self.treeview_sort(self.tview_search_results, _col, False)
        )
        self.tview_search_results.heading(
            "gen_area",
            text="General Area",
            command=lambda _col="gen_area": self.treeview_sort(self.tview_search_results, _col, False)
        )
        self.tview_search_results.heading(
            "dist_from_home",
            text="Dist from Home",
            command=lambda _col="dist_from_home": self.treeview_sort(self.tview_search_results, _col, False)
        )

        self.tview_search_results.bind("<Double-1>", self.on_double_click)

        # scrollbar for treeview
        vsb = ttk.Scrollbar(
            frame_search_results_box,
            orient="vertical",
            command=self.tview_search_results.yview
        )
        self.tview_search_results.configure(yscrollcommand=vsb.set)

        self.tview_search_results.pack(side='left')
        vsb.pack(side='right', fill='y')

        btn_back = tk.Button(
            master=self,
            text="Back",
            font=("Comic Book", 17, "bold"),
            bg="#1b4760",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            width=18,
            height=2,
            command=lambda: controller.show_frame(Search)
        )
        btn_back.pack(side='left', padx=50)

        btn_main = tk.Button(
            master=self,
            text="Return to Menu",
            font=("Comic Book", 17, "bold"),
            bg="#1b4760",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            width=18,
            height=2,
            command=lambda: controller.show_frame(MainMenu)
        )
        btn_main.pack(side='right', padx=50)

    def on_double_click(self, *args):
        value = self.tview_search_results.item(self.tview_search_results.focus())
        selected_hike = []
        for hike in hike_list:
            if hike[1] == value['values'][1]:
                selected_hike = hike
        pop_up = tk.Toplevel()
        pop_up.geometry("800x600")
        pop_up.title(value['values'][1])
        pop_up.iconbitmap(r"pp.ico")
        pop_up.resizable(False, False)
        frame = HikeDetails(pop_up, self, selected_hike)
        frame.grid_rowconfigure(0, weight=1)
        frame.pack(expand=True, fill="both")

    # populate treeview with hikes from search results
    def populate(self):
        # delete previous results, prep table to receive new results
        self.tview_search_results.delete(*self.tview_search_results.get_children())
        id_ = 1
        for hike in Search.search_results:
            if hike[9] == 1:
                complete = "✔"
            else:
                complete = " "
            if hike[5] == 0:
                prom = "N/A"
            else:
                prom = hike[5], "ft"
            self.tview_search_results.insert(
                parent='',
                index='end',
                iid=id_,
                text="",
                values=(complete, hike[1], (hike[2], "miles"), (hike[3], "ft"), (hike[4], "ft"), prom,
                        hike[6], hike[7], (hike[8], "hours"))
            )
            id_ += 1

    # sort treeview table
    ''' something funky is going on when sorting ints. need to look into later '''
    def treeview_sort(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k), in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda _col=col: self.treeview_sort(tv, _col, not reverse))


# view my hikes class
class MyHikes(tk.Frame):

    def __init__(self, parent, controller):
        self.main_background = ImageTk.PhotoImage(Image.open(r"peak_pro_main_bg.jpg"))
        self.my_hikes_title = ImageTk.PhotoImage(Image.open(r"my_hikes.png"))

        tk.Frame.__init__(self, parent)

        lbl_my_hikes_background = tk.Label(
            master=self,
            image=self.main_background,
            borderwidth=0,
            highlightthickness=0
        )
        lbl_my_hikes_background.place(x=0, y=0)

        lbl_my_hikes_text = tk.Label(
            master=self,
            image=self.my_hikes_title,
            borderwidth=0,
            highlightthickness=0
        )
        lbl_my_hikes_text.pack(pady=(23, 0))

        # create frame for search results box
        frame_my_hikes_box = tk.Frame(
            master=self,
            bg="#ffffff",
            highlightthickness=5,
            highlightbackground="black",
            height=475
        )
        frame_my_hikes_box.columnconfigure(0, weight=0)
        frame_my_hikes_box.pack_propagate(0)
        frame_my_hikes_box.pack(padx=25, pady=(15, 0), fill='x')

        ''' would like to figure out how to change table header height... '''

        # treeview style
        self.tview_my_hikes = ttk.Style()
        self.tview_my_hikes.configure("Treeview.Heading", font=("Comic Book", 10))
        self.tview_my_hikes = ttk.Style()
        self.tview_my_hikes.configure("Treeview", font=("Comic Book", 10), rowheight=55)

        # create treeview for search results
        self.tview_my_hikes = ttk.Treeview(frame_my_hikes_box, style="Custom.Treeview", selectmode="browse")
        self.tview_my_hikes['columns'] = ('complete', 'name', 'total_distance', 'elev_gain', 'max_elev',
                                          'prominence', 'diff_rating', 'gen_area', 'dist_from_home')
        self.tview_my_hikes.column("#0", width=0, minwidth=0)
        self.tview_my_hikes.column("complete", width=30, minwidth=30, anchor="c")
        self.tview_my_hikes.column("name", width=200, minwidth=200)
        self.tview_my_hikes.column("total_distance", width=100, minwidth=100)
        self.tview_my_hikes.column("elev_gain", width=100, minwidth=100)
        self.tview_my_hikes.column("max_elev", width=100, minwidth=100)
        self.tview_my_hikes.column("prominence", width=100, minwidth=100)
        self.tview_my_hikes.column("diff_rating", width=110, minwidth=110)
        self.tview_my_hikes.column("gen_area", width=150, minwidth=150)
        self.tview_my_hikes.column("dist_from_home", width=130, minwidth=130)

        self.tview_my_hikes.heading("#0", text="Label", anchor="w")
        self.tview_my_hikes.heading(
            "complete",
            text="✔",
            command=lambda _col="complete": self.treeview_sort(self.tview_my_hikes, _col, False)
        )
        self.tview_my_hikes.heading(
            "name",
            text="Name",
            command=lambda _col="name": self.treeview_sort(self.tview_my_hikes, _col, False)
        )
        self.tview_my_hikes.heading(
            "total_distance",
            text="Total Dist",
            command=lambda _col="total_distance": self.treeview_sort(self.tview_my_hikes, _col, False)
        )
        self.tview_my_hikes.heading(
            "elev_gain",
            text="Elev Gain",
            command=lambda _col="elev_gain": self.treeview_sort(self.tview_my_hikes, _col, False)
        )
        self.tview_my_hikes.heading(
            "max_elev",
            text="Max Elev",
            command=lambda _col="max_elev": self.treeview_sort(self.tview_my_hikes, _col, False)
        )
        self.tview_my_hikes.heading(
            "prominence",
            text="Prominence",
            command=lambda _col="prominence": self.treeview_sort(self.tview_my_hikes, _col, False)
        )
        self.tview_my_hikes.heading(
            "diff_rating",
            text="Diff Rating",
            command=lambda _col="diff_rating": self.treeview_sort(self.tview_my_hikes, _col, False)
        )
        self.tview_my_hikes.heading(
            "gen_area",
            text="General Area",
            command=lambda _col="gen_area": self.treeview_sort(self.tview_my_hikes, _col, False)
        )
        self.tview_my_hikes.heading(
            "dist_from_home",
            text="Dist from Home",
            command=lambda _col="dist_from_home": self.treeview_sort(self.tview_my_hikes, _col, False)
        )

        self.tview_my_hikes.bind("<Double-1>", self.on_double_click)

        # scrollbar for treeview
        vsb = ttk.Scrollbar(
            frame_my_hikes_box,
            orient="vertical",
            command=self.tview_my_hikes.yview
        )
        self.tview_my_hikes.configure(yscrollcommand=vsb.set)

        self.tview_my_hikes.pack(side='left')
        vsb.pack(side='right', fill='y')

        # add search results to treeview
        id_ = 1
        for hike in hike_list:
            if hike[9] == 1:
                complete = "✔"
            else:
                complete = " "
            if hike[5] == 0:
                prom = "N/A"
            else:
                prom = hike[5], "ft"
            if hike[10] == 1:
                self.tview_my_hikes.insert(
                    parent='',
                    index='end',
                    iid=id_,
                    text="",
                    values=(complete, hike[1], (hike[2], "miles"), (hike[3], "ft"), (hike[4], "ft"), prom,
                            hike[6], hike[7], (hike[8], "hours"))
                )
            id_ += 1

        btn_main = tk.Button(
            master=self,
            text="Return to Menu",
            font=("Comic Book", 17, "bold"),
            bg="#1b4760",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            width=18,
            height=2,
            command=lambda: controller.show_frame(MainMenu)
        )
        btn_main.pack(side='right', padx=50)

    def on_double_click(self, *args):
        value = self.tview_my_hikes.item(self.tview_my_hikes.focus())
        selected_hike = []
        for hike in hike_list:
            if hike[1] == value['values'][1]:
                selected_hike = hike
        pop_up = tk.Toplevel()
        pop_up.geometry("800x600")
        pop_up.title(value['values'][1])
        pop_up.iconbitmap(r"pp.ico")
        pop_up.resizable(False, False)
        frame = HikeDetails(pop_up, self, selected_hike)
        frame.grid_rowconfigure(0, weight=1)
        frame.pack(expand=True, fill="both")

    # sort treeview table
    def treeview_sort(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k), in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda _col=col: self.treeview_sort(tv, _col, not reverse))


# search results class
class AllHikes(tk.Frame):

    def __init__(self, parent, controller):
        self.main_background = ImageTk.PhotoImage(Image.open(r"peak_pro_main_bg.jpg"))
        self.all_hikes_title = ImageTk.PhotoImage(Image.open(r"all_hikes.png"))

        tk.Frame.__init__(self, parent)

        lbl_all_hikes_background = tk.Label(
            master=self,
            image=self.main_background,
            borderwidth=0,
            highlightthickness=0
        )
        lbl_all_hikes_background.place(x=0, y=0)

        lbl_all_hikes_text = tk.Label(
            master=self,
            image=self.all_hikes_title,
            borderwidth=0,
            highlightthickness=0
        )
        lbl_all_hikes_text.pack(pady=(23, 0))

        # create frame for search results box
        frame_all_hikes_box = tk.Frame(
            master=self,
            bg="#ffffff",
            highlightthickness=5,
            highlightbackground="black",
            height=475
        )
        frame_all_hikes_box.columnconfigure(0, weight=0)
        frame_all_hikes_box.pack_propagate(0)
        frame_all_hikes_box.pack(padx=25, pady=(25, 0), fill='x')

        # treeview style
        tview_heading_style = ttk.Style()
        tview_heading_style.configure("Treeview.Heading", font=("Comic Book", 10))
        tview_style = ttk.Style()
        tview_style.configure("Treeview", font=("Comic Book", 10), rowheight=55)

        # custom style for headers
        style = ttk.Style()
        style.element_create("Custom.Treeheading.border", "from", "default")
        style.layout("Custom.Treeview.Heading", [
            ("Custom.Treeheading.cell", {'sticky': 'nswe'}),
            ("Custom.Treeheading.border", {'sticky': 'nswe', 'children': [
                ("Custom.Treeheading.padding", {'sticky': 'nswe', 'children': [
                    ("Custom.Treeheading.image", {'side': 'right', 'sticky': ''}),
                    ("Custom.Treeheading.text", {'sticky': 'we'})
                ]})
            ]}),
        ])
        style.configure("Custom.Treeview.Heading",
                        background="black", foreground="white", relief="flat", rowheight=100)
        style.map("Custom.Treeview.Heading",
                  relief=[('active', 'groove'), ('pressed', 'sunken')])

        # create treeview for search results
        self.tview_all_hikes = ttk.Treeview(frame_all_hikes_box, style="Custom.Treeview", selectmode="browse")
        self.tview_all_hikes['columns'] = ('complete', 'name', 'total_distance', 'elev_gain', 'max_elev',
                                           'prominence', 'diff_rating', 'gen_area', 'dist_from_home')
        self.tview_all_hikes.column("#0", width=0, minwidth=0)
        self.tview_all_hikes.column("complete", width=30, minwidth=30, anchor="c")
        self.tview_all_hikes.column("name", width=200, minwidth=200)
        self.tview_all_hikes.column("total_distance", width=100, minwidth=100)
        self.tview_all_hikes.column("elev_gain", width=100, minwidth=100)
        self.tview_all_hikes.column("max_elev", width=100, minwidth=100)
        self.tview_all_hikes.column("prominence", width=100, minwidth=100)
        self.tview_all_hikes.column("diff_rating", width=110, minwidth=110)
        self.tview_all_hikes.column("gen_area", width=150, minwidth=150)
        self.tview_all_hikes.column("dist_from_home", width=130, minwidth=130)

        self.tview_all_hikes.heading("#0", text="Label", anchor="w")
        self.tview_all_hikes.heading(
            "complete",
            text="✔",
            command=lambda _col="complete": self.treeview_sort(self.tview_all_hikes, _col, False)
        )
        self.tview_all_hikes.heading(
            "name",
            text="Name",
            command=lambda _col="name": self.treeview_sort(self.tview_all_hikes, _col, False)
        )
        self.tview_all_hikes.heading(
            "total_distance",
            text="Total Dist",
            command=lambda _col="total_distance": self.treeview_sort(self.tview_all_hikes, _col, False)
        )
        self.tview_all_hikes.heading(
            "elev_gain",
            text="Elev Gain",
            command=lambda _col="elev_gain": self.treeview_sort(self.tview_all_hikes, _col, False)
        )
        self.tview_all_hikes.heading(
            "max_elev",
            text="Max Elev",
            command=lambda _col="max_elev": self.treeview_sort(self.tview_all_hikes, _col, False)
        )
        self.tview_all_hikes.heading(
            "prominence",
            text="Prominence",
            command=lambda _col="prominence": self.treeview_sort(self.tview_all_hikes, _col, False)
        )
        self.tview_all_hikes.heading(
            "diff_rating",
            text="Diff Rating",
            command=lambda _col="diff_rating": self.treeview_sort(self.tview_all_hikes, _col, False)
        )
        self.tview_all_hikes.heading(
            "gen_area",
            text="General Area",
            command=lambda _col="gen_area": self.treeview_sort(self.tview_all_hikes, _col, False)
        )
        self.tview_all_hikes.heading(
            "dist_from_home",
            text="Dist from Home",
            command=lambda _col="dist_from_home": self.treeview_sort(self.tview_all_hikes, _col, False)
        )

        self.tview_all_hikes.bind("<Double-1>", self.on_double_click)

        # scrollbar for treeview
        vsb = ttk.Scrollbar(
            frame_all_hikes_box,
            orient="vertical",
            command=self.tview_all_hikes.yview
        )
        self.tview_all_hikes.configure(yscrollcommand=vsb.set)

        self.tview_all_hikes.pack(side='left')
        vsb.pack(side='right', fill='y')

        # add all hikes to treeview
        id_ = 1
        for hike in hike_list:
            if hike[9] == 1:
                complete = "✔"
            else:
                complete = " "
            if hike[5] == 0:
                prom = "N/A"
            else:
                prom = hike[5], "ft"
            self.tview_all_hikes.insert(
                parent='',
                index='end',
                iid=id_,
                text="",
                values=(complete, hike[1], (hike[2], "miles"), (hike[3], "ft"), (hike[4], "ft"), prom,
                        hike[6], hike[7], (hike[8], "hours"))
            )
            id_ += 1

        btn_main = tk.Button(
            master=self,
            text="Return to Menu",
            font=("Comic Book", 17, "bold"),
            bg="#1b4760",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            width=18,
            height=2,
            command=lambda: controller.show_frame(MainMenu)
        )
        btn_main.pack(side='right', padx=50)

    def on_double_click(self, *args):
        value = self.tview_all_hikes.item(self.tview_all_hikes.focus())
        selected_hike = []
        for hike in hike_list:
            if hike[1] == value['values'][1]:
                selected_hike = hike
        pop_up = tk.Toplevel()
        pop_up.geometry("800x600")
        pop_up.title(value['values'][1])
        pop_up.iconbitmap(r"pp.ico")
        pop_up.resizable(False, False)
        frame = HikeDetails(pop_up, self, selected_hike)
        frame.grid_rowconfigure(0, weight=1)
        frame.pack(expand=True, fill="both")

    # sort treeview table
    def treeview_sort(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k), in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda _col=col: self.treeview_sort(tv, _col, not reverse))


# pop up class for hike details
class HikeDetails(tk.Frame):

    def __init__(self, parent, controller, hike_):

        self.details_bg = ImageTk.PhotoImage(Image.open(r"hike_details_bg.jpg"))
        self.hike_photo = ImageTk.PhotoImage(Image.open(r"summit_photo.jpg"))
        self.hike_ = hike_

        tk.Frame.__init__(self, parent)

        lbl_details_bg = tk.Label(
            master=self,
            image=self.details_bg,
            borderwidth=0,
            highlightthickness=0
        )
        lbl_details_bg.place(x=0, y=0)

        lbl_hike_title = tk.Label(
            master=self,
            text=hike_[1],
            font=("Comic Book", 36, "bold"),
            bg="#c6c2dd",
            fg="#103448",
            borderwidth=0,
            highlightthickness=0
        ).pack(pady=(5, 0))

        lbl_area = tk.Label(
            master=self,
            text=hike_[7],
            font=("Comic Book", 18, "bold"),
            bg="#c6c2dd",
            fg="#103448",
            borderwidth=0,
            highlightthickness=0
        ).pack()

        lbl_distance_from_home = tk.Label(
            master=self,
            text=(str(hike_[8]) + " hours from Tacoma"),
            font=("Comic Book", 18, "bold"),
            bg="#c6c2dd",
            fg="#103448",
            borderwidth=0,
            highlightthickness=0
        ).pack()

        frame_hike_info = tk.Frame(
            master=self,
            background="white",
            highlightthickness=5,
            highlightbackground="#1b4760"
        )
        frame_hike_info.columnconfigure(0, weight=1, minsize=100)
        frame_hike_info.columnconfigure(1, weight=1, minsize=200)
        frame_hike_info.pack(pady=10, padx=15)

        frame_hike_info_details = tk.Frame(
            master=frame_hike_info,
            background="white",
        )
        frame_hike_info_details.grid(column=0, row=0, sticky="n", pady=20, padx=(15, 0))

        lbl_total_distance = tk.Label(
            master=frame_hike_info_details,
            text=("Total Distance: " + str(hike_[2]) + " miles"),
            font=("Comic Book", 14, "bold"),
            bg="white",
            fg="#103448",
            borderwidth=0,
            highlightthickness=0
        ).grid(column=0, row=0, sticky="w", padx=(10, 0))

        lbl_elev_change = tk.Label(
            master=frame_hike_info_details,
            text=("Elevation Gain: " + str(hike_[3]) + " ft"),
            font=("Comic Book", 14, "bold"),
            bg="white",
            fg="#103448",
            borderwidth=0,
            highlightthickness=0
        ).grid(column=0, row=1, sticky="w", padx=(10, 0))

        lbl_max_elev = tk.Label(
            master=frame_hike_info_details,
            text=("Max Elevation: " + str(hike_[4]) + " ft"),
            font=("Comic Book", 14, "bold"),
            bg="white",
            fg="#103448",
            borderwidth=0,
            highlightthickness=0
        ).grid(column=0, row=2, sticky="w", padx=(10, 0))

        lbl_prom = tk.Label(
            master=frame_hike_info_details,
            text=("Prominence: " + str(hike_[5]) + " ft"),
            font=("Comic Book", 14, "bold"),
            bg="white",
            fg="#103448",
            borderwidth=0,
            highlightthickness=0
        ).grid(column=0, row=3, sticky="w", padx=(10, 0))

        lbl_diff_rating = tk.Label(
            master=frame_hike_info_details,
            text=("Difficulty Rating: " + hike_[6]),
            font=("Comic Book", 14, "bold"),
            bg="white",
            fg="#103448",
            borderwidth=0,
            highlightthickness=0
        ).grid(column=0, row=4, sticky="w", padx=(10, 0))

        lbl_trailhead_link = tk.Label(
            master=frame_hike_info_details,
            text="Trailhead Location",
            font=("Comic Book", 14, "bold"),
            bg="white",
            fg="#4c7298",
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2"
        )
        lbl_trailhead_link.grid(column=0, row=5, sticky="w", padx=(10, 0))
        lbl_trailhead_link.bind(
            "<Button-1>",
            lambda e: self.callback(
                "https://www.google.com/maps/place/Mt.+Si+Trailhead/@47.4891732,-121.7355853,14.25z/data=!4m13!1m7!3m6!"
                "1s0x54907e8ab5b8fa19:0xc5df1f9a8d23f99!2sMount+Si+Trail,+Washington+98045!3b1!8m2!3d47.4970068!4d-121."
                "731891!3m4!1s0x54907e67c323cddd:0xc8541391393bdc7d!8m2!3d47.4880423!4d-121.7231619!5m1!1e4"
            )
        )

        lbl_notes = tk.Label(
            master=frame_hike_info_details,
            text="Notes:",
            font=("Comic Book", 14, "bold"),
            bg="white",
            fg="#103448",
            borderwidth=0,
            highlightthickness=0,
        ).grid(column=0, row=6, sticky="w", padx=(10, 0))

        txt_notes = tk.Text(
            master=frame_hike_info_details,
            font=("Comic Book", 11, "bold"),
            bg="white",
            fg="#103448",
            height=4,
            width=22
        )
        txt_notes.grid(column=0, row=7, sticky="w", padx=(10, 0))

        frame_hike_complete = tk.Frame(
            master=frame_hike_info_details,
            background="white"
        )
        frame_hike_complete.grid(column=0, row=8, sticky="w", padx=(10, 0))

        lbl_complete = tk.Label(
            master=frame_hike_complete,
            text="Complete:",
            font=("Comic Book", 14, "bold"),
            bg="white",
            fg="#103448",
            borderwidth=0,
            highlightthickness=0
        ).grid(column=0, row=0, sticky="w")

        complete_val = tk.IntVar()
        tk.Radiobutton(
            master=frame_hike_complete,
            font=("Comic Book", 14, "bold"),
            bg="white",
            fg="#103448",
            text="Yes",
            variable=complete_val,
            value=1
        ).grid(column=1, row=0)

        tk.Radiobutton(
            master=frame_hike_complete,
            font=("Comic Book", 14, "bold"),
            bg="white",
            fg="#103448",
            text="No",
            variable=complete_val,
            value=0
        ).grid(column=2, row=0)

        btn_save = tk.Button(
            master=frame_hike_info_details,
            text="Save",
            font=("Comic Book", 14, "bold"),
            bg="#103448",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            width=10,
            command=self.save
        )
        btn_save.grid(column=0, row=9, pady=20, padx=(10, 0))

        frame_hike_photo = tk.Frame(
            master=frame_hike_info,
            background="white"
        )
        frame_hike_photo.grid(column=1, row=0)

        lbl_summit_photo = tk.Label(
            master=frame_hike_photo,
            image=self.hike_photo,
            borderwidth=0,
            highlightthickness=0
        ).grid(column=1, row=0, sticky="e", padx=(24, 15), pady=(15, 0))

        lbl_summit_photo_caption = tk.Label(
            master=frame_hike_photo,
            text="[Placeholder image caption]",
            font=("Comic Book", 12, "bold"),
            bg="white",
            fg="#103448",
            borderwidth=0,
            highlightthickness=0
        ).grid(column=1, row=1, sticky="ew")

    def callback(self, url):
        webbrowser.open_new(url)

    def save(self):
        messagebox.showinfo("Success", "Notes and completion status saved!")


app = MainApp()
app.geometry("1100x700")
app.title("Summit Register")
app.iconbitmap(r"pp.ico")
app.resizable(False, False)
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(0, weight=1)
app.mainloop()
