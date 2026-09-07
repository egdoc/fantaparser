# Fantaparser
#
# Author: Egidio Docile
#
# Parses fantacalcio.it quotations and grades.

import argparse
import json
import logging
import os
import sys
import urllib.error
import urllib.request
from importlib import resources

from bs4 import BeautifulSoup

from fantaparser.helpers import format_season, translate_role, write_frame, get_current_season_start_year


def parse_args() -> argparse.Namespace:
    def check_matchday_range(matchday: str = None) -> int:
        if matchday and matchday not in range(1, 39):
            raise argparse.ArgumentTypeError('Please specify a valid matchday')

        return int(matchday)

    def check_season_start_year(season_start_year) -> int:
        season_start_year = int(season_start_year)
        if season_start_year < 2015 or season_start_year > get_current_season_start_year():
            raise argparse.ArgumentTypeError('Please specify a valid season')

        return season_start_year


    parser = argparse.ArgumentParser(
        description='Parse fantacalcio.it grades and optionally quotations',
        epilog=('Before you use this script, ensure you have permission to scrape '
                'fantacalcio.it')
    )

    parser.add_argument(
        '-p', '--parsemap-file',
        metavar='FILE',
        help='Path to an alternative parsemap file',
        default=resources.files("fantaparser")/'data/parsemap.json'
    )

    parser.add_argument(
        '-d', '--day',
        help=('parse players grades for the specified matchday (1-38). By default, '
            'the script parses the last matchday of the season'),
        type=check_matchday_range,
    )

    parser.add_argument(
        '-c', '--csv',
        help='write results to csv file instead of json',
        action='store_true'
    )

    parser.add_argument(
        '-s', '--season',
        help=('the championship season starting year (e.g: for season 2026-27 just '
              'pass 2026). First valid year is 2015. Default to current season'),
        type=check_season_start_year,
        default=get_current_season_start_year()
    )

    parser.add_argument(
        '-v', '--verbose',
        help="run in verbose mode",
        action='store_true'
    )

    args = parser.parse_args()

    current_season = format_season()
    if format_season(args.season) != current_season and args.day is None:
        args.day = 38

    return args


def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    season = format_season(args.season)
    is_last_matchday = False

    try:
        with open(args.parsemap_file, 'r') as parsemap_file:
            parsemap = json.load(parsemap_file)
    except FileNotFoundError:
        logging.error(f'Could not find parsemap file.')
        return 1

    grades_url = f'{parsemap['grades']['base_url']}/{season}/{args.day or ""}'

    try:
        logging.info(f'Sending request to {grades_url}')
        with urllib.request.urlopen(grades_url) as response:
            soup = BeautifulSoup(response, features="html.parser")
    except urllib.error.HTTPError:
        logging.error("Cannot process request, aborting.")
        return 1

    matchdays_choices = soup.select('select#matchweek > option')
    matchday = int(soup.select_one('select#matchweek > option:checked')['value'])

    if len(matchdays_choices) == 0:
        logging.info(f'Grades for matchday not released yet.')
        return 0

    if args.day is None or args.day == len(matchdays_choices):
        is_last_matchday = True

    context = {
        "matchday": matchday,
        "season": season
    }

    grades = helpers.parse(soup, parsemap['grades'], context)

    if is_last_matchday:
        logging.info('Matchday is the last one in the season, parsing quotations')
        quotations_url = f'{parsemap['quotations']['base_url']}/{season}'

        try:
            logging.info(f'Sending request to {quotations_url}')
            with urllib.request.urlopen(quotations_url) as response:
                soup = BeautifulSoup(response, features="html.parser")
        except urllib.error.HTTPError:
            logging.error('Request failed, aborting.')
            return 1

        quotations = helpers.parse(soup, parsemap['quotations'], context)

        logging.info('Combining grades and quotations')
        grades = quotations.merge(
            grades,
            on='codice',
            how='left',
            suffixes=('', '_y')
        ).fillna(0)
        grades['giornata'] = matchday
        grades.drop(grades.filter(regex='_y$').columns, axis=1, inplace=True)


    target_file = os.path.abspath(f'season{season}_day{matchday}')
    write_frame(grades.sort_values(by=['ruolo', 'nome']), target_file, args.csv)
    logging.info(f'Grades saved to {target_file}')

    return 0


if __name__ == '__main__':
    sys.exit(main())