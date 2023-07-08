from PIL import Image
from itertools import product
from math import cos, pi

PNG_FILENAME = "jpeg_dct.png"
SVG_FILENAME = "jpeg_dct.svg"

SEAMLESS = False
SCALE = 3
NO_PADDING = False


# Layout
CELL_SIZE = 24*SCALE
PADDING = 3*SCALE
GRID_WIDTH = 1*SCALE

if NO_PADDING: PADDING = -GRID_WIDTH
if SEAMLESS: PADDING = GRID_WIDTH = 0

CELL_OFFSET = CELL_SIZE+PADDING+GRID_WIDTH

SVG_TEXT_SPACE = 20*SCALE
SVG_TEXT_SIZE = 10*SCALE

# JPEG specific:
CELL_COUNT = 8
BLOCK_SIZE = 8


GRID_COLOR = (0, 64, 192, 255)
TEXT_COLOR = (0, 64, 192, 255)



SIZE = CELL_SIZE*CELL_COUNT + PADDING*(CELL_COUNT-1) + GRID_WIDTH*(CELL_COUNT+1)

img = Image.new("RGBA", (SIZE,SIZE))
dat = img.load()

for y, x in product(range(SIZE),range(SIZE)):
    fx = x // CELL_OFFSET; cx = x % CELL_OFFSET - GRID_WIDTH
    fy = y // CELL_OFFSET; cy = y % CELL_OFFSET - GRID_WIDTH
    if cx >= CELL_SIZE + GRID_WIDTH or cy >= CELL_SIZE + GRID_WIDTH:
        continue
    border_x = cx < 0 or CELL_SIZE <= cx
    border_y = cy < 0 or CELL_SIZE <= cy
    if border_x or border_y:
        dat[x, y] = GRID_COLOR
    elif cx < CELL_SIZE and cy < CELL_SIZE:
        if BLOCK_SIZE:
            cx = int(cx/CELL_SIZE*BLOCK_SIZE)/BLOCK_SIZE
            cy = int(cy/CELL_SIZE*BLOCK_SIZE)/BLOCK_SIZE

            # place sample on center of pixel
            cx += 0.5/BLOCK_SIZE
            cy += 0.5/BLOCK_SIZE
        else:
            cx /= CELL_SIZE
            cy /= CELL_SIZE

            # place sample on center of pixel
            cx += 0.5/CELL_SIZE
            cy += 0.5/CELL_SIZE

        factor = cos(fx*cx*pi)*cos(fy*cy*pi)

        if SEAMLESS and (fx^fy)&2: factor = -factor

        dat[x, y] = (int((factor*0.5+0.5)*255),)*3 + (255,)

img.save(PNG_FILENAME)


import cairo
import numpy as np

def pil_image_to_cairo_surface(img):
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    img = Image.merge("RGBA", (b, g, r, a))

    arr = np.array(img)
    height, width, channels = arr.shape
    surface = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, width, height)
    return surface

sfc = cairo.SVGSurface(SVG_FILENAME, SIZE+SVG_TEXT_SPACE, SIZE+SVG_TEXT_SPACE)
ctx = cairo.Context(sfc)

ctx.set_source_surface(pil_image_to_cairo_surface(img), SVG_TEXT_SPACE, SVG_TEXT_SPACE)

ctx.paint()



ctx.set_source_rgba(*map(lambda x:x/255, TEXT_COLOR))
ctx.set_font_size(SVG_TEXT_SIZE)
ctx.select_font_face("monospace",
                     cairo.FONT_SLANT_NORMAL,
                     cairo.FONT_WEIGHT_NORMAL)


for f in range(CELL_COUNT):
    dd = SVG_TEXT_SPACE + CELL_OFFSET*f + GRID_WIDTH + CELL_SIZE/2
    s = f"{f}"
    extends = ctx.text_extents(s)
    print(extends)

    ctx.move_to(dd-extends.width/2, SVG_TEXT_SPACE/2+extends.height/2)
    ctx.show_text(s)

    ctx.move_to(SVG_TEXT_SPACE/2-extends.width/2, dd+extends.height/2)
    ctx.show_text(s)
