import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import PhotoImage
from tkinter import messagebox
from PIL import Image, ImageTk, ImageChops, ImageDraw, ImageFilter, ImageOps
import difflib as dl
#import color_generator as cg
import loader
#from pygerber.typs cg
#from pygerber.types import ColorSet
#from pygerber.parser.pillow.parser import ColorSet

photos  = []
imageDict = {}
directories  = ["", ""] # {left_frame: "", right_frame: ""}
left_file_list  = []
right_file_list = []
left_to_right_dict = {}
active_left_index = None
active_layer_image_left = None
active_layer_image_right = None
file_loader = loader.gerbLoader()

point_table = ([0] + ([255] * 255))
# diff code using only pillow
# from: https://stackoverflow.com/questions/30277447/compare-two-images-and-highlight-differences-along-on-the-second-image
# erode dilate using pillow:
# from: https://stackoverflow.com/questions/44195007/equivalents-to-opencvs-erode-and-dilate-in-pil
def new_gray(size, color):
    img = Image.new('L',size)
    dr = ImageDraw.Draw(img)
    dr.rectangle((0,0) + size, fill=color)
    return img

def new_color(size, color):
    img = Image.new(mode="RGBA", size=size, color=color)
    #dr = ImageDraw.Draw(img)
    #dr.rectangle((0,0) + size, fill=color)
    return img

def get_difference_outlines(a, b, opacity=0.85):
    """ Function to find differences in images

        Returns
        -------
        redmask : Image
            A semi transparent image with the differences of a & b highlighted with a thick red highlight outline
        """
    tellUser("checking for differences... hang on!", label_msg=True, record_msg=False)
    #convert the images to black and white - first
    a_gray = ImageOps.grayscale(a)
    b_gray = ImageOps.grayscale(b)
    #b_gray.show()
    #input()

    # threshold the images - since they are different colors - (anything above '1' becomes white)
    a_mask = a_gray.point(lambda x: 255 if x > 1 else 0, '1')
    b_mask = b_gray.point(lambda x: 255 if x > 1 else 0, '1')
    #b_mask.show()
    #input()


    a_inv = ImageOps.invert(a_mask)
    b_inv = ImageOps.invert(b_mask)
    #b_inv.show()
    #input()

    a_bw = a_inv.convert("1")
    b_bw = b_inv.convert("1")
    #b_bw.show()
    #input()
    diff = ImageChops.difference(a_bw, b_bw)
    diff = diff.convert('L')
    #diff.show()
    #input()

    new = diff.copy()
    shrink = new.filter(ImageFilter.MaxFilter(17))
    grow = shrink.filter(ImageFilter.MinFilter(3))
    inverted = ImageOps.invert(new)
    outline = ImageChops.difference(grow, inverted)
    outline = ImageOps.invert(outline)
    #outline.show()
    highlight_color = (247,  126,  185, 220)
    redmask = new_color(diff.size, color=(247,  126,  185, 0))  # same color but transparent - 
    #redmask.show()
    redmask.paste(highlight_color, (0,0), mask=outline)
    #redmask.show()
    #input()
    tellUser("displaying differences", label_msg=True, record_msg=False)
    return redmask
#    # Hack: there is no threshold in PILL,
#    # so we add the difference with itself to do
#    # a poor man's thresholding of the mask: 
#    #(the values for equal pixels-  0 - don't add up)
#    thresholded_diff = diff
#    for repeat in range(3):
#        thresholded_diff  = ImageChops.add(thresholded_diff, thresholded_diff)
#    h,w = size = diff.size
#    mask = new_gray(size, int(255 * (opacity)))
#    shade = new_gray(size, 0)
#    new = a.copy()
#    new.paste(shade, mask=mask)
#    # To have the original image show partially
#    # on the final result, simply put "diff" instead of thresholded_diff bellow
#    # was : new.paste(b, mask=thresholded_diff)
#    new.paste(b, mask=thresholded_diff)
#    shrink = new.filter(ImageFilter.MaxFilter(3))
#    grow = shrink.filter(ImageFilter.MinFilter(17))
#    
#    #outline  = grow.copy()
#    outline = ImageChops.difference(new, grow)
#    #outline2 = outline.filter(ImageFilter.MinFilter(5))
#    #outline.paste(shade, mask=mask)
#    redmask = new_color(size, color=(130,  166,  175, 100))#"#C0A60")#(230,  66,  75))
#    #redmask.show()
#    redmask.paste(shade, mask=grow)
#    #redmask.show()
#    tellUser("displaying differences", label_msg=True, record_msg=False)
#    #redmask.show()
#    return redmask


