import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import PhotoImage
from tkinter import messagebox
from PIL import Image, ImageTk
#, ImageChops, ImageDraw, ImageFilter, ImageOps
import difflib as dl
#import color_generator as cg
import loader
#from pygerber.typs cg
#from pygerber.types import ColorSet
#from pygerber.parser.pillow.parser import ColorSet

imageDict = {}
directories  = ["", ""] # {left_frame: "", right_frame: ""}
left_file_list  = []
right_file_list = []
photo_list = []
left_to_right_dict = {}
active_left_index = None
active_layer_image_left = None
active_layer_image_right = None
file_loader = loader.gerbLoader()
active_offset_x = 0.0
active_offset_y = 0.0
percent_diff_pixels = 0


point_table = ([0] + ([255] * 255))
# diff code using only pillow
# from: https://stackoverflow.com/questions/30277447/compare-two-images-and-highlight-differences-along-on-the-second-image
# erode dilate using pillow:
# from: https://stackoverflow.com/questions/44195007/equivalents-to-opencvs-erode-and-dilate-in-pil
#def new_gray(size, color):
#    img = Image.new('L',size)
#    dr = ImageDraw.Draw(img)
#    dr.rectangle((0,0) + size, fill=color)
#    return img
#
#def new_color(size, color):
#    img = Image.new(mode="RGBA", size=size, color=color)
#    #dr = ImageDraw.Draw(img)
#    #dr.rectangle((0,0) + size, fill=color)
#    return img

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
    global left_file_list, right_file_list, left_to_right_dict, directories, active_layer_image_left, active_layer_image_right, active_offset_x, active_offset_y
    left_file_path = os.path.join(directories[0], left_file_list[left_index])
    print(left_file_path)
    with open(left_file_path, "r") as left_file:
        right_file_path = os.path.join(directories[1], right_file_list[left_to_right_dict[left_index]])
        print(right_file_path)
        with open(right_file_path, "r") as right_file:
            similarity = dl.SequenceMatcher(None, left_file.read(), right_file.read())
            if similarity.ratio() == 1.0:
                tellUser("text difference: "+str(left_file_list[left_index])+" is identical")
            elif similarity.ratio() >= .2:
                tellUser("text difference: "+str(left_file_list[left_index])+" is %.2f%% similar"%(similarity.ratio() * 100.0) )
                c = file_loader.color.getWhite() # the files are already loaded, so they are in the dictionary in a suitable color
                active_layer_image_left,  lw, lx, ly =  file_loader.loadImage(left_file_path, color=c ) 
                active_layer_image_right, rw, lx, ly = file_loader.loadImage(right_file_path, color=c )
                active_offset_x = lx
                active_offset_y = ly
            else:
                tellUser("files: "+str(left_file_list[left_index])+" have same name but differ greatly")         

def load_images(directory):
    global imageDict
    """Load image files from the selected directory."""
    images = []
    filenames = []
    layer_colors = []
    xs = []
    ys = []
    for i, filename in enumerate(os.listdir(os.fsencode(directory))):
        if filename.decode().endswith((".jpg", ".png")):
            filepath = os.path.join(directory, filename.decode())
            image = Image.open(filepath)
            images.append(image)
            filenames.append(filename.decode())
        elif filename.decode().endswith((".gbr", ".grb")):
            filepath = os.path.join(directory, filename.decode())
            image, rgb, x, y = file_loader.loadImage(filepath)
            imageDict[filepath] = (image, rgb, x, y)
            xs.append(x)
            ys.append(y)
            images.append(image)
            filenames.append(filename.decode())
            layer_colors.append(rgb)
    return images, filenames, layer_colors, xs, ys

