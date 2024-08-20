import json
import time

import subprocess
import shutil

import cv2
import os
import glob
import numpy as np
from matplotlib.colors import AsinhNorm, Normalize
from matplotlib import colormaps, colors, pyplot as plt

from map import main as map_main

from constants import (
    DAILY_VISUALS_DIR, COLOR_NORM_VMAX, FINAL_VIDEOS_DIR, TRANSITION_FRAMES_DIR,
    TRANSITION_POLLING_RESULTS_DIR, TRANSITION_VISUALS_DIR, TRANSITION_ELECTORAL_COUNTS_DIR, HOLD_FRAME_COUNT,
    TRANSITION_FRAME_COUNT, POLLING_RESULTS_DIR, ELECTORAL_VOTE_COUNTS_DIR, ANIMATE_LAST_N_ONLY, COLOR_NORM_VMIN,
    GOOGLE_DRIVE_UPLOAD_PATH, SAVE_TO_GOOGLE_DRIVE
)

# Get a list of all the image files
image_files = glob.glob(f'{DAILY_VISUALS_DIR}/*.png')
image_files.sort()  # Sort the files

if ANIMATE_LAST_N_ONLY:
    image_files = image_files[-ANIMATE_LAST_N_ONLY:]  # Only use the last N days

# Get the size of the first image
img = cv2.imread(image_files[0])
height, width, layers = img.shape
size = (width, height)

date1_overall = image_files[0].split('_')[-1].split('.')[0]
date2_overall = image_files[-1].split('_')[-1].split('.')[0]

# Initialize the video writer
os.makedirs(FINAL_VIDEOS_DIR, exist_ok=True)
video = cv2.VideoWriter(f'{FINAL_VIDEOS_DIR}/maps/{date1_overall}_to_{date2_overall}_map.avi', cv2.VideoWriter_fourcc(*'DIVX'), 30,
                        size)


def create_transition_frames(count, from_date, to_date, cn, cms):
    # Create the directories if they don't exist
    os.makedirs(TRANSITION_FRAMES_DIR, exist_ok=True)
    os.makedirs(TRANSITION_POLLING_RESULTS_DIR, exist_ok=True)
    os.makedirs(TRANSITION_VISUALS_DIR, exist_ok=True)
    os.makedirs(TRANSITION_ELECTORAL_COUNTS_DIR, exist_ok=True)

    # ensure transition polling results and visuals directories are empty
    for f in glob.glob(f'{TRANSITION_POLLING_RESULTS_DIR}/*.json'):
        os.remove(f)
    for f in glob.glob(f'{TRANSITION_VISUALS_DIR}/*.png'):
        os.remove(f)
    for f in glob.glob(f'{TRANSITION_ELECTORAL_COUNTS_DIR}/*.json'):
        os.remove(f)

    from_polling_result = os.path.join(POLLING_RESULTS_DIR, f'polling_results_{from_date}.json')
    to_polling_result = os.path.join(POLLING_RESULTS_DIR, f'polling_results_{to_date}.json')

    from_elec_votes = os.path.join(ELECTORAL_VOTE_COUNTS_DIR, f'electoral_votes_{from_date}.json')
    to_elec_votes = os.path.join(ELECTORAL_VOTE_COUNTS_DIR, f'electoral_votes_{to_date}.json')

    with open(from_polling_result) as f:
        from_polling_results = json.load(f)
    with open(to_polling_result) as f:
        to_polling_results = json.load(f)

    with open(from_elec_votes) as f:
        from_elec_votes = json.load(f)
    with open(to_elec_votes) as f:
        to_elec_votes = json.load(f)

    # create fake polling results for the transition
    for alpha in np.linspace(0, 1, count):
        if from_polling_results == to_polling_results:
            transition_polling_results = from_polling_results
        else:
            transition_polling_results = {}
            for state in from_polling_results:

                from_winner = from_polling_results[state]['winner']
                from_point_diff = from_polling_results[state]['point_diff']
                to_winner = to_polling_results[state]['winner']
                to_point_diff = to_polling_results[state]['point_diff']

                if from_winner == to_winner:
                    if from_point_diff == to_point_diff:
                        transition_polling_results[state] = {
                            "winner": from_winner,
                            "point_diff": from_point_diff
                        }
                    else:
                        transition_polling_results[state] = {
                            "winner": from_winner,
                            "point_diff": from_point_diff * (1 - alpha) + to_point_diff * alpha,
                        }
                else:
                    if alpha < 0.5:
                        transition_polling_results[state] = {
                            "winner": from_winner,
                            "point_diff": from_point_diff * (0.5 - alpha) / 0.5
                        }
                    else:
                        transition_polling_results[state] = {
                            "winner": to_winner,
                            "point_diff": to_point_diff * (alpha - 0.5) / 0.5
                        }

        trump_from_elec_votes = from_elec_votes['Trump']
        harris_from_elec_votes = from_elec_votes['Harris']
        trump_to_elec_votes = to_elec_votes['Trump']
        harris_to_elec_votes = to_elec_votes['Harris']

        if trump_from_elec_votes == trump_to_elec_votes and harris_from_elec_votes == harris_to_elec_votes:
            transition_elec_votes = {
                "Trump": trump_from_elec_votes,
                "Harris": harris_from_elec_votes
            }
        else:
            transition_elec_votes = {
                "Trump": trump_from_elec_votes * (1 - alpha) + trump_to_elec_votes * alpha,
                "Harris": harris_from_elec_votes * (1 - alpha) + harris_to_elec_votes * alpha
            }

        # save the transition electoral vote counts
        with open(os.path.join(TRANSITION_ELECTORAL_COUNTS_DIR, f'electoral_votes_{int(alpha * 100)}_{from_date}.json'),
                  'w') as f:
            json.dump(transition_elec_votes, f)

        # save the transition polling results
        with open(os.path.join(TRANSITION_POLLING_RESULTS_DIR, f'polling_results_{int(alpha * 100)}_{from_date}.json'),
                  'w') as f:
            json.dump(transition_polling_results, f)

    # create the transition frames
    figs_with_names = map_main(TRANSITION_POLLING_RESULTS_DIR, TRANSITION_ELECTORAL_COUNTS_DIR,
                               [TRANSITION_VISUALS_DIR],
                               color_norm=cn, color_maps=cms, return_not_save=True)

    for fig, name in figs_with_names:
        fig.savefig(os.path.join(TRANSITION_VISUALS_DIR, name))
        plt.close(fig)


