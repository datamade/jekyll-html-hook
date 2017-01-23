import os
from datetime import datetime, timedelta
import json
import urllib.request
import sys

from flask import Flask, request, make_response
from raven.contrib.flask import Sentry
import app_config

from tasks import run_scripts

app = Flask(__name__)
app.config.from_object(app_config)

app.url_map.strict_slashes = False

sentry = Sentry(app, dsn=app_config.SENTRY_DSN)

# expects GeoJSON object as a string
# client will need to use JSON.stringify() or similar

class PayloadException(Exception):
    def __init__(self, message):
        
        super().__init__()
        
        self.message = message

def parsePost(post, branch):
    
    if 'ref' not in post.keys():
        return []

    # Parse webhook data for internal variables
    post['repo'] = post['repository']['name']
    post['branch'] = post['ref'].replace('refs/heads/', '')
    post['owner'] = post['repository']['owner']['name']

    # End early if not permitted account
    if post['owner'] not in app_config.ACCOUNTS:
        raise PayloadException('Account %s not permitted' % post['owner'])

    # End early if not permitted branch
    if post['branch'] != branch:
        raise PayloadException('Branch %s not permitted' % post['branch'])

    giturl = 'git@{server}:{owner}/{repo}.git'\
                 .format(server=app_config.GH_SERVER,
                         owner=post['owner'],
                         repo=post['repo'])

    # source
    source = '{temp}/{owner}/{repo}/{branch}/code'\
                 .format(temp=app_config.TEMP,
                         owner=post['owner'],
                         repo=post['repo'],
                         branch=post['branch'])

    build = '{temp}/{owner}/{repo}/{branch}/site'\
                .format(temp=app_config.TEMP,
                        owner=post['owner'],
                        repo=post['repo'],
                        branch=post['branch'])
    
    cname_url = 'https://api.github.com/repos/{owner}/{repo}/contents/CNAME?access_token={token}'
    cname_url = cname_url.format(owner=post['owner'],
                                 repo=post['repo'],
                                 token=app_config.GH_TOKEN)

    with urllib.request.urlopen(cname_url) as cname:
        if cname.status != 200:
            raise PayloadException('CNAME file does not seem to exist in repo')
    
    venv_bin_dir = os.path.dirname(sys.executable)
    
    appname = source.rsplit('/', 3)[-3]
    
    script_args = [
        post['repo'],
        post['branch'],
        post['owner'],
        giturl,
        source,
        build,
        venv_bin_dir,
        appname,
    ]

    return script_args

@app.route('/hooks/<site_type>/<branch_name>', methods=['POST'])
def execute(site_type, branch_name):
    post = request.get_json()
    
    resp = {'status': 'ok'}
    
    try:
        script_args = parsePost(post, branch_name)
    except PayloadException as e:
        script_args = None
        resp['status'] = e.message

    if script_args:
        
        scripts = app_config.SCRIPTS[site_type]
        
        run_scripts.delay(scripts, script_args)

    response = make_response(json.dumps(resp), 202)
    response.headers['Content-Type'] = 'application/json'
    return response

# INIT
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)
