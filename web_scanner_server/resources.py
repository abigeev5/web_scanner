from fileinput import filename
from flask import request, make_response, jsonify, send_file
from flask_restful import Resource
from authentication import verify_token, create_token, auth
from utils import get_user, make_error, make_success
from models import User, Result, Scanner
import db_session
import os


class AuthApi(Resource):
    
    # get token by login and password
    # input: username, hashed password
    # output: token
    def get(self):
        data = request.get_json()
        # decrypt
        if ('username' in data) and ('password' in data):
            user = get_user(username=data['username'])
            if user:
                if user.password == data['password']:
                    return make_response(jsonify({'token': user.token}), 200)
                else:
                    return make_error(401)
            else:
                return make_error(404)
        else:
            return make_error(400)


class UserApi(Resource):
    
    # get info
    # input: token
    # output: username, email, role
    @verify_token
    def get(self, user, data):
        session = db_session.create_session()
        if ("get_all" in data) and (user.role == 2):
            users = session.query(User).all()
            response = list()
            for cur_user in users:
                scanners = [i.id for i in session.query(Scanner).filter(Scanner.operators.contains(f'"{cur_user.id}"')).all()]
                response.append({
                    'id': cur_user.id,
                    'username': cur_user.username, 
                    'information': cur_user.information,
                    'FIO': cur_user.FIO, 
                    'role': cur_user.role,
                    'scanners': scanners})
            session.close()
            return ({'response': response}, 200)
        else:
            scanners = [i.id for i in session.query(Scanner).filter(Scanner.operators.contains(f'"{user.id}"')).all()]
            session.close()
            return ({'username': user.username, 'information': user.information, 'role': user.role, 'scanners': scanners}, 200)
            

    # Create user
    # input: username, password, role, token (admin)
    # output: None
    @verify_token(role=2)
    def post(self, admin, data):
        if ('username' in data) and ('password' in data):
            exuser = get_user(username=data['username'])
            if exuser == None:
                user = User()
                user.username = data['username']
                user.information = "test1@test.com"
                user.password = data['password']
                user.token = create_token()
                user.role = 1

                session = db_session.create_session()
                session.add(user)
                session.commit()
                session.close()
                return make_success(200)
            else:
                return make_error(409)
        else:
            return make_error(400)


    # Delete user
    # input: username, token (admin)
    # output: None
    @verify_token(role=2)
    def delete(self, admin, data):
        if ('username' in data):
            user = get_user(username=data['username'])
            if user:
                session = db_session.create_session()
                session.delete(user)
                session.commit()
                session.close()
                return make_success(200)
            else:
                return make_error(404)
        else:
            return make_error(400)


class ResultApi(Resource):
    
    # get results
    # input: scanner_id
    # output (if scanner): {results: {barcode: [list of dicts with metadata]]}
    @verify_token
    def get(self, user, data):
        if ('scanner_id' in data):
            session = db_session.create_session()
            results = session.query(Result).filter(Result.scanner_id == data['scanner_id']).all()
            
            users = {user_.id: user_.username for user_ in session.query(User).all()}
            scanners = {scanner.id: scanner.name for scanner in session.query(Scanner).all()}
            
            response = {'results': {}}
            for result in results:
                response['results'][result.barcode] = result.results
                response['results'][result.barcode].update({'user': users[result.user_id], 'scanner': scanners[result.scanner_id], 'enterobiasis': result.enterobiasis})
            session.close()
            return (response, 200)
        else:
            return make_error(400)


    # store images
    # input: barcode, scanner_id, pairs {id: filename}
    # output: result code
    @verify_token
    def post(self, user, data):
        return ({"meaning_of_life": 42}, 200)


    # delete images
    # input: barcode, filename.png (or not to delete result)
    # output: result code
    @verify_token
    def delete(self, user, data):
        if ('barcode' in data):
            session = db_session.create_session()
            if ('filename' in data):
                results = session.query(Result).filter(Result.barcode == data['barcode']).first()
                os.remove(results.folder_path + '/' + data['filename'])
                os.remove(results.folder_path + '/thumb_' + data['filename'].replace('.png', '.jpg'))
            else:
                results = session.query(Result).filter(Result.barcode == data['barcode']).all()
                session.delete(results)
                session.commit()
            session.close()
            return make_success(200)
        else:
            return make_error(400)


class ScannerApi(Resource):
    # get list scanners and settings which is avilable for user

    # input: None
    # output: name, settings, barcodes, version, description, connection data, metadata
    @verify_token
    def get(self, user, data):
        session = db_session.create_session()
        scanners = session.query(Scanner).filter(Scanner.operators.contains(f"\"{user.id}\"")).all()
        response = list()
        for scanner in scanners:
            response.append({
                'id': scanner.id,
                'name': scanner.name, 
                'settings': scanner.settings,
                'version': scanner.version, 
                'description': scanner.description, 
                'notifications': scanner.notifications, 
                'connection': scanner.connection, 
                'metadata': scanner.metadata_})
        session.close()
        return ({'response': response}, 200)


class StatusApi(Resource):
    # Server status

    # output: time, unit test results, status
    def get(self):
        return ({"meaning_of_life": 42}, 200)