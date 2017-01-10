if __name__ == "__main__":
    
    import sys
    import os

    from jinja2 import Template
    
    hostname, source, template_path = sys.argv[1:]
    
    print(hostname, source, template_path)

    appname = os.path.basename(source)
    
    outpath = '/etc/nginx/conf.d/'
    
    conf_name = '{0}/{1}.conf'.format(outpath, appname)

    with open(template_path) as f:
        conf_part_1 = Template(f.read())

        rendered = conf_part_1.render(hostname=hostname,
                                      appname=appname)
    
    with open(conf_name, 'w') as out:
        
        out.write(rendered)
