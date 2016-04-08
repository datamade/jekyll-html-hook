import os
from datetime import datetime, timedelta
import json

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

def parsePost(post, branch):
    
    # Parse webhook data for internal variables
    post['repo'] = post['repository']['name']
    post['branch'] = post['ref'].replace('refs/heads/', '')
    post['owner'] = post['repository']['owner']['name']

    # End early if not permitted account
    if post['owner'] not in app_config['accounts']:
        raise Exception('Account %s not permitted' % post['owner'])

    # End early if not permitted branch
    if post['branch'] != branch:
        raise Exception('Branch %s not permitted' % post['branch'])

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
    
    script_args = [
        post['repo'],
        post['branch'],
        post['owner'],
        giturl,
        source,
        build,
    ]

    return script_args


@app.route('/hooks/<site_type>/<branch_name>', methods=['POST'])
def execute(site_type, branch_name):
    post = request.get_json()
    
    script_args = parsePost(post, branch)
    scripts = app_config[site_type]
    
    run_scripts.delay(scripts, script_args)

    resp = {'status', 'ok'}
    response = make_response(json.dumps(resp), 202)
    response.headers['Content-Type'] = 'application/json'
    return response

# INIT
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)
