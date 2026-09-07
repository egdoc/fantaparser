import datetime
import logging
import re
import sys

import bs4
import pandas as pd


def float_comma(value: str) -> str:
    return value.replace(",", ".")


def get_current_season_start_year() -> int:
    now = datetime.datetime.now()
    # Season starts in september
    if now.month >= 9:
        return now.year

    return now.year - 1


def format_season(start_year: int = None) -> str:
    if start_year is None:
        start_year = get_current_season_start_year()

    return f'{start_year}-{str(start_year + 1)[-2:]}'


def translate_role(role: str) -> str:
    role_map = {
        'p': 0,
        'd': 1,
        'c': 2,
        'a': 3,
    }

    return str(role_map[role])


def translate_office_grade(vote: str) -> str:
    if vote == '55':
        vote = "0"

    return vote


def write_frame(dataframe: pd.DataFrame, filename: str, csv=False) -> None:
    if csv:
        dataframe.to_csv(f'{filename}.csv', index=False, sep="|")

    else:
        dataframe.to_json(
            f'{filename}.json',
            orient='records',
            indent=4
        )


def parse(soup: bs4.BeautifulSoup, parse_map: dict, context: dict) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    rows = []

    for tr in soup.select(parse_map['container']['selector']):
        row = {}

        for field, desc in parse_map['fields'].items():
            logger.debug(f'Processing {field}: {desc}')

            if "value" in desc:
                value = desc['value']
                if isinstance(value, str):
                    value = value.format(**context)

                row[field] = value
                continue

            element = tr.select_one(desc['selector'])

            if "extract" in desc:
                value = element.text if desc['extract'] == 'text' else element[desc['extract']]

                if 'extract_regex' in desc:
                    regex = desc['extract_regex'].format(**context)
                    value = re.search(regex, value).group(1)

                if 'replace_regex' in desc:
                    regex = desc['replace_regex']
                    value = re.sub(regex, desc['replace_value'], value)

                for func in desc.get('transform_functions', []):
                    func = getattr(sys.modules[__name__], func)
                    value = func(value)

            else:
                value = bool(element) if not desc.get('invert', False) else not bool(element)

            row[field] = value

        rows.append(row)


    data_type_map = dict(zip(
        parse_map['fields'].keys(),
        map(lambda x: x.get('data_type', 'unicode'), parse_map['fields'].values())
    ))

    return pd.DataFrame(rows).astype(data_type_map)