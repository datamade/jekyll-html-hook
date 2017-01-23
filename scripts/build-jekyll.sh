#!/bin/bash
set -e

repo=$1
branch=$2
owner=$3
giturl=$4
source=$5
build=$6
venv_bin_dir=$7

# Check to see if repo exists. If not, git clone it
# and run nginx setup
if [ ! -d $source ]; then
    git clone $giturl $source
    
    hostname=`cat $source/CNAME`
    
    scripts_dir=`pwd`/scripts
    part1=$scripts_dir/nginx_conf_part_1.conf
    part2=$scripts_dir/nginx_conf_part_2.conf
    
    echo "$venv_bin_dir/python $scripts_dir/write_nginx_conf.py $hostname $repo $part1"
    
    sudo $venv_bin_dir/python $scripts_dir/write_nginx_conf.py $hostname $repo $part1
    
    sudo service nginx reload
    
    sudo ../letsencrypt/letsencrypt-auto certonly -q --webroot -w /usr/share/nginx/html/$repo -d $hostname
    
    sudo $venv_bin_dir/python $scripts_dir/write_nginx_conf.py $hostname $repo $part2
    
    sudo service nginx restart
fi

# Git checkout appropriate branch, pull latest code
cd $source
git fetch --all
git reset --hard origin/$branch
cd -

# Run jekyll
cd $source
/home/ubuntu/.rvm/gems/ruby-2.3.0/wrappers/jekyll build -s $source -d $build
cd -
