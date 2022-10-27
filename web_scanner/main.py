from dataclasses import dataclass
from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime
import requests

app = Flask(__name__)

server_api = 'http://192.168.1.195:7070/api/v1'
session = requests.Session()
session.headers.update({'Content-Type': 'application/json'})

error_codes = {
    400: 'Bad request',
    401: 'Unauthorized',
    403: 'No permission',
    404: 'User not found',
    409: 'User already exist',
    500: 'Unknown error'
}

def get_user_info(token):
    global session
    response = session.get(server_api + '/user', json={'token': token})
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': response.status_code}


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    # userLogin = 'testUser'
    # userPassword = 'user'
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    response = session.get(server_api + '/auth', json={'username': username, 'password': password})
    if response.status_code == 200:
        token = response.json()['token']
        res = make_response(redirect(url_for('home', scanner_id=0, results_id=None, token=token)))
        age = 60*24*31 if remember else 60*24
        res.set_cookie('token', token, max_age=age)
        return res
    return render_template('login.html', error=response.status_code, message=error_codes.get(response.status_code, ''))


@app.route('/logout')
def logout():
    res = make_response(redirect(url_for('login')))
    token = request.cookies.get('token')
    res.set_cookie('token', token, max_age=0)
    return res


@app.route('/')
@app.route('/home')
@app.route('/home/results')
def home():
    global session
    if request.cookies.get('token'):
        token = request.cookies.get('token')
        user = get_user_info(token)
        if user["role"] == 1:
            return redirect(url_for('results_page'))
        else:
            return redirect(url_for('scanners_page'))
    else:
        return redirect(url_for('login'))


@app.route('/home/results/')
def results_page(token=None):
    global session
    if request.cookies.get('token') or token:
        token = token if token else request.cookies.get('token')
        user = get_user_info(token)
        if user["role"] == 1:
            response = session.get(server_api + '/scanner', json={'token': token})
            data = list()
            error_code = None
            message = None
            if response.status_code == 200:
                data = response.json()['response']
                for (idx, scanner) in enumerate(response.json()['response']):
                    r = session.get(server_api + '/result', json={'token': token, 'scanner_id': scanner['id']})
                    if r.status_code == 200:
                        results = r.json()['results']
                        data[idx]['results'] = dict()
                        for (barcode, info) in results.items():
                            for i in range(len(info['results'])):
                                info['results'][i].update({
                                    'image': f"{server_api}/image/{barcode}/{info['results'][i]['image']}", 
                                    'thumbnail': f"{server_api}/image/{barcode}/{info['results'][i]['thumbnail']}",
                                    'user': info['user'],
                                    'scanner': info['scanner'],
                                    })
                            tmp = info['enterobiasis']
                            info = info['results']
                            #info['enterobiasis'] = tmp
                            if not(info[0]['time'].split()[0]) in data[idx]['results']:
                                data[idx]['results'][info[0]['time'].split()[0]] = {barcode: {'enterobiasis': tmp, 'info': info}}
                            else:
                                data[idx]['results'][info[0]['time'].split()[0]][barcode] = {'enterobiasis': tmp, 'info': info}
                    else:
                        error_code = r.status_code
            else:
                error_code = response.status_code
            return render_template('results.html', results=data, active='results', user=user, error=error_code, message=error_codes.get(response.status_code, ''))
        else:
            return redirect(url_for('scanners_page')) 
    return redirect(url_for('login'))


@app.route('/home/scanners/')
def scanners_page():
    global session
    if request.cookies.get('token'):
        token = request.cookies.get('token')
        user = get_user_info(token)
        if user["role"] == 2:
            response = session.get(server_api + '/scanner', json={'token': token})
            error_code = None
            message = None
            if response.status_code == 200:
                data = response.json()['response']
            else:
                error_code = response.status_code
            return render_template('scanners.html', active='scanners', scanners=data, user=user, error=error_code, message=error_codes.get(response.status_code, ''))
        else:
           return redirect(url_for('results_page')) 
    return redirect(url_for('login'))


# old
@app.route('/delete_img')
def delete_img():
    global session
    if request.cookies.get('token'):
        token = request.cookies.get('token')
        # user = get_user_info(token)
        data = dict(request.args)
        response = session.delete(server_api + '/result', json={'token': token, 'barcode': data['barcode'], 'filename': data['filename']})
        return {'code': response.status_code, "message": error_codes.get(response.status_code, '')}
    return {'code': "-1", "message": ""}


@app.route('/home/users/')
def users_page(user_id=0):
    global session
    if request.cookies.get('token'):
        token = request.cookies.get('token')
        user = get_user_info(token)
        if user["role"] == 2:
            response = session.get(server_api + '/user', json={'token': token, 'get_all': True})
            users = {'Администраторы': list(), 'Операторы': list()}
            error_code = None
            message = None
            if response.status_code == 200:
                users = {'Администраторы': [i for i in response.json()['response'] if i["role"] == 2], 
                         'Операторы': [i for i in response.json()['response'] if i["role"] == 1]}
            else:
                error_code = response.status_code
            return render_template('users.html', active='users', user=user, users=users, error=error_code, message=error_codes.get(response.status_code, ''))
        else:
           return redirect(url_for('results_page')) 
    return redirect(url_for('login'))


@app.route('/home/log/')
def log_page():
    global session
    if request.cookies.get('token'):
        token = request.cookies.get('token')
        user = get_user_info(token)
        
        if user["role"] == 2:
            response = session.get(server_api + '/scanner', json={'token': token})
            logs = list()
            error_code = None
            message = None
            if response.status_code == 200:
                for scanner in response.json()['response']:
                    for notification in scanner['notifications']:
                        logs.append({
                            "name": scanner["name"], 
                            "type": notification["type"], 
                            "message": notification["message"], 
                            "time": datetime.strptime(notification["datetime"], '%d.%m.%Y %H:%M:%S')
                            })
                logs = sorted(logs, key=lambda x: x["time"])
            else:
                error_code = response.status_code
            return render_template('log.html', active='log', logs=logs, user=user, error=error_code, message=error_codes.get(error_code, ''))
        else:
           return redirect(url_for('results_page')) 
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
