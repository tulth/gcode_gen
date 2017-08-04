import matplotlib.pyplot as plt
from .. import iter_util


def poly_plot(poly, show=True, figure=True, color='r', title=None):
    if figure:
        plt.figure()
    if title is not None:
        plt.title(title)
    for edge in poly.get_edges():
        x_points = [point[0] for point in edge]
        y_points = [point[1] for point in edge]
        plt.plot(x_points, y_points, marker='o', color=color, ls='-')
    plt.grid()
    # plt.axis(vertex.getScaledBounds(poly.vertices).flatten())
    plt.axes().set_aspect('equal')
    if show:
        plt.show()


def plot_poly_and_fill_lines(poly, fill_result, show=True, figure=True, colors='krg', title=None):
    if figure:
        plt.figure()
    if title is not None:
        plt.title(title)
    for edge in poly.get_edges():
        x_points = [point[0] for point in edge]
        y_points = [point[1] for point in edge]
        plt.plot(x_points, y_points, marker='o', color=colors[0], ls='-', markersize=10)
    points = fill_result[0]
    is_cuts = fill_result[1]
    print(points)
    print(is_cuts)
    sequence = zip(points, is_cuts)
    for (p0, is_cut0), (p1, is_cut1) in iter_util.pairwise_iter(sequence):
        x_vals = [point.x for point in (p0, p1)]
        y_vals = [point.y for point in (p0, p1)]
        # print('p' * 40)
        # print(x_vals, y_vals)
        if is_cut1:
            plt.plot(x_vals, y_vals, marker='x', color=colors[1], ls='-')
        else:
            plt.plot(x_vals, y_vals, marker='s', color=colors[2], ls='-')
    plt.grid()
    # plt.axis(vertex.getScaledBounds(poly.vertices).flatten())
    plt.axes().set_aspect('equal')
    if show:
        plt.show()
