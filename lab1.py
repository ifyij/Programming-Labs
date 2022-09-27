#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y, boundary_behavior = 'zero'):
    pixels = image.get('pixels')
    width = image.get('width')
    height = image.get('height')
    if boundary_behavior == 'zero':
        if x >= 0 and y >= 0 and x<width and y<height:
            return pixels[(x)+(width*(y))]
        else:
            return 0
    if boundary_behavior == 'extend':
        if x<0 and y<0:
            return pixels[(0)+(width*(0))]
        elif x>=width and y>=height:
            return pixels[(width-1)+(width*(height-1))]
        elif x<0 and y>=height:
            return pixels[(0)+(width*(height-1))] #changed width-1 to 0
        elif y<0 and x>=width:
            return pixels[(width-1)+(width*(0))]
        elif y<0:
            return pixels[(x)+(width*(0))]
        elif y>=height:
            return pixels[(x)+(width*(height-1))]
        elif x<0:
            return pixels[(0)+(width*(y))]
        elif x>=width:
            return pixels[(width-1)+(width*(y))]
        else:
            return pixels[(x)+(width*(y))]
    if boundary_behavior == 'wrap':
        if x >= 0 and y >= 0 and x<width and y<height:
            return pixels[(x)+(width*(y))]
        elif x < 0 or x>=width:
            if y >= 0 and y<height:
                return pixels[(x%width)+(width*(y))]
            else:
                return pixels[(x%width)+(width*(y%height))]
        elif y < 0 or y>=height:
            if x >= 0 and x<width:
                return pixels[(x)+(width*(y%height))]
            else:
                return pixels[(x%width)+(width*(y%height))]
        else:
            return pixels[(x%width)+(width*(y%height))]
    
    


def set_pixel(image, x, y, c):
    pixels = image.get('pixels')
    width = image.get('width')
    del image['pixels']
    pixels[(x)+(width*(y))]=c
    image['pixels']= pixels

    


