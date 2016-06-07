from flask import json
from flask.ext.testing import TestCase
from hypothesis import given, example
from hypothesis.strategies import text
from user_settings import app, db, valid_chars


def valid_word(word):
    return all(c in valid_chars for c in word)


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

    @given(text())
    def test_get_missing(self, s):
        resp = self.app.get('/?key=%s' % s)
        assert resp.status_code == 404

    def test_get(self):
        resp = self.app.get('/')
        assert resp.status_code == 200
        assert resp.json == {'key1': 'value1'}

    @given(text(min_size=1, alphabet=list(valid_chars)), text(alphabet=list(valid_chars)))
    def test_update(self, k, v):
        resp = self.app.put('/',
                            data=json.dumps({k: v}),
                            content_type='application/json')

        self.assertEqual(resp.status_code, 200)

        resp = self.app.get('/')
        assert (k, v) in resp.json.items()

        self.app.delete('/%s' % k, content_type='application/json')

    @given(text().filter(valid_word), text())
    @example('', '')
    @example('', 'value')
    def test_add_non_ascii_key(self, k, v):
        resp = self.app.put('/',
                            data=json.dumps({k: v}),
                            content_type='application/json')

        assert resp.status_code == 400

    def test_add_json(self):
        resp = self.app.put('/',
                            data=json.dumps({'key3': [1, 2, 3]}),
                            content_type='application/json')

        resp = self.app.get('/?key=key3')
        self.assertEqual(resp.json, {'key3': [1, 2, 3]})

    def test_delete(self):
        resp = self.app.delete('/key1', content_type='application/json')

        assert resp.status_code == 200
        assert self.app.get('/').json == {}

    def test_delete_via_json(self):
        resp = self.app.delete('/', data=json.dumps({'key': 'key1'}), content_type='application/json')

        assert resp.status_code == 200
        assert self.app.get('/').json == {}

    @given(text(min_size=1, alphabet=list(valid_chars)))
    def test_delete_missing_key(self, k):
        resp = self.app.delete('/%s' % k, content_type='application/json')

        assert resp.status_code == 200
        assert self.app.get('/').json == {'key1': 'value1'}

    @given(text(min_size=1))
    def test_delete_missing_json_key(self, k):
        resp = self.app.delete('/', data=json.dumps({'key': k}), content_type='application/json')

        assert resp.status_code == 200
        assert self.app.get('/').json == {'key1': 'value1'}
