"""
analyze_maze.py — Maze Experiment Data Visualiser
==================================================
Reads the most recent (or specified) run folder and produces:

  1. Trajectory overlaid on maze walls — one panel per trial
  2. Speed profile over time — per trial
  3. Trial summary bar chart — duration and stars collected

Usage
-----
  python analyze_maze.py                        # auto-find newest run
  python analyze_maze.py path/to/run_folder     # specify run folder
"""

import sys
import os
import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_newest_run(base: str) -> str:
    pattern = os.path.join(base, 'run_*')
    runs = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    if not runs:
        raise FileNotFoundError(f"No run_* folders found under {base}")
    return runs[0]


def load_run(run_dir: str):
    traj_path  = os.path.join(run_dir, 'trajectory.csv')
    walls_path = os.path.join(run_dir, 'maze_walls.csv')
    summ_path  = os.path.join(run_dir, 'maze_practice.csv')

    # Try alternate summary filename
    if not os.path.exists(summ_path):
        for name in ('maze_experiment.csv', 'maze_experiment_vr.csv',
                     'experiment_data.csv'):
            alt = os.path.join(run_dir, name)
            if os.path.exists(alt):
                summ_path = alt
                break

    traj  = pd.read_csv(traj_path)
    walls = pd.read_csv(walls_path)
    summ  = pd.read_csv(summ_path) if os.path.exists(summ_path) else pd.DataFrame()
    return traj, walls, summ


def speed_series(traj: pd.DataFrame, trial_id: int) -> tuple:
    """Return (time, speed) for a single trial (m/s, smoothed)."""
    t = traj[traj.trial == trial_id].copy()
    if len(t) < 2:
        return np.array([]), np.array([])
    dt   = t.time_s.diff().fillna(0.1)
    dx   = t.x.diff().fillna(0)
    dz   = t.z.diff().fillna(0)
    spd  = np.sqrt(dx**2 + dz**2) / dt.replace(0, 0.1)
    # simple rolling average (window=3)
    spd  = spd.rolling(3, min_periods=1, center=True).mean()
    return t.time_s.values, spd.values


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_walls(ax, walls: pd.DataFrame, trial_id: int, alpha: float = 0.7):
    tw = walls[walls.trial == trial_id]
    for _, row in tw.iterrows():
        x0 = row.x - row.sx / 2
        z0 = row.z - row.sz / 2
        rect = patches.Rectangle(
            (x0, z0), row.sx, row.sz,
            linewidth=0.5, edgecolor='k',
            facecolor='#888888', alpha=alpha,
        )
        ax.add_patch(rect)


def draw_trajectory(ax, traj: pd.DataFrame, trial_id: int):
    t = traj[traj.trial == trial_id]
    if len(t) < 2:
        return

    x = t.x.values
    z = t.z.values
    time_norm = (t.time_s.values - t.time_s.values[0])
    time_norm = time_norm / max(time_norm[-1], 1e-3)

    # Colour segments by elapsed time (blue → yellow)
    pts   = np.array([x, z]).T.reshape(-1, 1, 2)
    segs  = np.concatenate([pts[:-1], pts[1:]], axis=1)
    norm  = Normalize(vmin=0, vmax=1)
    lc    = LineCollection(segs, cmap='plasma', norm=norm, lw=1.8, alpha=0.85)
    lc.set_array(time_norm[:-1])
    ax.add_collection(lc)

    # Start / end markers
    ax.scatter(x[0],  z[0],  marker='o', s=60, color='lime',  zorder=5, label='Start')
    ax.scatter(x[-1], z[-1], marker='X', s=60, color='red',   zorder=5, label='End')

    # Collect events
    collect = t[t.event == 'collect']
    if not collect.empty:
        ax.scatter(collect.x, collect.z, marker='*', s=100,
                   color='gold', zorder=6, label='Collect')

    return lc


# ---------------------------------------------------------------------------
# Main plot
# ---------------------------------------------------------------------------

