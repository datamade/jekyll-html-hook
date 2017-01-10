#!/bin/bash
set -e

# This script is meant to be run automatically
# as part of the jekyll-hook application.
# https://github.com/developmentseed/jekyll-hook

repo=$1
branch=$2
owner=$3
giturl=$4
source=$5
build=$6
venv_bin_dir=$7

# Check to see if repo exists. If not, git clone it
if [ ! -d $source ]; then
    git clone $giturl $source
    
    hostname=`cat $source/CNAME`
    
    scripts_dir=`pwd`/scripts
    part1=$scripts_dir/nginx_conf_part_1.conf
    part2=$scripts_dir/nginx_conf_part_2.conf
    
    sudo $venv_bin_dir/python $scripts_dir/write_nginx_conf.py $hostname $source $part1
    
    sudo service nginx restart
    
    sudo $HOME/letsencrypt/letsencrypt-auto certonly -q --webroot -w /usr/share/nginx/html -d $hostname
    
    sudo $venv_bin_dir/python write_nginx_conf.py $hostname $source $part2
    
    sudo service nginx restart
fi

# Git checkout appropriate branch, pull latest code
cd $source
git fetch --all
git reset --hard origin/$branch
cd -

