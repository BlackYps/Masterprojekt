# Point Tracking Algorithm for Master Project Thesis WiSe 2020/2021
# University of Bremen, Department of Mechanical Engineering
# Master Project Thesis Title: "Deformation capabilities of mechanical meta Materials"

# Created on 13th of March 2021
# Author: Mika León Altmann, B.Sc., m.altmann@uni-bremen.de

# Update History
# 13th of April 2021: Cropping, Progressbar
# 14th of April 2021: Threshold Input, Plots for Movement and Position


# Imports
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import os
import sys


print("\r")

print("Please set a Threshold Value between 0 and 255: ")
inputThresh = int(input())

print("\r")

# load video file and get number of frames
cap = cv.VideoCapture('video.avi')
lenCap = int(cap.get(cv.CAP_PROP_FRAME_COUNT))


# Set up Detector for Blob Detection

params = cv.SimpleBlobDetector_Params()

params.filterByColor = True
params.blobColor = 0
params.filterByArea = True
params.filterByInertia = False
params.filterByConvexity = False

detector = cv.SimpleBlobDetector_create(params)


# create all needed array for saving the temporary data
caps = []
coordinates = []
blobs = []
xCoordinates = []
yCoordinates = []


# loop to load, manipulate and analyze the frames

current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r'binary')
if not os.path.exists(final_directory):
   os.makedirs(final_directory)

# Setup cropping Points

points = []

_, mask = cap.read(1)

while len(points) < 2:  # Schleifenkonstrukt, damit das Fenster automatisch schließt

  def set_points(event, x, y, flags, params):  # Erfasst Druecken und Loslassen, um Kasten aufzuziehen
    if event == cv.EVENT_LBUTTONDOWN:
      points.append((x, y))

    if event == cv.EVENT_LBUTTONUP:
      points.append((x, y))


  cv.imshow("Maske aufziehen", mask)

  cv.moveWindow("Maske aufziehen", 100, 20)
  cv.setMouseCallback("Maske aufziehen", set_points)
  cv.waitKey(1)

cv.destroyWindow("Maske aufziehen")


# Einzelne Frames croppen, umwandlen und auswerten

def progress(count, total, status=''):
  bar_len = 60
  filled_len = int(round(bar_len * count / float(total)))

  percents = round(100.0 * count / float(total), 1)
  bar = '>' * filled_len + '-' * (bar_len - filled_len)

  sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
  sys.stdout.flush()


for i in range (200, lenCap-200, 4): #lenCap-2
  progress(i, lenCap-10, status="finished")

  # load first frame, convert into HSV room, thresholding the v plane and save binary in caps array
  success, image = cap.read()
  hsvImage = cv.cvtColor(image, cv.COLOR_BGR2HSV)
  h, s, v = hsvImage[:, :, 0], hsvImage[:, :, 1], hsvImage[:, :, 2]
  #th, binaryCap = cv.adaptiveThreshold(v, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C) #127
  th, binaryCap = cv.threshold(v, inputThresh, 255, cv.THRESH_BINARY_INV)  # 127
  binaryCap = binaryCap[points[0][1]:points[1][1], points[0][0]:points[1][0]]
  caps.append(binaryCap)

  # detect keypoints in binary, mark keypoints, save binary with keypoints and save keypoints in coordinates array
  keypoints = detector.detect(binaryCap)
  imKeypoints = cv.drawKeypoints(binaryCap, keypoints, np.array([]), (0, 0, 255),
                                 cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
  keypoints.sort(key=lambda keypoint: pow(keypoint.pt[0], 2) + pow(keypoint.pt[1], 2))

  coordinates.append(keypoints)
  blobs.append(len(keypoints))
  cv.imwrite("binary/frame%d.jpg" % i, imKeypoints)  # save frame as JPEG file

  #cv.imwrite("binary/frameV%d.jpg" % i, v)
  #cv.imwrite("binary/frameB%d.jpg" % i, binaryCap)

# loop for getting all x coordinates for all blobs of all frames
# xCoordinates includes a list of the x coordinates of all blobs in a frame, for all frames

for x in range(0, len(coordinates)):
  xCorCap = []
  yCorCap = []

  # x coordinates of all blobs in each frame
  for j in range(0, blobs[x]):
    xCor = coordinates[x][j].pt[0]
    xCorCap.append(xCor)
    yCor = coordinates[x][j].pt[1]
    yCorCap.append(yCor)

  xCoordinates.append(xCorCap)
  yCoordinates.append(yCorCap)

np.savetxt('x-Coordinates.txt', xCoordinates)
np.savetxt('y-Coordinates.txt', yCoordinates)


# Plot the x and y Coordinates of each blob over the Frames

capNumber = [] # List with increasing number for plotting

for x in range(0, len(coordinates)):
  capNumber.append(x+1)

xAxis = capNumber
yAxis = xCoordinates
y1Axis = yCoordinates

fig, axs = plt.subplots(2)

axs[0].plot(xAxis, yAxis)
axs[0].set_title('Transversal (0 linker Bildrand)')

axs[1].plot(xAxis, y1Axis)
axs[1].set_title('Axial (0 oberer Bildrand)')

for ax in axs.flat:
  ax.set(xlabel='Frames', ylabel='Centroid Koordinate [Px]')

for ax in axs.flat:
  ax.label_outer()

plt.savefig("plot-Pos.png")
#plt.show()

print("\r")


# Converting Lists into Arrays and Calculating and Plotting the Movement of all Centroids

firstLineX = np.array(xCoordinates[0])
firstLineY = np.array(yCoordinates[0])

xCoordinatesRel = np.array(xCoordinates)-firstLineX
yCoordinatesRel = np.array(yCoordinates)-firstLineY

xAxisRel = capNumber
yAxisRel = xCoordinatesRel
y1AxisRel = yCoordinatesRel

figRel, axs = plt.subplots(2)

axs[0].plot(xAxisRel, yAxisRel)
axs[0].set_title('Transversal')
axs[0].set_ylim([-2,-4])
axs[0].axhline(y=0, linewidth=1, color='k')

axs[1].plot(xAxisRel, y1AxisRel)
axs[1].set_title('Axial')
#axs[1].set_ylim([-10,-4])
axs[1].axhline(y=0, linewidth=1, color='k')

for ax in axs.flat:
  ax.set(xlabel='Frames', ylabel='Centroid Verschiebung [Px]')

for ax in axs.flat:
  ax.label_outer()

plt.savefig("plot-Ver.png")


# Berechnung des Poisson-Verhältnisses 
# Plotten der Poissonverhältnisse abhängig vom axialen Weg der Metamaterialien

