from . import simple_color_generator
from PIL import Image
import pygerber as pyg
from pygerber import API2D
import gerber
#import gerber.render
from gerber.render.cairo_backend import GerberCairoContext
#from gerber.render import GerberCairoContext
from gerber import pcb
from io import BytesIO


class gerbLoader():
    option = None
    def __init__(self):
        self.option = "Import using pcb-tools"
        self.color = simple_color_generator.simple_color_generator()
        #print ("initialised gerbLoader")

    def get_image_size(self, gerber_data):
        min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
        for shape in gerber_data.shapes:
            for point in shape.points:
                x, y = point[0], point[1]
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

        img_width = int(max_x - min_x)
        img_height = int(max_y - min_y)
        return img_width, img_height
    
    def color_to_alpha(self, img, col=(0, 0, 0, 254)):
        width, height = img.size
        pixdata = img.load()
        for y in range(height):
            for x in range(width):
                if pixdata[x, y] == col:
                    pixdata[x, y] = (255, 255, 255, 0)

    def loadImage(self, file_path, color):
        if self.option == "Import using pygerber":
            return pyg.API2D.render_file(file_path, colors=color) 
        elif self.option == "Import using pcb-tools":
                print("importing file: "+file_path)
                # Load the Gerber file
                camfile = gerber.read(file_path)
                c,rgbstr = self.color.getNextColor()
                ctx = GerberCairoContext()
                ctx.max_width = 800
                camfile.render(ctx)
    #            camfile = gerber.load_layer(file_path, max_width=1940)
    #            ctx = GerberCairoContext()
    #            ctx.render_layer(camfile)

                #img_scale = ctx.scale[0]
                #img_size = ctx.size_in_pixels
                #print("***")
                #print(ctx.size_in_pixels)
                #print(img_scale)
                #print("***")
                #while img_size[0] > 4000 and img_size[1] > 4000:
                #        print("looping on reducing the scale ")
                #        print(img_scale)
                #        img_scale = int(img_scale * 0.9)
                #        ctx.scale = (img_scale, img_scale)
                #        camfile.render(ctx)
                #        img_size = ctx.size_in_pixels
                #        print(img_size)
                #size_int = tuple(int(x*1.5) for x in ctx.size_in_pixels)
                #print(size_int)
                #ctx.size_in_pixels = size_int
                rawbytes = ctx.dump_str()
                img = Image.open(BytesIO(rawbytes))
                img.convert("RGBA")
                self.color_to_alpha(img, (0,0,0,0))
                img.putalpha(210)
                #img.show()
                return img
                #pcb.render(pcb_file, img) 
        else:
            return pyg.API2D.render_file(file_path, colors=colors)
    
