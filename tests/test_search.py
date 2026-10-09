import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.create_database import Database
from backend.dashboard import list_records
from backend.management import save_record


class SearchTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        env = patch.dict(os.environ, {'PERSONAL_MANAGER_DB': str(Path(directory.name)/'search.db')})
        env.start()
        self.addCleanup(env.stop)
        Database()

    def employee(self, name, email='test@example.com'):
        return save_record('employees', dict(fullname=name,email=email,phone='00123',gender='Femme'))

    def test_unicode_casefold_and_secondary_fields(self):
        identifier = self.employee('ÉLODIE', 'elodie@example.com')
        self.employee('Alice')
        self.assertEqual(list_records('employees', search='élodie')[0][0][0], identifier)
        self.assertEqual(list_records('employees', search='ELODIE@')[1], 1)
        self.assertEqual(list_records('employees', search='00123')[1], 2)

    def test_special_characters_are_literals_not_wildcards_or_sql(self):
        self.employee('100%_done')
        self.employee('100Xdone')
        self.employee("O'Connor")
        self.employee('Back\\slash')
        for term, expected in [('%_',1), ("O'Connor",1), ('\\',1), ("'; DROP TABLE Employee;--",0)]:
            with self.subTest(term=term):
                self.assertEqual(list_records('employees', search=term)[1], expected)
        self.assertEqual(list_records('employees')[1], 4)

    def test_search_and_status_combine_and_filtered_pages_are_consistent(self):
        for i in range(30):
            save_record('finances', dict(reason=f'Loyer {i}',amount='1000',date='2026-10-09',
                                        status='Payée',type='Décaissement'))
        save_record('finances', dict(reason='Loyer impayé',amount='1000',date='2026-10-09',
                                    status='Non Payée',type='Décaissement'))
        first,total = list_records('finances',search='loyer',status='Payée')
        second,_ = list_records('finances',page=1,search='loyer',status='Payée')
        self.assertEqual(total,30)
        self.assertEqual([len(first),len(second)], [25,5])
        self.assertEqual(len({row[0] for row in first+second}),30)
        self.assertEqual(list_records('finances',search='loyer',status='Non Payée')[1],1)
        self.assertEqual(list_records('finances',search='loyer',status='Tous')[1],31)

    def test_empty_term_no_match_and_invalid_filters(self):
        self.employee('Alice')
        self.assertEqual(list_records('employees',search='  ')[1],1)
        self.assertEqual(list_records('employees',search='Nobody'),([],0))
        for kwargs in ({'search':'x'*201}, {'search':None}, {'status':'Payée'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                list_records('employees', **kwargs)

    def test_events_searches_name_place_and_reason(self):
        save_record('events', dict(meet_with='Bob',gender='Homme',phone='00123',place='Lisbonne',
                                  event_status='Effectué',reason_event='Réunion technique',
                                  eventdate='2026-10-09',hour_event='09:00'))
        for term in ('bob','lisbonne','technique'):
            self.assertEqual(list_records('events',search=term,status='Effectué')[1],1)
        self.assertEqual(list_records('events',status='Non Effectué')[1],0)
