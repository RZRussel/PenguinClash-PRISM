from math import *


def radial_moves(velocity):
    """
    Algorithm takes points which lies on the circle with given radius and step 1 degree.
    Than rounds their coordinates.
    will be thrown.
    :param velocity: target's movement velocity. Must be none negative otherwise type error will be thrown.
    :return: List of 360 (x, y) tuples
    """

    if velocity < 0:
        raise TypeError("Velocity must be none negative")

    positions = []
    for i in range(0, 360):
        x = round(velocity * cos(radians(i)))
        y = round(velocity * sin(radians(i)))

        positions.append((x, y))

    return positions


def rotate_position(position):
    """
    Algorithm takes position and generates all it's rotations around (0, 0)
    with 1 degree step. Final coordinates are rounded.
    :param position: (x, y) tuple
    :return: List of 360 (x, y) tuples
    """

    if type(position) != tuple or len(position) != 2:
        TypeError("Position must be valid 2d tuple")

    positions = []
    for i in range(0, 360):
        x = round(position[0]*cos(radians(i)) - position[1]*sin(radians(i)))
        y = round(position[0]*sin(radians(i)) + position[1]*cos(radians(i)))
        positions.append((x, y))

    return positions


def fading_velocities_list(friction, initial_velocity):
    """
    Calculates future velocities until stop for movement with friction. The list is
    nonincreasing.
    :param friction: float value
    :param initial_velocity: int value
    :return: List of int values
    """

    velocities = [initial_velocity]

    t = 1
    while velocities[-1] > 0:
        velocities.append(round(initial_velocity*exp(-t*friction)))
        t = t + 1

    return list(reversed(velocities))


def collision_offsets_for_circle_bodies(src_radius, src_velocity, dst_radius, dst_velocity):
    """
    Creates set of possible position offsets between two circle bodies when collision must be detected.
    :param src_radius: int radius of the first body
    :param src_velocity: int velocity of the first body
    :param dst_radius: int radius of the second body
    :param dst_velocity: int velocity of the second body
    :return: Set of (x, y) tuples
    """

    max_distance = src_radius + dst_radius
    min_distance = max_distance - (src_velocity + dst_velocity)

    offsets = set()
    for x in range(-max_distance, max_distance + 1):
        for y in range(-max_distance, max_distance + 1):
            if (x * x + y * y >= min_distance * min_distance) and (x * x + y * y <= max_distance * max_distance):
                offsets.add((x, y))

    return offsets


def reachable_points_from_ellipsis(center, a, b, velocity):
    """
    Creates a set of reachable points outside of the ellipsis from any which lies inside in one step.
    :param center: (x, y) ellipsis's center tuple
    :param a: ellipsis's vertical small radius. Must be not greater than b.
    :param b: ellipsis's horizontal big radius. Must be not less than a.
    :param velocity: distance in points to travel in one step.
    :return: Set of (x, y) tuples
    """

    moves = set(filter(lambda p: p[0] <= 0 and p[1] <= 0, radial_moves(velocity)))

    dead_points = set()

    for x in range(center[0] - b, center[0] + 1):
        for y in range(center[1] - a, center[1] + 1):
            for ox, oy in moves:
                if ellipsis_contains_position(center, a, b, (x, y)) \
                   and not ellipsis_contains_position(center, a, b, (x + ox, y + oy)):

                    dead_points.add((x + ox, y + oy))

                    if 2 * center[0] - x - ox != x + ox:
                        dead_points.add((2 * center[0] - x - ox, y + oy))

                    if 2 * center[1] - y - oy != y + oy:
                        dead_points.add((x + ox, 2 * center[0] - y - oy))

                    if 2 * center[0] - x - ox != x + ox and 2 * center[1] - y - oy != y + oy:
                        dead_points.add((2 * center[0] - x - ox, 2 * center[1] - y - oy))

    return dead_points


def ellipsis_contains_position(center, a, b, position):
    """
    Checks whether position lies inside ellipsis
    :param center: (x, y) tuple
    :param a: ellipsis's small radius int value. Must be not greater than b.
    :param b: ellipsis's big radius int value. Must be not less than a.
    :param position: (x, y) tuple
    :return: true if position lies inside ellipsis and false otherwise

    For example:
    >>> ellipsis_contains_position((368, 207), 50, 50, (350, 200))
    True
    >>> ellipsis_contains_position((368, 207), 50, 100, (200, 150))
    False
    >>> ellipsis_contains_position((368, 207), 50, 100, (368, 157))
    True
    """

    lf = (center[0] - sqrt(b*b - a*a), center[1])
    rf = (center[0] + sqrt(b*b - a*a), center[1])
    d1 = sqrt((lf[0] - position[0]) * (lf[0] - position[0]) + (lf[1] - position[1]) * (lf[1] - position[1]))
    d2 = sqrt((rf[0] - position[0]) * (rf[0] - position[0]) + (rf[1] - position[1]) * (rf[1] - position[1]))
    return d1 + d2 <= 2 * b


def reversed_direction(vector):
    """
    Calculates angle for the direction which is opposite to provided one
    :param vector: (x, y) vector which determines direction
    :return: int value in range 0..359

    For example:
    >>> reversed_direction((1, 1))
    225
    >>> reversed_direction((-1, 1))
    315
    >>> reversed_direction((0, -1))
    90
    """

    if vector[0] == 0:
        if vector[1] > 0:
            return 270
        else:
            return 90
    elif vector[0] > 0 and vector[1] >= 0:
        return 180 + round(atan(vector[1] / vector[0]) * 180 / pi)
    elif vector[0] > 0 and vector[1] < 0:
        return 180 - round(atan(-vector[1] / vector[0]) * 180 / pi)
    elif vector[0] < 0 and vector[1] > 0:
        return 360 - round(atan(vector[1] / -vector[0]) * 180 / pi) % 360
    elif vector[0] < 0 and vector[1] <= 0:
        return round(atan(-vector[1] / -vector[0]) * 180 / pi)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
