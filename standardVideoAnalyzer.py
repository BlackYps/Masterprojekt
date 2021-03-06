# Point Tracking Algorithm for Master Project Thesis WiSe 2020/2021
# University of Bremen, Department of Mechanical Engineering
# Master Project Thesis Title: "Deformation capabilities of mechanical meta Materials"

# Created on 13th of March 2021
# Authors: Mika León Altmann, B.Sc., m.altmann@uni-bremen.de
#                Jonas Brill, B.Sc., jobr@uni-bremen.de

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


def set_up_cropping_points_by_user(video):
    croppingPoints = []
    try:
        points = np.loadtxt('croppingPoints.txt', int)
        confirmation = confirm("Use croppings points from last time?")
        if confirmation:
            croppingPoints.extend(points)
            return croppingPoints
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
    return croppingPoints


def set_up_origin_by_user(video, croppingPoints):
    origin = []
    try:
        points = np.loadtxt('origin.txt', int)
        confirmation = confirm("Use origin from last time? Caution! Origin is relative to cropped area.")
        if confirmation:
            origin.extend(points)
            return origin
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
    return origin


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '>' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def set_point_location_by_user():
    try:
        points = np.loadtxt('point_location.txt', int)
        confirmation = confirm("Use point order from last time?")
        if confirmation:
            point_location = np.array(points)
            return point_location
    except IOError:
        pass

    prompt = "Type the location of the points in a matrix-like fashion." \
             "(E.g for three rows and two columns it could be: 0 1; 3 2; 4 5).  "
    matrix = input(prompt)
    point_location = np.array(np.mat(matrix))
    np.savetxt('point_location.txt', point_location, "%1i")
    return point_location


def set_up_detector_for_blob_detection():
    params = cv.SimpleBlobDetector_Params()
    params.filterByColor = True
    params.blobColor = 0
    params.filterByArea = True
    params.filterByInertia = False
    params.filterByConvexity = False
    return cv.SimpleBlobDetector_create(params)


def detect_keypoints(final_directory, video, croppingPoints, origin, detector, inputThresh):
    videoLength = int(video.get(cv.CAP_PROP_FRAME_COUNT))
    keypointsList = []
    numberOfDetectedPoints = 0

    for root, dirs, files in os.walk(final_directory):
        for file in files:
            os.remove(os.path.join(root, file))

    for i in range(0, videoLength - 200):  # lenCap-2
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
            cv.line(imageKeypoints, tuple(map(int, point.pt)), tuple(map(int, keypoints[max(index - 1, 0)].pt)), color,
                    2)
        keypointsList.append(keypoints)

        if i > 0 and numberOfDetectedPoints != len(keypoints):
            raise Exception(
                "Number of detected keypoints is not consistent. Detected {} last frame, detected {} now.".format(
                    numberOfDetectedPoints, len(keypoints)))
        numberOfDetectedPoints = len(keypoints)
        cv.imwrite("binary/frame%d.jpg" % i, imageKeypoints)
    print("\r")
    return keypointsList


def write_coordinates_and_dehnungen(keypointsList):
    xCoordinates = []
    yCoordinates = []
    dehnungen_vertikal = []
    dehnungen_horizontal = []
    l_null_vertikal_list = []
    l_null_horizontal_list = []

    first_frame = cv.imread("binary/frame200.jpg")
    cv.imshow("Reihenfolge der Punkte von blau nach gruen", first_frame)
    cv.waitKey(1)
    point_location = set_point_location_by_user()
    cv.destroyWindow("Reihenfolge der Punkte von blau nach gruen")

    for column in point_location.transpose():
        l_null_vertikal_list.append(keypointsList[0][column[-1]].pt[1] - keypointsList[0][column[0]].pt[1])
    for row in point_location:
        l_null_horizontal_list.append(keypointsList[0][row[-1]].pt[0] - keypointsList[0][row[0]].pt[0])

    frame = 0
    total = len(keypointsList)
    for keypoints in keypointsList:
        progress((frame - 0), total, status="finished")
        xCoordinatesForFrame = []
        yCoordinatesForFrame = []
        dehnung_vertikal = []
        dehnung_horizontal = []
        image = cv.imread("binary/frame%d.jpg" % frame)

        for index, l_null_vertikal in enumerate(l_null_vertikal_list):
            dehnung_vertikal.append((keypoints[point_location[-1][index]].pt[1] -
                                     keypoints[point_location[0][index]].pt[1] - l_null_vertikal) / l_null_vertikal)
            # Graue Linen für vertikale Dehnung
            cv.line(image, tuple(map(int, keypoints[point_location[-1][index]].pt)),
                    tuple(map(int, keypoints[point_location[0][index]].pt)), (120, 120, 120), 2)
        for index, l_null_horizontal in enumerate(l_null_horizontal_list):
            dehnung_horizontal.append((keypoints[point_location[index][-1]].pt[0] -
                                       keypoints[point_location[index][0]].pt[
                                           0] - l_null_horizontal) / l_null_horizontal)
            # Gelbe Linen für horizontale Dehnung
            cv.line(image, tuple(map(int, keypoints[point_location[index][-1]].pt)),
                    tuple(map(int, keypoints[point_location[index][0]].pt)), (0, 255, 255), 2)

        cv.imwrite("binary/frame%d.jpg" % frame, image)
        frame += 1

        for point in keypoints:
            xCoordinatesForFrame.append(point.pt[0])
            yCoordinatesForFrame.append(point.pt[1])

        xCoordinates.append(xCoordinatesForFrame)
        yCoordinates.append(yCoordinatesForFrame)
        dehnungen_vertikal.append(dehnung_vertikal)
        dehnungen_horizontal.append(dehnung_horizontal)

    np.savetxt('x-Coordinates.txt', xCoordinates)
    np.savetxt('y-Coordinates.txt', yCoordinates)
    np.savetxt('dehnungen_vertikal.txt', dehnungen_vertikal)
    np.savetxt('dehnungen_horizontal.txt', dehnungen_horizontal)
    return xCoordinates, yCoordinates, dehnungen_vertikal, dehnungen_horizontal


