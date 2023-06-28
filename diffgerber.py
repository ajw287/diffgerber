import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import pygerber as pyg
import pygerber.API2D as api

import color_generator as cg

#from pygerber.types import ColorSet
from pygerber.parser.pillow.parser import ColorSet

photos  = []
imageDict = {}

#DEFAULT_COLOR_SET_ORANGE = ColorSet(
#    (209, 110, 44),
#    (0, 0, 0, 0),
#    (0, 0, 0, 0),
#)

colorGen = cg.color_generator()

def load_images(directory):
    """Load image files from the selected directory."""
    images = []
    filenames = []
    layer_colors = []
    for i, filename in enumerate(os.listdir(os.fsencode(directory))):
        if filename.decode().endswith((".jpg", ".png")):
            filepath = os.path.join(directory, filename.decode())
            image = Image.open(filepath)
            images.append(image)
            filenames.append(filename.decode())
        elif filename.decode().endswith((".gbr", ".grb")):
            filepath = os.path.join(directory, filename.decode())
            c, rgb = colorGen.getNextColorSet()
            image = pyg.API2D.render_file(filepath, colors=c )
            images.append(image)
            filenames.append(filename.decode())
            layer_colors.append(rgb)
    return images, filenames, layer_colors

def show_image(image, filename):
    if not True:
        hide_image(image,filename)
        return 
    """Display the selected image on the canvas."""
    img_width, img_height = image.size
    photo = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor="nw", image=photo)
    canvas.image = photo  # Store a reference to prevent garbage collection
    #photos.append(photo) # add images to list to stop garbage collection
    imageDict.update({filename: photo})
    #print(imageDict)
    
def hide_image(image, filename):
    print("remove the image from the photos")

def directory_selected(frame, directory_entry):
    """Handle the event when a directory is selected."""
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(tk.END, selected_directory)
        images, filenames, layer_colors = load_images(selected_directory)

        # Clear the checkboxes
        for checkbox in frame_checkboxes[frame]:
            checkbox.destroy()
        frame_checkboxes[frame].clear()

        # Create checkboxes
        for i, image in enumerate(images):
            checkbox = tk.Checkbutton(
                frame,
                #text=f"Image {i+1}",
                text = filenames[i],
                variable=selected_images_var,
                onvalue=i,
                offvalue=-1,
                selectcolor= layer_colors[i],
                command=lambda i=i: show_image( images[i], filenames[i])
                #command=lambda checked, img=images[i], flnm=filenames[i]: show_image(checked, img, flnm)
            )
            checkbox.pack(anchor="w")
            frame_checkboxes[frame].append(checkbox)

        #selected_images_var.set(-1)
        # TODO: make this the check for differences and display them
        if images:
            show_image( images[0], filenames[0])

#def toolbar_button_clicked():
#    """Handle the event when the toolbar button is clicked."""
#    print("Toolbar button clicked!")
def button1_clear_clicked():
    #print("Button 1 clicked")
    # Clear the checkboxes
    for frame in frame_checkboxes:
        for checkbox in frame_checkboxes[frame]:
            checkbox.destroy()
        frame_checkboxes[frame].clear()
    canvas.delete("all")
    imageDict = {}
    photos  = []
    


def button2_reload_clicked():
    print("Reload Button clicked -  reload dirs \n\n *** NOT IMPLEMENTED ***\n\n")

def button3_export_clicked():

    print("Button 3 clicked - export an image \n\n *** NOT IMPLEMENTED ***\n\n")
    f = filedialog.asksaveasfile(parent=window, title="Save postscript", mode='w', defaultextension=".ps")
    if f is None:
        return
    print (f.name)
    canvas.postscript(file=f.name, colormode='color')

def button4_zoomin_clicked():
    print("Button 4 clicked zoom +\n\n *** NOT IMPLEMENTED ***\n\n")

def button5_zoomout_clicked():
    print("Button 5 clicked zoom -\n\n *** NOT IMPLEMENTED ***\n\n")

def button6_diff_clicked():
    print("Button 6 clicked (hightlight differences)\n\n *** NOT IMPLEMENTED ***\n\n")
 
#from: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar 
# doesn't work... 
#def OnMouseWheel(self,event):
#    hscrollbar.yview("scroll",event.delta,"units")
#    return "break" 
    
