import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import quaternion


def setup_figure():
    fig = plt.figure(figsize=(10, 8), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    lim = (-1.5, 1.5)
    ax.set(xlim=lim, ylim=lim, zlim=lim,
           title='Rings with Perpendicular Spinning Axes')
    ax.view_init(elev=25, azim=45)
    return fig, ax


def create_geometry():
    theta = np.linspace(0, 2*np.pi, 100)
    x, y = np.cos(theta), np.sin(theta)

    rings = [
        np.column_stack((x, y, np.zeros_like(x))),  # XY plane (red)
        np.column_stack((np.zeros_like(x), x, y)),  # YZ plane (green)
        np.column_stack((x, np.zeros_like(x), y))   # XZ plane (blue)
    ]

    # Axes exactly matching plot limits
    axes = [
        np.array([[0, 0, -1.5], [0, 0, 1.5]]),  # Z-axis
        np.array([[-1.5, 0, 0], [1.5, 0, 0]]),  # X-axis
        np.array([[0, -1.5, 0], [0, 1.5, 0]])   # Y-axis
    ]

    return rings, axes


def initialize_artists(ax):
    colors = ['r', 'g', 'b']
    # Thicker solid lines for rings (linewidth=2.5)
    ring_artists = [
        ax.plot([], [], [], f'{c}-', linewidth=2.5, alpha=0.8)[0] for c in colors]
    # Thinner solid lines for axes (linewidth=1.2)
    axis_artists = [
        ax.plot([], [], [], f'{c}-', linewidth=1.2, alpha=0.8)[0] for c in colors]
    return ring_artists, axis_artists


class CombinedQuaternionRotator:
    def __init__(self):
        self.speeds = np.array([0.03, 0.02, 0.04])
        self.angles = np.zeros(3)

    def update_rotations(self):
        self.angles += self.speeds
        cos_angles = np.cos(self.angles/2)
        sin_angles = np.sin(self.angles/2)

        q_x = np.quaternion(cos_angles[0], sin_angles[0], 0, 0)
        q_y = np.quaternion(cos_angles[1], 0, sin_angles[1], 0)
        q_z = np.quaternion(cos_angles[2], 0, 0, sin_angles[2])

        return (q_z * q_y * q_x).normalized()


def update(frame, rotator, rings, axes, ring_artists, axis_artists):
    q_combined = rotator.update_rotations()

    for r_artist, ring in zip(ring_artists, rings):
        rotated = quaternion.rotate_vectors(q_combined, ring)
        r_artist.set_data(rotated[:, :2].T)
        r_artist.set_3d_properties(rotated[:, 2])

    for a_artist, axis in zip(axis_artists, axes):
        rotated = quaternion.rotate_vectors(q_combined, axis)
        a_artist.set_data(rotated[:, :2].T)
        a_artist.set_3d_properties(rotated[:, 2])

    return ring_artists + axis_artists


def main():
    fig, ax = setup_figure()
    rings, axes = create_geometry()
    ring_artists, axis_artists = initialize_artists(ax)
    rotator = CombinedQuaternionRotator()

    ani = FuncAnimation(
        fig, update, frames=200,
        fargs=(rotator, rings, axes, ring_artists, axis_artists),
        interval=20, blit=False
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
