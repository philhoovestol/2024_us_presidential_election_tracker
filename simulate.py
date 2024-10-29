# for each state in the US, go to https://projects.fivethirtyeight.com/polls/[state] and read the winner of the most
# recent polling match up between Trump and Harris. If there is none, try Trump and Biden. If nothing there, use 2020
# results.

import json
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from pprint import pprint
import time

from constants import (
    STATE_AND_THEIR_ELECTORAL_VOTES, STATES_AND_2020_OUTCOME, POLLING_RESULTS_DIR, ELECTORAL_VOTE_COUNTS_DIR
)


def fix_state_name(s):
    return s.replace('-', ' ').title()


def contains_our_candidates(cells, dem='Harris'):
    found_trump = False
    found_dem = False
    for cell in cells:
        if 'Trump' in cell.text:
            found_trump = True
        if dem in cell.text:
            found_dem = True
    return found_trump and found_dem


def get_point_diff(r):
    return int(r.find_element(By.CLASS_NAME, 'net').text.strip())


def parse_date_string(date_string):
    if date_string.startswith('Polls ending '):
        date_string = date_string.replace('Polls ending ', '')
    if 'Sept' in date_string:
        date_string = date_string.replace('Sept', 'Sep')
    if date_string == 'today':
        return datetime.now().date()
    try:
        cur_date = datetime.strptime(date_string, '%B %d, %Y').date()
    except ValueError:
        try:
            cur_date = datetime.strptime(date_string, '%b. %d, %Y').date()
        except ValueError:
            print(f"Could not parse date: {date_string}")
            return None
    return cur_date


def gather_results(polls_counted, dem_total, s, dem, return_first, weeks_back):
    if polls_counted > 0:
        if dem_total == 0:  # it's a tie
            if not return_first:
                print(f"Tie in {fix_state_name(s)} after averaging {polls_counted} poll"
                      f"{'' if polls_counted == 1 else 's'}. Trying just the most recent poll...")
                return find_polled_winner(s, dem=dem, return_first=True, weeks_back=weeks_back)
            else:  # we tried returning the first poll, but no poll with a winner was found
                return None, None
        else:  # we have a winner
            return ('Harris', dem_total / polls_counted) if dem_total > 0 else ('Trump', -dem_total /
                                                                                polls_counted)
    else:
        return None, None  # no poll with a winner was found in given time frame


# Average polling results from the past week for the given state, as taken from fivethirtyeight.com, between
# Trump and the given Democratic candidate. If the average is a tie, return the winner of the most recent poll.
# Returns the winner and the average point differential.
def find_polled_winner(s, dem='Harris', return_first=False, weeks_back=1):
    try:
        url = f'https://projects.fivethirtyeight.com/polls/{s}'
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(2)
        search_text = f'{dem} trump'
        search = driver.find_element(By.ID, 'search-box')
        search.send_keys(search_text)
        polls = driver.find_element(By.CLASS_NAME, 'polls')
        polls_children = polls.find_elements(By.XPATH, ".//*")

        dem_total = 0
        polls_counted = 0

        min_date = datetime.now().date() - timedelta(weeks=weeks_back)

        for child in polls_children:
            if child.get_attribute('class') == 'day-container':

                header_text = child.find_element(By.CLASS_NAME, 'poll-group-hed').text.strip()
                if '2024' not in header_text:  # skip polls not for 2024 election
                    continue

                rows = child.find_elements(By.CLASS_NAME, 'visible-row')
                for row in rows:
                    cells = row.find_elements(By.CLASS_NAME, 'answer')
                    if contains_our_candidates(cells, dem=dem):
                        polls_counted += 1
                        w = row.find_element(By.CLASS_NAME, 'leader').text.strip()
                        if w:
                            point_diff = get_point_diff(row)
                            if return_first:
                                return w, point_diff
                            if w == 'Trump':
                                dem_total -= point_diff
                            else:
                                dem_total += point_diff

            if child.get_attribute('class') == 'date':

                # check which date we're on
                date_string = child.text.strip()
                cur_date = parse_date_string(date_string)

                if cur_date and cur_date >= min_date:
                    print(f"Checking polls from {date_string} for {fix_state_name(s)}...")
                    continue
                else:
                    if cur_date and cur_date < min_date:  # we're done
                        return gather_results(polls_counted, dem_total, s, dem, return_first, weeks_back)

        # for case when last poll is within our time frame
        return gather_results(polls_counted, dem_total, s, dem, return_first, weeks_back)

    except StaleElementReferenceException:
        print(f"Stale element reference exception for {fix_state_name(s)}. Trying again...")
        return find_polled_winner(s, dem, return_first, weeks_back)


