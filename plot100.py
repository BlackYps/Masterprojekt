import matplotlib.pyplot as plt
import numpy as np


def plot_dehnungen(y_limit, filename):
    dehnungen_horizontal = np.loadtxt('dehnungen_horizontal.txt')
    dehnungen_vertikal = np.loadtxt('dehnungen_vertikal.txt')
    frame_number = np.arange(len(dehnungen_vertikal))

    xAxis = frame_number / 50
    yAxis = dehnungen_horizontal * 100
    y1Axis = dehnungen_vertikal * 100

    font = {'family': 'sans-serif',
            'weight': 600,
            'size': 10,
            }

    plt.rcParams['axes.prop_cycle'] = plt.cycler(
        color=['brown', 'salmon', 'orange', 'teal', 'turquoise', 'lightblue', 'gold'])

    fig, ax = plt.subplots()

    if yAxis.shape[1] == 2:
        ax.plot(xAxis, yAxis, label=['transversal oben', 'transversal unten'])
        plt.rcParams['axes.prop_cycle'] = plt.cycler(
            color=['brown', 'salmon', 'teal', 'turquoise', 'lightblue', 'darkgreen'])
    else:
        ax.plot(xAxis, yAxis, label=['transversal oben', 'transversal mitte', 'transversal unten'])

    if y1Axis.shape[1] == 2:
        ax.plot(xAxis, y1Axis, label=['axial links', 'axial rechts'])
    else:
        ax.plot(xAxis, y1Axis, label=['axial links', 'axial mitte', 'axial rechts'])

    ax.set_ylim(y_limit)
    ax.label_outer()
    ax.axhline(y=0, linewidth=1, color='k')
    ax.legend()
    ax.margins(0.02)
    ax.set_xlim(left=0)
    plt.xlabel('Zeit (s)', fontdict=font)
    plt.ylabel('Relative Dehnung (%)', fontdict=font)
    plt.subplots_adjust(left=0.17, right=0.95)
    plt.savefig(filename)


plot_dehnungen([-1.5, 0.5], "plot-Dehnung-100.png")