def update_file_pairs():
    global left_file_list, right_file_list, left_to_right_dict
    #print("updating file list" + str(left_file_list))
    for left_itr, left,  in enumerate(left_file_list):
        for right_itr, right in enumerate(right_file_list):
            if dl.SequenceMatcher(None, left, right).ratio() == 1.0:
                left_to_right_dict.update({left_itr: right_itr})
                tellUser("matched files named:" +left, label_msg=False)
                get_layer_similarity(left_itr)
    #print()
    if len(left_file_list) == 0:
        tellUser("no files in left list", label_msg=False)
    if len(right_file_list) == 0:
        tellUser("no files in right list", label_msg=False)

def get_layer_similarity(left_index):
    global left_file_list, right_file_list, left_to_right_dict, directories, active_layer_image_left, active_layer_image_right
    left_file_path = os.path.join(directories[0], left_file_list[left_index])
    print(left_file_path)
    with open(left_file_path, "r") as left_file:
        right_file_path = os.path.join(directories[1], right_file_list[left_to_right_dict[left_index]])
        print(right_file_path)
        with open(right_file_path, "r") as right_file:
            similarity = dl.SequenceMatcher(None, left_file.read(), right_file.read())
            if similarity.ratio() == 1.0:
                tellUser("file: "+str(left_file_list[left_index])+" is identical")
            elif similarity.ratio() >= .2:
                tellUser("file: "+str(left_file_list[left_index])+" is "+str(similarity.ratio() * 100.0)+"% similar")
                c = file_loader.color.getWhite()
                active_layer_image_left, lw =  file_loader.loadImage(left_file_path, color=c ) 
                active_layer_image_right, rw = file_loader.loadImage(right_file_path, color=c )
            else:
                tellUser("files: "+str(left_file_list[left_index])+" have same name but differ greatly")         

def load_images(directory):
    global photos
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
            image, rgb = file_loader.loadImage(filepath)
            images.append(image)
            filenames.append(filename.decode())
            layer_colors.append(rgb)
    return images, filenames, layer_colors

def show_image(image, full_filename):
    global imageDict
    #if not True:
    #    hide_image(image,filename)
    #    return 

    """Display the selected image on the canvas."""
    #img_width, img_height = image.size
    photo = imageDict.get(full_filename)
    if photo is None:
        photo = ImageTk.PhotoImage(image)
        imageDict.update({full_filename: photo})
    canvas.create_image(0, 0, anchor="nw", image=photo)
    canvas.image = photo  # Store a reference to prevent garbage collection
    #photos.append(photo) # add images to list to stop garbage collection
    
    
def layer_selected(image, full_filename, index):
    global active_left_index
    #TODO: this is a hacky way of finding the left-to-right lookup - is there a better way?
    
    # extract directory from full_filename -
    dirname = os.path.dirname(full_filename)
    active_left_index = None
    print("layer selected")
    print(directories)
    print(dirname)
    print("---")
    if dirname == directories[0]: #LHS selected
        if index in left_to_right_dict:
            get_layer_similarity(index)
            active_left_index = index
    elif dirname == directories[1]: #RHS selected
        print ("lhs value  (from rhs lookup)")
        keyFromValue = list(left_to_right_dict.keys())[list(left_to_right_dict.values()).index(index)]
        print(keyFromValue)
        active_left_index = keyFromValue
    if active_left_index:
        #there is an active pair for this layer...
        print("active layer selected")
    show_image(image, full_filename)
    #set the matched layer to selected bg = "grey"
    print(full_filename)
    
def hide_image(image, full_filename):
    print("remove the image from the photos")

def directory_select_btn(frame, directory_entry):
    """Handle the event when a directory is selected."""
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        tellUser("Please wait... loading gerbers")
        tellUser("directory "+ str(selected_directory), label_msg=False)
        directory_selected(frame, directory_entry, selected_directory)

