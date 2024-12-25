from flask import jsonify
import sqlite3
from flask_restful import Resource
from sqlite3 import connect

con = connect(r'api\users.db', check_same_thread=False)
cur = con.cursor()


class GetTries(Resource):
    def get(self, user_id):
        ans = {}
        try:
            tries = list(cur.execute(fr'select tries from tries where id = {user_id}'))
            con.commit()
            if tries[0][0] > 0:
                ans['status'] = True
                ans['tries'] = tries
            else:
                ans['status'] = False
                ans['error'] = "У вас недостаточно попыток для прокручивания колеса."
        except sqlite3.Error:
            ans['status'] = False
        return jsonify(ans)


class GetCodes(Resource):
    def get(self):
        ans = {}
        try:
            codes = list(cur.execute(fr'select code from sectors'))
            con.commit()
            ans['status'] = True
            ans['codes'] = codes
        except sqlite3.Error:
            ans['status'] = False
        return jsonify(ans)


class UserLoading(Resource):
    def post(self, user_id, username, tries):
        cur.execute(fr'insert into tries (id, username, tries) values("{user_id}", "{username}", {int(tries)})')
        cur.execute(fr'insert into usernames (username) values("{username}")')
        con.commit()


class UserWin(Resource):
    def post(self, username, prize):
        cur.execute(fr'insert into prizes (username, prize) values("{username}", "{prize}")')
        con.commit()


class UserSpinUpdate(Resource):
    def post(self, user_id, tries):
        cur.execute(fr'update tries set tries = {int(tries)} where id = "{user_id}"')
        con.commit()


class PrizeLoading(Resource):
    def post(self, prize_id, name):
        cur.execute(fr'insert into sectors (id, name) values("{prize_id}", "{name}")')
        con.commit()
