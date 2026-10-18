import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from linkage import (grashof_type, solve_position, coupler_point,
                     transmission_angle)

# Link lengths (arbitrary units): crank-rocker example
GROUND, CRANK, COUPLER, ROCKER = 4.0, 1.0, 3.5, 3.0
P_DIST, P_ANGLE = 2.0, np.radians(30)   # coupler point position

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

print("Type:", grashof_type(GROUND, CRANK, COUPLER, ROCKER))

# Full crank rotation
angles = np.radians(np.arange(0, 360, 3))
frames = []
for th in angles:
    o2, o4, a, b = solve_position(th, GROUND, CRANK, COUPLER, ROCKER)
    p = coupler_point(a, b, P_DIST, P_ANGLE)
    mu = transmission_angle(a, b, o4)
    rocker_angle = np.degrees(np.arctan2(b[1] - o4[1], b[0] - o4[0]))
    frames.append((a, b, p, mu, rocker_angle))

trace = np.array([f[2] for f in frames])
mu_all = np.array([f[3] for f in frames])
rocker_all = np.array([f[4] for f in frames])
print(f"Min transmission angle: {mu_all.min():.1f} deg")
print(f"Max transmission angle: {mu_all.max():.1f} deg")
print(f"Rocker swing: {rocker_all.min():.1f} to {rocker_all.max():.1f} deg "
      f"({rocker_all.max() - rocker_all.min():.1f} deg)")

# Animation
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-3, 7)
ax.set_ylim(-4, 6)
ax.set_aspect("equal")
ax.grid(True)
ax.set_title("Four-bar linkage (crank-rocker)")
ax.plot(trace[:, 0], trace[:, 1], "r-", lw=1, label="coupler curve")
ax.legend(loc="lower left")
ax.plot([0, GROUND], [0, 0], "k-", lw=3)
crank_line, = ax.plot([], [], "o-", lw=4, color="tab:blue")
coupler_line, = ax.plot([], [], "o-", lw=4, color="tab:green")
rocker_line, = ax.plot([], [], "o-", lw=4, color="tab:orange")
point, = ax.plot([], [], "ro")


def update(i):
    a, b, p, _, _ = frames[i]
    crank_line.set_data([0, a[0]], [0, a[1]])
    coupler_line.set_data([a[0], b[0]], [a[1], b[1]])
    rocker_line.set_data([GROUND, b[0]], [0, b[1]])
    point.set_data([p[0]], [p[1]])
    return crank_line, coupler_line, rocker_line, point


anim = FuncAnimation(fig, update, frames=len(frames), interval=40)
anim.save(os.path.join(OUT, "fourbar.gif"), writer="pillow", fps=25)
plt.close(fig)

# Transmission angle and rocker angle plots
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
deg = np.degrees(angles)
ax1.plot(deg, mu_all)
ax1.axhline(40, color="r", ls="--", lw=1, label="40 deg guideline")
ax1.set_xlabel("Crank angle (deg)")
ax1.set_ylabel("Transmission angle (deg)")
ax1.set_title("Transmission angle")
ax1.grid(True)
ax1.legend(loc="lower center")
ax2.plot(deg, rocker_all)
ax2.set_xlabel("Crank angle (deg)")
ax2.set_ylabel("Rocker angle (deg)")
ax2.set_title("Rocker output angle")
ax2.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "analysis.png"), dpi=150)
plt.close(fig2)
