import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rcParams, image as mpimg
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import os
import json
import numpy as np
from scipy.interpolate import interp1d

from map import write_out_date as write_out_date_map

from constants import ELECTORAL_VOTE_COUNTS_DIR, FINAL_VIDEOS_DIR, SOURCE_IMAGES_DIR, BOX_COLOR, BOX_TRANSPARENCY, \
    DAILY_PLOTS_DIR, PLOT_LAST_N_ONLY, GOOGLE_DRIVE_UPLOAD_PATH, BACKGROUND_IMAGE, SAVE_TO_GOOGLE_DRIVE, ADD_TITLE, \
    FINAL_HOLD_IN_SECONDS, FRAMES_PER_SECOND, FRAMES_PER_DAY


def write_out_date_fully(filename):
    hyphenated = filename.split('.')[0].split('_')[-1]
    full = write_out_date_map(hyphenated)
    return full.replace(', 2024', '')


def write_out_date(filename):
    hyphenated = filename.split('.')[0].split('_')[-1]
    return hyphenated.split('-', 1)[-1]


fps = FRAMES_PER_SECOND  # Increase frames per second for smoother animation

# Set the path to ffmpeg
rcParams['animation.ffmpeg_path'] = r'C:\Users\philh\ffmpeg\bin\ffmpeg.exe'

# Set default font
rcParams['font.size'] = 16
rcParams['font.weight'] = 'bold'
rcParams['axes.labelweight'] = 'bold'

print("Gathering data...")

# Get all electoral vote counts available
electoral_vote_counts = []
files = os.listdir(ELECTORAL_VOTE_COUNTS_DIR)
files.sort(key=lambda x: os.path.getmtime(os.path.join(ELECTORAL_VOTE_COUNTS_DIR, x)))

if PLOT_LAST_N_ONLY:
    files = files[-PLOT_LAST_N_ONLY:]  # Only use the last 7 days

for f in files:
    if f.endswith('.json'):
        with open(os.path.join(ELECTORAL_VOTE_COUNTS_DIR, f), 'r') as file:
            electoral_vote_counts.append(json.load(file))

# Create result list for each candidate
harris = [r['Harris'] for r in electoral_vote_counts]
trump = [r['Trump'] for r in electoral_vote_counts]

print("Creating plots...")

# Interpolate data for smoother transitions
x_original = np.arange(len(harris))
x_interpolated = np.linspace(0, len(harris) - 1, ((len(harris) - 1) * FRAMES_PER_DAY) + 1)  # Increase the number of points by FRAMES_PER_DAY times

harris_interpolated = interp1d(x_original, harris, kind='linear')(x_interpolated)
trump_interpolated = interp1d(x_original, trump, kind='linear')(x_interpolated)

# Create a figure and axis
fig, ax = plt.subplots(figsize=(11, 11))

# Initialize a line object with a black outline
line_trump = Line2D([], [], label='Trump', color='tab:red', linewidth=7, path_effects=[pe.Stroke(linewidth=9, foreground='black'), pe.Normal()])
line_harris = Line2D([], [], label='Harris', color='tab:blue', linewidth=7, path_effects=[pe.Stroke(linewidth=9, foreground='black'), pe.Normal()])

# Add lines to the axis
ax.add_line(line_trump)
ax.add_line(line_harris)

# Set plot limits
gap = 15
ax.set_ylim(min(harris + trump) - gap, max(harris + trump) + gap)

# Add title and legend
if ADD_TITLE:
    ax.set_title(f'2024 US Presidential Election\nsimulated electoral vote count by most recent polling\nfrom {write_out_date_fully(files[0])} to {write_out_date_fully(files[-1])} (last {len(harris)} days)')
ax.legend(loc='upper right')

# Adjust title font
plt.setp(ax.title, fontweight='bold')
plt.setp(ax.title, fontsize=18)

# Set axis labels
ax.set_xlabel(f'Date ({write_out_date_fully(files[0]).split(" ")[0]}{"/"+write_out_date_fully(files[-1]).split(" ")[0] if write_out_date_fully(files[0]).split(" ")[0] != write_out_date_fully(files[-1]).split(" ")[0] else ""})')
ax.set_ylabel('Electoral Votes')


# Initialization function
def init():
    line_harris.set_data([], [])
    line_trump.set_data([], [])
    return line_harris, line_trump


