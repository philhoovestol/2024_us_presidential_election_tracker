import geopandas as gpd
import matplotlib.pyplot as plt
import json
import os

import numpy as np
import pandas as pd

from matplotlib.colors import Normalize, AsinhNorm
from shapely.affinity import scale, translate
import matplotlib.image as mpimg
import matplotlib.patches as patches

from bar import plot_horizontal_bar

from constants import (
    BOX_COLOR, BOX_TRANSPARENCY, GOOGLE_DRIVE_UPLOAD_PATH, DAILY_MAPS_DIR,
    ELECTORAL_VOTE_COUNTS_DIR, POLLING_RESULTS_DIR, SOURCE_IMAGES_DIR, BACKGROUND_IMAGE, ADD_TITLE
)


def fix_state_name(n):
    return n.replace('-', ' ').upper()


def write_out_date(date):
    year, month, day = date.split('-')
    month_dict = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
                  '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
    return f'{month_dict[month]} {int(day)}, {year}'


def main(poll_res_dir=POLLING_RESULTS_DIR, elec_votes_dir=ELECTORAL_VOTE_COUNTS_DIR, out_dirs=None,
         color_maps=None, return_not_save=False):
    if out_dirs is None:
        out_dirs = [DAILY_MAPS_DIR]

    # Set default font
    plt.rcParams['font.size'] = 22
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['axes.labelweight'] = 'bold'

    # Load US states shapefile
    us_states = gpd.read_file(f'{SOURCE_IMAGES_DIR}/States_shapefile.shp')

    # Translate Hawaii
    us_states.loc[us_states['State_Name'] == 'HAWAII', 'geometry'] = us_states.loc[
        us_states['State_Name'] == 'HAWAII', 'geometry'].apply(lambda geom: translate(geom, xoff=15, yoff=5))

    # Get the bounds of Alaska
    alaska_bounds = us_states.loc[us_states['State_Name'] == 'ALASKA', 'geometry'].bounds

    # Get the bottom right corner of Alaska
    alaska_bottom_right = (alaska_bounds['maxx'].values[0], alaska_bounds['miny'].values[0])

    # Scale Alaska
    us_states.loc[us_states['State_Name'] == 'ALASKA', 'geometry'] = us_states.loc[
        us_states['State_Name'] == 'ALASKA', 'geometry'].apply(
        lambda geom: scale(geom, xfact=0.5, yfact=0.5, origin=alaska_bottom_right))
    us_states.loc[us_states['State_Name'] == 'HAWAII', 'geometry'] = us_states.loc[
        us_states['State_Name'] == 'HAWAII', 'geometry'].apply(
        lambda geom: scale(geom, xfact=1.2, yfact=1.2, origin='center'))

    for output_dir in out_dirs:
        os.makedirs(output_dir, exist_ok=True)

    filenames = os.listdir(poll_res_dir)

    def sort_key(f):
        res = None
        for part in f.split('.')[0].split('_'):
            res = part
            if part.isdigit():
                return int(part)
        return res

    filenames.sort(key=sort_key)
    result = []
    # Iterate over polling results files
    for filename in filenames:
        if filename.endswith('.json'):
            # Load polling results
            with open(os.path.join(poll_res_dir, filename)) as f:
                polling_results = json.load(f)

            # Create a DataFrame from polling results
            df_polling_results = pd.DataFrame(polling_results).T.reset_index().rename(columns={'index': 'state'})

            # Fix state names
            df_polling_results['state'] = df_polling_results['state'].apply(fix_state_name)

            # Merge geopandas DataFrame with polling results
            merged_states = us_states.set_index('State_Name').join(df_polling_results.set_index('state'))

            # Create a map
            fig, axes = plt.subplots(2, figsize=(16, 16), gridspec_kw={'height_ratios': [1, 5]})
            # Adjust subplot parameters to reduce side margins
            plt.subplots_adjust(left=0.05, right=0.95)
            stretch_amount = 2.5

            # Create a rectangle with the desired color and transparency
            rectangle = patches.Rectangle(
                (merged_states.total_bounds[0] - stretch_amount, merged_states.total_bounds[1] - stretch_amount),
                merged_states.total_bounds[2] - merged_states.total_bounds[0] + stretch_amount * 2,
                merged_states.total_bounds[3] - merged_states.total_bounds[1] + stretch_amount * 2, facecolor=BOX_COLOR,
                alpha=BOX_TRANSPARENCY, zorder=-3)
            # Add the rectangle to the axes for the map
            axes[1].add_patch(rectangle)
            # Create outer rectangle with the desired color and transparency
            rectangle = patches.Rectangle(
                (merged_states.total_bounds[0] - stretch_amount, merged_states.total_bounds[1] - stretch_amount),
                merged_states.total_bounds[2] - merged_states.total_bounds[0] + stretch_amount * 2,
                merged_states.total_bounds[3] - merged_states.total_bounds[1] + stretch_amount * 2, facecolor='black',
                alpha=0.8, fill=False, zorder=-1, linewidth=1.5)
            # Add the rectangle to the axes for the map
            axes[1].add_patch(rectangle)

            harris_states = merged_states.loc[(merged_states['winner'] == 'Harris')]
            trump_states = merged_states.loc[(merged_states['winner'] == 'Trump')]

            # Function to get color for each state
            def get_state_color(state):

                # create point_diff to color mapping
                def map_value_to_color(x):
                    if x <= 2000:
                        return x / 3333.33  # Maps 0-2000 (pd of 0-20) to 0-0.6
                    elif x <= 2500:
                        return 0.6 + (x - 2000) / 5000  # Maps 2001-2500 (pd of 20-25) to 0.6-0.7
                    else:
                        return 0.7 + (x - 2500) / 24997  # Maps 2501-9999 (pd of 25 to 100) to 0.7-1

                if state in harris_states.index:
                    return color_maps[1](map_value_to_color(harris_states.loc[state, 'point_diff'] * 100))
                if state in trump_states.index:
                    return color_maps[0](map_value_to_color(trump_states.loc[state, 'point_diff'] * 100))
                print(f'Warning: {state} not found in either harris_states or trump_states')
                return 'white'

            # Apply the color to each state in the DataFrame
            harris_states.loc[:, 'color'] = harris_states.index.map(get_state_color)
            trump_states.loc[:, 'color'] = trump_states.index.map(get_state_color)

            # Plot the states with the specified colors
            harris_states.plot(color=harris_states['color'], linewidth=0.8, ax=axes[1], edgecolor='0.8', zorder=5)
            trump_states.plot(color=trump_states['color'], linewidth=0.8, ax=axes[1], edgecolor='0.8', zorder=5)

            # remove the axes labels from the map
            axes[1].axis('off')

            # states_of_interest = ['ARIZONA', 'MICHIGAN', 'FLORIDA', 'WISCONSIN', "NEW YORK", "COLORADO"]
            # print(f'Polling results for {filename}:')
            # for state in states_of_interest:
            #     print(f'{state}: {merged_states.loc[state, "winner"]}, by {merged_states.loc[state, "point_diff"]}')
            # print("")

            # Plot the horizontal bar chart
            with open(os.path.join(elec_votes_dir, filename.replace('polling_results', 'electoral_votes'))) as file:
                electoral_vote_counts = json.load(file)
            plot_horizontal_bar(fig, axes[0], electoral_vote_counts['Trump'], electoral_vote_counts['Harris'])

            # Load the image
            img = mpimg.imread(f'{SOURCE_IMAGES_DIR}/{BACKGROUND_IMAGE}')

            background_ax = plt.axes((0, 0, 1, 1))  # create a dummy subplot for the background
            background_ax.set_zorder(-5)  # set the background subplot behind the others
            background_ax.imshow(img, aspect='auto')  # show the background image

            # Set the title of the figure
            date = filename.split('_')[-1].split('.')[0]
            if ADD_TITLE:
                fig.suptitle(f'2024 election outcome based on most recent polling as of {write_out_date(date)}',
                             fontsize=25, weight='semibold', y=0.95)
                fig.patches.extend([plt.Rectangle((0.03, 0.92), 0.94, 0.05,
                                                  fill=True, color=BOX_COLOR, alpha=BOX_TRANSPARENCY, zorder=-3,
                                                  transform=fig.transFigure, figure=fig)])
                fig.patches.extend([plt.Rectangle((0.03, 0.92), 0.94, 0.05,
                                                  fill=False, color='black', alpha=0.8, zorder=-1,
                                                  transform=fig.transFigure, figure=fig, linewidth=1.5)])

            if return_not_save:
                result.append([fig, f'{filename[:-5]}.png'])
                continue

            # Save the map
            for output_dir in out_dirs:
                fig.savefig(os.path.join(output_dir, f'{filename[:-5]}.png'))

            plt.close(fig)

    if return_not_save:
        return result


if __name__ == '__main__':
    cmap_r = plt.colormaps['Reds']
    cmap_b = plt.colormaps['Blues']
    map_color_maps = (cmap_r, cmap_b)
    main(color_maps=map_color_maps)
