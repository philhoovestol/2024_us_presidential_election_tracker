# polling information

STATE_AND_THEIR_ELECTORAL_VOTES = {
    "alabama": 9,
    "alaska": 3,
    "arizona": 11,
    "arkansas": 6,
    "california": 54,
    "colorado": 10,
    "connecticut": 7,
    "delaware": 3,
    "florida": 30,
    "georgia": 16,
    "hawaii": 4,
    "idaho": 4,
    "illinois": 19,
    "indiana": 11,
    "iowa": 6,
    "kansas": 6,
    "kentucky": 8,
    "louisiana": 8,
    "maine": 4,
    "maryland": 10,
    "massachusetts": 11,
    "michigan": 15,
    "minnesota": 10,
    "mississippi": 6,
    "missouri": 10,
    "montana": 4,
    "nebraska": 5,
    "nevada": 6,
    "new-hampshire": 4,
    "new-jersey": 14,
    "new-mexico": 5,
    "new-york": 28,
    "north-carolina": 16,
    "north-dakota": 3,
    "ohio": 17,
    "oklahoma": 7,
    "oregon": 8,
    "pennsylvania": 19,
    "rhode-island": 4,
    "south-carolina": 9,
    "south-dakota": 3,
    "tennessee": 11,
    "texas": 40,
    "utah": 6,
    "vermont": 3,
    "virginia": 13,
    "washington": 12,
    "district-of-columbia": 3,
    "west-virginia": 4,
    "wisconsin": 10,
    "wyoming": 3
}

STATES_AND_2020_OUTCOME = {
    "alabama": ("Trump", 25.5),
    "alaska": ("Trump", 10.1),
    "arizona": ("Biden", 0.3),
    "arkansas": ("Trump", 27.7),
    "california": ("Biden", 29.2),
    "colorado": ("Biden", 13.5),
    "connecticut": ("Biden", 20.4),
    "delaware": ("Biden", 19.0),
    "florida": ("Trump", 3.4),
    "georgia": ("Biden", 0.2),
    "hawaii": ("Biden", 29.5),
    "idaho": ("Trump", 30.8),
    "illinois": ("Biden", 17.0),
    "indiana": ("Trump", 16.1),
    "iowa": ("Trump", 8.2),
    "kansas": ("Trump", 14.7),
    "kentucky": ("Trump", 26.0),
    "louisiana": ("Trump", 19.6),
    "maine": ("Biden", 9.1),
    "maryland": ("Biden", 33.2),
    "massachusetts": ("Biden", 33.5),
    "michigan": ("Biden", 2.8),
    "minnesota": ("Biden", 7.1),
    "mississippi": ("Trump", 16.5),
    "missouri": ("Trump", 15.4),
    "montana": ("Trump", 16.4),
    "nebraska": ("Trump", 19.1),
    "nevada": ("Biden", 2.4),
    "new-hampshire": ("Biden", 7.4),
    "new-jersey": ("Biden", 15.9),
    "new-mexico": ("Biden", 10.8),
    "new-york": ("Biden", 23.1),
    "north-carolina": ("Trump", 1.3),
    "north-dakota": ("Trump", 34.1),
    "ohio": ("Trump", 8.0),
    "oklahoma": ("Trump", 33.1),
    "oregon": ("Biden", 16.1),
    "pennsylvania": ("Biden", 1.2),
    "rhode-island": ("Biden", 20.8),
    "south-carolina": ("Trump", 11.7),
    "south-dakota": ("Trump", 26.2),
    "tennessee": ("Trump", 23.2),
    "texas": ("Trump", 5.6),
    "utah": ("Trump", 20.5),
    "vermont": ("Biden", 35.4),
    "virginia": ("Biden", 10.1),
    "washington": ("Biden", 19.2),
    "district-of-columbia": ("Biden", 86.8),
    "west-virginia": ("Trump", 38.9),
    "wisconsin": ("Biden", 0.6),
    "wyoming": ("Trump", 43.4)
}

# Directory where polling results are stored
POLLING_RESULTS_DIR = 'polling_results/'

# Directory where electoral vote counts are stored
ELECTORAL_VOTE_COUNTS_DIR = 'electoral_vote_counts/'


# images/plots

BOX_COLOR = 'white'
BOX_TRANSPARENCY = 0.55

COLOR_NORM_VMIN = 0
COLOR_NORM_VMAX = 22.5  # the closer to zero, the more intense the colors in the map

ADD_TITLE = True

DAILY_VISUALS_DIR = 'daily_maps'

SOURCE_IMAGES_DIR = 'source_images'
BACKGROUND_IMAGE = 'trump_harris_1_of_2.png'

DAILY_PLOTS_DIR = 'daily_plots'

PLOT_LAST_N_ONLY = None


# animations

ANIMATE_LAST_N_ONLY = None

TRANSITION_FRAMES_DIR = 'transition_frames'
TRANSITION_POLLING_RESULTS_DIR = f'{TRANSITION_FRAMES_DIR}/polling_results'
TRANSITION_VISUALS_DIR = f'{TRANSITION_FRAMES_DIR}/daily_visuals'
TRANSITION_ELECTORAL_COUNTS_DIR = f'{TRANSITION_FRAMES_DIR}/electoral_vote_counts'

FINAL_VIDEOS_DIR = 'videos'

HOLD_FRAME_COUNT = 20
TRANSITION_FRAME_COUNT = 10


GOOGLE_DRIVE_UPLOAD_PATH = "G:\\My Drive\\election_sims_2024\\today"
SAVE_TO_GOOGLE_DRIVE = True  # whether animate_map.py and plot.py will upload to Google Drive