# Create the main window
window = tk.Tk()
window.title("Gerber Difference Viewer")

# Calculate the window size based on screen size
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window_width = int(screen_width * 2 / 3)
window_height = int(screen_height * 2 / 3)
window.geometry(f"{window_width}x{window_height}")

# Create a main frame
main_frame = tk.Frame(window)
main_frame.pack(fill=tk.BOTH, expand=True)
# Create the toolbar frame
toolbar_frame = tk.Frame(main_frame)
toolbar_frame.pack(side="top", fill="x")

# Create the buttons in the toolbar
button1 = tk.Button(toolbar_frame, text="Clear", command=button1_clear_clicked)
button1.pack(side="left", padx=5, pady=5)

button2 = tk.Button(toolbar_frame, text="Reload", command=button2_reload_clicked)
button2.pack(side="left", padx=5, pady=5)

button3 = tk.Button(toolbar_frame, text="Export Image", command=button3_export_clicked)
button3.pack(side="left", padx=5, pady=5)

button4 = tk.Button(toolbar_frame, text="Zoom +", command=button4_zoomin_clicked)
button4.pack(side="left", padx=5, pady=5)

button5 = tk.Button(toolbar_frame, text="Zoom -", command=button5_zoomout_clicked)
button5.pack(side="left", padx=5, pady=5)

button6 = tk.Button(toolbar_frame, text="Hightlight Differences", command=button6_diff_clicked)
button6.pack(side="left", padx=5, pady=5)

layer_similarity_label = tk.Label(toolbar_frame, text="Selected Layers are not paired")
layer_similarity_label.pack(side=tk.RIGHT, padx = 150, pady = 10)

# Create the three vertical columns
left_frame = tk.Frame(main_frame, width=75)
left_frame.pack(side="left", padx=10, fill=tk.Y, expand=False)
middle_frame = tk.Frame(main_frame)
middle_frame.pack(side="left", fill=tk.BOTH, expand=True)
right_frame = tk.Frame(main_frame, width=150)
right_frame.pack(side="right", padx=10, fill=tk.Y, expand=False)

# Left column: Directory selector
left_directory_label = tk.Label(left_frame, text="Gerber directory 1:")
left_directory_label.pack(anchor=tk.NW)
left_directory_entry = tk.Entry(left_frame)
left_directory_entry.pack(anchor=tk.NW)
left_directory_button = tk.Button(left_frame, text="Browse", command=lambda: directory_selected(left_frame, left_directory_entry))
left_directory_button.pack(anchor=tk.NW)

# Right column: Directory selector
right_directory_label = tk.Label(right_frame, text="Gerber directory 2:")
right_directory_label.pack(anchor=tk.NW)
right_directory_entry = tk.Entry(right_frame)
right_directory_entry.pack(anchor=tk.NW)
right_directory_button = tk.Button(right_frame, text="Browse", command=lambda: directory_selected(right_frame, right_directory_entry))
right_directory_button.pack(anchor=tk.NW)

# Middle column: Canvas to display the images with scrollbars
# Create a canvas with scrollbars
#canvas = tk.Canvas(middle_frame, width=400, height=400)
canvas = tk.Canvas(middle_frame, width=400, height=400, bg="grey")
canvas.pack(fill=tk.BOTH, expand=True)

# Create vertical and horizontal scrollbars for the image frame
vscrollbar = tk.Scrollbar(canvas, orient=tk.VERTICAL, command=canvas.yview)

hscrollbar = tk.Scrollbar(canvas, orient=tk.HORIZONTAL, command=canvas.xview)

vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)


# Configure the canvas to use the scrollbars
canvas.configure(yscrollcommand=vscrollbar.set)
canvas.configure(xscrollcommand=hscrollbar.set)

# workscanvas.configure( xscrollcommand=hscrollbar.set, yscrollcommand=vscrollbar.set)
#canvas.bind("<MouseWheel>", canvas)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
#canvas.bind("<MouseWheel>", OnMouseWheel)

# Right column: List of checkboxes
selected_images_var = tk.StringVar()
selected_images_var.set(-1)
frame_checkboxes = {left_frame: [], right_frame: []}

# Run the GUI
window.mainloop()
