import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os


non_gerber_but_related = ['*-PTH.drl', '*.drl', '*.txt', '*.xln', '*.exc', '*.drd', '*.tap', '*.fab.gbr', '*.plated-drill.cnc', 'drl', '*-NPTH.drl', '*-User?Eco1.*', '*-Eco1?User.*', 'vcut', '*.gm1', '*-Edge?Cuts.*', '*.gko', '*.gm3', '*.dim', '*.gml', '*.fab', '*.out.gbr', '*.boardout.ger', 'ko',]


class dirSelectDialog():
    """
    dirSelectDialog a dialog that lets you select a 
    gerber file or a directory and opens the directory 
    that contains the file (or the directory) - sounds simple... not at all!
    """
    gerber_filetypes = (
                '*.gtp', '*-F*Paste.*', '*.crc', '*.tsp', '*.stp', '*.toppaste.gbr', '*.tcream.ger',
                '*.gto', '*-F*SilkS.*', '*.plc', '*.tsk', '*.sst', '*.topsilk.gbr', '*.topsilkscreen.ger', 'to',
                '*.gts', '*-F*Mask.*', '*.stc', '*.tsm', '*.smt', '*.topmask.gbr', '*.topsoldermask.ger', 'ts',
                '*.gtl', '*-L1.*', '*.g1', '*-F*Cu*', '*.cmp', '*.top', '*.top.gbr', '*.toplayer.ger', 'tl',
                '*.g1', '*.g2', '*-L2.*', '*-In1*Cu*', '*-Inner1*Cu*', '*.ly1', '*.ly2', '*.in1', '*.internalplane1.ger', '*.gbl', '*-B*Cu*', '*.sol', '*.bot', '*.bottom.gbr', '*.bottomlayer.ger', 'l2', 'bl',
                '*.g2', '*.g3', '*-L3.*', '*-In2*Cu*', '*-Inner2*Cu*', '*.ly2', '*.ly3', '*.in2', '*.internalplane2.ger', '*.gbl', '*-B*Cu*', '*.sol', '*.bot', '*.bottom.gbr', '*.bottomlayer.ger', 'l3', 'bl',
                '*.g3', '*.g4', '*-L4.*', '*-In3*Cu*', '*-Inner3*Cu*', '*.ly3', '*.ly4', '*.in3', '*.internalplane3.ger', '*.gbl', '*-B*Cu*', '*.sol', '*.bot', '*.bottom.gbr', '*.bottomlayer.ger', 'l4', 'bl',
                '*.g4', '*.g5', '*-L5.*', '*-In4*Cu*', '*-Inner4*Cu*', '*.ly4', '*.ly5', '*.in4', '*.internalplane4.ger', '*.gbl', '*-B*Cu*', '*.sol', '*.bot', '*.bottom.gbr', '*.bottomlayer.ger', 'l5', 'bl',
                '*.g5', '*.g6', '*-L6.*', '*.gbl', '*-B*Cu*', '*.sol', '*.bot', '*.bottom.gbr', '*.bottomlayer.ger', 'bl',
                '*.gbs', '*-B*Mask.*', '*.sts', '*.bsm', '*.smb', '*.bottommask.gbr', '*.bottomsoldermask.ger', 'bs',
                '*.gbo', '*-B*SilkS.*', '*.pls', '*.bsk', '*.ssb', '*.bottomsilk.gbr', '*.bottomsilkscreen.ger',
                '*.gbp', '*-B*Paste.*', '*.crs', '*.bsp', '*.spb', '*.bottompaste.gbr', '*.bcream.ger',
    )

    def __init__(self, parent = None):
        if parent is None:
            self.root = tk.Tk()
        else:
            self.root = parent
        self.selected_directory = None
        self.nav_path = os.getcwd()
        self.file_filter = {"PNG images": (".png"), "GerberX2 files": (".gbr", ".grb"), "All known gerbers":self.gerber_filetypes, "All files": ("*.*")}  # Example file filters
        self.filter_var = tk.StringVar()
        self.dialog = None
        self.dialogFlag = False

    def browse(self):
        #filetypes = [("PNG files", "*.png"), ("GerberX2 files", (".gbr", ".grb")), ("All known gerbers", self.gerber_filetypes), ("Python files", "*.py"), ("All files", "*.*")]
        self.dialog = tk.Toplevel(self.root)
        self.dialogFlag = True
        self.dialog.title("Select example Gerber file or directory to compare")
        self.dialog.geometry('600x350')
        
        #SOLUTION from: https://stackoverflow.com/questions/26957845/ttk-treeview-cant-change-row-height
        style = ttk.Style(self.dialog)
        style.configure('gerberFileDialog.Treeview', rowheight=25)  
        treeview = ttk.Treeview(self.dialog, columns=("name", "type"), show="headings", style='gerberFileDialog.Treeview')
        treeview.heading("name", text="Filename")
        treeview.heading("type", text="Type")

        def select_item():
            selected_item = treeview.focus()
            if selected_item:
                item_type = treeview.item(selected_item, "values")[1]
                if item_type == "file":
                    self.selected_directory = os.path.dirname(treeview.item(selected_item, "text"))
                else:
                    self.selected_directory = treeview.item(selected_item, "text")
            else:
                self.selected_directory = self.nav_path
            print(self.selected_directory)
            self.dialogFlag = False
            self.dialog.destroy()

        def populate_treeview(path):
            treeview.delete(*treeview.get_children())

            # Insert parent directory button
            treeview.insert("", tk.END, values=("..", "directory above"), text=os.path.dirname(path))
            self.nav_path = path #os.path.dirname(path)
            for item in os.scandir(path):
                if item.is_file() and item.name.lower().endswith(self.file_filter[self.filter_var.get()]):
                    treeview.insert("", tk.END, values=(item.name, "file"), text=item.path)
                elif item.is_dir():
                    treeview.insert("", tk.END, values=(item.name, "directory"), text=item.path)

        def browse_parent_directory():
            selected_item = treeview.focus()
            if selected_item:
                path = os.path.dirname(treeview.item(selected_item, "text"))
                populate_treeview(path)

        def browse_sub_directory(event):
            selected_item = treeview.focus()
            if selected_item:
                item_type = treeview.item(selected_item, "values")[1]
                if item_type == "directory" or item_type == "directory above":
                    path = treeview.item(selected_item, "text")
                    populate_treeview(path)

        treeview.pack(fill=tk.BOTH, expand=True)

        # Create file filter drop-down box
        
        self.filter_var.set("GerberX2 files")  # Set default filter
        filter_dropdown = ttk.Combobox(self.dialog, values=list(self.file_filter.keys()), textvariable=self.filter_var)
        filter_dropdown.pack()

        select_button = ttk.Button(self.dialog, text="Select", command=select_item)
        select_button.pack(pady=5)
        populate_treeview(os.getcwd())
        treeview.bind("<Double-1>", browse_sub_directory)

        self.dialog.mainloop()
    
    def get_filetypes(self, selected_filetype):
        if selected_filetype == "PNG files":
            return [(".png",)]
        elif selected_filetype == "Python files":
            return [(".py",)]
        else:
            return [("*.*",)]

def subwindow_closed ():
    print("dailog closed and directory has been got...")

def checkDialog(root, dialog):
    if dialog.dialogFlag: #isinstance(dialog.dialog, object):
        print("dialog exists")
        print(dialog.dialog)
    else:
        print("dialog doesn't exist.. time to do a thing with the dir: ")
        print(dialog.selected_directory)
        print(dialog)
    root.after(2000, checkDialog, root, dialog)

if __name__ == "__main__":
    root = tk.Tk()
    dialog = dirSelectDialog(root)
    browse_button = ttk.Button(root, text="Browse", command=dialog.browse)
    browse_button.pack()
    checkDialog(root, dialog)
    root.mainloop()
    
    
