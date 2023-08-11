"""
Visualization functions.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_dt(obslist, master, show_unused=False):
    """
    Plot the travel time differences of observations.
    """
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    # Geographic distribution of traveltime differences.
    latitudes = np.array([i.latitude for i in obslist if i.use == 1])
    longitudes = np.array([i.longitude for i in obslist if i.use == 1])
    dt = np.array([i.dt for i in obslist if i.use == 1])
    az = np.array([i.azimuth for i in obslist if i.use == 1])
    labels = np.array([f"{i.station}({i.phase})" for i in obslist if i.use == 1])

    ax = axs[0]
    factor = 100 / np.abs(dt).max()
    # plot positive traveltime differences
    ax.scatter(
        longitudes[dt >= 0],
        latitudes[dt >= 0],
        s=dt[dt >= 0] * factor,
        edgecolors="r",
        facecolors="none",
        marker="o",
    )
    # plot negative traveltime differences
    ax.scatter(
        longitudes[dt < 0],
        latitudes[dt < 0],
        s=abs(dt[dt < 0]) * factor,
        edgecolors="b",
        facecolors="none",
        marker="s",
    )
    # plot event location
    ax.scatter(master.longitude, master.latitude, marker="*", s=100, c="k", alpha=0.5)
    # plot station names
    for i in range(len(labels)):
        ax.annotate(
            labels[i],
            (longitudes[i], latitudes[i]),
            fontsize=6,
            xytext=(0, -5),
            textcoords="offset points",
            horizontalalignment="center",
            verticalalignment="top",
        )
    ax.set_title("Observed traveltime differences")

    # Traveltime differences as a function of azimuth.
    ax = axs[1]
    ax.scatter(az, dt, s=25, marker="o")
    ax.set_xlabel("Azimuth (deg)")
    ax.set_ylabel("Traveltime difference (s)")
    ax.set_title("Traveltime differences as a function of azimuth")

    if show_unused:
        latitudes = np.array([i.latitude for i in obslist if i.use == 0])
        longitudes = np.array([i.longitude for i in obslist if i.use == 0])
        dt = np.array([i.dt for i in obslist if i.use == 0])
        az = np.array([i.azimuth for i in obslist if i.use == 0])
        labels = np.array([f"{i.station}({i.phase})" for i in obslist if i.use == 0])

        ax = axs[0]
        ax.scatter(
            longitudes[dt >= 0],
            latitudes[dt >= 0],
            s=dt[dt >= 0] * factor,
            edgecolors="gray",
            facecolors="none",
            marker="o",
            alpha=0.5,
        )
        ax.scatter(
            longitudes[dt < 0],
            latitudes[dt < 0],
            s=abs(dt[dt < 0]) * factor,
            edgecolors="gray",
            facecolors="none",
            marker="s",
            alpha=0.5,
        )
        for i in range(len(labels)):
            ax.annotate(
                labels[i],
                (longitudes[i], latitudes[i]),
                fontsize=6,
                color="gray",
                xytext=(0, -5),
                textcoords="offset points",
                horizontalalignment="center",
                verticalalignment="top",
            )

        ax = axs[1]
        ax.scatter(az, dt, s=25, marker="o", c="gray", alpha=0.5)

    fig.tight_layout()
    plt.show()


def plot_residual(obslist, master, slave):
    """
    Plot the residuals of observations.
    """
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    latitudes = np.array([i.latitude for i in obslist if i.use == 1])
    longitudes = np.array([i.longitude for i in obslist if i.use == 1])
    dt = np.array([i.residual for i in obslist if i.use == 1])
    az = np.array([i.azimuth for i in obslist if i.use == 1])
    labels = np.array([f"{i.station}({i.phase})" for i in obslist if i.use == 1])

    ax = axs[0]
    factor = 100 / np.abs(dt).max()
    ax.scatter(
        longitudes[dt >= 0],
        latitudes[dt >= 0],
        s=dt[dt >= 0] * factor,
        edgecolors="r",
        facecolors="none",
        marker="o",
    )
    ax.scatter(
        longitudes[dt < 0],
        latitudes[dt < 0],
        s=abs(dt[dt < 0]) * factor,
        edgecolors="b",
        facecolors="none",
        marker="s",
    )
    for i in range(len(labels)):
        ax.annotate(
            labels[i],
            (longitudes[i], latitudes[i]),
            fontsize=6,
            xytext=(0, -5),
            textcoords="offset points",
            horizontalalignment="center",
            verticalalignment="top",
        )
    ax.scatter(master.longitude, master.latitude, marker="*", s=100, c="k", alpha=0.5)
    ax.scatter(slave.longitude, slave.latitude, marker="*", s=100, c="b", alpha=0.5)
    ax.set_title("After relocation")

    ax = axs[1]
    ax.scatter(az, dt, s=25, marker="o")
    ax.set_xlabel("Azimuth (deg)")
    ax.set_ylabel("Residual (s)")
    ax.set_title("Residual as a function of azimuth")

    fig.tight_layout()
    plt.show()
