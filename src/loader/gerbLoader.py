from PIL import Image, ImageFile, ImageChops, ImageFilter, ImageOps # ImageDraw
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
        self.dpi = 400
        pass
    
    def loadImage(self, file_path, color=None):
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
                        dpi=self.dpi,
                        source_path=file_path,
                        colors=cunning_scheme,
                ),
            )
            #out.render().save("./tmp.png")
            #layerImage = Image.open('./tmp.png')
            #print(file_path)
            render_result = out.render()
            layerImage =  render_result._result_handle.result
            coords = render_result._properties.target_coordinate_origin
            #coords = render_result._properties.gerber_coordinate_origin
            #print("gerber offset")
            #print(coords)
            verticalFlip = layerImage.transpose(Image.FLIP_TOP_BOTTOM)
                        #layerImage = out_handle.get_result_handle().result
            #layerImage.convert("RGBA")
            offset_x = coords.x.value   # convert coords to offsets
            offset_y = coords.y.value  
            #if offset_x < 0 : 
            #    offset_x =0
            #if offset_y < 0:
            #    offset_y = 0
            width, height = verticalFlip.size
            vFlipCrop = verticalFlip.crop((offset_x, offset_y, width, height))
            self.imageDict [file_path] = (vFlipCrop, rgb, offset_x, offset_y)
            return vFlipCrop, rgb, offset_x, offset_y 
        else:
            return self.imageDict[file_path]


    def get_difference_outlines(self, a, b, opacity=0.85):
        """ Function to find differences in images
            Parameters
            ----------
            a: Image
            The first Image to difference
            b: Image
            The second image to difference (must be same dimensions)
            opacity: float
            Number from zero to one that represents the opacity of the diff layer. 0 is transparent, 1 is opaque

            Returns
            -------
            redmask : Image
                A semi transparent image with the differences of a & b highlighted with a thick red highlight outline
            percent_diff_pixels: Float
                The percentage of pixels that are different between Image a & Image b.
        """
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

        # invert both images 
        a_inv = ImageOps.invert(a_mask)
        b_inv = ImageOps.invert(b_mask)
        #b_inv.show()
        #input()

        a_bw = a_inv.convert("1")
        b_bw = b_inv.convert("1")
        #b_bw.show()
        #input()
        diff = ImageChops.difference(a_bw, b_bw)
        
        # telluser what the total different pixels are...
        tot_different_pixels = 0
        tot_pixels = diff.size[0] * diff.size[1]
        for pixel in diff.getdata():
            if pixel != 0:
                tot_different_pixels += 1
        percent_diff_pixels = (1- (tot_different_pixels/tot_pixels) ) * 100
        diff = diff.convert('L')

        new = diff.copy()
        shrink = new.filter(ImageFilter.MaxFilter(17))
        grow = shrink.filter(ImageFilter.MinFilter(3))
        inverted = ImageOps.invert(new)
        outline = ImageChops.difference(grow, inverted)
        outline = ImageOps.invert(outline)
        highlight_color = (247,  126,  185, 220)
        redmask = self.new_color(diff.size, color=(247,  126,  185, 0))  # same color but transparent - 
        redmask.paste(highlight_color, (0,0), mask=outline)
        return redmask, percent_diff_pixels

    # diff code using only pillow
    # from: https://stackoverflow.com/questions/30277447/compare-two-images-and-highlight-differences-along-on-the-second-image
    # erode dilate using pillow:
    # from: https://stackoverflow.com/questions/44195007/equivalents-to-opencvs-erode-and-dilate-in-pil
    def new_color(self, size, color):
        ''' Function returns a new image of the defined size and color
            Parameters
            ----------
            size: a tuple of (x,y)
            color: a tuple of Floats of the form (red, green, blue)
            
            Returns
            -------
            img: an Image of the specified size and color           
        '''
        img = Image.new(mode="RGBA", size=size, color=color)
        #dr = ImageDraw.Draw(img)
        #dr.rectangle((0,0) + size, fill=color)
        return img