def directory_selected(frame, directory_entry, selected_directory):
    global left_file_list, right_file_list, directories, frame_images, frame_checkboxes, frame_selected_layer_vars
    directory_entry.delete(0, tk.END)
    directory_entry.insert(tk.END, selected_directory)
    images, filenames, layer_colors = load_images(selected_directory)
    tellUser("loaded: "+selected_directory)
    frame_images.update({frame: images})

    # Clear the checkboxes
    for checkbox in frame_checkboxes[frame]:
        checkbox.destroy()
    frame_checkboxes[frame].clear()

    # Create checkboxes
    for i, image in enumerate(images):
        frame_selected_layer_vars[frame].append(tk.StringVar())
        checkbox = tk.Checkbutton(
            frame,
            #text=f"Image {i+1}",
            text = filenames[i],
            variable=frame_selected_layer_vars[frame][i],
            onvalue=i,
            #font = 12,
            #width = 10,
            #height = 1,
            #image=checkbutton_image,
            offvalue=-1,
            selectcolor= layer_colors[i],
            #command=lambda i=i: layer_selected(frame_images[frame][i], os.path.join(selected_directory, filenames[i]), i) if frame_selected_layer_vars[frame][i].get() == i else None
            command=lambda i=i: layer_selected( frame_images[frame][i], os.path.join(selected_directory, filenames[i]), i)
            #command=lambda checked, img=images[i], flnm=filenames[i]: show_image(checked, img, flnm)
        )
        checkbox.pack(anchor="w")
        frame_checkboxes[frame].append(checkbox)
        tellUser("Loaded file: " + filenames[i], label_msg=False, record_msg=True)

    #record the directory
    if frame is left_frame:
        directories[0] = selected_directory
        left_file_list = filenames
    elif frame is right_frame:
        directories[1] = selected_directory
        right_file_list = filenames
    #print(str(left_file_list))
    #print(str(right_file_list))
    update_file_pairs()
    #selected_images_var.set(-1)
    # TODO: make this the check for differences and display them
    if images:
        show_image( images[0], os.path.join(selected_directory, filenames[0]))

#def toolbar_button_clicked():
#    """Handle the event when the toolbar button is clicked."""
#    print("Toolbar button clicked!")
def button1_clear_clicked(clear_dirs=True):
    global imageDict, photos, left_directory , right_directory, left_file_list , right_file_list, left_to_right_dict
    #print("Button 1 clicked")
    # Clear the checkboxes
    for frame in frame_checkboxes:
        for checkbox in frame_checkboxes[frame]:
            checkbox.destroy()
        frame_checkboxes[frame].clear()
    canvas.delete("all")
    imageDict = {}
    photos  = []
    directories = ["", ""]
    right_file_list = []
    left_to_right_dict = {}
    if clear_dirs:
        left_directory_entry.delete(0,tk.END)
        right_directory_entry.delete(0,tk.END)

def button2_reload_clicked():
    #print("Reload Button clicked -  reload dirs")
    global left_frame, right_frame, left_directory_entry, right_directory_entry
    button1_clear_clicked(clear_dirs=False)
    if len(left_directory_entry.get()) >1:
        directory_selected(left_frame, left_directory_entry, left_directory_entry.get())
    if len(right_directory_entry.get()) >1:
        directory_selected(right_frame, right_directory_entry, right_directory_entry.get())

def button3_export_clicked():
    #print("Button 3 clicked - export an image \n\n *** NOT IMPLEMENTED ***\n\n")
    tellUser("export is experimental - consider using screen capture!")
    items = canvas.find_all()
    proceed_anyway = False
    if len(items) == 0:
         proceed_anyway = messagebox.askyesno("No data to export!", "The file will be blank - Are you sure you want to proceed?")
    if len(items) != 0 or proceed_anyway == True:
        f = filedialog.asksaveasfile(parent=window, title="Save postscript", mode='w', defaultextension=".ps")
        if f is None:
            return
        #print (f.name)
        canvas.postscript(file=f.name, colormode='color')

def button4_zoomin_clicked():
    print("Button 4 clicked zoom +\n\n *** NOT IMPLEMENTED ***\n\n")
    tellUser("zoom not implemented")

def button5_zoomout_clicked():
    print("Button 5 clicked zoom -\n\n *** NOT IMPLEMENTED ***\n\n")
    tellUser("zoom not implemented")

def button6_diff_clicked():
    if active_left_index is None:
        tellUser("Active layer unpaired - nothing to highlight")
        return
    diff_image = get_difference_outlines(active_layer_image_left, active_layer_image_right, opacity=0.55)
    show_image (diff_image, "diff_"+str(active_left_index))

def import_option_selected(event):
    global file_loader
    selected_option = import_option.get()
    file_loader.option = selected_option
    tellUser("Set to " + selected_option)

