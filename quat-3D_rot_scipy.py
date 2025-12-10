import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.spatial.transform import Rotation as R


def setup_figure():
    fig = plt.figure(figsize=(10, 8), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    lim = (-1.5, 1.5)
    ax.set(xlim=lim, ylim=lim, zlim=lim,
           xlabel='X', ylabel='Y', zlabel='Z',
           title='Combined Intrinsic Rotations (X → Y → Z)')
    ax.view_init(elev=25, azim=45)
    return fig, ax


def create_geometry():
    """Create three unit circles lying in the XY, YZ and XZ planes."""
    theta = np.linspace(0, 2 * np.pi, 200)
    c, s = np.cos(theta), np.sin(theta)

    ring_xy = np.column_stack((c, s, np.zeros_like(theta)))   # XY plane (red)
    ring_yz = np.column_stack((np.zeros_like(theta), c, s))   # YZ plane (green)
    ring_xz = np.column_stack((c, np.zeros_like(theta), s))   # XZ plane (blue)

    return [ring_xy, ring_yz, ring_xz]


def initialize_artists(ax):
    colors = ['tab:red', 'tab:green', 'tab:blue']
    lines = []
    for color in colors:
        line, = ax.plot([], [], [], color=color, lw=2.5)
        lines.append(line)
    return lines


class CombinedRotator:
    def __init__(self):
        # Angular velocities (radians per frame) for X, Y, Z rotations
        self.speeds = np.array([0.03, 0.02, 0.04])
        self.angles = np.zeros(3)               # current angles

    def update(self):
        """Increment angles and return the combined rotation (intrinsic z-y-x)."""
        self.angles += self.speeds

        # Create individual rotations (intrinsic means body-fixed)
        rot_x = R.from_euler('x', self.angles[0])
        rot_y = R.from_euler('y', self.angles[1])
        rot_z = R.from_euler('z', self.angles[2])

        # Combine in the order: first X, then Y, then Z (intrinsic z-y-x)
        combined = rot_z * rot_y * rot_x
        return combined


def animation_update(frame, rotator, rings, artists):
    combined_rot = rotator.update()

    for ring, artist in zip(rings, artists):
        rotated_points = combined_rot.apply(ring)
        artist.set_data(rotated_points[:, 0], rotated_points[:, 1])
        artist.set_3d_properties(rotated_points[:, 2])

    return artists


def main():
    fig, ax = setup_figure()
    rings = create_geometry()
    artists = initialize_artists(ax)

    rotator = CombinedRotator()

    ani = FuncAnimation(fig,
                        animation_update,
                        frames=1000,           # practically infinite
                        fargs=(rotator, rings, artists),
                        interval=30,            # ~33 fps
                        blit=False)             # 3D plots don't support blitting well

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
