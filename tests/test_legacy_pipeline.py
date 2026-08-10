import contextlib
import io
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

import pandas as pd

import champion_matrix
import champion_relation
import data_preprocess


ROOT = Path(__file__).resolve().parents[1]


class LegacyPipelineTests(unittest.TestCase):
    def setUp(self):
        self._previous_cwd = Path.cwd()
        self._temp_dir = tempfile.TemporaryDirectory()
        os.chdir(self._temp_dir.name)
        self.db_path = Path('lola.db')
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.executescript((ROOT / 'sqlite_schema.sql').read_text())

    def tearDown(self):
        os.chdir(self._previous_cwd)
        self._temp_dir.cleanup()

    def _insert_participant(
        self,
        conn,
        match_id,
        participant_id,
        champion,
        *,
        kills=0,
        deaths=0,
        assists=0,
        participant_win=0,
    ):
        columns = conn.execute('PRAGMA table_info(Participant)').fetchall()
        overrides = {
            'summoner_id': '{}-{}'.format(match_id, participant_id),
            'match_id': str(match_id),
            'participant_id': str(participant_id),
            'side': 'blue' if participant_id <= 5 else 'red',
            'champion': champion,
            'summoner_spell_d': 'spell-d',
            'summoner_spell_f': 'spell-f',
            'kills': kills,
            'deaths': deaths,
            'assists': assists,
            'participant_win': participant_win,
        }
        values = []
        for _, name, declared_type, _, _, _ in columns:
            if name in overrides:
                values.append(overrides[name])
            elif declared_type.lower() == 'text':
                values.append('')
            else:
                values.append(0)
        conn.execute(
            'INSERT INTO Participant VALUES({})'.format(
                ','.join('?' for _ in values)
            ),
            values,
        )

    def _insert_match(self, conn, match_id, first_champion='A', first_kills=0):
        conn.execute(
            'INSERT INTO Match VALUES(?,?,?,?,?,?)',
            (str(match_id), 'test', 30, None, 1, 0),
        )
        for participant_id in range(1, 11):
            champion = first_champion if participant_id == 1 else 'C{}'.format(
                participant_id
            )
            self._insert_participant(
                conn,
                match_id,
                participant_id,
                champion,
                kills=first_kills if participant_id == 1 else 0,
                deaths=1 if participant_id == 1 else 0,
                assists=2 if participant_id == 1 else 0,
                participant_win=1 if participant_id <= 5 else 0,
            )

    def test_kill_matrix_uses_full_event_identity(self):
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn, conn:
            for champion in ('A', 'B', 'C'):
                conn.execute(
                    'INSERT INTO ChampionMatchStats(champion, picks) VALUES(?,?)',
                    (champion, 1),
                )
            conn.executemany(
                'INSERT INTO FrameKillEvent VALUES(?,?,?,?,?,?)',
                [
                    ('m1', 10, 'B', 0, 'A', 'C'),
                    ('m1', 10, 'B', 0, 'A', None),
                    ('m2', 10, 'B', 0, 'A', None),
                    ('m3', 10, 'C', 0, 'A', None),
                ],
            )

        matrix = champion_matrix.kill_matrix()

        self.assertEqual(matrix.loc['A', 'B'], 2)
        self.assertEqual(matrix.loc['A', 'C'], 1)

    def test_matrix_loaders_apply_pick_normalization_by_orientation(self):
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.executemany(
                'INSERT INTO ChampionMatchStats(champion, picks) VALUES(?,?)',
                [('A', 4), ('B', 2), ('Helper', 6)],
            )
            conn.execute(
                'INSERT INTO ChampionKillMatrix(killer,victim,kills) VALUES(?,?,?)',
                ('A', 'B', 2),
            )
            conn.execute(
                'INSERT INTO ChampionAssistMatrix(killer,assist,assists) VALUES(?,?,?)',
                ('A', 'Helper', 3),
            )

        self.assertEqual(champion_matrix.sqlite_to_kill_matrix('picks').loc['A', 'B'], 0.5)
        self.assertEqual(champion_matrix.sqlite_to_death_matrix('picks').loc['B', 'A'], 1.0)
        self.assertEqual(
            champion_matrix.sqlite_to_assist_matrix('picks').loc['Helper', 'A'],
            0.5,
        )
        with self.assertRaises(ValueError):
            champion_matrix.sqlite_to_kill_matrix('unknown')

    def test_preprocessing_is_idempotent_and_refreshes_all_stats(self):
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn, conn:
            self._insert_match(conn, '1', first_kills=2)
            conn.execute(
                'INSERT INTO TeamBan VALUES(?,?,?)', ('1', 'blue', 'A')
            )

        with contextlib.redirect_stdout(io.StringIO()):
            data_preprocess.match_champion_to_sqlite(str(self.db_path))
            data_preprocess.match_champion_to_sqlite(str(self.db_path))
            data_preprocess.champion_match_stats_to_sqlite(str(self.db_path))

        with contextlib.closing(sqlite3.connect(self.db_path)) as conn, conn:
            self.assertEqual(
                conn.execute('SELECT COUNT(*) FROM MatchChampion').fetchone()[0],
                1,
            )
            self.assertEqual(
                conn.execute(
                    'SELECT picks,bans,kills FROM ChampionMatchStats '
                    'WHERE champion = ?',
                    ('A',),
                ).fetchone(),
                (1, 1, 2),
            )
            self._insert_match(conn, '2', first_kills=5)

        with contextlib.redirect_stdout(io.StringIO()):
            data_preprocess.match_champion_to_sqlite(str(self.db_path))
            data_preprocess.champion_match_stats_to_sqlite(str(self.db_path))

        with contextlib.closing(sqlite3.connect(self.db_path)) as conn, conn:
            self.assertEqual(
                conn.execute('SELECT COUNT(*) FROM MatchChampion').fetchone()[0],
                2,
            )
            self.assertEqual(
                conn.execute(
                    'SELECT picks,bans,kills FROM ChampionMatchStats '
                    'WHERE champion = ?',
                    ('A',),
                ).fetchone(),
                (2, 1, 7),
            )

    def test_relationship_math_preserves_labels_and_counter_direction(self):
        adjacency = pd.DataFrame(
            [[1.0, 2.0], [3.0, 4.0]],
            index=['A', 'B'],
            columns=['x', 'y'],
        )
        expected = adjacency.dot(adjacency.T)
        pd.testing.assert_frame_equal(
            champion_relation.bibliographic_coupling(adjacency), expected
        )

        kill_matrix = pd.DataFrame(
            [[0, 7, 1], [2, 0, 9], [5, 3, 0]],
            index=['A', 'B', 'C'],
            columns=['A', 'B', 'C'],
        )
        counters = champion_relation.top_counter_scores(kill_matrix, 'B')
        self.assertEqual(list(counters.index), ['A', 'C'])
        self.assertEqual(list(counters.values), [7, 3])


if __name__ == '__main__':
    unittest.main()
