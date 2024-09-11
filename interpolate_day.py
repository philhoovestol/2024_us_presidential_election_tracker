import json

from constants import POLLING_RESULTS_DIR, ELECTORAL_VOTE_COUNTS_DIR

from simulate import simulate_election

day_before = '2024-08-23'
day_after = '2024-08-25'
day_to_create = '2024-08-24'

# Load the polling results from the day before and after
with open(f'{POLLING_RESULTS_DIR}/{day_before}.json') as f:
    polling_results_day_before = json.load(f)
with open(f'{POLLING_RESULTS_DIR}/{day_after}.json') as f:
    polling_results_day_after = json.load(f)

# Create new polling results by interpolating between the two days
interpolated_polling_results = {}
for state in polling_results_day_before:
    # Interpolate the winner
    winner_day_before = polling_results_day_before[state]['winner']
    winner_day_after = polling_results_day_after[state]['winner']
    point_diff_day_before = polling_results_day_before[state]['point_diff']
    point_diff_day_after = polling_results_day_after[state]['point_diff']
    if winner_day_after == winner_day_before:

        # Interpolate the point difference
        interpolated_point_diff = point_diff_day_before + (point_diff_day_after - point_diff_day_before) / 2

        interpolated_polling_results[state] = {
            'winner': winner_day_before,
            'point_diff': interpolated_point_diff
        }
    else:
        interpolated_polling_results[state] = {
            'winner': winner_day_before if point_diff_day_before > point_diff_day_after else winner_day_after,
            'point_diff': point_diff_day_before - (point_diff_day_before + point_diff_day_after) / 2 if point_diff_day_before > point_diff_day_after else point_diff_day_after - (point_diff_day_before + point_diff_day_after) / 2
        }

interpolated_polling_results['is_interpolated'] = True

# Save the interpolated polling results
with open(f'{POLLING_RESULTS_DIR}/{day_to_create}.json', 'w') as f:
    json.dump(interpolated_polling_results, f, indent=4)

print(f'Interpolated polling results for {day_to_create} saved to {POLLING_RESULTS_DIR}/{day_to_create}.json')

# get electoral votes outcomes from before and after days
with open(f'{ELECTORAL_VOTE_COUNTS_DIR}/{day_before}.json') as f:
    electoral_votes_day_before = json.load(f)
with open(f'{ELECTORAL_VOTE_COUNTS_DIR}/{day_after}.json') as f:
    electoral_votes_day_after = json.load(f)

# create new electoral vote outcome by simulating election with interpolated polling results
electoral_votes_where_we_used_biden_2024_polling = electoral_votes_day_after['electoral_votes_where_we_used_biden_2024_polling']
electoral_votes_where_we_used_2020_outcome = electoral_votes_day_after['electoral_votes_where_we_used_2020_outcome']
electoral_votes_filename = f'electoral_votes_{day_to_create}.json'
simulate_election(interpolated_polling_results, electoral_votes_filename, electoral_votes_where_we_used_biden_2024_polling,
                  electoral_votes_where_we_used_2020_outcome)

print(f'Electoral vote counts for {day_to_create} saved to {ELECTORAL_VOTE_COUNTS_DIR}/{electoral_votes_filename}')