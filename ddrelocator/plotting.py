"""
Visualization functions.
"""
import matplotlib.pyplot as plt
import numpy as np
from ddrelocator.helpers import obslist_to_dataframe


def plot_dt_as_azimuth(ax, obslist, residual=False):
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
    """
    df = obslist_to_dataframe(obslist)
    if residual:
        dt, title, ylabel = df.residual, "Residual vs azimuth", "Residual (s)"
    else:
        dt, title, ylabel = df.dt, "dt vs azimuth", "dt (s)"

    ax.scatter(df.azimuth, dt, s=25, marker="o")
    ax.set_xlabel("Azimuth (deg)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)


def plot_dt_on_map(ax, obslist, master, slave=None, residual=False):
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
    """
    df = obslist_to_dataframe(obslist)

    if residual:
        dt, title = df.residual, "Residuals"
    else:
        dt, title = df.dt, "Travel time differences"
    dt *= 1000  # convert to ms

    # scale factor for marker size
    factor = 200 / max(dt.abs().max(), 100)
    # plot positive dt
    ax.scatter(
        df.longitude[dt >= 0],
        df.latitude[dt >= 0],
        s=dt[dt >= 0] * factor,
        edgecolors="r",
        facecolors="none",
        marker="o",
    )
    # plot negative dt
    ax.scatter(
        df.longitude[dt < 0],
        df.latitude[dt < 0],
        s=abs(dt[dt < 0]) * factor,
        edgecolors="b",
        facecolors="none",
        marker="s",
    )
    # Add station labels
    for i in range(len(obslist)):
        ax.annotate(
            f"{obslist[i].station}({obslist[i].phase})",
            (df.longitude[i], df.latitude[i]),
            fontsize=6,
            xytext=(0, -5),
            textcoords="offset points",
            horizontalalignment="center",
            verticalalignment="top",
        )

    # Add legend
    for dt in [-60, -40, -20, 20, 40, 60]:
        if dt > 0:
            edgecolor, marker = "r", "o"
        else:
            edgecolor, marker = "b", "s"
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


def plot_dt(obslist, master):
    """
    Plot the travel time differences of observations.
    """
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    plot_dt_on_map(axs[0], obslist, master, residual=False)
    plot_dt_as_azimuth(axs[1], obslist, residual=False)
    fig.tight_layout()
    plt.show()


def plot_residual(obslist, master, slave):
    """
    Plot the residuals of observations.
    """
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    plot_dt_on_map(axs[0], obslist, master, slave=slave, residual=True)
    plot_dt_as_azimuth(axs[1], obslist, residual=True)
    fig.tight_layout()
    plt.show()


def plot_misfit(grid, Jout, sol_type):
    """
    Plot the misfit of solutions.

    This function is adapted from https://stackoverflow.com/questions/49015138.
    """
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(15, 4))

    if sol_type == "geographic":
        names = ["latitude (degree)", "longitude (degree)", "ddepth (km)"]
    elif sol_type == "cylindrical":
        names = ["distance (m)", "azimuth (degree)", "ddepth (m)"]

    i = 0
    for xi, yi, zi in ((0, 1, 2), (0, 2, 1), (1, 2, 0)):
        ax = axs[i]
        X, Y = grid[xi], grid[yi]
        cf = ax.pcolormesh(
            np.amin(X, axis=zi),
            np.amin(Y, axis=zi),
            np.amin(Jout, axis=zi),
            cmap="viridis_r",
        )
        fig.colorbar(cf, ax=ax, orientation="vertical", label="Misfit")

        # plot the best solution
        idx = np.argmin(Jout)
        ax.scatter(X.flat[idx], Y.flat[idx], s=50, c="r", marker="*")

        ax.set_xlabel(names[xi])
        ax.set_ylabel(names[yi])
        i += 1

    fig.tight_layout()
    plt.show()