def show_image(full_filename):
    '''
    Shows the image in the imageDict, from the full_filename key
    note if full_filename is not in dict this is an error for now.. could catch but shouldn't happen!
    '''
    global imageDict, middle_frame, canvas
    #if not True:
    #    hide_image(filename)
    #    return 
    """Display the selected image on the canvas."""
    #img_width, img_height = image.size
    x = 0.0
    y = 0.0
    dirname = os.path.dirname(full_filename)
    if dirname == directories[1]: #RHS selected
        x_offset = float(x_offset_var.get())
        y_offset = float(y_offset_var.get())
        x += x_offset
        y += y_offset

    photo = None
    if imageDict:
        image, rgb, offset_x_from_dict, offset_y_from_dict = imageDict.get(full_filename)
        photo = ImageTk.PhotoImage(image)
        #print("loaded from imageDict")
        #print(imageDict)
    if photo is None:
        image, rgb, x_off, y_off = file_loader.loadImage(full_filename)
        photo = ImageTk.PhotoImage(image)
        imageDict.update({full_filename: (image, rgb, x_off, y_off)})
        x += x_off
        y += y_off
        print ("got an empty entry in the dictionary: - this shouldn't happen!")
        print (full_filename)
        exit()
    x += float(offset_x_from_dict)
    y += float(offset_y_from_dict)
    #print(full_filename)
    #print(photo)
    canvas.create_image(x, y, anchor="nw", image=photo)
    #canvas.image = photo  # Store a reference to prevent garbage collection
    photo_list.append(photo)

def layer_selected(full_filename, index):
    global active_left_index, imageDict
    #TODO: this is a hacky way of finding the left-to-right lookup - is there a better way?
    image, rgb, x, y  = imageDict[full_filename]
    # extract directory from full_filename -
    dirname = os.path.dirname(full_filename)
    active_left_index = None
    #print("layer selected")
    #print(directories)
    #print(dirname)
    #print("---")
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
    show_image(full_filename)
    #set the matched layer to selected bg = "grey"
    #print(full_filename)
    
def hide_image(full_filename):
    print("remove the image from the photos")

def directory_select_btn(frame, directory_entry):
    """Handle the event when a directory is selected."""
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        tellUser("Please wait... loading gerbers")
        tellUser("directory "+ str(selected_directory), label_msg=False)
        directory_selected(frame, directory_entry, selected_directory)

def directory_selected(frame, directory_entry, selected_directory):
    global left_file_list, right_file_list, directories, frame_images, frame_checkboxes, frame_selected_layer_vars, canvas
    directory_entry.delete(0, tk.END)
    directory_entry.insert(tk.END, selected_directory)
    images, filenames, layer_colors, x_offs, y_offs = load_images(selected_directory)

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
            #command=lambda i=i: layer_selected( frame_images[frame][i], os.path.join(selected_directory, filenames[i]), i)
            command=lambda i=i: layer_selected( os.path.join(selected_directory, filenames[i]), i)
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
        show_image(os.path.join(selected_directory, filenames[0]))
    # set the scroll bars to a specific point
    canvas.update_idletasks() 
    canvas.xview_moveto(0.6)  # Horizontal scrollbar to the middle
    canvas.yview_moveto(0.7)  # Vertical scrollbar to the middle
    canvas.update_idletasks() 
    print(x_offs)

#def toolbar_button_clicked():
#    """Handle the event when the toolbar button is clicked."""
#    print("Toolbar button clicked!")
def button1_clear_clicked(clear_dirs=True):
    global imageDict, left_directory , right_directory
    global left_file_list , right_file_list, left_to_right_dict, canvas, photo_list
    #print("Button 1 clicked")
    # Clear the checkboxes
    for frame in frame_checkboxes:
        for checkbox in frame_checkboxes[frame]:
            checkbox.destroy()
        frame_checkboxes[frame].clear()
    canvas.delete("all")

    imageDict = {}
    directories = ["", ""]
    right_file_list = []
    left_to_right_dict = {}
    photo_list = []
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
    global canvas
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
    global canvas
    print("Button 4 clicked zoom +\n\n *** NOT IMPLEMENTED ***\n\n")
    tellUser("zoom not implemented")
    canvas.scale("all", 0, 0, 1.1, 1.1)  # Increase scale factor

