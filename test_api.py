from flask import json
from flask.ext.testing import TestCase
from user_settings import app, db


class ApiTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def setUp(self):
        self.app = app.test_client()
        db.create_all()

        self.app.put('/',
                     data=json.dumps({'key1': 'value1'}),
                     content_type='application/json')

    def tearDown(self):
        db.drop_all()

    def test_get(self):
        resp = self.app.get('/')
        assert resp.status_code == 200
        assert resp.json == {'key1': 'value1'}

    def test_get_missing(self):
        resp = self.app.get('/?key=missing')
        assert resp.status_code == 404

    def test_update(self):
        resp = self.app.put('/',
                            data=json.dumps({'key1': 'value2'}),
                            content_type='application/json')

        self.assertEqual(resp.status_code, 200)

        resp = self.app.get('/')
        self.assertEqual(resp.json, {'key1': 'value2'})

    def test_add(self):
        resp = self.app.put('/',
                            data=json.dumps({'key2': 'value2'}),
                            content_type='application/json')

        resp = self.app.get('/')
        self.assertEqual(resp.json, {'key1': 'value1', 'key2': 'value2'})

    def test_add_json(self):
        resp = self.app.put('/',
                            data=json.dumps({'key3': [1, 2, 3]}),
                            content_type='application/json')

        resp = self.app.get('/?key=key3')
        self.assertEqual(resp.json, {'key3': [1, 2, 3]})

    def test_delete_via_json(self):
        resp = self.app.delete('/key1', content_type='application/json')

        assert resp.status_code == 200
        assert self.app.get('/').json == {}

    def test_delete_missing_key(self):
        resp = self.app.delete('/missing', content_type='application/json')

        assert resp.status_code == 200
        assert self.app.get('/').json == {'key1': 'value1'}
