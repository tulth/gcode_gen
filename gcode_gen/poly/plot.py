import matplotlib.pyplot as plt


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


def plot_poly_and_fill_lines(poly, cuts, jogs, show=True, figure=True, colors='krg', title=None):
    if figure:
        plt.figure()
    if title is not None:
        plt.title(title)
    for edge in poly.get_edges():
        x_points = [point[0] for point in edge]
        y_points = [point[1] for point in edge]
        plt.plot(x_points, y_points, marker='o', color=colors[0], ls='-', markersize=10)
    for cut in cuts:
        x_points = [point.x for point in cut]
        y_points = [point.y for point in cut]
        plt.plot(x_points, y_points, marker='x', color=colors[1], ls='-')
    for jog in jogs:
        x_points = [point.x for point in jog]
        y_points = [point.y for point in jog]
        plt.plot(x_points, y_points, marker='s', color=colors[2], ls='-')
    plt.grid()
    # plt.axis(vertex.getScaledBounds(poly.vertices).flatten())
    plt.axes().set_aspect('equal')
    if show:
        plt.show()


def plot_fill_line(edges, segments, show=True, figure=True, colors='br', title=None):
    if figure:
        plt.figure()
    if title is not None:
        plt.title(title)
    for edge in edges:
        x_points = [point.x for point in (edge.p0, edge.p1)]
        y_points = [point.y for point in (edge.p0, edge.p1)]
        plt.plot(x_points, y_points, marker='o', color=colors[0], ls='-')
    print(segments)
    for segment in segments:
        x_points = [point[0] for point in segment]
        y_points = [point[1] for point in segment]
        plt.plot(x_points, y_points, marker='x', color=colors[1], ls='-')
    plt.grid()
    # plt.axis(vertex.getScaledBounds(poly.vertices).flatten())
    plt.axes().set_aspect('equal')
    if show:
        plt.show()

