from PIL import Image, ImageFile
from . import simple_color_generator
#from pygerber.backend.rasterized_2d import Rasterized2DBackend
ImageFile.LOAD_TRUNCATED_IMAGES = True


from pygerber.gerberx3.api import ColorScheme
from pygerber.gerberx3.api._layers import (
      Rasterized2DLayer,
      Rasterized2DLayerParams,
      Rasterized2DBackend,
)
#from pygerber.backend.rasterized_2d import Rasterized2DResult
from pygerber.common.rgba import RGBA

class gerbLoader():
    """
    gerbLoader is an abstraction layer
    this implementation relys on pygerber 2.0
    'the only way to import gerbers' ;-)
    """

    def __init__(self):
        self.option = "Import using pygerber"
        self.color = simple_color_generator.simple_color_generator()
        #print ("initialised gerbLoader")
        self.imageDict = {}
        pass
    
    def loadImage(self, file_path, color=None):
        dpi = 400
        if file_path not in self.imageDict : 
            if color == None:
                color = self.color.getNextColor()
            c, rgb = color
            cunning_scheme = ColorScheme( # simple transparent of fill color scheme
                                background_color=RGBA.from_rgba(0, 0, 0, 0),
                                clear_color=RGBA.from_rgba(0, 0, 0, 0),
                                solid_color=RGBA.from_rgba(*c[0]),
                                clear_region_color=RGBA.from_rgba(0, 0, 0, 0),
                                solid_region_color=RGBA.from_rgba(*c[0]),
                                )

            out =  Rasterized2DLayer(
                options=Rasterized2DLayerParams(
                        dpi=dpi,
                        source_path=file_path,
                        colors=cunning_scheme,
                ),
            )
            #out.render().save("./tmp.png")
            #layerImage = Image.open('./tmp.png')
            render_result = out.render()
            layerImage =  render_result._result_handle.result
            coords = render_result._properties.target_coordinate_origin
            #coords = render_result._properties.gerber_coordinate_origin
            #print("gerber offset")
            #print(coords)
            verticalFlip = layerImage.transpose(Image.FLIP_TOP_BOTTOM)
                        #layerImage = out_handle.get_result_handle().result
            #layerImage.convert("RGBA")
            offset_x = coords.x.value * dpi * -1 # convert coords to offsets
            offset_y = coords.y.value * dpi * -1
            print("Absolute offsets x, y:")
            print(offset_x)
            print(offset_y)
            self.imageDict [file_path] = (verticalFlip, rgb, offset_x, offset_y)
            return verticalFlip, rgb, offset_x, offset_y 
        else:
            return self.imageDict[file_path]

