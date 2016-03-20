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
    bluered = {}
    bluegreen = {}
    greenred = {}
    greenblue = {}
    redblue = {}
    redgreen = {}
    fileList = listdir(imgfolder)

    for f in fileList:
        img = cv2.imread("%s/%s" % (imgfolder, f))

        b = np.mean(img[:,:,0])
        g = np.mean(img[:,:,1])
        r = np.mean(img[:,:,2])

        if b > g and b > r:
            if g > r:
                bluegreen[f] = (b,g,r)
            else:
                bluered[f] = (b,g,r)
        elif g > b and g > r:
            if b > r:
                greenblue[f] = (b,g,r)
            else:
                greenred[f] = (b,g,r)
        else:
            if b > g:
                redblue[f] = (b,g,r)
            else:
                redgreen[f] = (b,g,r)
        
    with open('json/bluegreen.json', 'w') as outfile:
        json.dump(bluegreen, outfile)
    with open('json/greenblue.json', 'w') as outfile:
        json.dump(greenblue, outfile)
    with open('json/redblue.json', 'w') as outfile:
        json.dump(redblue, outfile)
    with open('json/bluered.json', 'w') as outfile:
        json.dump(bluered, outfile)
    with open('json/greenred.json', 'w') as outfile:
        json.dump(greenred, outfile)
    with open('json/redgreen.json', 'w') as outfile:
        json.dump(redgreen, outfile)

def mosaic(imgfile, n, scale):
    x = n*scale
    bluered = {}
    bluegreen = {}
    greenred = {}
    greenblue = {}
    redblue = {}
    redgreen = {}
    
    with open('json/bluered.json') as infile:
        bluered = json.load(infile)
    with open('json/greenred.json') as infile:
        greenred = json.load(infile)
    with open('json/redblue.json') as infile:
        redblue = json.load(infile)
    with open('json/bluegreen.json') as infile:
        bluegreen = json.load(infile)
    with open('json/greenblue.json') as infile:
        greenblue = json.load(infile)
    with open('json/redgreen.json') as infile:
        redgreen = json.load(infile)

    img = cv2.imread(imgfile)
    rows, cols, _ = img.shape
    newRows = (rows/n)*x
    newCols = (cols/n)*x
    mosaicImg = np.zeros((newRows, newCols, 3))

    newRow = 0
    newCol = 0
    for row in xrange(0, rows, n):
        for col in xrange(0, cols, n):
            b = np.mean(img[row:row+n,col:col+n,0])
            g = np.mean(img[row:row+n,col:col+n,1])
            r = np.mean(img[row:row+n,col:col+n,2])

            filename = ''
            if b > g and b > r:
                if g > r:
                    filename = compare(bluegreen, (b,g,r))
                else:
                    filename = compare(bluered, (b,g,r))
            elif g > b and g > r:
                if b > r:
                    filename = compare(greenblue, (b,g,r))
                else:
                    filename = compare(greenred, (b,g,r))
            else:
                if b > g:
                    filename = compare(redblue, (b,g,r))
                else:
                    filename = compare(redgreen, (b,g,r))
            
            #replace pixels with image
            replace = cv2.imread("albums/"+filename)
            replace = cv2.resize(replace, (x,x))
            mosaicImg[newRow:newRow+x,newCol:newCol+x,:] = replace
            
            newCol+= x
        newRow += x
        newCol = 0

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
    parser.add_argument('N',help='Replace the image in NxN chunks')
    parser.add_argument('--scale',help='Scale the image by this amount')

    args = parser.parse_args()

    if not args.scale:
        args.scale = 1
    if args.means:
        calculateMeans(args.folder)
        mosaic(args.imgfile, int(args.N), int(args.scale))
    else:
        mosaic(args.imgfile, int(args.N), int(args.scale))
