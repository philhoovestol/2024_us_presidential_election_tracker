import matplotlib.pyplot as plt
from constants import BOX_COLOR, BOX_TRANSPARENCY, POLLING_RESULTS_DIR, ELECTORAL_VOTE_COUNTS_DIR

import os
import json


def get_max_votes():
    # Determine the maximum number of electoral votes
    max_votes = 0
    for fn in os.listdir(POLLING_RESULTS_DIR):
        if fn.endswith('.json'):
            # Load electoral vote counts
            with open(os.path.join(ELECTORAL_VOTE_COUNTS_DIR,
                                   fn.replace('polling_results', 'electoral_votes'))) as file:
                electoral_vote_counts = json.load(file)
            max_votes = max(max_votes, max(electoral_vote_counts.values()))
    return max_votes


def plot_horizontal_bar(fig, ax, val1, val2):

    # Plot the bar
    ax.barh(0, val1, color='tab:red', edgecolor='none', height=0.5, label='Republicans')
    ax.barh(0, val2, color='tab:blue', left=val1, edgecolor='none', height=0.5, label='Democrats')

    # Remove axes and ticks
    ax.axis('off')

    gap_size = 1

    # Add text labels
    ax.text(-gap_size, 0.5, f'Trump : {int(val1)}', color='black', va='center', ha='left', fontsize=30)
    ax.text(val1 + val2 + gap_size, 0.5, f'Harris : {int(val2)}', color='black', va='center', ha='right', fontsize=30)

    # Calculate the midpoint
    midpoint = (val1 + val2) / 2

    # Add a marker at the midpoint
    ax.plot(midpoint, 0.5, marker='v', color='black', markersize=30, zorder=10)

    # Adjust the plot limits and display
    ax.set_xlim(-gap_size, val2 + val1 + gap_size)
    ax.set_ylim(-1, 1)  # Ensure the text labels are within the y-axis limits

    # Add the rectangle to the figure as background
    fig.patches.extend([plt.Rectangle((0.03, 0.755), .94, 0.15,
                                      fill=True, color=BOX_COLOR, alpha=BOX_TRANSPARENCY, zorder=-3,
                                      transform=fig.transFigure, figure=fig)])
    fig.patches.extend([plt.Rectangle((0.03, 0.755), .94, 0.15,
                                      fill=False, color='black', alpha=0.8, zorder=-1,
                                      transform=fig.transFigure, figure=fig, linewidth=1.5)])


def plot_vertical_bars(fig, ax, electoral_vote_count_data):

    max_votes = get_max_votes()

    # Create a bar chart
    ax.set_facecolor('none')  # make the facecolor transparent
    candidates = ['Trump', 'Harris']
    votes = [electoral_vote_count_data['Trump'], electoral_vote_count_data['Harris']]
    colors = ['tab:red', 'tab:blue']
    bars = ax.bar(candidates, votes, color=colors, alpha=0.6, zorder=5)
    ax.set_ylabel('Electoral Votes')

    # Add labels to the bars
    for bar, vote in zip(bars, votes):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(vote), ha='center', va='bottom')

    # Set the limits of the y-axis
    ax.set_ylim([0, max_votes])

    # Remove x-axis labels
    ax.set_xticklabels([])

    # Add the rectangle to the axes for the bar chart
    fig.patches.extend([plt.Rectangle((0.03, 0.57), 0.94, 0.335,
                                      fill=True, color=BOX_COLOR, alpha=BOX_TRANSPARENCY, zorder=-3,
                                      transform=fig.transFigure, figure=fig)])
    fig.patches.extend([plt.Rectangle((0.03, 0.57), 0.94, 0.335,
                                      fill=False, color='black', alpha=0.8, zorder=-1,
                                      transform=fig.transFigure, figure=fig, linewidth=1.5)])