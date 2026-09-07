import os
import unittest
import pandas as pd
import subprocess
import sys


class TestGrades(unittest.TestCase):
    results_file = 'season2025-26_day38.json'

    def setUp(self):
        if not os.path.exists(self.results_file):
            subprocess.check_call([
                sys.executable, '-m', 'fantaparser',
                '--season=2025',
                '--verbose'
            ])

    def tearDown(self):
        try:
            os.remove(self.results_file)
        except FileNotFoundError:
            pass

    def testPlayerGrades(self):
        frame = pd.read_json(self.results_file, orient='records')
        elmas = frame.query('codice == 4479').to_dict('records')[0]

        self.assertEqual(
            elmas,
            {
                'codice': 4479,
                'nome': 'Elmas',
                'ruolo': 2,
                'club': 'napoli',
                'giornata': 38,
                'presenza': 1,
                'attivo': 1,
                'quotazione': 7,
                'voto_giornale': 5.5,
                'voto_fc': 5.5,
                'gol_segnati': 0,
                'gol_subiti': 0,
                'autogol': 0,
                'rigore_segnato': 0,
                'rigore_sbagliato': 0,
                'rigore_parato': 0,
                'assists': 0,
                'entrato_a_partita_iniziata': 0,
                'sostituito': 0,
                'titolare': 1,
                'ammonizione': 0,
                'espulsione': 0
            }
        )