def tellUser(text_to_output, label_msg=True, record_msg=True):
    global window
    # Insert The text.
    if record_msg:
        text_area["state"] = tk.NORMAL
        text_area.insert(tk.END, '\n'+ text_to_output)
        text_area.configure(height=200)
        text_area.see("end")
        text_area["state"] = tk.DISABLED
    if label_msg:
        layer_similarity_label['text'] = text_to_output
        window.update_idletasks()
        
 
#from: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar 
# doesn't work... 
#def OnMouseWheel(self,event):
#    hscrollbar.yview("scroll",event.delta,"units")
#    return "break" 
    
# Create the main window
window = tk.Tk()
window.title("Gerber Difference Viewer")

# Load the icon image
icon = PhotoImage(file="icon.png")

# Set the application icon
window.iconphoto(True, icon)

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
toolbar_frame = tk.Frame(main_frame, height=100)
toolbar_frame.pack(side="top", fill="x")

# Create the buttons in the toolbar
button1 = tk.Button(toolbar_frame, text="Clear", command=button1_clear_clicked)
button1.pack(side=tk.LEFT, padx=5, pady=5)

button2 = tk.Button(toolbar_frame, text="Reload", command=button2_reload_clicked)
button2.pack(side="left", padx=5, pady=5)

button3 = tk.Button(toolbar_frame, text="Export Image", command=button3_export_clicked)
button3.pack(side="left", padx=5, pady=5)

button4 = tk.Button(toolbar_frame, text="🔎zoom🔍☐", command=button4_zoomin_clicked)
button4.pack(side="left", padx=5, pady=5)

#button5 = tk.Button(toolbar_frame, text="Zoom -", command=button5_zoomout_clicked)
#button5.pack(side="left", padx=5, pady=5)

button6 = tk.Button(toolbar_frame, text="Hightlight Differences", command=button6_diff_clicked)
button6.pack(side="left", padx=5, pady=5)

# toolbar for choosing the importer code
# List of options for the drop-down menu
backend_label = tk.Label(toolbar_frame, text="backend:")
backend_label.pack(side=tk.LEFT, padx = 5, pady = 10)

import_options = ["Import using pygerber", "Import using pcb-tools", "Import using gerbv"]
# Variable to store the selected import option
import_option = tk.StringVar()
import_option.set(import_options[0])
# Create the drop-down menu
option_dropdown = ttk.Combobox(toolbar_frame, textvariable=import_option, values=import_options, state="readonly")
option_dropdown.pack(side=tk.LEFT, padx=1, pady=5)
# Bind the event when the selection is changed
option_dropdown.bind("<<ComboboxSelected>>", import_option_selected)
selected_option = import_option.get()
file_loader.option = selected_option

layer_similarity_label = tk.Label(toolbar_frame, text="Select directories to compare gerber files in")#text="Selected Layers are not paired")
layer_similarity_label.pack(side=tk.RIGHT, padx = 30, pady = 10)

toolbar_frame = tk.Frame(main_frame)
toolbar_frame.pack(side="top", fill="x")


text_frame = tk.Frame(window, height = 150)
text_area = tk.Text(text_frame, pady=5, padx=5, bg = "white", state=tk.NORMAL)
# TODO: scrollbar didn't work - not needed, but maybe return to this
#text_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_area.yview)
#text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_frame.pack_propagate(0)
text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
text_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)
text_area.insert(tk.END, "Ready to compare gerber files")
text_area.see("end")
text_area["state"] = tk.DISABLED

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
left_directory_button = tk.Button(left_frame, text="Browse", command=lambda: directory_select_btn(left_frame, left_directory_entry))
left_directory_button.pack(anchor=tk.NW)

# Right column: Directory selector
right_directory_label = tk.Label(right_frame, text="Gerber directory 2:")
right_directory_label.pack(anchor=tk.NW)
right_directory_entry = tk.Entry(right_frame)
right_directory_entry.pack(anchor=tk.NW)
right_directory_button = tk.Button(right_frame, text="Browse", command=lambda: directory_select_btn(right_frame, right_directory_entry))
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
#selected_images_var = tk.StringVar()
#selected_images_var = tk.StringVar() # ListVar()#
#selected_images_var.set(0)
frame_selected_layer_vars = {left_frame: [], right_frame: []}
frame_checkboxes = {left_frame: [], right_frame: []}
frame_images = {left_frame: [], right_frame: []}

## Create a custom image for the checkbutton
#checkbutton_image = tk.PhotoImage(file="checkbutton_image.png").subsample(3)  # Adjust the subsample factor to resize the image

# Run the GUI
window.mainloop()