def button5_zoomout_clicked():
    global canvas
    print("Button 5 clicked zoom -\n\n *** NOT IMPLEMENTED ***\n\n")
    tellUser("zoom not implemented")
    canvas.scale("all", 0, 0, 0.9, 0.9)  # Decrease scale factor

def button6_diff_clicked():
    global imageDict, active_layer_image_left, active_layer_image_right, active_offset_x, active_offset_y
    global percent_diff_pixels
    if active_left_index is None:
        tellUser("Active layer unpaired - nothing to highlight")
        return
    tellUser("checking for differences... hang on!", label_msg=True, record_msg=False)
    diff_image, percent_diff_pixels = file_loader.get_difference_outlines(active_layer_image_left, active_layer_image_right, opacity=0.55)
    tellUser("pixel difference : %.2f%% pixels are similar at %d dpi"%(percent_diff_pixels, file_loader.dpi), label_msg=False, record_msg=True)
    photo = ImageTk.PhotoImage(diff_image)
    rgb = '#%02x%02x%02x%02x' % (247,  126,  185, 220) 
    print(active_offset_x)
    imageDict["diff_"+str(active_left_index)] = (diff_image, rgb, active_offset_x, active_offset_y)
    tellUser("displaying differences", label_msg=True, record_msg=False)
    show_image("diff_"+str(active_left_index))

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

def move_set_of_gerbers(event=None):
    global x_offset, y_offset, canvas, window, photo_list
    x_offset = 0.0
    y_offset = 0.0
    if mode_button_var.get():
        x_offset = float(x_offset_var.get())
        y_offset = float(y_offset_var.get())

    #x_current, y_current, _, _ = canvas.coords(canvas_elements)
    x_current, y_current = 0,0

    if event:
        if event.keysym == 'Left':
            x_offset -= 10
        elif event.keysym == 'Right':
            x_offset += 10
        elif event.keysym == 'Up':
            y_offset -= 10
        elif event.keysym == 'Down':
            y_offset += 10
    
    x_move = x_offset - x_current
    y_move = y_offset - y_current

    x_offset_var.set("{:.2f}".format(x_offset))
    y_offset_var.set("{:.2f}".format(y_offset))
    
    canvas.delete("all")
    photo_list = []
    for image in left_file_list:
        show_image(os.path.join(directories[0],image))
    for image in right_file_list:
        show_image(os.path.join(directories[1], image))
    canvas.update_idletasks()
    #window.update()

def toggle_move_mode():
    global x_offset_entry, y_offset_entry, mode_button_var, move_msg_label, x_offset_label, y_offset_label, update_button
    if mode_button_var.get():
        x_offset_entry.config(state=tk.NORMAL)
        y_offset_entry.config(state=tk.NORMAL)
        update_button["state"] = tk.NORMAL
        move_msg_label.configure(state=tk.NORMAL)
        x_offset_label.configure(state=tk.NORMAL)
        y_offset_label.configure(state=tk.NORMAL)
        #canvas.itemconfig(canvas_elements, state=tk.NORMAL)
    else:
        x_offset_entry.config(state=tk.DISABLED)
        y_offset_entry.config(state=tk.DISABLED)
        update_button["state"] = tk.DISABLED
        move_msg_label.configure(state=tk.DISABLED)
        x_offset_label.configure(state=tk.DISABLED)
        y_offset_label.configure(state=tk.DISABLED)
        #canvas.itemconfig(canvas_elements, state=tk.HIDDEN)

