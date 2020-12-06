from app import app
from flask import render_template
import markdown
import requests
from bs4 import BeautifulSoup
import urllib.parse

@app.errorhandler(404)
def page_not_found(error):
    #print(error)
	return render_template('page_not_found.html'), 404

def index(path):
    return render_template('index.html')

def get_space_size(s):
    sz = 4
    for line in s.splitlines():
        ls = len(line) - len(line.lstrip())
        if ls > 0:
            return ls
    return sz

def get_md_contents(path, url_tmpl):
    slash = path.find('/')
    if slash >= 0:
        if path.lower().endswith(".md") or path.lower().endswith("/raw"):
            url = url_tmpl % path[slash+1:]
            r = requests.get(url)
            print(r.status_code, url)
            if r.status_code == 200 and r.text:
                extensions = ['markdown.extensions.extra',
                              'markdown.extensions.attr_list',
                              'markdown.extensions.fenced_code',
                              'markdown.extensions.codehilite',
                              'mdx_math',
				]
                s = str(r.text)
                tab_length = get_space_size(s)
                html = markdown.markdown(s, extensions=extensions, tab_length=tab_length)
                soup = BeautifulSoup(html, features="html.parser")
                is_relative = lambda x: not x.startswith('http')
                absolute = url[:url.rfind('/')]+'/'
                for e in soup.find_all("img", src=is_relative):
                    e['src'] = urllib.parse.urljoin(absolute, e['src'])
                return render_template('md.html', text=str(soup))
            else:
                #print("Fail to load the url!")
                return page_not_found("Fail to load the url!")
        else:
            #print("Allow only .md file!")
            return page_not_found("Allow only .md file!")
    return page_not_found("Could'nt find the url!")

def github(path):
    return get_md_contents(path, "https://raw.githubusercontent.com/%s")

def gist(path):
    return get_md_contents(path, "https://gist.githubusercontent.com/%s")

#def rest(path):
#    return "You want path: %s" % path

route_dic = {'': index, 'github': github, 'gist': gist}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def path_func(path):
    folders = path.split('/')
    first = folders[0] if len(folders) > 0 else ""
    return route_dic.get(first, page_not_found)(path)
    #return 'You want path: %s' % path
