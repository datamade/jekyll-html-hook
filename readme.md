# jekyll-hook

A server that listens for webhook posts from GitHub, generates a website with
Jekyll, or just copies files in the case of a static HTML site and moves it
somewhere to be published. Use this to run your own GitHub Pages-style web
server. Great for when you need to serve your websites behind a firewall, need
extra server-level features like HTTPS for your domain or HTTP basic auth. It's
cutomizable with a config file. The original concept for this is heavily
influenced by [Development Seed's NodeJS based
project](https://github.com/developmentseed/jekyll-hook) with the same name.

## Dependencies Installation

First install main dependencies

    sudo apt-get update
    sudo apt-get install git python3.4-dev ruby ruby1.9.1-dev redis-server nginx

We also need Jekyll

    sudo gem install jekyll rdiscount json

## Installation

We recommend using
[virtualenv](http://virtualenv.readthedocs.org/en/latest/virtualenv.html) and
[virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/install.html)
for working in a virtualized development environment. [Read how to set up
virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/). One thing
to remember is that this app requires at least Python 3.4.

Once you have virtualenvwrapper set up,

    mkvirtualenv jekyll-hook
    git clone https://github.com/datamade/jekyll-hook.git
    cd jekyll-hook
    pip install -r requirements.txt

Afterwards, whenever you want to work on jekyll-hook,

    workon jekyll-hook

## Configuration

Copy `config.sample.json` to `config.json` in the root directory and customize:

    cp app_config.py.example app_config.py
    vim app_config.py

Configuration attributes:

- `GH_SERVER` The GitHub server from which to pull code, e.g. github.com
- `TEMP` A directory to store code and site files
- `SECRET` Optional. GitHub webhook secret.
- `SCRIPTS` A dictionary where the keys are the names of the kinds of sites you
have (by default this app can handle generating a Jekyll site or just handle
static HTML) and the values are the relative paths to the scripts that
are used to build and/or deploy those sites.
- `ACCOUNTS` A list of organizations whose repositories can be used with this
server.
- `SENTRY_DSN` Optional. DSN to configure [Sentry logging](https://getsentry.com).
- `REDIS_QUEUE_KEY` A unique string used to identify messages in Redis that the
app should pay attention to.

You can also adjust the default scripts in the `scripts` directory to suit your
workflow. By default, they generate a site with Jekyll or just copy static HTML
files and publish it to an NGINX web directory.

## Webhook Setup on Github

Set a [Web hook](https://developer.github.com/webhooks/) on your GitHub
repository that points to your jekyll-hook server
`https://example.com/hooks/:site_type/:branch`, where `:site_type` one of the
site types you configured in the `SCRIPTS` variable above (by default either
`jekyll` or `static`) `:branch` is the branch you want to publish. So,
for example, if you'd like to configure a webhook for a Jekyll site and
only deploy when you push to the `deploy` branch, your webhook URL would
look like this:

    https://example.com/hooks/jekyll/deploy

## Configure a webserver (nginx)

The default `publish.sh` is setup for nginx and copies the generated (or
static) HTML to `/usr/share/nginx/html/<repo_name>`.

If you would like to copy the website to another location, make sure to update
nginx virtual hosts which is located at `/etc/nginx/nginx/site-available` on Ubuntu 14.

You also need to update `publish.sh`

An example Nginx configuration (complete with Gzip and SSL/TLS settings based
upon using [Let's Encryt](https://letsencrypt.org/)) [is in the `scripts` folder](https://github.com/datamade/jekyll-hook/blob/master/scripts/nginx_template.conf)

## Run the app

There are two processes, one to handle incoming webhooks and one to actually generate and/or deploy the site. 

    python app.py
    python worker.py

As an an example of how you might daemonize the app and worker, an example
Supervisor configuration file [is in the `scripts` folder](https://github.com/datamade/jekyll-hook/blob/master/scripts/supervisor_conf.example).

## Other random stuff

You probably want to configure your server to only respond POST requests from GitHub's
public IP addresses, found on the webhooks settings page.

## Team

* Eric van Zanten - developer
* Derek Eder - developer

## Errors / Bugs

If something is not behaving intuitively, it is a bug, and should be reported.
Report it here: https://github.com/datamade/jekyll-hook/issues

## Note on Patches/Pull Requests
 
* Fork the project.
* Make your feature addition or bug fix.
* Send a pull request. Bonus points for topic branches.

## Copyright

Copyright (c) 2016 DataMade. Released under the [MIT License](https://github.com/datamade/jekyll-hook/blob/master/LICENSE).
