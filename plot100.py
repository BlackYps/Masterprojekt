import os

import matplotlib.pyplot as plt
import numpy as np


def plot_dehnungen(y_limit, filename, path):
    dehnungen_horizontal = np.loadtxt(os.path.join(path, 'dehnungen_horizontal.txt'))
    dehnungen_vertikal = np.loadtxt(os.path.join(path, 'dehnungen_vertikal.txt'))
    frame_number = np.arange(len(dehnungen_vertikal))

    xAxis = frame_number / 28
    yAxis = dehnungen_horizontal * 100
    y1Axis = dehnungen_vertikal * 100

    fontsize = 14   #font size for axis ticks and legend

    font = {'family': 'sans-serif',
            'weight': 600,
            'size': 16,
            }
    plt.rcParams["legend.loc"] = 'lower left'

    plt.rcParams['axes.prop_cycle'] = plt.cycler(
        color=['brown', 'salmon', 'orange', 'teal', 'turquoise', 'lightblue', 'gold'])

    if yAxis.shape[1] == 2:
        plt.rcParams['axes.prop_cycle'] = plt.cycler(
            color=['brown', 'salmon', 'teal', 'turquoise', 'lightblue', 'darkgreen'])
        fig, ax = plt.subplots()
        ax.plot(xAxis, yAxis, label=['transversal oben', 'transversal unten'])
    elif yAxis.shape[1] == 4:
        plt.rcParams['axes.prop_cycle'] = plt.cycler(
            color=['brown', 'salmon', 'orange', 'gold', 'teal', 'turquoise', 'lightblue'])
        fig, ax = plt.subplots()
        ax.plot(xAxis, yAxis, label=['transversal oben', 'transv. mitte oben', 'transv. mitte unten', 'transversal unten'])
    else:
        fig, ax = plt.subplots()
        ax.plot(xAxis, yAxis, label=['transversal oben', 'transversal mitte', 'transversal unten'])

    if y1Axis.shape[1] == 2:
        ax.plot(xAxis, y1Axis, label=['axial links', 'axial rechts'])
    else:
        ax.plot(xAxis, y1Axis, label=['axial links', 'axial mitte', 'axial rechts'])

    ax.set_ylim(y_limit)
    ax.label_outer()
    ax.axhline(y=0, linewidth=1, color='k')
    ax.legend(prop={"size":fontsize})
    ax.margins(0.02)
    ax.set_xlim(left=0)
    ax.tick_params(axis='both', which='major', labelsize=fontsize)
    ax.tick_params(axis='both', which='minor', labelsize=fontsize)
    plt.xlabel('Zeit (s)', fontdict=font)
    plt.ylabel('Relative Dehnung (%)', fontdict=font)
    plt.subplots_adjust(left=0.17, right=0.95)
    plt.savefig(os.path.join(path, filename))


def batch_plot(y_limit, filename):
    current_directory = os.getcwd()
    for path, dirs, files in os.walk(current_directory):
        try:
            plot_dehnungen(y_limit, filename, path)
        except IOError:
            pass


if __name__ == '__main__':
    batch_plot([-0.4, 0.25], "plot-Dehnung-100.png")
