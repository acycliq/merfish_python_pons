import json
import os
import glob
import csv
import numpy as np
import numba
import skimage
from .overides import overide
from .base_logger import logger


def _get_file(OUT_DIR, n, header_line):
    filename = os.path.basename(OUT_DIR).split('.')[0]
    file = os.path.join(OUT_DIR, filename + '_%d.%s' % (n, 'tsv'))
    handle = open(file, "a", newline='', encoding='utf-8')
    write = csv.writer(handle, delimiter='\t')
    write.writerow(header_line)
    return file, handle


def worker(arg_in, OUT_DIR):
    n = arg_in[0]
    df = arg_in[1]
    filename = os.path.basename(OUT_DIR).split('.')[0]
    file = os.path.join(OUT_DIR, filename + '_%d.%s' % (n, 'tsv'))
    df.to_csv(file, index=False, sep='\t')


def dapi_dims(cfg):
    dapi = skimage.io.imread(cfg['dapi_tif'])
    img = {'width': dapi.shape[1],
           'height': dapi.shape[0]}
    return img


def dapi_dims_2(cfg):
    """
    Gets the dapi dimension from the manifest.
    :param cfg:
    :return:
    """
    try:
        with open(cfg['manifest']) as f:
            settings = json.load(f)
    except FileNotFoundError:
        # logger.info('File doesnt exist', exc_info=True)
        logger.warning('File doesnt exist: %s' % cfg['manifest'])
        logger.warning('Getting img dimensions from the overide module')
        settings = {}
        settings['mosaic_width_pixels'] = overide[cfg["slice_id"]][cfg["region_id"]]["img_width"]
        settings['mosaic_height_pixels'] = overide[cfg["slice_id"]][cfg["region_id"]]['img_height']

    # image width and height in pixels
    img = {'width': settings['mosaic_width_pixels'],
           'height': settings['mosaic_height_pixels']}
    return img


def transformation(cfg):
    """
        Micron to pixel transformation
    """
    um_to_px = np.genfromtxt(cfg['micron_to_mosaic_pixel_transform'], delimiter=' ')
    assert um_to_px.shape == (3,3), 'The file %s should contain a space delimited 3-by-3 array' % cfg['micron_to_mosaic_pixel_transform']
    a = um_to_px[0, 0]
    b = um_to_px[0, 2]
    c = um_to_px[1, 1]
    d = um_to_px[1, 2]

    img = dapi_dims_2(cfg)

    # bounding box in microns
    bbox = {}
    bbox['x0'] = -1 * b/a
    bbox['x1'] = img['width']/a + bbox['x0']
    bbox['y0'] = -1 * d/c
    bbox['y1'] = img['height']/a + bbox['y0']

    tx = lambda x: a * x + b
    ty = lambda y: c * y + d
    return tx, ty, img, bbox


@numba.jit(nopython=True)
def is_inside_sm(polygon, point):
    # From https://github.com/sasamil/PointInPolygon_Py/blob/master/pointInside.py
    # and
    # https://github.com/sasamil/PointInPolygon_Py/blob/master/pointInside.py
    length = len(polygon)-1
    dy2 = point[1] - polygon[0][1]
    intersections = 0
    ii = 0
    jj = 1

    while ii<length:
        dy  = dy2
        dy2 = point[1] - polygon[jj][1]

        # consider only lines which are not completely above/bellow/right from the point
        if dy*dy2 <= 0.0 and (point[0] >= polygon[ii][0] or point[0] >= polygon[jj][0]):

            # non-horizontal line
            if dy<0 or dy2<0:
                F = dy*(polygon[jj][0] - polygon[ii][0])/(dy-dy2) + polygon[ii][0]

                if point[0] > F: # if line is left from the point - the ray moving towards left, will intersect it
                    intersections += 1
                elif point[0] == F: # point on line
                    return 2

            # point on upper peak (dy2=dx2=0) or horizontal line (dy=dy2=0 and dx*dx2<=0)
            elif dy2==0 and (point[0]==polygon[jj][0] or (dy==0 and (point[0]-polygon[ii][0])*(point[0]-polygon[jj][0])<=0)):
                return 2

        ii = jj
        jj += 1

    #print 'intersections =', intersections
    return intersections & 1


@numba.njit(parallel=True)
def is_inside_sm_parallel(points, polygon):
    ln = len(points)
    D = np.empty(ln, dtype=numba.boolean)
    for i in numba.prange(ln):
        D[i] = is_inside_sm(polygon,points[i])
    return D


def check_path(path_str):
    """
    checks if a dir exists. If it exists it will delete its contents.
    If it does not exist it will create it
    :param path_str:
    :return:
    """
    if not os.path.exists(path_str):
        os.makedirs(path_str)
    else:
        files = glob.glob(path_str + '/*.*')
        for f in files:
            os.remove(f)