def apply_per_pixel(image, func):
    result = {
        'height': image.get('height'),
        'width': image.get('width'),
        'pixels': [0 for i in range(len(image.get('pixels')))],
    }
     
    for x in range( image.get('width')):
        for y in range( image.get('height')):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.009
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    kernel is a dictionary :
        kernel = {
            'width': 5,
            'height' 5,
            'pixels':[0 0 0
                      0 1 0
                      0 0 0],
        }
    """
    result = {
        'height': image.get('height'),
        'width': image.get('width'),
        'pixels': [0 for i in range(len(image.get('pixels')))],
    }
    
    side = kernel.get('width')
    bound = side//2
    
    for x in range( image.get('width')):
        for y in range( image.get('height')):
            if boundary_behavior != 'zero' and boundary_behavior != 'extend' and boundary_behavior != 'wrap':
                return None
            if boundary_behavior == 'zero':
                ans = 0
                for i in range(-bound, bound+1):
                    for j in range(-bound, bound+1):
                        ans += get_pixel(image, x+i, y+j,'zero')*get_pixel(kernel, i+bound, j+bound)            
                set_pixel(result, x, y, ans)
            elif boundary_behavior == 'extend':
                ans = 0
                for i in range(-bound, bound+1):
                    for j in range(-bound, bound+1):
                        ans+= get_pixel(image, x+i, y+j,'extend')*get_pixel(kernel, i+bound, j+bound)
                set_pixel(result, x, y, ans)
            elif boundary_behavior == 'wrap':
                ans =0 
                for i in range(-bound, bound+1):
                    for j in range(-bound, bound+1):
                        ans+= get_pixel(image, x+i, y+j,'wrap')*get_pixel(kernel, i+bound, j+bound)
                set_pixel(result, x, y, ans)
    return result
                        
                            
        
        


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    result = {
        'height': image.get('height'),
        'width': image.get('width'),
        'pixels': [0 for i in range(len(image.get('pixels')))],
    }
    appropriate_vals = set(range(256))
    for x in range( image.get('width')):
        for y in range( image.get('height')):
            if get_pixel(image, x, y) not in appropriate_vals:
                if get_pixel(image, x, y) < 0:
                    set_pixel(result, x, y, 0)
                elif get_pixel(image, x, y) > 255:
                    set_pixel(result, x, y, 255)
                else:
                    set_pixel(result, x, y, round(get_pixel(image, x, y)))
            else:
                set_pixel(result, x, y, int(get_pixel(image, x, y)))
    return result
            
            
    


# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    def blur_kernel(num):
        kernel = {
            'height': num,
            'width': num,
            'pixels': [(1/num**2) for i in range(num**2)],
        }
        return kernel

    # then compute the correlation of the input image with that kernel using
    # the 'extend' behavior for out-of-bounds pixels
    ans = correlate(image,blur_kernel(n), 'extend')
    

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    realans = round_and_clip_image(ans)
    return realans

def sharpened(image,n):
    """
    Return a new image representing the result of applying a sharpening (corresponding with
    a box blur of kernel size n) to the given input image.
    """
    def blur_kernel(num):
        kernel = {
            'height': num,
            'width': num,
            'pixels': [(1/num**2) for i in range(num**2)],
        }
        return kernel
    ans = {
        'height': image.get('height'),
        'width': image.get('width'),
        'pixels': [0 for i in range(len(image.get('pixels')))],
    }
    doubledimage =  {
        'height': image.get('height'),
        'width': image.get('width'),
        'pixels': [ele*2 for ele in image['pixels']],
    }
    correspondingblur = correlate(image,blur_kernel(n), 'extend')
    for x in range( image.get('width')):
        for y in range( image.get('height')):
            w = get_pixel(doubledimage, x, y) - get_pixel(correspondingblur, x, y)
            set_pixel(ans, x, y, w)
    realans = round_and_clip_image(ans)
    return realans
    
            
def edges(image):
    """
    Returns a new image with the edges of the image passed in emphasized 
    """
    ans = {
        'height': image.get('height'),
        'width': image.get('width'),
        'pixels': [0 for i in range(len(image.get('pixels')))],
    }
    
    k1 = {
        'height': 3,
        'width': 3,
        'pixels': [-1,0, 1,
                   -2, 0, 2,
                   -1, 0, 1],
        }
    k2 = {
        'height': 3,
        'width': 3,
        'pixels': [-1, -2, -1,
                   0,  0,  0,
                   1,  2,  1],
        }
    cor1 = correlate(image, k1, 'extend')
    cor2 = correlate(image, k2, 'extend')
    for x in range( image.get('width')):
        for y in range( image.get('height')):
            w = math.sqrt((get_pixel(cor1, x, y))**2 + get_pixel(cor2, x, y)**2)
            set_pixel(ans, x, y, w)
    realans = round_and_clip_image(ans)
    return realans
    

# COLOR FILTERS

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    
    def grey_to_color(image):
        redim = {
            'height': image.get('height'),
            'width': image.get('width'),
            'pixels': [0 for i in range(len(image.get('pixels')))]
        }
        greenim = {
            'height': image.get('height'),
            'width': image.get('width'),
            'pixels': [0 for i in range(len(image.get('pixels')))]
        }
        blueim = {
            'height': image.get('height'),
            'width': image.get('width'),
            'pixels': [0 for i in range(len(image.get('pixels')))]
        }
        
        for x in range(image.get('width')):
            for y in range( image.get('height')):
                w = get_pixel(image, x, y)
                set_pixel(redim, x, y, w[0])
                set_pixel(greenim, x, y, w[1])
                set_pixel(blueim, x, y, w[2])
        
    
        filtered_color_image = {
            'height': image.get('height'),
            'width': image.get('width'),
            'pixels': [0 for i in range(len(image.get('pixels')))],
        }
        newred = filt(redim)
        newgreen = filt(greenim)
        newblue = filt(blueim)
        for x in range(image.get('width')):
            for y in range( image.get('height')):
                new = ()             
                new = new + (get_pixel(newred, x, y),)
                new = new + (get_pixel(newgreen, x, y),)
                new = new + (get_pixel(newblue, x, y),)                
                set_pixel(filtered_color_image, x, y, new)
        
        return filtered_color_image
    return grey_to_color
        

def combine_photos(image1, image2):
    """
    Takes in two images
    Returns a photo that combines the first and second image.
    """
    height = max(image1['height'],image2['height'])
    width = max(image1['width'],image2['width'])

    
    result = {
        'height': height,
        'width': width,
        'pixels': [0 for i in range(width*height)],
    }
    
    for x in range(0,width,2):
        for y in range(0,height,2):
            set_pixel(result, x, y, get_pixel(image1,x,y,'extend'))
    
    for x in range(1,width,2):
        for y in range(1,height,2):
            set_pixel(result, x, y, get_pixel(image2,x,y,'extend'))
    
    realans = round_and_clip_image(result)
    return realans
            
            
    
    

def make_blur_filter(n):
    def new_blur(image):
        return blurred(image,n)
    return new_blur


def make_sharpen_filter(n):
    def new_sharpen(image):
        return sharpened(image, n)
    return new_sharpen


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def combined_filters(image):
        newim = image
        for ele in filters:
            newim = ele(newim)
        return newim
    return combined_filters
            
        


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    #bg = load_greyscale_image('bluegill.png')
    #bgnew = inverted(bg)
    #save_greyscale_image(bgnew, 'bluegillinverted.png')
    
    kern ={
        'height': 13,
        'width': 13,
        'pixels': [0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
1,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0],
    }


    '''
    pigbird = load_greyscale_image('pigbird.png')
    centpix = load_greyscale_image('centered_pixel.png')
    construct = load_greyscale_image('construct.png')
    construct_new = edges(construct)
    '''
    
    #print(edges(centpix))
    #save_greyscale_image(construct_new, 'constructnew.png')
    #cat = load_greyscale_image('cat.png')
    #blurcat_extend = blurred(cat, 13)
    #pyth = load_greyscale_image('python.png')
    #cat = load_color_image('cat.png')
    #inverted_color = color_filter_from_greyscale_filter(inverted)
    #invertcat = inverted_color(cat)
    
    '''
    sharpen7 = make_sharpen_filter(7)
    color_sharpen = color_filter_from_greyscale_filter(sharpen7)
    sparrow = load_color_image('sparrowchick.png')
    sharpsparrow = color_sharpen(sparrow)
    save_color_image(sharpsparrow, 'sharp_sparrow.png')
    '''
    '''
    filter1 = color_filter_from_greyscale_filter(edges)
    filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    filt = filter_cascade([filter1, filter1, filter2, filter1])
    frog = load_color_image('test_images/frog.png')
    newfrog = filt(frog)
    save_color_image(newfrog, 'newfrog.png')
    '''
    
    #blur9 = make_blur_filter(9)
    #color_blur = color_filter_from_greyscale_filter(blur9)
    #pyth = load_color_image('python.png')
    #blurredpython = color_blur(pyth)
    #save_color_image(blurredpython, 'blurredpython.png')
    #save_color_image(invertcat, 'colorinvertedcat.png')
    #python_sharpened = sharpened(pyth, 11)
    #save_greyscale_image(python_sharpened, 'python_sharpened.png')
    #save_greyscale_image(blurcat_extend, 'blurcat_extend.png')
    #pbzero = correlate(pigbird, kern, 'zero')
    #pbextend = correlate(pigbird, kern, 'extend')
    #pbwrap = correlate(pigbird, kern, 'wrap')
    #save_greyscale_image(pbzero, 'pigbirdzero.png')
    #save_greyscale_image(pbextend, 'pigbirdextend.png')
    #save_greyscale_image(pbwrap, 'pigbirdwrap.png')
    
    #FOR ADDITIONAL FREESTYLE FUNCTION
    frog = load_greyscale_image('test_images/smallfrog.png')
    sparrow = load_greyscale_image('test_images/smallmushroom.png')
    frogsparrow_mix = combine_photos(frog, sparrow)
    save_greyscale_image(frogsparrow_mix, 'fromushroom.png')
    