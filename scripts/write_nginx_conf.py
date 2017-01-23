if __name__ == "__main__":
    
    import sys
    import os

    from jinja2 import Template
    

    hostname, code_dir, template_path = sys.argv[1:]
    
    outpath = '/etc/nginx/conf.d/'
    
    conf_name = '{0}/{1}.conf'.format(outpath, hostname)
    
    appname = code_dir.rsplit('/', 3)[-3]
    os.makedirs('/usr/share/nginx/html/{}'.format(appname), exist_ok=True)

    with open(template_path) as f:
        conf_part_1 = Template(f.read())

        rendered = conf_part_1.render(hostname=hostname,
                                      appname=appname)
    
    with open(conf_name, 'w') as out:
        
        out.write(rendered)
