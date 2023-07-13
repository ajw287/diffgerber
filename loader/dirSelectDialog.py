import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os

class dirSelectDialog():
    """
    dirSelectDialog a dialog that lets you select a 
    gerber file or a directory and opens the directory 
    that contains the file (or the directory) - sounds simple... not at all!
    """
    def __init__(self, parent = None):
        if parent is None:
            self.root = tk.Tk()
        else:
            self.root = parent
        self.selected_directory = None
        self.nav_path = os.getcwd()
        self.file_filter = {"PNG images": (".png"), "Gerber files": (".gbr", ".grb"), "All files": ("*.*")}  # Example file filters
        self.filter_var = tk.StringVar()
        self.dialog = None
        self.dialogFlag = False

    def browse(self):
        filetypes = [("PNG files", "*.png"), ("Gerber files", (".gbr", ".grb")), ("Python files", "*.py"), ("All files", "*.*")]
        self.dialog = tk.Toplevel(self.root)
        self.dialogFlag = True
        self.dialog.title("File Dialog")
        treeview = ttk.Treeview(self.dialog, columns=("name", "type"), show="headings")
        treeview.heading("name", text="Name")
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
            treeview.insert("", tk.END, values=("..", "directory"), text=os.path.dirname(path))
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
                if item_type == "directory":
                    path = treeview.item(selected_item, "text")
                    populate_treeview(path)

        treeview.pack(fill=tk.BOTH, expand=True)

        # Create file filter drop-down box
        
        self.filter_var.set("Gerber files")  # Set default filter
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
        print("dialog doesn't exist")
        print(dialog)
    root.after(2000, checkDialog, root, dialog)

if __name__ == "__main__":
    root = tk.Tk()
    dialog = dirSelectDialog(root)
    browse_button = ttk.Button(root, text="Browse", command=dialog.browse)
    browse_button.pack()
    checkDialog(root, dialog)
    root.mainloop()
    
    