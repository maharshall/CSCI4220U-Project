#Alexander Marshall 100487187
import argparse
import cv2
import math
import numpy as np
from scipy import linalg
from os import listdir
import matplotlib.pyplot as plt

def mosaic(imgfolder):
    n = 50
    imgs = []
    means = []
    fileList = listdir(imgfolder)

    for f in fileList:
        img = cv2.imread("%s/%s" % (imgfolder, f))
        img = cv2.resize(img, (n,n))

        b = np.mean(img[:,:,0])
        g = np.mean(img[:,:,1])
        r = np.mean(img[:,:,2])

        imgs.append(img)
        means.append([b, g, r])

    test = stack(imgs, False)

    cv2.imshow('test', test[0])
    cv2.waitKey(0)

def stack(imgs, v):
    print len(imgs)
    if len(imgs) < 2:
        return imgs

    mat = []
    for i in xrange(0, len(imgs)-1, 2):
        if v:
            mat.append(np.vstack((imgs[i], imgs[i+1])))
        else:
            mat.append(np.hstack((imgs[i], imgs[i+1])))

    return stack(mat, not v)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CSCI 4420U Project')

    mosaic("albums/")
