"""
Loader is an abstraction layer, do whatever it takes just return an image from the directory you are given.
At this time I'm experimenting with pygerber 1.0 and pcb-tools, neither meet requirements - may need a gerbv backend too.
"""
from .gerbLoader import gerbLoader
from .dirSelectDialog import dirSelectDialog
#TODO: Delete these commented lines
#from loader.gerbLoader import loadImage
#import gerbLoader.loadImage
#print("start init load")
#print(dir(gerbLoader))
#print("end init load")
#gerbLoader.loadImage("./example/1/top.grb")