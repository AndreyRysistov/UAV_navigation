import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.transforms import Bbox
import os


class Visualizer:

    def __init__(self, config):
        self.config = config

    def plot_landscape(self, x, y, z):
        fig = plt.figure(figsize=self.config.visualizer.figsize)
        self.plot_height_map(x, y, z, fig=fig, subplot_place=(2, 1, 1))
        self.plot_heatmap(z, fig=fig, subplot_place=(1, 1, 1))
        self.plot_contour(x, y, z, fig=fig, subplot_place=(2, 2, 4))
        plt.show()
        return fig

    def plot_height_map(self, x, y, z, fig=None, subplot_place=(1, 1, 1)):
        if not fig:
            fig = plt.figure(figsize=self.config.visualizer.figsize)
        ax = fig.add_subplot(*subplot_place, projection='3d')
        ax.plot_surface(x, y, z,
                        cmap=self.config.visualizer.cmap,
                        linewidth=self.config.visualizer.linewidth,
                        vmin=self.config.visualizer.vmin,
                        vmax=self.config.visualizer.vmax,
                        antialiased=self.config.visualizer.antialiased)
        ax.set_zlim(0, 255)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        ax.set_title('Height map of landscape')
        #extent = Visualizer.full_extent(ax).transformed(fig.dpi_scale_trans.inverted())

    def plot_heatmap(self, z, fig=None, subplot_place=(1, 1, 1)):
        if not fig:
            fig = plt.figure(figsize=self.config.visualizer.figsize)
        ax = fig.add_subplot(*subplot_place)
        sns.heatmap(z[::-1, ],
                    vmin=self.config.visualizer.vmin,
                    vmax=self.config.visualizer.vmax,
                    cmap=self.config.visualizer.cmap,
                    yticklabels=False,
                    xticklabels=False,
                    ax=ax
                    )
        ax.set_title('Heat map of landscape')

    def plot_contour(self, x, y, z, fig=None, subplot_place=(1, 1, 1)):
        if not fig:
            fig = plt.figure(figsize=self.config.visualizer.figsize)
        ax = fig.add_subplot(*subplot_place)
        ax.contour(x, y, z,
                   levels=100,
                   cmap=self.config.visualizer.cmap,
                   vmin=self.config.visualizer.vmin,
                   vmax=self.config.visualizer.vmax,
                   linestyles='solid')
        ax.set_title('Contour map of landscape')

    def create_heatmap(self, height_map, file_name, figsize=(20, 20)):
        fig = plt.figure(figsize=figsize)
        plt.tick_params(
            top='off',
            bottom='off',
            left='off',
            right='off',
            labelleft='off',
            labelbottom='on'
        )
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        ax.set(frame_on=False)
        plt.imshow(height_map, 'terrain')
        fig.savefig(
            os.path.join(self.config.visualizer.log_dir.heat_map, file_name),
            transparent=True,
            format='jpg',
            edgecolor='white',
            facecolor='white'
        )

    @staticmethod
    def full_extent(ax, pad=0.0):
        ax.figure.canvas.draw()
        items = ax.get_xticklabels() + ax.get_yticklabels()
        items += [ax, ax.title]
        bbox = Bbox.union([item.get_window_extent() for item in items])

        return bbox.expanded(1.0 + pad, 1.0 + pad)
