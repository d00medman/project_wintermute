import numpy as np

'''
TODO: encapsulate as a class
'''


def create_pixel_grid(screen_data_capture):
    """
    The screen data capture is a raw string. The nes drew graphics by essentially going pixel by pixel across the screen f
    rom top.
    Every 256 pixels, a new row would be displayed on tv
    Nintaco recovers the pixels in a single stream, as though the scanline never broke.
    Our first step, as seen here, is to do this: produce an array of pixel rows

    At start of this step pixels = [33, 26, 41, 20, 15, 15, 41, 41, 15, 15, 15, 15, 15, 15, 15, 15]
    at end of this step pixels = [
        [33, 26, 41, 20],
        [15, 15, 41, 41],
        [15, 15, 15, 15],
        [15, 15, 15, 15]
    ]
    """
    scanline_rows = np.array([screen_data_capture[i-256:i] for i in range(len(screen_data_capture) + 1) if i % 256 == 0 and i > 0])

    """
    When the scanline rows are stacked, we can trim the first and last 8 rows off the array. These rows are used
    for buffering, and are not visible to a human player.

    It is unknown whether this has a negative impact on state construction
    """
    scanline_rows = scanline_rows[8:-8]


    """
    This code annoys me. Basically, we want to find all the x and y points which will deliniate the shape of the state
    space. These breakpoints will be combined against the trimmed, formatted, scanline row array.

    It is worth noting the relationship between the nested arrays for x and y. This has made me utterly miserable because I cannot
    keep it straight,
    [
        [(33, [y=0, x=0]), (26, [y=0, x=1]), (41, [y=0, x=2]), (20, [y=0, x=3])],
        [(15, [y=1, x=0]), (15, [y=1, x=1]), (41, [y=1, x=2]), (41, [y=1, x=3])],
        [(15, [y=2, x=0]), (15, [y=2, x=1]), (15, [y=2, x=2]), (15, [y=2, x=3])],
        [(15, [y=3, x=0]), (15, [y=3, x=1]), (15, [y=3, x=2]), (15, [y=3, x=3])]
    ]

    the *_up_range variables are given an additional 1 to include the final breakpoint. Quirk of range function. Being python 2.7, unwilling to look for a fix

    The breaks are pretty consistent, we then tabulate them into two lists. I have the feeling these can be coalesced into tuples, but am unwilling to rethink this now
    """
    # Note: there was an IndexError here
    x_up_range = len(scanline_rows[0]) + 1
    y_up_range = len(scanline_rows) + 1
    x_breaks = [x for x in range(x_up_range)  if x % 16 == 0]
    y_breaks = [y for y in range(y_up_range) if y % 16 == 0]


    """
    We now build the grid. Our outer loop goes by the y breaks.
    At the start of each y breakpoint, we creat a grid row
    We then iterate across the x breakpoints
    For all the breakpoints, we use the numpy array's built in multi-index slicing to put the next square in the grid row
    When we have reached the last x breakpoint in the row, we append the grid row to the grid
    We repeat this for all 13(give or take 1, as I mentioned earlier, some confusion on bounding) rows.

    colummn and row sizes are bounded. Until full confidence check, unsure of whether this is fucking with the readout
    """
    grid = []
    for y in y_breaks:
        if len(grid) < 13:
            grid_row = []
            for x in x_breaks:
                if len(grid_row) < 15:
                    square = scanline_rows[y:y+16, x:x+16]
                    grid_row.append(square)
                if x == 256:
                    grid.append(grid_row)
    return np.array(grid)


"""
initial effort to crunch the massive state data set into something more immediately usable

These two methods Produce a new grid which retains the same shape but has the most common number in each square.
I have found this method effective for checking my own work, as it does allow a (quite rough) grid to be drawn
"""


def reduce_pixel_square(target):
    return np.argmax(np.bincount(np.array([np.argmax(np.bincount(np.array(row))) for row in target if len(row) > 0])))


def reduce_grid(pixel_grid):
    reduced_grid = []
    for row in pixel_grid:
        reduced_row = []
        for column in row:
            if len(column) > 1:
                reduced_row.append(reduce_pixel_square(column))
        reduced_grid.append(reduced_row)
    return reduced_grid
