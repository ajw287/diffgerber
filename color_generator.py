from pygerber.parser.pillow.parser import ColorSet

class color_generator():
#    LARGE_PRIME= [ 39847,  69857,  40277]
    LARGE_PRIME= [227,  163, 197]
    LIST_OF_COLORS = []
    #LIST_OF_COLORS.append(DEFAULT_COLOR_SET_ORANGE)
    #LIST_OF_COLORS.append(DEFAULT_COLOR_SET_GREEN)
    counter = 0
    
    def __init__(self):
        for i in range(75,135): # range numbers need to be away from 1, but are not important
            self.LIST_OF_COLORS.append(ColorSet(
                             (( (i+23)*self.LARGE_PRIME[0])%255, ((i+253)*self.LARGE_PRIME[1])%255, ((i+3)*self.LARGE_PRIME[2])%255 , 160),
                             (100,100,100,50),
                             (50,50,50,50),
            ))
        self.counter = 0

    def getNextColorSet(self):
        self.counter= (self.counter+1) % len(self.LIST_OF_COLORS)
        print(self.LIST_OF_COLORS[self.counter].dark)
        rgb = '#%02x%02x%02x%02x' % self.LIST_OF_COLORS[self.counter].dark
        print("rgb:" +str(rgb))
        return self.LIST_OF_COLORS[self.counter], rgb[:-2]