def plot(run_dir: str, traj: pd.DataFrame, walls: pd.DataFrame,
         summ: pd.DataFrame) -> None:

    trials = sorted(traj.trial.unique())
    n      = len(trials)

    fig = plt.figure(figsize=(6 * n, 14))
    fig.suptitle(
        f'Maze Run  —  {os.path.basename(run_dir)}',
        fontsize=14, fontweight='bold',
    )
    outer = gridspec.GridSpec(3, n, figure=fig, hspace=0.45, wspace=0.35)

    # Row 0: maze + trajectory
    for col, tid in enumerate(trials):
        ax = fig.add_subplot(outer[0, col])
        draw_walls(ax, walls, tid)
        lc = draw_trajectory(ax, traj, tid)

        cond  = ''
        stars_n = stars_c = ''
        dur   = ''
        if not summ.empty and tid <= len(summ):
            row   = summ.iloc[tid - 1]
            cond  = row.get('condition', '')
            stars_n = int(row.get('n_stars',   0))
            stars_c = int(row.get('collected', 0))
            dur   = f"{float(row.get('duration_s', 0)):.1f} s"

        ax.set_title(
            f'Trial {tid}  [{cond}]\n'
            f'Stars {stars_c}/{stars_n}  |  {dur}',
            fontsize=9,
        )
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Z (m)')
        ax.set_aspect('equal')
        ax.autoscale_view()
        ax.legend(fontsize=7, loc='upper right')
        if lc:
            plt.colorbar(lc, ax=ax, label='Time →', pad=0.02, shrink=0.8)

    # Row 1: speed profile
    for col, tid in enumerate(trials):
        ax = fig.add_subplot(outer[1, col])
        ts, spd = speed_series(traj, tid)
        if len(ts) > 1:
            ax.plot(ts, spd, color='tab:blue', lw=1.0)
            ax.fill_between(ts, spd, alpha=0.2, color='tab:blue')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Speed (m/s)')
            ax.set_title(f'Trial {tid} — speed', fontsize=9)
            ax.grid(True, alpha=0.3)

    # Row 2: summary bar chart (if summary data available)
    if not summ.empty:
        ax = fig.add_subplot(outer[2, :])
        x_pos   = np.arange(len(summ))
        dur_col = 'duration_s'
        col_col = 'collected'
        n_col   = 'n_stars'

        durations  = summ[dur_col].astype(float).values if dur_col in summ else np.zeros(len(summ))
        collected  = summ[col_col].astype(float).values if col_col in summ else np.zeros(len(summ))
        n_stars    = summ[n_col].astype(float).values   if n_col  in summ else np.ones(len(summ))

        colors = ['#2ecc71' if c >= n else '#e74c3c'
                  for c, n in zip(collected, n_stars)]

        bars = ax.bar(x_pos, durations, color=colors, alpha=0.8, edgecolor='k', lw=0.5)
        for bar, c, n in zip(bars, collected, n_stars):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.3,
                    f'{int(c)}/{int(n)}',
                    ha='center', va='bottom', fontsize=9)

        cond_labels = [f"T{i+1}\n{row.get('condition','')}"
                       for i, row in summ.iterrows()]
        ax.set_xticks(x_pos)
        ax.set_xticklabels(cond_labels, fontsize=9)
        ax.set_ylabel('Duration (s)')
        ax.set_title('Trial summary  (green = completed, red = incomplete)', fontsize=10)
        ax.grid(axis='y', alpha=0.3)

    out_path = os.path.join(run_dir, 'maze_analysis.png')
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f'Saved → {out_path}')
    plt.show()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # Locate run directory
    if len(sys.argv) > 1:
        run_dir = sys.argv[1]
    else:
        base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', '..', 'exercises', 'ex7_maze_explorer',
        )
        run_dir = find_newest_run(os.path.abspath(base))
        print(f'Using: {run_dir}')

    traj, walls, summ = load_run(run_dir)
    print(f'Trials: {sorted(traj.trial.unique())}   |   '
          f'{len(traj)} trajectory rows')
    plot(run_dir, traj, walls, summ)
