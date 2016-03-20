#Alexander Marshall 100487187
import argparse
import sys
import cv2
import math
import json
import numpy as np
from scipy import linalg
from os import listdir
import matplotlib.pyplot as plt

def calculateMeans(imgfolder):
    blue = {}
    green = {}
    red = {}
    fileList = listdir(imgfolder)

    for f in fileList:
        img = cv2.imread("%s/%s" % (imgfolder, f))

        b = np.mean(img[:,:,0])
        g = np.mean(img[:,:,1])
        r = np.mean(img[:,:,2])

        if b > g and b > r:
            blue[f] = (b,g,r)
        elif g > b and g > r:
            green[f] = (b,g,r)
        else:
            red[f] = (b,g,r)
        
    '''
    print 'blue:\t', len(blue)
    print 'green:\t', len(green)
    print 'red:\t', len(red)
    print 'total:\t', len(blue)+len(green)+len(red)
    '''

    with open('blue.json', 'w') as outfile:
        json.dump(blue, outfile)
    with open('green.json', 'w') as outfile:
        json.dump(green, outfile)
    with open('red.json', 'w') as outfile:
        json.dump(red, outfile)

def mosaic(imgfile,n):
    blue = {}
    green = {}
    red = {}
    imgs = []
    
    with open('blue.json') as infile:
        blue = json.load(infile)
    with open('green.json') as infile:
        green = json.load(infile)
    with open('red.json') as infile:
        red = json.load(infile)

    img = cv2.imread(imgfile)
    rows, cols, _ = img.shape
    mosaicImg = np.zeros(img.shape)

    for row in xrange(0, rows, n):
        for col in xrange(0, cols, n):
            b = np.mean(img[row:row+n,col:col+n,0])
            g = np.mean(img[row:row+n,col:col+n,1])
            r = np.mean(img[row:row+n,col:col+n,2])

            filename = ''
            if b > g and b > r:
                filename = compare(blue, (b,g,r))
            elif g > b and g > r:
                filename = compare(green, (b,g,r))
            else:
                filename = compare(red, (b,g,r))
            
            imgs.append(filename)

            #replace pixels with image
            replace = cv2.imread("albums/"+filename)
            replace = cv2.resize(replace, (n,n))
            mosaicImg[row:row+n,col:col+n,:] = replace

    cv2.imwrite(imgfile.split('.')[0]+'_mosaic.jpg', mosaicImg)
    print 'Wrote mosaic to', imgfile.split('.')[0]+'_mosaic.jpg'

def compare(dic, bgr):
    img = ''
    close = (-255,-255,-255)
    for key in dic:
        dist1 = math.sqrt(math.pow((bgr[0]-dic[key][0]), 2)+math.pow((bgr[1]-dic[key][1]), 2)+math.pow((bgr[2]-dic[key][2]), 2))
        dist2 = math.sqrt(math.pow((bgr[0]-close[0]), 2)+math.pow((bgr[1]-close[1]), 2)+math.pow((bgr[2]-close[2]), 2))
        if dist1 <= dist2:
            img = key
            close = dic[key]
            
    return img

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CSCI 4420U Project')
    parser.add_argument('--means', action='store_true', help='Calculate means for a folder of images')
    parser.add_argument('--folder', help='A folder of images to be used for mosaicing')
    parser.add_argument('imgfile', help='The image to be mosaicified')
    parser.add_argument('size',help='TODO - Alex')

    args = parser.parse_args()

    if args.means:
        calculateMeans(args.folder)
        mosaic(args.imgfile,args.size)
    else:
        mosaic(args.imgfile,int(args.size))
