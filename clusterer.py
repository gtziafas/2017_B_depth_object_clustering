#!/usr/bin/python

from __future__ import division
from PIL import Image
import sys
import math
import numpy as np
import cv2
from sklearn.cluster import KMeans

# Load a color image
imgrgb = cv2.imread('5rgb.png')
imgdepth = cv2.imread('5d.png',cv2.IMREAD_GRAYSCALE)
# Convert the image to Lab color space 
imglab = cv2.cvtColor(imgrgb, cv2.COLOR_RGB2Lab)

L = imglab[:,:,0]
a = imglab[:,:,1]
b = imglab[:,:,2]
#~ cv2.imshow('a',a)
#~ cv2.imshow('b',b)
#~ cv2.imshow('L',L)

sigma_L = np.std(L)
sigma_a = np.std(a)
sigma_b = np.std(b)
imglab = (3/(sigma_L+sigma_a+sigma_b)) * imglab

imgcoord = np.zeros((480,640,3))
imgcoord[:,:,0] = np.transpose(np.tile(np.array(range(480)),(640,1))) + 1
imgcoord[:,:,1] = np.tile(np.array(range(640)),(480,1)) + 1
imgcoord[:,:,2] = imgdepth[:,:]

sigma_x = np.std(np.std(imgcoord[:,:,0])) + 0.0000000001 # avoid zeros
sigma_y = np.std(np.std(imgcoord[:,:,1])) + 0.0000000001 # avoid zeros
sigma_z = np.std(np.std(imgcoord[:,:,2])) + 0.0000000001 # avoid zeros
imgcoord = (3/(sigma_x + sigma_y + sigma_z)) * imgcoord
#~ coord_weight = 0.00000000000005
coord_weight = 0.00000000001

feature_vector = np.zeros((480,640,6))
feature_vector[:,:,0:3] = imglab
#~ feature_vector[:,:,3:6] = imgcoord * coord_weight # x+y+z
feature_vector[:,:,5] = imgcoord[:,:,2] * coord_weight # only z

# Visualize Data with Scatterplot Matrix
#~ import matplotlib.pyplot as plt
#~ import pandas
#~ from pandas.tools.plotting import scatter_matrix
#~ scatter_matrix(feature_vector)
#~ plt.show()

nclusters = 7
feature_vectorarray = feature_vector.reshape(480*640,6)
kmeans = KMeans(n_clusters=nclusters,n_jobs=-1).fit(feature_vectorarray[:,1:]) # use only a and b
print "Kmeans is done!"
segmimg = np.zeros((480,640,3),dtype=np.uint8)

coldict = {
'[0]': [230, 25, 75],
'[1]': [60, 180, 75],
'[2]': [255, 225, 25],
'[3]': [0, 130, 200],
'[4]': [245, 130, 48],
'[5]': [145, 30, 180],
'[6]': [70, 240, 240],
'[7]': [240, 50, 230],
'[8]': [210, 245, 60],
'[9]': [250, 190, 190],
'[10]': [0, 128, 128],
'[11]': [230, 190, 255],
'[12]': [170, 110, 40],
'[13]': [255, 250, 200],
'[14]': [128, 0, 0],
'[15]': [170, 255, 195],
'[16]': [128, 128, 0],
'[17]': [255, 215, 180],
'[18]': [0, 0, 128],
'[19]': [128, 128, 128],
'[20]': [255, 255, 255],
'[21]': [0, 0, 0]
}

for i in range(0, 480):
  sys.stdout.write("Progress: %.2f%%   \r" % ((i/480)*100) )
  sys.stdout.flush()
  for j in range(0, 640):
    if imgdepth[i,j] < imgdepth.max() - 3: # apply a depth threshold
      segmimg[i,j,:] = coldict[str(kmeans.predict([feature_vector[i,j,1:]]))]
    else:
      segmimg[i,j,:] = 0

vis = np.concatenate((imgrgb, segmimg), axis=1)
cv2.imshow('kmeans',vis)

cv2.waitKey(0)
raw_input("Press Esc and Enter to end...")
cv2.destroyAllWindows()
