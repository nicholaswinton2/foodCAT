#! /usr/bin/env python

import os, sys
import time
from PIL import Image
import glob
import numpy as np
sys.path.append('./routine')
from ImageSR import SCN#edit: , Bicubic
#edit: import utils

'''edit:
def evalimg(im_h_y, im_gt, shave=0):
    if len(im_gt.shape)==3:
        im_gt_ycbcr = utils.rgb2ycbcr(im_gt/255.0)*255.0
        im_gt_y = im_gt_ycbcr[:, :, 0]
    else:
        im_gt_y = im_gt

    im_h_y_uint8 = np.rint( np.clip(im_h_y, 0, 255))
    im_gt_y_uint8 = np.rint( np.clip(im_gt_y, 0, 255))
    diff = im_h_y_uint8 - im_gt_y_uint8
    #diff = im_h_y - im_gt_y
    if shave>0:
        diff = utils.shave(diff, [shave, shave])
    res = {}
    res['rmse'] = np.sqrt((diff**2).mean())
    res['psnr'] = 20*np.log10(255.0/res['rmse'])
    return res
'''

if __name__ == '__main__':
    #input with two images
    IMAGE_FILE='./data/slena.bmp'
    #edit: IMAGE_GT_FILE='./data/mlena.bmp'
    """
    # input with ground truth images only (Matlab required)
    IMAGE_FILE=''
    IMAGE_GT_FILE='./data/Set5/*.bmp'
    """

    MODEL_FILE=['./mdl/weights_srnet_x2_52.p', './mdl/weights_srnet_x2_310.p']
    UP_SCALE=4
    SHAVE=1 #set 1 to be consistant with SRCNN

    # load inputs
    #edit: im_gt = []
    #edit: files_gt = glob.glob(IMAGE_GT_FILE)

    '''edit: 	
    for f in files_gt:
        #print 'loading', f
        im = np.array(Image.open(f))
        im = utils.modcrop(im, UP_SCALE).astype(np.float32)
        im_gt += [im]
    '''
	
    
    im_l = []
    if len(IMAGE_FILE)>0:
        #edit: assert(len(im_gt)==1)
	# array with all images
        im_l = [np.array(Image.open(IMAGE_FILE)).astype(np.float32)]
    else: #down scale from ground truth using Matlab
        try:
	    '''edit: 
            from pymatbridge import Matlab
            mlab = Matlab()
            mlab.start()
            for im in im_gt:
                mlab.set_variable('a', im)
                mlab.set_variable('s', 1.0/UP_SCALE)
                mlab.run_code('b=imresize(a, s);')
                im_l += [mlab.get_variable('b')]
            mlab.stop()
	    '''
        except:
            print 'failed to load Matlab!'
            assert(0)
            #im_l = utils.imresize(im_gt, 1.0/UP_SCALE)

    #upscaling
    #sr = Bicubic()
    sr = SCN(MODEL_FILE)
    #edit: res_all = []
    for i in range(len(im_l)):
        t=time.time();
        im_h, im_h_y=sr.upscale(im_l[i], UP_SCALE)
        t=time.time()-t;
        print 'time elapsed:', t

        # evaluation
	'''edit: 
        if SHAVE==1:
            shave = round(UP_SCALE)
        else:
            shave = 0
        res = evalimg(im_h_y, im_gt[i], shave)
        res_all += [res]
        print 'evaluation against {}, rms={:.4f}, psnr={:.4f}'.format(files_gt[i], res['rmse'], res['psnr'])
	'''

        # save
        #edit: img_name = os.path.splitext(os.path.basename(im_l[i]))[0]
	img_name = os.path.splitext(os.path.basename(IMAGE_FILE))[0]
        Image.fromarray(np.rint(im_h).astype(np.uint8)).save('./data/{}_x{}.png'.format(img_name, UP_SCALE))

    #edit: print 'mean PSNR:', np.array([_['psnr'] for _ in res_all]).mean()

