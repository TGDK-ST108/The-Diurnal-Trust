import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Wedge, Circle, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.animation as animation
from typing import List, Dict, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuadDoVisualizer:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_facecolor('#0a1a2a')  # Deep navy background
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        # Design elements
        self._draw_cone()
        self._draw_forescope()
        self._draw_tertiary_lattice()
        self._draw_tightscope()
        self._draw_centroid_tail_gate()
        self._draw_9_realms_ring()
        self._draw_bridge_nodes()
        self._add_legend()

        # Developer trace panel placeholder
        self.trace_text = self.ax.text(
            1.1, -1.8,
            "Developer Trace:\nWaiting for trajectory...",
            color='white', fontsize=8, ha='left'
        )

    def _draw_cone(self):
        """Draw the entry cone."""
        cone = Wedge((0, 2), 0.5, 180, 360, fc='none', ec='cyan', lw=1.5, alpha=0.7)
        self.ax.add_patch(cone)
        self.ax.text(0, 2.1, "Cone", color='cyan', ha='center', fontsize=10)

    def _draw_forescope(self):
        """Draw the forescope chamber."""
        forescope = Circle((0, 1.2), 0.4, fc='none', ec='cyan', lw=1.5, alpha=0.7)
        self.ax.add_patch(forescope)
        self.ax.text(0, 1.6, "Forescope", color='cyan', ha='center', fontsize=10)

    def _draw_tertiary_lattice(self):
        """Draw the rotating lattice helix."""
        theta = np.linspace(0, 2 * np.pi, 24)
        x = 0.4 * np.cos(theta)
        y = 0.4 * np.sin(theta)
        self.ax.plot(x, y, color='cyan', lw=1, alpha=0.5, label='Lattice')

        # Add lattice nodes
        for i, (xi, yi) in enumerate(zip(x, y)):
            self.ax.scatter(xi, yi, color='cyan', s=20, alpha=0.7)
            self.ax.text(xi, yi, f"L{i}", color='white', ha='center', fontsize=6)

    def _draw_tightscope(self):
        """Draw the tightscope chamber."""
        tightscope = Circle((0, -0.4), 0.3, fc='none', ec='cyan', lw=1.5, alpha=0.7)
        self.ax.add_patch(tightscope)
        self.ax.text(0, -0.1, "Tightscope", color='cyan', ha='center', fontsize=10)

    def _draw_centroid_tail_gate(self):
        """Draw the centroid and tail gate."""
        centroid = Circle((0, -1.2), 0.2, fc='magenta', ec='cyan', lw=1.5, alpha=0.8)
        self.ax.add_patch(centroid)
        self.ax.text(0, -1.45, "Centroid", color='white', ha='center', fontsize=10, fontweight='bold')

        # Tail gate glow
        tail_gate_glow = Circle((0, -1.2), 0.25, fc='magenta', ec='none', alpha=0.3)
        self.ax.add_patch(tail_gate_glow)
        self.ax.text(0, -1.7, "Tail Gate", color='white', ha='center', fontsize=10)

    def _draw_9_realms_ring(self):
        """Draw the 9 realms ring around the tightscope and centroid."""
        realms = [
            "Potential", "Alignment", "Clarity",
            "Focus", "Precision", "Convergence",
            "Resolution", "Release", "Transcendence"
        ]
        theta = np.linspace(0, 2 * np.pi, 9, endpoint=False)
        x = 0.6 * np.cos(theta) - 0.0
        y = 0.6 * np.sin(theta) - 0.8

        for i, (xi, yi, realm) in enumerate(zip(x, y, realms)):
            self.ax.text(xi, yi, realm, color='cyan', ha='center', fontsize=7, rotation=360/9*i-90)

        # Draw the ring
        ring = Circle((0, -0.8), 0.6, fc='none', ec='cyan', lw=0.8, alpha=0.5)
        self.ax.add_patch(ring)

    def _draw_bridge_nodes(self):
        """Draw and label the 7 bridge nodes."""
        bridge_nodes = [
            (0, 1.8, "1: Acquire"),
            (0, 1.3, "2: Align"),
            (0, 0.8, "3: Engage"),
            (0.3, 0.2, "4: Amplify"),  # Highlighted
            (0, -0.2, "5: Refine"),
            (0, -0.7, "6: Constrict"),
            (0, -1.1, "7: Resolve")   # Highlighted
        ]

        for xi, yi, label in bridge_nodes:
            self.ax.scatter(xi, yi, color='cyan', s=50, alpha=0.9)
            self.ax.text(xi + 0.1, yi, label, color='white', ha='left', fontsize=8)

        # Highlight Stage 4 and Stage 7
        self.ax.scatter(0.3, 0.2, color='yellow', s=80, alpha=0.9)
        self.ax.scatter(0, -1.1, color='yellow', s=80, alpha=0.9)

    def _add_legend(self):
        """Add a legend for the visual elements."""
        legend_elements = [
            plt.Line2D([0], [0], color='cyan', lw=1.5, label='Lattice/Path'),
            plt.Line2D([0], [0], marker='o', color='cyan', markersize=8, label='Bridge Node'),
            plt.Line2D([0], [0], marker='o', color='yellow', markersize=8, label='Key Node (4, 7)'),
            plt.Line2D([0], [0], marker='o', color='magenta', markersize=8, label='Centroid'),
            plt.Rectangle((0, 0), 0, 0, fc='#0a1a2a', ec='none', label='Scope Body')
        ]
        self.ax.legend(handles=legend_elements, loc='upper right', facecolor='#0a1a2a', labelcolor='white')

    def update_trace(self, trace_message: str):
        """Update the developer trace panel."""
        self.trace_text.set_text(f"Developer Trace:\n{trace_message}")

    def animate_trajectory(self, trajectory_points: List[Tuple[float, float]]):
        """Animate the trajectory path through the scope."""
        line, = self.ax.plot([], [], color='white', lw=1.5, alpha=0.8)

        def init():
            line.set_data([], [])
            return line,

        def animate(i):
            x, y = trajectory_points[i]
            line.set_data(trajectory_points[:i+1][0], trajectory_points[:i+1][1])
            return line,

        ani = animation.FuncAnimation(
            self.fig, animate, init_func=init,
            frames=len(trajectory_points), interval=500, blit=True
        )
        plt.show()

    def render_static(self):
        """Render the static scope design."""
        plt.title("Quad-Do Trajectory Scope", color='white')
        plt.tight_layout()
        plt.show()

# Example usage
if __name__ == "__main__":
    visualizer = QuadDoVisualizer()

    # Simulate a trajectory path
    trajectory = [
        (0, 2), (0, 1.5), (0, 1.0),  # Cone → Forescope
        (0.2, 0.5), (0.3, 0.2),      # Tertiary Lattice
        (0, -0.2), (0, -0.5),         # Tightscope
        (0, -1.0), (0, -1.2)          # Centroid
    ]

    # Update trace message
    visualizer.update_trace(
        "Trajectory acquired at Cone\n"
        "→ Aligned in Forescope\n"
        "→ Engaged lattice at L3\n"
        "→ Amplified at Stage 4\n"
        "→ Resolved at Centroid"
    )

    # Animate the trajectory
    visualizer.animate_trajectory(trajectory)