def simulate_election(polling_results, output_filename, electoral_votes_where_we_used_biden_2024, electoral_votes_where_we_used_2020_results):
    trump_votes = 0
    harris_votes = 0
    for state, state_polling_result in polling_results.items():
        state_winner = state_polling_result['winner']
        if state_winner == 'Trump':
            trump_votes += STATE_AND_THEIR_ELECTORAL_VOTES[state.lower()]
        else:
            harris_votes += STATE_AND_THEIR_ELECTORAL_VOTES[state.lower()]

    if trump_votes > harris_votes:
        print(f'Trump wins the election with {trump_votes} electoral votes, where Harris received {harris_votes} votes')
    elif harris_votes > trump_votes:
        print(f'Harris wins the election with {harris_votes} electoral votes, where Trump received {trump_votes} votes')
    else:
        print(f'The election is a... tie? at {harris_votes} votes each')

    # save the number of electoral votes each candidate received to a file called 'electoral_votes.json'
    final_counts = {
        'Trump': trump_votes,
        'Harris': harris_votes
    }

    final_counts['electoral_votes_where_we_used_biden_2024'] = electoral_votes_where_we_used_biden_2024
    final_counts['electoral_votes_where_we_used_2020_results'] = electoral_votes_where_we_used_2020_results

    with open(f'{ELECTORAL_VOTE_COUNTS_DIR}/{output_filename}', 'w') as f:
        json.dump(final_counts, f)


def main():
    print('Getting polling results for each state...')

    start_time = datetime.now()

    polling_results = {}

    electoral_votes_where_we_used_biden_2024 = 0
    electoral_votes_where_we_used_2020_results = 0
    for state in STATE_AND_THEIR_ELECTORAL_VOTES.keys():

        used_biden_2024_polling = False
        used_2020_results = False

        winner, pd = find_polled_winner(state)
        cur_weeks_back = 1
        while not winner and cur_weeks_back < 16:
            print(f"No decisive Harris/Trump polling data found for last {cur_weeks_back} weeks in {fix_state_name(state)}. "
                  f"Searching the last {cur_weeks_back * 2} weeks.")
            cur_weeks_back *= 2
            winner, pd = find_polled_winner(state, weeks_back=cur_weeks_back)
        if not winner:
            print(f"No decisive Harris/Trump polling data found for last {cur_weeks_back} weeks in {fix_state_name(state)}. "
                  f"Searching the last year. Will use numbers from first poll found.")
            winner, pd = find_polled_winner(state, return_first=True, weeks_back=52)

        if not winner:
            print(f"No decisive Harris/Trump polling data found for last year in {fix_state_name(state)}.")
            print(f"Trying Biden instead of Harris, going back one year. Will use numbers from first poll found.")
            winner, pd = find_polled_winner(state, dem='Biden', return_first=True, weeks_back=52)
            if winner:
                used_biden_2024_polling = True
                electoral_votes_where_we_used_biden_2024 += STATE_AND_THEIR_ELECTORAL_VOTES[state]

        if not winner:
            past_winner, pd = STATES_AND_2020_OUTCOME[state]
            print(f'No decisive polling data found for {fix_state_name(state)}. Using 2020 result, where {past_winner} won.')
            used_2020_results = True
            winner = 'Harris' if past_winner == 'Biden' else 'Trump'
            electoral_votes_where_we_used_2020_results += STATE_AND_THEIR_ELECTORAL_VOTES[state]

        polling_result = {
            'winner': 'Harris' if winner == 'Biden' else winner,
            'point_diff': pd,
            'used_biden_2024_polling': used_biden_2024_polling,
            'used_2020_results': used_2020_results,
        }

        print(f'Averaged polling data found for {fix_state_name(state)}: {polling_result}')
        polling_results[state] = polling_result

    print(
        f"Polling results, where\n"
        f"{electoral_votes_where_we_used_biden_2024} electoral votes had Biden as the nominee\n"
        f"{electoral_votes_where_we_used_2020_results} electoral votes used 2020 results\n"
    )
    pprint(polling_results)

    with open(f'{POLLING_RESULTS_DIR}/polling_results_{start_time.strftime("%Y-%m-%d")}.json', 'w') as f:
        json.dump(polling_results, f)

    print(f"Polling results saved to polling_results_{start_time.strftime('%Y-%m-%d')}.json")

    # using polling_results, count up how many electoral votes each candidate would get if the election were held with
    # those results to simulate the election. Print out the winner of the election and the number of electoral votes they
    # received.

    print('Simulating the election...')

    electoral_votes_filename = f'electoral_votes_{start_time.strftime("%Y-%m-%d")}.json'
    simulate_election(polling_results, electoral_votes_filename, electoral_votes_where_we_used_biden_2024, electoral_votes_where_we_used_2020_results)

    print(f"Electoral votes saved to {electoral_votes_filename}")

    print(f"Time taken: {datetime.now() - start_time}")


if __name__ == '__main__':
    main()
