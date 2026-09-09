# Fantaparser
This little tool can be used to parse grades and quotations from fantacalcio.it, for all the available
seasons and matchdays.

## Installation
You can install fantaparser with pip. Clone the repository or download the latest release archive, extract it,
enter the extracted directory and run:

```$ pip install .```

Alternatively, you can install directly from GitHub by running:

```$ pip install git+https://github.com/egdoc/fantaparser```

## Usage
To parse grades and quotations from the latest matchday of the current season, just invoke the script
without any option:

```$ fantaparser```

Grades and quotations will be merged in order to produce a file similar to those which used to be
provided by Maxi Manager of Gazzetta dello Sport. Since on fantacalcio.it quotations are updated in place,
they are merged only when parsing the latest matchday.

By default, the script stores the parsing results in a .json file in the current working directory. If you
prefer using the csv format, just run the script with the `-c` option.

### Parse a specific matchday
To parse grades for a specific matchday just use the `-d` option and pass the matchday as argument. To parse
the grades relative to the 2 matchday of the current season, for example, you would run:

```$ fantaparser -d 2```

To parse grades of a specific season, you use the `-s` option, instead. Just as an example, to parse
grades for the latest matchday of the 2025-2026 season, you would provide the **starting** year of the 
season as argument:

```$ fantaparser -s 2025```

You can parse the grades of a specific matchday of a specific season, by combining the two options. To 
parse the grades of the 2 matchday of the 2025-2026, season, you would run:

```$ fantaparser -s 2025 -d 2```