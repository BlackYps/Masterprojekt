# Point Tracking Algorithm for Master Project Thesis WiSe 2020/2021
# University of Bremen, Department of Mechanical Engineering
# Master Project Thesis Title: "Deformation capabilities of mechanical meta Materials"

# Created on 13th of March 2021
# Author: Mika León Altmann, B.Sc., m.altmann@uni-bremen.de

# Update History
# 13th of April 2021: Cropping, Progressbar
# 14th of April 2021: Threshold Input, Plots for Movement and Position


import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import os
import sys


def confirm(prompt=None):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.
    """

    if prompt is None:
        prompt = 'Confirm'
    prompt = '%s %s/%s: ' % (prompt, 'y', 'n')

    while True:
        answer = input(prompt)
        if answer not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if answer == 'y' or answer == 'Y':
            return True
        if answer == 'n' or answer == 'N':
            return False


def distance(keypoint, origin):
    return pow(keypoint.pt[0] - origin[0], 2) + pow(keypoint.pt[1] - origin[1], 2)


print("\r")

print("Please set a Threshold Value between 0 and 255: ")
inputThresh = int(input())

print("\r")

# load video file and get number of frames
video = cv.VideoCapture('video.avi')
videoLength = int(video.get(cv.CAP_PROP_FRAME_COUNT))

# Set up Detector for Blob Detection

params = cv.SimpleBlobDetector_Params()

params.filterByColor = True
params.blobColor = 0
params.filterByArea = True
params.filterByInertia = False
params.filterByConvexity = False

detector = cv.SimpleBlobDetector_create(params)

current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r'binary')
if not os.path.exists(final_directory):
    os.makedirs(final_directory)


def set_up_cropping_points_by_user():
    try:
        points = np.loadtxt('croppingPoints.txt', int)
        confirmation = confirm("Use croppings points from last time?")
        if confirmation:
            croppingPoints.extend(points)
            return
    except IOError:
        pass

    def set_croppingpoints(event, x, y, flags, params):  # Erfasst Druecken und Loslassen, um Kasten aufzuziehen
        if event == cv.EVENT_LBUTTONDOWN:
            croppingPoints.append((x, y))

        if event == cv.EVENT_LBUTTONUP:
            croppingPoints.append((x, y))

    _, mask = video.read(1)
    while len(croppingPoints) < 2:  # Schleifenkonstrukt, damit das Fenster automatisch schließt
        cv.imshow("Maske aufziehen", mask)
        cv.moveWindow("Maske aufziehen", 100, 20)
        cv.setMouseCallback("Maske aufziehen", set_croppingpoints)
        cv.waitKey(1)
    cv.destroyWindow("Maske aufziehen")
    np.savetxt('croppingPoints.txt', croppingPoints, "%1i")


def set_up_origin_by_user():
    try:
        points = np.loadtxt('origin.txt', int)
        confirmation = confirm("Use origin from last time? Caution! Origin is relative to cropped area.")
        if confirmation:
            origin.extend(points)
            return
    except IOError:
        pass

    def set_origin(event, x, y, flags, params):
        if event == cv.EVENT_LBUTTONDOWN:
            origin.extend([x, y])

    _, mask = video.read(1)
    while len(origin) < 1:
        cv.imshow("Punkt fuer Sortierung nach Abstand festlegen", mask)
        cv.moveWindow("Punkt fuer Sortierung nach Abstand festlegen", 100, 20)
        cv.setMouseCallback("Punkt fuer Sortierung nach Abstand festlegen", set_origin)
        cv.waitKey(1)
    cv.destroyWindow("Punkt fuer Sortierung nach Abstand festlegen")
    origin[0] -= croppingPoints[0][0]
    origin[1] -= croppingPoints[0][1]
    np.savetxt('origin.txt', origin, "%1i")


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '>' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


croppingPoints = []
origin = []

set_up_cropping_points_by_user()
set_up_origin_by_user()

caps = []
keypointsList = []
numberOfDetectedPoints = 0

for root, dirs, files in os.walk(final_directory):
    for file in files:
        os.remove(os.path.join(root, file))

for i in range(200, videoLength - 200, 4):  # lenCap-2
    progress(i, videoLength - 10, status="finished")

    # load first frame, convert into HSV room, thresholding the v plane and save binary in caps array
    success, image = video.read()
    hsvImage = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    h, s, v = hsvImage[:, :, 0], hsvImage[:, :, 1], hsvImage[:, :, 2]
    # alternative threshold method for local separation (Inversion of binary needed):
    # th, binaryCap = cv.adaptiveThreshold(v, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C)
    th, binaryImage = cv.threshold(v, inputThresh, 255, cv.THRESH_BINARY_INV)
    binaryImage = binaryImage[croppingPoints[0][1]:croppingPoints[1][1], croppingPoints[0][0]:croppingPoints[1][0]]

    keypoints = detector.detect(binaryImage)
    imageKeypoints = cv.drawKeypoints(binaryImage, keypoints, np.array([]), (0, 0, 255),
                                      cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    keypoints.sort(key=lambda keypoint: distance(keypoint, origin))
    for index, point in enumerate(keypoints):
        color = (max(255 - (index * 30), 0), min(index * 30, 255), 0)
        cv.line(imageKeypoints, tuple(map(int, point.pt)), tuple(map(int, keypoints[max(index-1, 0)].pt)), color, 2)
    keypointsList.append(keypoints)

    if i > 200 and numberOfDetectedPoints != len(keypoints):
        raise Exception("Number of detected keypoints is not consistent. Detected {} last frame, detected {} now.".format(
                        numberOfDetectedPoints, len(keypoints)))
    numberOfDetectedPoints = len(keypoints)
    cv.imwrite("binary/frame%d.jpg" % i, imageKeypoints)

# loop for getting all x coordinates for all blobs of all frames
# xCoordinates includes a list of the x coordinates of all blobs in a frame, for all frames

xCoordinates = []
yCoordinates = []

for frame in range(0, len(keypointsList)):
    xCoordinatesForFrame = []
    yCoordinatesForFrame = []

    for point in range(0, numberOfDetectedPoints):
        keypointXCoordinates = keypointsList[frame][point].pt[0]
        xCoordinatesForFrame.append(keypointXCoordinates)
        keypointYCoordinates = keypointsList[frame][point].pt[1]
        yCoordinatesForFrame.append(keypointYCoordinates)

    xCoordinates.append(xCoordinatesForFrame)
    yCoordinates.append(yCoordinatesForFrame)

np.savetxt('x-Coordinates.txt', xCoordinates)
np.savetxt('y-Coordinates.txt', yCoordinates)

# Plot the x and y Coordinates of each blob over the Frames

capNumber = []  # List with increasing number for plotting

for frame in range(0, len(keypointsList)):
    capNumber.append(frame + 1)

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
# plt.show()

print("\r")

# Converting Lists into Arrays and Calculating and Plotting the Movement of all Centroids

firstLineX = np.array(xCoordinates[0])
firstLineY = np.array(yCoordinates[0])

xCoordinatesRel = np.array(xCoordinates) - firstLineX
yCoordinatesRel = np.array(yCoordinates) - firstLineY

xAxisRel = capNumber
yAxisRel = xCoordinatesRel
y1AxisRel = yCoordinatesRel

figRel, axs = plt.subplots(2)

axs[0].plot(xAxisRel, yAxisRel)
axs[0].set_title('Transversal')
# axs[0].set_ylim([-2, -4])
axs[0].axhline(y=0, linewidth=1, color='k')

axs[1].plot(xAxisRel, y1AxisRel)
axs[1].set_title('Axial')
# axs[1].set_ylim([-10,-4])
axs[1].axhline(y=0, linewidth=1, color='k')

for ax in axs.flat:
    ax.set(xlabel='Frames', ylabel='Centroid Verschiebung [Px]')

for ax in axs.flat:
    ax.label_outer()

plt.savefig("plot-Ver.png")

# TODO Berechnung des Poisson-Verhältnisses
# TODO Plotten der Poissonverhältnisse abhängig vom axialen Weg der Metamaterialien