# Animation function
def animate(i):
    if i < len(x_interpolated) + 1:
        line_harris.set_data(x_interpolated[:i], harris_interpolated[:i])
        line_trump.set_data(x_interpolated[:i], trump_interpolated[:i])
        if i > 0:
            ax.set_xlim(x_interpolated[0], x_interpolated[i - 1] + 1.0)  # Ensure the plot fills the width
        else:
            ax.set_xlim(x_interpolated[0], x_interpolated[1] + 1.0)  # Avoid identical low and high xlims

        # Update ticks and labels
        tick_indices = np.arange(0, i, fps)  # Every [fps]th interpolated point corresponds to an original point
        ax.set_xticks(x_interpolated[tick_indices])
        ax.set_xticklabels([int(write_out_date(files[j]).split('-')[-1]) for j in tick_indices // fps])
    return line_harris, line_trump


# Create the animation
frames = len(x_interpolated)
hold_frames = int(fps * FINAL_HOLD_IN_SECONDS)  # Number of frames to hold the last frame

# make the back of the axis transparent
ax.set_facecolor('none')

# Add the rectangle to the figure as background
fig.patches.extend([plt.Rectangle((0.03, 0.03), .94, 0.94,
                                  fill=True, color=BOX_COLOR, alpha=BOX_TRANSPARENCY, zorder=-3,
                                  transform=fig.transFigure, figure=fig)])
fig.patches.extend([plt.Rectangle((0.03, 0.03), .94, 0.94,
                                  fill=False, color='black', alpha=0.8, zorder=-1,
                                  transform=fig.transFigure, figure=fig, linewidth=1.5)])

# Load the image
img = mpimg.imread(f'{SOURCE_IMAGES_DIR}/{BACKGROUND_IMAGE}')

background_ax = plt.axes((0, 0, 1, 1))  # create a dummy subplot for the background
background_ax.set_zorder(-5)  # set the background subplot behind the others
background_ax.imshow(img, aspect='auto')  # show the background image

print("Generating animation...")

ani = animation.FuncAnimation(fig, animate, init_func=init, frames=frames + hold_frames, interval=1000/fps, blit=True)


# Save the animation as a video file
print(f"Saving animation to {FINAL_VIDEOS_DIR}/plots/{write_out_date(files[0])}_to_{write_out_date(files[-1])}_line.mp4")
ani.save(f'{FINAL_VIDEOS_DIR}/plots/{write_out_date(files[0])}_to_{write_out_date(files[-1])}_line.mp4', writer='ffmpeg')
if SAVE_TO_GOOGLE_DRIVE:
    print(f"Saving animation to {GOOGLE_DRIVE_UPLOAD_PATH}/{write_out_date(files[0])}_to_{write_out_date(files[-1])}_line.mp4")
    ani.save(f'{GOOGLE_DRIVE_UPLOAD_PATH}/{write_out_date(files[0])}_to_{write_out_date(files[-1])}_line.mp4', writer='ffmpeg')

#
# create a single image plot of the data
#

print("Creating single image plot...")

fig, ax = plt.subplots(figsize=(11, 11))
ax.plot(trump, label='Trump', color='tab:red', linewidth=5, path_effects=[pe.Stroke(linewidth=7, foreground='black'), pe.Normal()])
ax.plot(harris, label='Harris', color='tab:blue', linewidth=5, path_effects=[pe.Stroke(linewidth=7, foreground='black'), pe.Normal()])
fig.suptitle(f'2024 US Presidential Election\nsimulated electoral vote count by most recent polling\nfrom {write_out_date_fully(files[0])} to {write_out_date_fully(files[-1])}',
                         fontsize=15, weight='semibold', y=0.95)
ax.set_xlabel(f'Date ({write_out_date_fully(files[0]).split(" ")[0]}{"/"+write_out_date_fully(files[-1]).split(" ")[0] if write_out_date_fully(files[0]).split(" ")[0] != write_out_date_fully(files[-1]).split(" ")[0] else ""})')
ax.set_ylabel('Electoral Votes')
ax.legend()
ax.set_facecolor('none')

ax.set_xlim(0, len(harris) - 1)
ax.set_xticks(range(len(harris)))
ax.set_xticklabels([int(write_out_date(f).split('-')[-1]) for f in files])

background_ax = plt.axes((0, 0, 1, 1))  # create a dummy subplot for the background
background_ax.set_zorder(-5)  # set the background subplot behind the others
background_ax.imshow(img, aspect='auto')  # show the background image

# add the rectangle to the figure as background
fig.patches.extend([plt.Rectangle((0.03, 0.03), .94, 0.94,
                                fill=True, color=BOX_COLOR, alpha=BOX_TRANSPARENCY, zorder=-3,
                                transform=fig.transFigure, figure=fig)])
fig.patches.extend([plt.Rectangle((0.03, 0.03), .94, 0.94,
                                fill=False, color='black', alpha=0.8, zorder=-1,
                                transform=fig.transFigure, figure=fig, linewidth=1.5)])

print(f"Saving single image plot to {DAILY_PLOTS_DIR}/{write_out_date(files[0])}_to_{write_out_date(files[-1])}_line.png")

plt.savefig(f'{DAILY_PLOTS_DIR}/{write_out_date(files[0])}_to_{write_out_date(files[-1])}_line.png')