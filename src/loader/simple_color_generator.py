# color generator is based on earlier code that used pygerber
# I've simplified it to use just a tuple as this is all that;s needed.

class simple_color_generator():
#    LARGE_PRIME= [ 39847,  69857,  40277]
    LARGE_PRIME= [227,  163, 197]
    LIST_OF_COLORS = []
    #LIST_OF_COLORS.append(DEFAULT_COLOR_SET_ORANGE)
    #LIST_OF_COLORS.append(DEFAULT_COLOR_SET_GREEN)
    counter = 0
    BRIGHT_RED = None
    WHITE = None
    
    def __init__(self, transparency=160):
        for i in range(173,285): # range numbers need to be away from 1, but are not important
            self.LIST_OF_COLORS.append((
                             (( (i+23)*self.LARGE_PRIME[0])%150, ((i+253)*self.LARGE_PRIME[1])%255, ((i+3)*self.LARGE_PRIME[2])%255 , transparency),
                             (100,100,100, 50),
                             ( 50, 50, 50, 50),
            ))
        self.BRIGHT_RED = (
                             (230,  66,  75, 100),
                             (100, 100, 100, 255),
                             ( 50,  50,  50, 255),
            )
        self.WHITE = (
                             (255, 255, 255, 0),
                             (  0,   0,   0, 0),
                             (  0,   0,   0, 0),
            )
        self.counter = 0

    def getWhite(self):
        rgbstr = '#%02x%02x%02x%02x' % self.WHITE[0]
        return self.WHITE, rgbstr

    def getBrightRed(self):
        rgbstr = '#%02x%02x%02x%02x' % self.BRIGHT_RED[0]
        return self.BRIGHT_RED, rgbstr

    def getNextColor(self):
        self.counter= (self.counter+1) % len(self.LIST_OF_COLORS)
        rgb = '#%02x%02x%02x%02x' % self.LIST_OF_COLORS[self.counter][0]
        return self.LIST_OF_COLORS[self.counter], rgb[:-2]