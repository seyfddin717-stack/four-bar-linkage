"""Planar four-bar linkage: position analysis, Grashof check, transmission angle."""
import numpy as np


def grashof_type(ground, crank, coupler, rocker):
    """Classify a four-bar linkage with the Grashof condition (s + l <= p + q)."""
    links = {"ground": ground, "crank": crank, "coupler": coupler, "rocker": rocker}
    s, p, q, l = sorted(links.values())
    if s + l > p + q:
        return "non-Grashof (triple-rocker)"
    shortest = min(links, key=links.get)
    if shortest == "crank":
        return "Grashof crank-rocker"
    if shortest == "ground":
        return "Grashof double-crank (drag link)"
    if shortest == "coupler":
        return "Grashof double-rocker"
    return "Grashof rocker-crank"


def solve_position(theta2, ground, crank, coupler, rocker, branch=1):
    """Return joints O2, O4, A, B for the crank angle theta2 (radians).

    O2 = (0, 0) and O4 = (ground, 0). Joint A is on the crank, joint B is the
    intersection of a circle around A (radius = coupler) and a circle around
    O4 (radius = rocker). branch = +1 or -1 selects the assembly configuration.
    Returns None if the linkage cannot be assembled at this angle.
    """
    o2 = np.array([0.0, 0.0])
    o4 = np.array([ground, 0.0])
    a = np.array([crank * np.cos(theta2), crank * np.sin(theta2)])

    d = np.linalg.norm(o4 - a)
    if d > coupler + rocker or d < abs(coupler - rocker) or d == 0:
        return None
    x = (coupler**2 - rocker**2 + d**2) / (2 * d)
    h = np.sqrt(max(coupler**2 - x**2, 0.0))
    u = (o4 - a) / d
    n = np.array([-u[1], u[0]])
    b = a + x * u + branch * h * n
    return o2, o4, a, b


def coupler_point(a, b, dist, angle):
    """Point attached to the coupler: dist from A, at angle (rad) from the A->B line."""
    ab = b - a
    base = np.arctan2(ab[1], ab[0])
    return a + dist * np.array([np.cos(base + angle), np.sin(base + angle)])


def transmission_angle(a, b, o4):
    """Angle (deg, 0-90) between coupler and rocker at joint B."""
    v1 = a - b
    v2 = o4 - b
    cosang = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    ang = np.degrees(np.arccos(np.clip(cosang, -1, 1)))
    return min(ang, 180 - ang)