move_msg_label = None
y_offset_label = None
x_offset_label = None
update_button = None
def add_move_layers_gui(target_frame):
    '''
    function to add a set of gui elements for controlling position of one side
    Parameters:
    -----------
    target_frame Frame

    '''
    global x_offset_entry, y_offset_entry, mode_button_var, move_msg_label, x_offset_label, y_offset_label, update_button   

    # Create an "Update" button to move the rectangle to the specified coordinates
    update_button = tk.Button(target_frame, text="Update", command=move_set_of_gerbers)
    update_button.configure(state='disable')
    update_button.pack(side=tk.BOTTOM)

    x_offset_var.set("0.00")
    y_offset_var.set("0.00")

    y_offset_entry = tk.Entry(target_frame, textvariable=y_offset_var, state=tk.DISABLED)
    y_offset_entry.pack(side=tk.BOTTOM)

    y_offset_label = tk.Label(target_frame, text="Y Offset:")
    y_offset_label.configure(state='disable')
    y_offset_label.pack(side=tk.BOTTOM)

    x_offset_entry = tk.Entry(target_frame, textvariable=x_offset_var, state=tk.DISABLED)
    x_offset_entry.pack(side=tk.BOTTOM)

    x_offset_label = tk.Label(target_frame, text="X Offset:")
    x_offset_label.configure(state='disable')
    x_offset_label.pack(side=tk.BOTTOM)
    
    move_msg_label = tk.Label(target_frame, text="Use arrow keys to move: ←↑→↓")
    move_msg_label.configure(state='disable')
    move_msg_label.pack(side=tk.BOTTOM)

    # Create a mode button
    mode_button = tk.Checkbutton(target_frame, text="Set Position:", variable=mode_button_var, command=toggle_move_mode)
    mode_button.pack(side=tk.BOTTOM)

    # Bind arrow keys to move the rectangle and update offsets
    window.bind('<Left>', move_set_of_gerbers)
    window.bind('<Right>', move_set_of_gerbers)
    window.bind('<Up>', move_set_of_gerbers)
    window.bind('<Down>', move_set_of_gerbers)



#from: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar 
# doesn't work... 
#def OnMouseWheel(self,event):
#    hscrollbar.yview("scroll",event.delta,"units")
#    return "break" 
    
# Create the main window
window = tk.Tk()
window.title("Gerber Difference Viewer")

#globals for the move layers
x_offset_var = tk.StringVar()
y_offset_var = tk.StringVar()
mode_button_var = tk.BooleanVar()

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

button4 = tk.Button(toolbar_frame, text="🔎zoom🔍☐+", command=button4_zoomin_clicked)
button4.pack(side="left", padx=5, pady=5)

button5 = tk.Button(toolbar_frame, text="Zoom-", command=button5_zoomout_clicked)
button5.pack(side="left", padx=5, pady=5)

button6 = tk.Button(toolbar_frame, text="Hightlight Differences", command=button6_diff_clicked)
button6.pack(side="left", padx=5, pady=5)

# toolbar for choosing the importer code
# List of options for the drop-down menu
#backend_label = tk.Label(toolbar_frame, text="backend:")
#backend_label.pack(side=tk.LEFT, padx = 5, pady = 10)

import_options = ["Import using pygerber", "Import using pcb-tools", "Import using gerbv"]
# Variable to store the selected import option
import_option = tk.StringVar()
import_option.set(import_options[0])
# Create the drop-down menu
option_dropdown = ttk.Combobox(toolbar_frame, textvariable=import_option, values=import_options, state="readonly")
#option_dropdown.pack(side=tk.LEFT, padx=1, pady=5)

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


add_move_layers_gui(right_frame)

# Middle column: Canvas to display the images with scrollbars
# Create a canvas with scrollbars
#canvas = tk.Canvas(middle_frame, width=400, height=400)
canvas = tk.Canvas(middle_frame, width=1400, height=1400, bg="black")
canvas.pack(fill=tk.BOTH, expand=True)

# Create a background rectangle with a solid color (e.g., white)
#background_color = "#ffffff"  # White color
#canvas.create_rectangle(0, 0, 800, 600, fill=background_color, outline=background_color)

#image1 = Image.open("icon.png")
#photo1 = ImageTk.PhotoImage(image1)
#canvas.create_image(100, 100, image=photo1, anchor=tk.NW)

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
if __name__ == "__main__":
    window.mainloop()
