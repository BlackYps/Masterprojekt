import os

import matplotlib.pyplot as plt
import numpy as np


def plot_poisson(filename, path):
    dehnungen_horizontal = np.loadtxt(os.path.join(path, 'dehnungen_horizontal.txt'))
    dehnungen_vertikal = np.loadtxt(os.path.join(path, 'dehnungen_vertikal.txt'))
    frame_number = np.arange(len(dehnungen_vertikal))

    poisson = []

    dehnung_vertikal = np.average(dehnungen_vertikal, axis=1)
    dehnung_vertikal[dehnung_vertikal == 0] = 1.0
    for column in dehnungen_horizontal.T:
        p = (-1) * column / dehnung_vertikal
        p[np.isnan(p)] = 0
        movavg = moving_average(p, 301)

        poisson.append(np.concatenate((np.zeros(300), movavg)))

    xAxis = frame_number / 28
    yAxis = np.array(poisson).T
    y1Axis = np.average(np.array(poisson).T, axis=1)
    right_half = y1Axis[len(y1Axis) // 2:]
    poisson_average = np.average(right_half)
    print("poisson in right half of " + path + ": " + str(poisson_average))

    fontsize = 14  # font size for axis ticks and legend
    font = {'family': 'sans-serif',
            'weight': 600,
            'size': 16,
            }
    plt.rcParams['axes.prop_cycle'] = plt.cycler(
        color=['brown', 'salmon', 'orange', 'turquoise', 'lightblue', 'gold'])

    fig, ax = plt.subplots()
    ax.plot(xAxis, yAxis, label=['oben', 'mitte', 'unten'])
    ax.plot(xAxis, y1Axis, label='Mittelwert')
    ax.set_ylim([-1, 1])
    plt.xlabel('Zeit (s)', fontdict=font)
    plt.ylabel('Querkontraktionszahl', fontdict=font)
    ax.legend(prop={"size": fontsize})
    ax.label_outer()
    ax.tick_params(axis='both', which='major', labelsize=fontsize)
    ax.tick_params(axis='both', which='minor', labelsize=fontsize)
    ax.axhline(y=0, linewidth=1, color='k')
    plt.subplots_adjust(left=0.17, bottom=0.15)

    plt.savefig(os.path.join(path, filename))


def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def batch_plot(filename):
    current_directory = os.getcwd()
    for path, dirs, files in os.walk(current_directory):
        try:
            plot_poisson(filename, path)
        except IOError:
            pass


if __name__ == '__main__':
    batch_plot("poisson.png")
