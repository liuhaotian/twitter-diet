#!/usr/bin/env python
import functools
import httplib

import flask
import requests_oauthlib

import config


app = flask.Flask(__name__)
app.config.update(
    SECRET_KEY=config.APP_SECRET,
    SESSION_COOKIE_SECURE=True,
)


def oauth_from_session(session):
    return requests_oauthlib.OAuth1Session(
        config.API_KEY,
        client_secret=config.API_SECRET,
        resource_owner_key=session['username'],
        resource_owner_secret=session['password'])


def requires_auth(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        username = flask.session.get('username')
        password = flask.session.get('password')
        if not username or not password:
            return flask.redirect(flask.url_for('logout'))
        return f(*args, **kwargs)
    return wrapper


@app.route("/")
@requires_auth
def index():
    return """
<html>
  <head>
    <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=0">
    <script src="https://vuejs.org/js/vue.js"></script>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
  </head>
  <body>
    <div id="app"></div>
    <script src="/static/main.js"></script>
  </body>
</html>
    """


@app.route('/api/<path:path>', methods=['GET', 'POST'])
@requires_auth
def proxy(path):
    oauth = oauth_from_session(flask.session)
    url = config.API_URL_TEMPLATE.format(path=path)
    if flask.request.method == 'GET':
        resp = oauth.get(url)
    elif flask.request.method == 'POST':
        data = flask.request.form or flask.request.json
        resp = oauth.post(url, data=data)
    return resp.content, resp.status_code


@app.route('/bookmark')
@app.route('/bookmark/<session>')
def bookmark(session=None):
    bookmark = flask.request.cookies.get('bookmark', 'off')
    if bookmark == 'on':
        resp = flask.make_response('save the url as bookmark now')
        resp.set_cookie('bookmark', value='off')
    elif session:
        r = flask.redirect(flask.url_for('index'))
        resp = flask.make_response(r)  
        resp.set_cookie('session', value=session, samesite='Strict',
                        secure=app.config['SESSION_COOKIE_SECURE'],
                        httponly=app.config['SESSION_COOKIE_HTTPONLY'])
    else:
        s = flask.request.cookies.get('session')
        r = flask.redirect(flask.url_for('bookmark', session=s))
        resp = flask.make_response(r)  
        resp.set_cookie('bookmark', value='on')
        
    return resp


@app.route('/authorize', methods=['POST'])
def authorize():
    oauth = requests_oauthlib.OAuth1Session(
        config.API_KEY,
        client_secret=config.API_SECRET,
        callback_uri='oob')
    resp = oauth.fetch_request_token(config.REQUEST_TOKEN_URL)
    authorization_url = oauth.authorization_url(config.AUTHORIZE_URL)
    body = '''
      <form method="post" action="/verify">
        <p>Token:
          <input type=text name=token value={t}>
        <p>Secret:
          <input type=text name=secret value={s}>
        <p>Obtain PIN here:
          <a target='_blank' href={r}>{r}</a>
        <p>PIN:
          <input type=text name=verifier>
        <p><input type=submit value=Verify>
      </form>
    '''.format(t=resp['oauth_token'], s=resp['oauth_token_secret'],
        r=authorization_url)
    return body, httplib.SEE_OTHER


@app.route('/verify', methods=['POST'])
def verify():
    verifier = flask.request.form.get('verifier')
    token = flask.request.form.get('token')
    secret = flask.request.form.get('secret')
    oauth = requests_oauthlib.OAuth1Session(
        config.API_KEY,
        client_secret=config.API_SECRET,
        resource_owner_key=token,
        resource_owner_secret=secret,
        verifier=verifier)
    oauth_tokens = oauth.fetch_access_token(config.ACCESS_TOKEN_URL)
    body = '''
      <form method="post" action="/login">
        <p>Username: <input type=text name=username value={u}>
        <p>Password: <input type=password name=password value={p}>
        <p><input type=submit value=Login>
      </form>
    '''.format(u=oauth_tokens.get('oauth_token'),
               p=oauth_tokens.get('oauth_token_secret'))
    return body, httplib.ACCEPTED


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form.get('username')
        password = flask.request.form.get('password')
        oauth = requests_oauthlib.OAuth1Session(
            config.API_KEY,
            client_secret=config.API_SECRET,
            resource_owner_key=username,
            resource_owner_secret=password)
        resp = oauth.get('https://api.twitter.com/1.1/account/settings.json')
        flask.session['username'] = username
        flask.session['password'] = password
        return resp.content, resp.status_code
    elif 'username' in flask.session:
        return flask.redirect(flask.url_for('index'))
    else:
        return '''
          <form method="post" action="/authorize">
            <p><input type=submit value=Authorize>
          </form>
          <hr>
          <form method="post">
            <p>Username: <input type=text name=username>
            <p>Password: <input type=password name=password>
            <p><input type=submit value=Login>
          </form>
        '''


@app.route('/logout')
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for('login'))


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.config['SESSION_COOKIE_SECURE'] = False
    app.run()
