import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import quaternion  # Requires 'numpy-quaternion' package


def setup_figure():
    fig = plt.figure(figsize=(10, 8), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    lim = (-1.5, 1.5)
    ax.set(xlim=lim, ylim=lim, zlim=lim,
           title='Combined Quaternion Rotation')

    ax.view_init(elev=25, azim=45)
    return fig, ax


def create_geometry():
    theta = np.linspace(0, 2 * np.pi, 100)
    x, y = np.cos(theta), np.sin(theta)
    return [
        np.column_stack((x, y, np.zeros_like(x))),     # XY plane
        np.column_stack((np.zeros_like(x), x, y)),     # YZ plane
        np.column_stack((x, np.zeros_like(x), y))      # XZ plane
    ]


def initialize_artists(ax):
    colors = ['r', 'g', 'b']
    return [ax.plot([], [], [], f'{c}-', linewidth=2, alpha=0.8)[0] for c in colors]


class CombinedQuaternionRotator:
    def __init__(self):
        self.speeds = np.array([0.03, 0.02, 0.04])
        self.angles = np.zeros(3)

    def update_rotations(self):
        self.angles += self.speeds

        cos_angles = np.cos(self.angles / 2)
        sin_angles = np.sin(self.angles / 2)

        q_x = np.quaternion(cos_angles[0], sin_angles[0], 0, 0)
        q_y = np.quaternion(cos_angles[1], 0, sin_angles[1], 0)
        q_z = np.quaternion(cos_angles[2], 0, 0, sin_angles[2])

        q_combined = q_z * q_y * q_x
        return q_combined.normalized()


def update(frame, rotator, rings, artists):
    q_combined = rotator.update_rotations()

    for artist, ring in zip(artists, rings):
        rotated = quaternion.rotate_vectors(q_combined, ring)
        artist.set_data(rotated[:, :2].T)
        artist.set_3d_properties(rotated[:, 2])

    return artists


def main():
    fig, ax = setup_figure()
    rings = create_geometry()
    artists = initialize_artists(ax)
    rotator = CombinedQuaternionRotator()

    ani = FuncAnimation(
        fig, update, frames=200,
        fargs=(rotator, rings, artists),
        interval=20, blit=False  # blit=False for 3D animations
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
