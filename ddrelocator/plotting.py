"""
Visualization functions.
"""
import matplotlib.pyplot as plt
import numpy as np


def plot_dt_as_azimuth(ax, obslist, residual=False, show_unused=False):
    """
    Plot the travel time differences/residuals as a function of azimuth.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes object to plot.
    obslist : list of Obs
        List of observations.
    residual : bool, optional
        If True, plot residuals. Else, plot travel time differences.
    show_unused : bool, optional
        If True, show unused observations.
    """
    usemask = np.array([i.use for i in obslist])
    az = np.array([i.azimuth for i in obslist])
    if residual:
        dt = np.array([i.residual for i in obslist])
        title = "Residual vs azimuth"
        ylabel = "Residual (s)"
    else:
        dt = np.array([i.dt for i in obslist])
        title = "dt vs azimuth"
        ylabel = "dt (s)"

    ax.scatter(az[usemask], dt[usemask], s=25, marker="o")
    if show_unused:
        ax.scatter(az[~usemask], dt[~usemask], s=25, marker="o", c="gray", alpha=0.5)

    ax.set_xlabel("Azimuth (deg)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)


def plot_dt_on_map(ax, obslist, master, slave=None, residual=False, show_unused=False):
    """
    Plot the travel time differences/residuals of observations on a map.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes object to plot.
    obslist : list of Obs
        List of observations.
    master : Event
        Master event.
    slave : Event, optional
        Slave event.
    residual : bool, optional
        If True, plot residuals. Else, plot travel time differences.
    show_unused : bool, optional
        If True, show unused observations.
    """
    usemask = np.array([i.use for i in obslist])
    latitudes = np.array([i.latitude for i in obslist])
    longitudes = np.array([i.longitude for i in obslist])
    labels = np.array([f"{i.station}({i.phase})" for i in obslist])
    if residual:
        dt = np.array([i.residual for i in obslist])
        title = "Residuals"
    else:
        dt = np.array([i.dt for i in obslist])
        title = "Travel time differences"
    dt *= 1000  # convert to ms

    # scale factor for marker size
    factor = 200 / max(np.abs(dt).max(), 100)
    # plot positive dt
    ax.scatter(
        longitudes[usemask & (dt >= 0)],
        latitudes[usemask & (dt >= 0)],
        s=dt[usemask & (dt >= 0)] * factor,
        edgecolors="r",
        facecolors="none",
        marker="o",
    )
    # plot negative dt
    ax.scatter(
        longitudes[usemask & (dt < 0)],
        latitudes[usemask & (dt < 0)],
        s=abs(dt[usemask & (dt < 0)]) * factor,
        edgecolors="b",
        facecolors="none",
        marker="s",
    )
    # Add station labels
    for i, label in enumerate(labels):
        if not usemask[i]:
            continue
        ax.annotate(
            label,
            (longitudes[i], latitudes[i]),
            fontsize=6,
            xytext=(0, -5),
            textcoords="offset points",
            horizontalalignment="center",
            verticalalignment="top",
        )

    if show_unused:
        # plot positive dt
        ax.scatter(
            longitudes[~usemask & (dt >= 0)],
            latitudes[~usemask & (dt >= 0)],
            s=dt[~usemask & (dt >= 0)] * factor,
            edgecolors="gray",
            facecolors="none",
            marker="o",
            alpha=0.5,
        )
        # plot negative dt
        ax.scatter(
            longitudes[~usemask & (dt < 0)],
            latitudes[~usemask & (dt < 0)],
            s=abs(dt[~usemask & (dt < 0)]) * factor,
            edgecolors="gray",
            facecolors="none",
            marker="s",
            alpha=0.5,
        )
        for i, label in enumerate(labels):
            if usemask[i]:
                continue
            ax.annotate(
                label,
                (longitudes[i], latitudes[i]),
                fontsize=6,
                color="gray",
                xytext=(0, -5),
                textcoords="offset points",
                horizontalalignment="center",
                verticalalignment="top",
            )

    # Add legend
    for dt in [-60, -40, -20, 20, 40, 60]:
        if dt > 0:
            edgecolor = "r"
            marker = "o"
        else:
            edgecolor = "b"
            marker = "s"
        ax.scatter(
            [],
            [],
            s=abs(dt) * factor,
            edgecolors=edgecolor,
            facecolor="none",
            marker=marker,
            label=f"{dt} ms",
        )
    ax.legend(loc="upper left", scatterpoints=1, fontsize=8)

    ax.scatter(master.longitude, master.latitude, marker="*", s=100, c="k", alpha=0.5)
    if slave is not None:
        ax.scatter(slave.longitude, slave.latitude, marker="*", s=75, c="r", alpha=0.5)
    ax.set_title(title)


def plot_dt(obslist, master, show_unused=False):
    """
    Plot the travel time differences of observations.
    """
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    plot_dt_on_map(axs[0], obslist, master, residual=False, show_unused=show_unused)
    plot_dt_as_azimuth(axs[1], obslist, residual=False, show_unused=show_unused)

    fig.tight_layout()
    plt.show()


def plot_residual(obslist, master, slave, show_unused=False):
    """
    Plot the residuals of observations.
    """
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    plot_dt_on_map(
        axs[0], obslist, master, slave=slave, residual=True, show_unused=show_unused
    )
    plot_dt_as_azimuth(axs[1], obslist, residual=True, show_unused=show_unused)
    fig.tight_layout()
    plt.show()