def plot_positions(frame_number, xCoordinates, yCoordinates):
    xAxis = frame_number
    yAxis = xCoordinates
    y1Axis = yCoordinates

    fig, axs = plt.subplots(2)

    axs[0].plot(xAxis, yAxis)
    axs[0].set_title('Transversal (0 linker Bildrand)')

    axs[1].plot(xAxis, y1Axis)
    axs[1].set_title('Axial (0 oberer Bildrand)')

    for ax in axs.flat:
        ax.set(xlabel='Frames', ylabel='Centroid Koordinate [Px]')
        ax.label_outer()

    plt.savefig("plot-Pos.png")


def plot_movement(frame_number, xCoordinates, yCoordinates):
    firstLineX = np.array(xCoordinates[0])
    firstLineY = np.array(yCoordinates[0])

    xCoordinatesRel = np.array(xCoordinates) - firstLineX
    yCoordinatesRel = np.array(yCoordinates) - firstLineY
    xAxisRel = frame_number
    yAxisRel = xCoordinatesRel
    y1AxisRel = yCoordinatesRel

    figRel, axs = plt.subplots(2)

    axs[0].plot(xAxisRel, yAxisRel)
    axs[0].set_title('Transversal')
    # axs[0].set_ylim([-2, -4])

    axs[1].plot(xAxisRel, y1AxisRel)
    axs[1].set_title('Axial')
    # axs[1].set_ylim([-10,-4])

    for ax in axs.flat:
        ax.set(xlabel='Frames', ylabel='Centroid Verschiebung [Px]')
        ax.label_outer()
        ax.axhline(y=0, linewidth=1, color='k')

    plt.savefig("plot-Ver.png")


def plot_dehnungen(frame_number, dehnungen_vertikal, dehnungen_horizontal):
    xAxis = frame_number
    yAxis = dehnungen_horizontal
    y1Axis = dehnungen_vertikal

    fig, axs = plt.subplots(2)

    axs[0].plot(xAxis, yAxis)
    axs[0].set_title('Transversale Dehnung')

    axs[1].plot(xAxis, y1Axis)
    axs[1].set_title('Axiale Dehnung')

    for ax in axs.flat:
        ax.set(xlabel='Frames', ylabel='Relative Dehnung')
        ax.label_outer()
        ax.axhline(y=0, linewidth=1, color='k')

    plt.savefig("plot-Dehnung.png")


def plot_poisson(frame_number, dehnungen_vertikal, dehnungen_horizontal):
    poisson = (-1) * np.array(dehnungen_horizontal) / np.array(dehnungen_vertikal)
    xAxis = frame_number
    yAxis = poisson

    fig, ax = plt.subplots()
    ax.plot(xAxis, yAxis)
    ax.set_ylim([-1, 1])
    ax.set_title('Querkontraktionszahl')
    ax.set(xlabel='Frames', ylabel='Querkontraktionszahl')
    ax.label_outer()
    ax.axhline(y=0, linewidth=1, color='k')

    plt.savefig("plot-Poisson.png")


def main():
    print("\r")
    print("Please set a Threshold Value between 0 and 255: ")
    inputThresh = int(input())
    print("\r")

    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, r'binary')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)

    video = cv.VideoCapture('video.avi')
    croppingPoints = set_up_cropping_points_by_user(video)
    origin = set_up_origin_by_user(video, croppingPoints)
    detector = set_up_detector_for_blob_detection()

    keypointsList = detect_keypoints(final_directory, video, croppingPoints, origin, detector, inputThresh)
    xCoordinates, yCoordinates, dehnungen_vertikal, dehnungen_horizontal = write_coordinates_and_dehnungen(keypointsList)

    frame_number = []  # List with increasing number for plotting
    for frame in range(len(keypointsList)):
        frame_number.append(frame + 1)

    plot_positions(frame_number, xCoordinates, yCoordinates)
    plot_movement(frame_number, xCoordinates, yCoordinates)
    plot_dehnungen(frame_number, dehnungen_vertikal, dehnungen_horizontal)
    plot_poisson(frame_number, dehnungen_vertikal, dehnungen_horizontal)


main()
