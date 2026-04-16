"""
gaze_analysis.py — Gaze Data Visualiser
========================================
Reads the CSV produced by gaze_demo.py and generates four plots:

  1. Gaze direction over time  (gaze_x, gaze_y, gaze_z as time series)
  2. Horizontal / vertical gaze angle over time  (yaw / pitch in degrees)
  3. 2-D scatter of gaze directions  (yaw vs pitch — like a "field of regard" map)
  4. Heatmap of dwell density  (Gaussian-smoothed 2-D histogram)

Usage
-----
  python gaze_analysis.py                     # auto-find newest gaze_*.csv
  python gaze_analysis.py gaze_20260416.csv   # specify file explicitly

Output
------
  gaze_analysis_<stem>.png   saved next to the CSV
"""

import sys
import os
import glob
import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LogNorm
from scipy.ndimage import gaussian_filter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_csv() -> str:
    """Return the newest gaze_*.csv in the script directory."""
    here = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(here, 'gaze_*.csv')
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    if not files:
        raise FileNotFoundError(
            f"No gaze_*.csv found in {here}.\n"
            "Run gaze_demo.py first to record data."
        )
    return files[0]


def vec_to_angles(gx: np.ndarray, gy: np.ndarray, gz: np.ndarray):
    """
    Convert unit gaze vectors to yaw (horizontal) and pitch (vertical) in degrees.

    Coordinate convention matches Ursina Y-up world space:
      +X  = right
      +Y  = up
      +Z  = forward (into scene)

    yaw   = signed angle around Y axis from +Z axis  (positive = rightward gaze)
    pitch = elevation angle above/below horizontal plane (positive = upward gaze)
    """
    yaw   = np.degrees(np.arctan2(gx, gz))           # atan2(x, z)
    pitch = np.degrees(np.arctan2(gy, np.hypot(gx, gz)))  # elevation
    return yaw, pitch


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {'time_s', 'gaze_x', 'gaze_y', 'gaze_z'}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    df = df.dropna(subset=list(required))
    # Re-normalise vectors (proxy gaze may not be exactly unit-length)
    mag = np.sqrt(df.gaze_x**2 + df.gaze_y**2 + df.gaze_z**2)
    mask = mag > 0
    df.loc[mask, 'gaze_x'] /= mag[mask]
    df.loc[mask, 'gaze_y'] /= mag[mask]
    df.loc[mask, 'gaze_z'] /= mag[mask]
    df['yaw'], df['pitch'] = vec_to_angles(
        df.gaze_x.values, df.gaze_y.values, df.gaze_z.values
    )
    return df


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

def plot(df: pd.DataFrame, out_path: str) -> None:
    n = len(df)
    duration = df.time_s.iloc[-1] if n > 0 else 0
    title_stem = os.path.splitext(os.path.basename(out_path))[0]

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(
        f'{title_stem}   |   {n} samples   |   {duration:.1f} s',
        fontsize=13, fontweight='bold',
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

    # ------------------------------------------------------------------
    # Plot 1 — gaze vector components over time
    # ------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(df.time_s, df.gaze_x, label='gaze_x (right)', color='tab:red',   lw=0.8)
    ax1.plot(df.time_s, df.gaze_y, label='gaze_y (up)',    color='tab:green', lw=0.8)
    ax1.plot(df.time_s, df.gaze_z, label='gaze_z (fwd)',   color='tab:blue',  lw=0.8)
    ax1.axhline(0, color='black', lw=0.5, ls='--')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Direction component')
    ax1.set_title('Gaze direction over time')
    ax1.legend(fontsize=8)
    ax1.set_ylim(-1.1, 1.1)
    ax1.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # Plot 2 — yaw and pitch over time
    # ------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(df.time_s, df.yaw,   label='Yaw (horizontal °)',  color='tab:orange', lw=0.8)
    ax2.plot(df.time_s, df.pitch, label='Pitch (vertical °)',  color='tab:purple', lw=0.8)
    ax2.axhline(0, color='black', lw=0.5, ls='--')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Angle (degrees)')
    ax2.set_title('Gaze angles over time')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # Plot 3 — scatter: yaw vs pitch (field of regard)
    # ------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 0])
    sc = ax3.scatter(
        df.yaw, df.pitch,
        c=df.time_s, cmap='viridis', s=4, alpha=0.6, linewidths=0,
    )
    plt.colorbar(sc, ax=ax3, label='Time (s)', pad=0.02)
    # Mark start and end
    ax3.scatter(df.yaw.iloc[0],  df.pitch.iloc[0],  marker='o', s=80,
                color='lime',   zorder=5, label='Start')
    ax3.scatter(df.yaw.iloc[-1], df.pitch.iloc[-1], marker='X', s=80,
                color='red',    zorder=5, label='End')
    ax3.set_xlabel('Yaw — horizontal (°)')
    ax3.set_ylabel('Pitch — vertical (°)')
    ax3.set_title('Gaze trajectory  (field of regard)')
    ax3.legend(fontsize=8)
    ax3.axhline(0, color='black', lw=0.5, ls='--')
    ax3.axvline(0, color='black', lw=0.5, ls='--')
    ax3.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # Plot 4 — heatmap (Gaussian-smoothed 2-D histogram)
    # ------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 1])

    yaw_range   = (-90, 90)
    pitch_range = (-60, 60)
    bins = (120, 80)

    H, xedges, yedges = np.histogram2d(
        df.yaw, df.pitch,
        bins=bins,
        range=[yaw_range, pitch_range],
    )
    H_smooth = gaussian_filter(H.T, sigma=2.0)   # transpose: H[x,y] → rows=y
    H_smooth = np.where(H_smooth < 0.01, np.nan, H_smooth)  # mask empty bins

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    im = ax4.imshow(
        H_smooth,
        origin='lower', extent=extent,
        cmap='hot', aspect='auto',
        norm=LogNorm(vmin=0.1),
    )
    plt.colorbar(im, ax=ax4, label='Dwell density (log)', pad=0.02)
    ax4.set_xlabel('Yaw — horizontal (°)')
    ax4.set_ylabel('Pitch — vertical (°)')
    ax4.set_title('Gaze heatmap')
    ax4.axhline(0, color='white', lw=0.5, ls='--', alpha=0.5)
    ax4.axvline(0, color='white', lw=0.5, ls='--', alpha=0.5)

    # ------------------------------------------------------------------
    # Summary stats in figure footer
    # ------------------------------------------------------------------
    stats = (
        f"Samples: {n}   |   "
        f"Duration: {duration:.1f} s   |   "
        f"Sample rate: {n / duration:.0f} Hz   |   "
        f"Yaw range: {df.yaw.min():.0f}° … {df.yaw.max():.0f}°   |   "
        f"Pitch range: {df.pitch.min():.0f}° … {df.pitch.max():.0f}°"
    ) if duration > 0 else ''
    fig.text(0.5, 0.01, stats, ha='center', fontsize=9, color='gray')

    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f'Saved → {out_path}')
    plt.show()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = find_csv()
        print(f'Using: {csv_path}')

    df = load(csv_path)
    print(f'Loaded {len(df)} samples  ({df.time_s.iloc[-1]:.1f} s)')

    stem     = os.path.splitext(os.path.basename(csv_path))[0]
    out_dir  = os.path.dirname(os.path.abspath(csv_path))
    out_path = os.path.join(out_dir, f'gaze_analysis_{stem}.png')

    plot(df, out_path)
