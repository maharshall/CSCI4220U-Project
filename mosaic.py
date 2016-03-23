#Alexander Marshall 100487187
#Dylan Crawford 100490070

#Program Arguments
#Input file - Name of the file to be made into a mosaic
#N          - [Integer] Number of rows and colums of the mosaic, NxN replacement images

#--means    - Calculate the means of the source images and save them to json files, only needs to be done once
#--folder   - Specify a folder to be used by the calculateMeans function, to allow different source images
#--scale    - [Integer] Scale the image, resulting image will be N*scale rows and columns. replace NxN pixels with XxX images

import argparse
import sys
import cv2
import math
import time
import json
import numpy as np
from scipy import linalg
from os import listdir

#Calculate the mean of every image from the source folder
#The mean values are stored in 6 json files
def calculateMeans(imgfolder):
	bluered = {}
	bluegreen = {}
	greenred = {}
	greenblue = {}
	redblue = {}
	redgreen = {}
	fileList = listdir(imgfolder)

	print 'Calculating mean values'

	for f in fileList:
		img = cv2.imread("%s/%s" % (imgfolder, f))

		b = np.mean(img[:,:,0])
		g = np.mean(img[:,:,1])
		r = np.mean(img[:,:,2])

		#Find the greatest 2 color values in the image
		#Store in respective dictionary [fileName,(B,G,R)]
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
	
	#Write dictionaries to json files
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

	print 'Mean calculations complete'

def mosaic(imgfile, n, scale):
	x = n*scale
	bluered = {}
	bluegreen = {}
	greenred = {}
	greenblue = {}
	redblue = {}
	redgreen = {}
	
	#Load dictionaries from json files
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

	#Read image, get rows and columns
	#Create np.array to hold the output image
	img = cv2.imread(imgfile)
	rows, cols, _ = img.shape

	#Resize the imput image to the nearest multiple of n
	if rows%n != 0:
		img = cv2.resize(img,(cols,rows-(rows%n)))		
		rows, _, _ = img.shape
	if cols%n !=0:
		img = cv2.resize(img,(cols-(cols%n),rows))
		_, cols, _ = img.shape

	newRows = (rows/n)*x
	newCols = (cols/n)*x
	mosaicImg = np.zeros((newRows, newCols, 3))

	start = time.time()
	newRow = 0
	newCol = 0
	#Calculate the mean of an nxn square of pixels
	#Check for highest 2 B,G,R color values and search the respective dictionary
	for row in xrange(0, rows, n):
		sys.stdout.write('\r%d/%d chunks completed (%.2fs elapsed)' % (row/n, rows/n, time.time()-start))
		sys.stdout.flush()
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

	sys.stdout.write('\r%d/%d chunks completed (%.2fs elapsed)\n' % (rows/n, rows/n, time.time()-start))
	sys.stdout.flush()
	
	#Write the image to a file
	outfile = imgfile.split('.')[0]+'_mosaic_scale_'+str(x/n)+'.jpg'
	cv2.imwrite(outfile, mosaicImg)
	print 'Wrote mosaic to', outfile

#Calculates the color distance between the mean of the nxn square of pixels and each image in the dictionary
#And the distance between the nxn square and the current closest image
#Return the current closest image name
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
	parser.add_argument('--folder', help='[Folder Path] A folder of images to be used for mosaicing')
	parser.add_argument('imgfile', help='[File Path]The image to be mosaicified')
	parser.add_argument('N',type=int,help='[Integer] Replace the image in NxN chunks')
	parser.add_argument('--scale',type=int,help='[Integer] Scale the image by this amount')

	args = parser.parse_args()

	if not args.scale:
		args.scale = 1
	if args.means and args.folder:
		calculateMeans(args.folder)
		mosaic(args.imgfile, args.N, args.scale)
	elif args.means and not args.folder:
		print 'Must specify folder to use for mosaic images'
	else:
		mosaic(args.imgfile, args.N, args.scale)
