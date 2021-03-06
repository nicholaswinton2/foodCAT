#! /usr/bin/env python

import os, sys, getopt
import time
from PIL import Image
import glob
import numpy as np
sys.path.append('./routine')
from ImageSR import SCN
import math
from scipy import misc

DIMENSION = 256
SR_MAX_FACTOR = 4.0


def sr(img_path, factor, sr_net):

    IMAGE_FILE=img_path
    UP_SCALE=factor
    SHAVE=1 #set 1 to be consistant with SRCNN
    #print 'factor: ', UP_SCALE
    im_l = []
    if len(IMAGE_FILE)>0:
	    # array with all images
        im_l = [np.array(Image.open(IMAGE_FILE)).astype(np.float32)]

    for i in range(len(im_l)):
        t=time.time();
        im_h, im_h_y=sr_net.upscale(im_l[i], UP_SCALE)
        t=time.time()-t;
        #print 'time elapsed:', t

        # delete the old image
        os.remove(IMAGE_FILE)
        # save the new image
        # first take just the name of the file (last '/'), then take just the text without the format (before '.')
        path_to_save = '{}.jpg'.format( IMAGE_FILE.split('/')[-1].split('.')[0] )
        # add the full path
        path_to_save = os.path.join('/'.join(IMAGE_FILE.split('/')[:-1]), path_to_save)
        try:
        	Image.fromarray(np.rint(im_h).astype(np.uint8)).save(path_to_save)
        	#print 'SR res: ', misc.imread(path_to_save).shape[:2]
        	print 'saved: ', path_to_save
        except:
        	print '! can\'t save image: ', img_path


def getDirData(path):

    # get the generator of subdirs contents
    dirsData = os.walk(path)

    # left out the frist element, wich contains only the names of subdirectories
    a = dirsData.next()

    dirs = {}

    for (root , dirnames, filenames) in dirsData:
        dirs[root] = filenames
        # also we replace white spaces with underline
        #dirs[root[2:].replace (' ', '_')] = [files.replace (' ', '_') for files in filenames]

    #print 'dirs keys:', dirs.keys()
    return dirs



def superresolution(path, min_resolution):

    # get image names for every folder as {'globalPath/bacalla': [bacalla1.jpg, ...], ...}
    allImage = getDirData(path)

    #upscaling
    MODEL_FILE=['./mdl/weights_srnet_x2_52.p', './mdl/weights_srnet_x2_310.p']
    sr_net = SCN(MODEL_FILE)

    # for each class
    for clas, images in allImage.iteritems():
        #print '########'
        #print 'clas: ', clas
        #for each image
        for img in images:
            img_path = os.path.join(clas, img)
            #print '###'
            #print 'img: ', img
            #print 'original res: ', misc.imread(img_path).shape[:2]

            # get the minima resolution between width and height: '.shape[:2]'
            min_img_res = min( misc.imread(img_path).shape[:2] )
            #let's resize images which the minima is lower than the required minima
            if min_img_res < min_resolution:
                # we'll SR as maximum the SR_MAX_FACTOR. OBS: maybe some pictures will not SR to the minima required
                factor = min( math.ceil(min_resolution/min_img_res), SR_MAX_FACTOR)
                # compute and save the super-resolution
                sr(img_path, factor, sr_net)


def getArgs(argv):

    path = ''
    min_resolution = DIMENSION

    try:
        opts, args = getopt.getopt(argv, 'p:R:')
    except getopt.GetoptError:
        print 'bad usage'
        sys.exit(2)

    for opt, arg in opts:
        #print 'opt: ',opt
        if opt == "-p":
            path = str(arg)
        if opt == "-R":
            min_resolution = float(arg)

    if not os.path.exists(path):
        print 'incorrect source path of classes'
        sys.exit(2)


    return path, min_resolution



# unbuffer python superresolution.py -p 'data' -R 256 2>&1 | tee outfile
# unbuffer python superresolution.py -p '../../../data/resized_images/' -R 256 2>&1 | tee outfile

# unbuffer python superresolution.py -p '../../../data/1/' -R 256 2>&1 | tee outfile1
# unbuffer python superresolution.py -p '../../../data/2/' -R 256 2>&1 | tee outfile2

if __name__=='__main__':
    '''
        -p path wich holds all directories (classes) where each directory has the images

    '''

    # get paths of superClasses*, num images of train/val and target path to hold all files
    path, min_resolution = getArgs( sys.argv[1:] )
    #print min_resolution
    superresolution(path, min_resolution)
