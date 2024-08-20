import json
from constants import POLLING_RESULTS_DIR, ELECTORAL_VOTE_COUNTS_DIR
import os

from map import write_out_date
from simulate import fix_state_name

PD_DIFF_THRESHOLD = 0.75

# get the two newest polling results

fn1 = sorted([f for f in os.listdir(POLLING_RESULTS_DIR) if f.endswith('.json')])[-1]
fn2 = sorted([f for f in os.listdir(POLLING_RESULTS_DIR) if f.endswith('.json')])[-2]


with (open(os.path.join(POLLING_RESULTS_DIR, fn1), 'r') as f):
    p2 = json.load(f)
with (open(os.path.join(POLLING_RESULTS_DIR, fn2), 'r') as f):
    p1 = json.load(f)

# get the two newest electoral vote counts

fn1 = sorted([f for f in os.listdir(ELECTORAL_VOTE_COUNTS_DIR) if f.endswith('.json')])[-1]
fn2 = sorted([f for f in os.listdir(ELECTORAL_VOTE_COUNTS_DIR) if f.endswith('.json')])[-2]

with (open(os.path.join(ELECTORAL_VOTE_COUNTS_DIR, fn1), 'r') as f):
    e2 = json.load(f)
with (open(os.path.join(ELECTORAL_VOTE_COUNTS_DIR, fn2), 'r') as f):
    e1 = json.load(f)

date1 = fn1.split('.')[0].split('_')[-1]
date2 = fn2.split('.')[0].split('_')[-1]


def fix_point_diff(pd):
    return f'{pd:.1f}' if pd % 1 else f'{int(pd)}'


print(f'Comparing polling and election simulation results from dates {write_out_date(date2)} and {write_out_date(date1)}'
      f'\n')

for state in p1:

    winner1 = p1[state]['winner']
    winner2 = p2[state]['winner']

    old_pd = p1[state]['point_diff']
    new_pd = p2[state]['point_diff']

    if winner1 != winner2:
        print(f'{fix_state_name(state)} changed from {winner1} (with a {fix_point_diff(old_pd)} point lead) to {winner2} (with a {fix_point_diff(new_pd)} point lead)')

    elif old_pd > new_pd and (old_pd - new_pd)/old_pd > PD_DIFF_THRESHOLD:  # check for significant lead drops
        print(f"{winner1}'{'' if winner1 == 'Harris' else 's'} lead in {fix_state_name(state)} drops from {fix_point_diff(old_pd)} to {fix_point_diff(new_pd)}")

    elif old_pd < new_pd and (new_pd - old_pd)/old_pd > PD_DIFF_THRESHOLD:
        print(f"{winner1}'{'' if winner1 == 'Harris' else 's'} lead in {fix_state_name(state)} increases from {fix_point_diff(old_pd)} to {fix_point_diff(new_pd)}")

    old_used_biden = p1[state]['used_biden_2024_polling']
    old_used_2020 = p1[state]['used_2020_results']
    new_used_biden = p2[state]['used_biden_2024_polling']
    new_used_2020 = p2[state]['used_2020_results']

    if old_used_2020 and not new_used_2020 and new_used_biden and not old_used_biden:
        print('- after switching from using 2020 results to using Biden\'s 2024 polling')
    elif old_used_biden and not new_used_biden and new_used_2020 and not old_used_2020:
        print('- after switching from using Biden\'s 2024 polling to using 2020 results')
    elif old_used_biden and not new_used_biden and not new_used_2020 and not old_used_2020:
        print('- after switching from using Biden\'s 2024 polling to Harris\'')
    elif old_used_2020 and not new_used_2020 and not new_used_biden and not old_used_biden:
        print('- after switching from using 2020 results to Harris\' 2024 polling')

print('')

old_harris_count = e1['Harris']
new_harris_count = e2['Harris']
old_trump_count = e1['Trump']
new_trump_count = e2['Trump']

old_used_biden = e1['electoral_votes_where_we_used_biden_2024']
old_used_2020 = e1['electoral_votes_where_we_used_2020_results']
new_used_biden = e2['electoral_votes_where_we_used_biden_2024']
new_used_2020 = e2['electoral_votes_where_we_used_2020_results']

if old_used_biden != new_used_biden:
    print(f"Electoral votes where we used Biden's 2024 polling changed from {old_used_biden} to {new_used_biden}")
if old_used_2020 != new_used_2020:
    print(f"Electoral votes where we used 2020 results changed from {old_used_2020} to {new_used_2020}")

if old_harris_count != new_harris_count:
    print(f"Harris overall: {old_harris_count} -> {new_harris_count}")

if old_trump_count != new_trump_count:
    print(f"Trump overall: {old_trump_count} -> {new_trump_count}")

if old_harris_count == new_harris_count and old_trump_count == new_trump_count:
    print('No changes in overall electoral vote counts')

old_winner = 'Harris' if old_harris_count > old_trump_count else 'Trump'
new_winner = 'Harris' if new_harris_count > new_trump_count else 'Trump'

if old_winner != new_winner:
    print(f"The overall winner changed from {old_winner} to {new_winner}")
