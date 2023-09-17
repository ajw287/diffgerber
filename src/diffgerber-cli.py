import sys
import loader
import os
import difflib as dl
import argparse

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

def diff_gerbers(directories, out_file, dpi, quiet_mode=False, display_image=False):
    filenames1 = os.listdir(directories[0])#os.listdir(os.fsencode(directories[0]))
    filenames2 = os.listdir(directories[1])#os.listdir(os.fsencode(directories[1]))
    merge_image_list = []
    highlight_image_list = []

    file_loader.dpi = dpi

    files_to_diff = []
    for i, name in enumerate(filenames1):
        print(name)
        if any(name == fname for fname in filenames2) and \
            name.endswith((".gbr", ".grb")) :
            files_to_diff.append(i)
    if not files_to_diff:
        print("Error: no gerber files detected!\n")
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
    
    #crop the image
    out_image = merge_image_list[0].crop(merge_image_list[0].getbbox())

    #show and save ... maybe just save?
    out_image.save(out_file,"PNG")
    if display_image:
        out_image.show()

def main():
    parser = argparse.ArgumentParser(
                    prog='diffgerber-cli',
                    description='Command line gerber directory diff tool, recognises layers by filename and diffs if they can be paired',
                    epilog='\nexample usage: (creates a low-res thumbnail image)\n \n> python diffgerber-cli.py ../examples/pcb-1-a ../examples/pcb-1-b/ 100 out.png --quiet\n')
    parser.add_argument("input_directory1", help="Path to input directory 1")
    parser.add_argument("input_directory2", help="Path to input directory 2")
    parser.add_argument("dpi", type=int, default=300, help="DPI (dots per inch) value")
    parser.add_argument("output_filename", help="Output filename (png file)")
    parser.add_argument("--quiet", "-q", default=False, action="store_true", help="Run in quiet mode")
    parser.add_argument("--display", "-D", default=False, action="store_true", help="Display the image when the script finishes with default image viewer")


    args = parser.parse_args()

    diff_gerbers(
        [args.input_directory1,
        args.input_directory2],
        args.output_filename,
        args.dpi,
        args.quiet,
        args.display,
    )

if __name__ == "__main__":
    main()