#from . import simple_color_generator
#from PIL import Image, ImageFile
#ImageFile.LOAD_TRUNCATED_IMAGES = True
#import pygerber as pyg
#from pygerber import API2D
##from pygerber.parser.pillow import ColorSet
#import gerber
##import gerber.render
#from gerber.render.cairo_backend import GerberCairoContext
##from gerber.render import GerberCairoContext
#from gerber import pcb
#from io import BytesIO
#import subprocess
#from typing import Tuple
#
#from pygerber.parser.pillow.parser import ColorSet
#
#class gerbLoader():
#    """
#    gerbLoader is an abstraction layer
#    there are at least three ways to load a gerber file.  :(
#    """
#    option = None
#    def __init__(self):
#        #self.option = "Import using pcb-tools"
#        self.color = simple_color_generator.simple_color_generator()
#        #print ("initialised gerbLoader")
#
#    def get_image_from_gerbv(self, path, color):
#        hex = color[1]
#        try:
#            result = subprocess.run([
#                "gerbv",
#                "--export=png",
#                "-o",
#                "./tmp.png",
#                f"--background=#050515",
#                f"--foreground={hex}",
#                "--dpi=600",
#                #"--window=5709x1576",
#                f"{path}",
#            ]
#            , check=True)
#            # Process completed successfully
#            layerImage = Image.open(r'./tmp.png')
#            layerImage.convert("RGBA")
#            self.color_to_alpha(layerImage, (0,0,0,0))
#            print("Process completed with return code:", result.returncode)
#            return layerImage
#        except subprocess.CalledProcessError as e:
#            # Process returned non-zero exit status
#            print("Error executing the command:\n")
#            print(e)
#            print("\nCheck that you have 'gerbv' installed and can run it.")
#            return None
#        #subprocess.run(
#        #    [
#        #        "gerbview",
#        #        f"--export={type}",
#        #        "-o",
#        #        f"{folder_name}/{name}.png",
#        #        "--dpi=1000",
#        #        #"--window=5709x1576",
#        #        f"{path}",
#        #    ],
#        #    check=True,
#        #)
#
#    def get_image_size(self, gerber_data):
#        min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
#        for shape in gerber_data.shapes:
#            for point in shape.points:
#                x, y = point[0], point[1]
#                min_x = min(min_x, x)
#                max_x = max(max_x, x)
#                min_y = min(min_y, y)
#                max_y = max(max_y, y)
#
#        img_width = int(max_x - min_x)
#        img_height = int(max_y - min_y)
#        return img_width, img_height
#    
#    def color_to_alpha(self, img, col=(0, 0, 0, 254)):
#        width, height = img.size
#        pixdata = img.load()
#        for y in range(height):
#            for x in range(width):
#                if pixdata[x, y] == col:
#                    pixdata[x, y] = (255, 255, 255, 0)
#
#    def loadImage(self, file_path, color=None):
#        if color == None:
#            color = self.color.getNextColor()
#        c, rgb = color
#        print(c)
#        print(rgb)
#        if self.option == "Import using pygerber":
#            print("importing file: "+file_path+" using " + self.option)
#            return pyg.API2D.render_file(file_path, colors=ColorSet(c[0], c[1], c[2])), rgb
#        elif self.option == "Import using pcb-tools":
#                print("importing file: "+file_path+" using " + self.option)
#                # Load the Gerber file
#                camfile = gerber.read(file_path)
#                #c,rgbstr = self.color.getNextColor()
#                # doesn't work ctx = GerberCairoContext(scale=0.1)
#                ctx = GerberCairoContext()
#                ctx.max_width = 800
#                # can be initialised with a scale...
#                img_scale = 10  # 'magic' scale that looks ok for kicad gerbers
#                ctx.scale = (img_scale, img_scale)
#                camfile.render(ctx)
#    #            camfile = gerber.load_layer(file_path, max_width=1940)
#    #            ctx = GerberCairoContext()
#    #            ctx.render_layer(camfile)
#
#                #img_scale = ctx.scale[0]
#                #img_size = ctx.size_in_pixels
#                #print("***")
#                #print(ctx.size_in_pixels)
#                #print(img_scale)
#                #print("***")
#                #while img_size[0] > 4000 and img_size[1] > 4000:
#                #        print("looping on reducing the scale ")
#                #        print(img_scale)
#                #        img_scale = int(img_scale * 0.9)
#                #        ctx.scale = (img_scale, img_scale)
#                #        camfile.render(ctx)
#                #        img_size = ctx.size_in_pixels
#                #        print(img_size)
#                #size_int = tuple(int(x*1.5) for x in ctx.size_in_pixels)
#                #print(size_int)
#                #ctx.size_in_pixels = size_int
#                rawbytes = ctx.dump_str()
#                img = Image.open(BytesIO(rawbytes))
#                img.convert("RGBA")
#                self.color_to_alpha(img, (0,0,0,0))
#                img.putalpha(210)
#                #img.show()
#                return img, rgb
#                #pcb.render(pcb_file, img)
#        elif  self.option == "Import using gerbv":
#            img = self.get_image_from_gerbv(file_path, color)
#            if img is None:
#                print("\n\nfailed to get an image back from gerbv\n")
#                exit()
#            return img, rgb
#        else:
#            print(self.option)
#            exit()
#            #return pyg.API2D.render_file(file_path, colors=colors)