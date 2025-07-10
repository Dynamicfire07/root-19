from django.test import TestCase, Client
import os
import mongomock
os.environ.setdefault('MONGO_URI', 'mongodb://localhost:27017')
from main import db


class FetchQuestionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        mock_client = mongomock.MongoClient()
        database = mock_client['testdb']
        db.questions_col = database['questions']
        db.users_col = database['users']
        db.user_activity_col = database['user_activity']
        # Also patch module-level references in views
        from main import views
        views.questions_col = db.questions_col
        views.users_col = db.users_col
        views.user_activity_col = db.user_activity_col
        for i in range(15):
            db.questions_col.insert_one({
                'question_id': f'Q{i}',
                'session_code': 'S1',
                'subtopic': 'T1',
                'image_base64': '',
                'answer': 'A',
            })

    def test_fetch_questions_limit(self):
        resp = self.client.get('/fetch-questions/', {
            'session_code': 'S1',
            'subtopic': 'T1',
            'limit': 10
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['questions']), 10)

    def test_exclude_parameter(self):
        first = self.client.get('/fetch-questions/', {
            'session_code': 'S1',
            'subtopic': 'T1',
            'limit': 5
        }).json()['questions']
        exclude = ','.join(q['question_id'] for q in first)
        second = self.client.get('/fetch-questions/', {
            'session_code': 'S1',
            'subtopic': 'T1',
            'exclude': exclude,
            'limit': 5
        }).json()['questions']
        ids = {q['question_id'] for q in second}
        self.assertTrue(not ids.intersection(set(exclude.split(','))))