class CustomNormalizer(Normalize):
    def __init__(self, vmin=None, vmax=None):
        super().__init__(vmin, vmax)

    def __call__(self, value, clip=None):
        result = value / COLOR_NORM_VMAX
        for val_i, val in enumerate(result):
            if val > 1.0:
                result[val_i] = 1.0
        return result

    def inverse(self, value):
        return 1.0 - self.__call__(value)


map_color_norm = CustomNormalizer()

cmap_r = colormaps['Reds']
cmap_b = colormaps['Blues']

map_color_maps = (cmap_r, cmap_b)

print("regenerating the daily_visuals with color normalization for video")
map_main(color_norm=map_color_norm, color_maps=map_color_maps)

# Loop through each pair of consecutive image files
for i in range(len(image_files) - 1):
    print(f'Creating transition frames for {image_files[i]} to {image_files[i + 1]}')
    img1 = cv2.imread(image_files[i])
    img2 = cv2.imread(image_files[i + 1])
    img1 = cv2.resize(img1, size)  # Resize the image
    img2 = cv2.resize(img2, size)  # Resize the image

    # Write the first image multiple times
    for _ in range(HOLD_FRAME_COUNT):
        video.write(img1)

    time.sleep(2)

    date1 = image_files[i].split('_')[-1].split('.')[0]
    date2 = image_files[i + 1].split('_')[-1].split('.')[0]

    create_transition_frames(TRANSITION_FRAME_COUNT, date1, date2, map_color_norm, map_color_maps)
    final_image_files = glob.glob(f'{TRANSITION_VISUALS_DIR}/*.png')


    def sort_key(f):
        return int(f.split('_')[-2])


    final_image_files.sort(key=sort_key)  # Sort the files
    # print("sorted order of final_image_files:")
    for file in final_image_files:
        # print(file)
        img = cv2.imread(file)
        video.write(img)

# Write the last image multiple times
img = cv2.imread(image_files[-1])
img = cv2.resize(img, size)  # Resize the image
for _ in range(HOLD_FRAME_COUNT):  # Show the last image for one second
    video.write(img)

print("Rendering video...")
# Release the video writer
video.release()

# Convert to mp4 using ffmpeg
subprocess.run(['C:\\Users\\philh\\ffmpeg\\bin\\ffmpeg.exe', '-i', f'{FINAL_VIDEOS_DIR}/maps/{date1_overall}_to_{date2_overall}_map.avi', f'{FINAL_VIDEOS_DIR}/maps/{date1_overall}_to_{date2_overall}_map.mp4'])

# Remove the .avi file
os.remove(f'{FINAL_VIDEOS_DIR}/maps/{date1_overall}_to_{date2_overall}_map.avi')

if SAVE_TO_GOOGLE_DRIVE:
    print("Uploading video to Google Drive...")
    # Copy the .mp4 file to Google Drive upload path
    shutil.copy(f'{FINAL_VIDEOS_DIR}/maps/{date1_overall}_to_{date2_overall}_map.mp4', f'{GOOGLE_DRIVE_UPLOAD_PATH}/{date1_overall}_to_{date2_overall}_map.mp4')
print("Done!")
