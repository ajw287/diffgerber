import sys
import loader
import os
import difflib as dl

file_loader = loader.gerbLoader()

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

def main(directories, out_file, dpi):
    #images1 = []
    #images2 = []
    filenames1 = os.listdir(directories[0])#os.listdir(os.fsencode(directories[0]))
    filenames2 = os.listdir(directories[1])#os.listdir(os.fsencode(directories[1]))
    #layer_colors1 = []
    #layer_colors2 = []
    #xs1 = []
    #xs2 = []
    #ys1 = []
    #ys2 = []

    merge_image_list = []
    highlight_image_list = []

    file_loader.dpi = dpi

    #images1, filenames1, layer_colors1, x_offs1, y_offs1 = load_images(directories[0])
    #images2, filenames2, layer_colors2, x_offs2, y_offs2 = load_images(directories[1])
    files_to_diff = []
    for i, name in enumerate(filenames1):
        print(name)
        if any(name == fname for fname in filenames2):
            files_to_diff.append(i)
    if not files_to_diff:
        print("Error no gerber files detected!\n")
        exit()
    for index in files_to_diff:
        sim = 0.0
        file_path1 = os.path.join(directories[0], filenames1[index])
        file_path2 = os.path.join(directories[1], filenames1[index])
        with open(file_path1, "r") as file1:
            with open(file_path2, "r") as file2:
                similarity = dl.SequenceMatcher(None, file1.read(), file2.read())
                if similarity.ratio() == 1.0:
                    print(f"text diff: {name} is identical")
                elif similarity.ratio() >= .2:
                    print("text diff: "+str(name)+" is %.2f%% similar"%(similarity.ratio() * 100.0) )
                    active_layer_image_old, lw, lx, ly = file_loader.loadImage(file_path1) 
                    active_layer_image_new, rw, lx, ly = file_loader.loadImage(file_path2)
                    highlight, sim = file_loader.get_difference_outlines(active_layer_image_old, active_layer_image_new)
                    print (f"file: {filenames1[index]} has {sim}% diff")
                    highlight_image_list.append(highlight)
                    merge_image_list.append(active_layer_image_new)
    if len(merge_image_list) >= 2:
        for i, img in enumerate(merge_image_list):
            if i == 0:
                pass
            else:
                merge_image_list[0].paste(merge_image_list[i], (0, 0), merge_image_list[i])
        for i, img in enumerate(highlight_image_list):
            merge_image_list[0].paste(highlight_image_list[i], (0, 0), highlight_image_list[i])
    elif len(merge_image_list) == 1:
        for i, img in enumerate(highlight_image_list):
            merge_image_list[0].paste(highlight_image_list[i], (0, 0), highlight_image_list[i])
    else:
        print("no differences to show")
        exit()
    merge_image_list[0].save(out_file,"PNG")
    merge_image_list[0].show()

def help_message():
    """
    A simple help message for users of the command line
    """
    print (f"{sys.argv[0]}: Script usage help message")
    argument_descriptions =  ["Script Name", "old gerber directory", "new gerber directory", "output filename", "dpi of output"]
    for i, arg in enumerate(argument_descriptions):
        print(f"Argument {i:>6}:  {arg}")
    exit()

if __name__ == "__main__":
    # just check that we got enough command line args
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        help_message()
    if len(sys.argv) == 5:
        main(directories=[sys.argv[1], sys.argv[2]], out_file=sys.argv[3], dpi=sys.argv[4])
    else:
        print("\nWrong number of command line arguments\n")
        help_message()