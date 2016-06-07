import os
from flask import Flask, request, jsonify, json
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import String, Column


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI', 'sqlite:///:memory:')
db = SQLAlchemy(app)


user_id = 'test_user'


class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    user_id = Column(String, primary_key=True)
    settings = Column(String, default='{}')

    def upsert(self, kv):
        s = self.sd
        s.update(kv)
        self.settings = json.dumps(s)

    def remove_key(self, key):
        s = self.sd
        s.pop(key, None)
        self.settings = json.dumps(s)

    @property
    def sd(self):
        return json.loads(self.settings)

    def single_kv(self, key=None):
        if key is None:
            return self.settings

        s = self.sd

        if key not in s:
            return "error", 404

        return json.dumps({key: s[key]})


def save_settings(us):
    db.session.add(us)
    db.session.commit()


@app.route('/', methods=['GET', 'PUT', 'DELETE'])
def settings():
    us = UserSettings.query.one_or_none()

    if not us:
        us = UserSettings(user_id=user_id)
        save_settings(us)

    if request.method == 'GET':
        return us.single_kv(request.args.get('key', None))

    if request.method == 'PUT':
        us.upsert(request.get_json())
        save_settings(us)

    if request.method == 'DELETE':
        us.remove_key(request.get_json()['key'])
        save_settings(us)

    return jsonify({'status': 'ok'})


@app.route('/<string:key>', methods=['DELETE'])
def delete_key(key):
        us = UserSettings.query.one_or_none()

        if not us:
            return jsonify({})

        us.remove_key(key)
        save_settings(us)

        return jsonify({'status': 'ok'})
