# Что ещё умеет делать pip
# Пробежимся по основным командам pip:
# pip help - помощь по доступным командам.
# pip install package_name - установка пакета(ов).
# pip uninstall package_name - удаление пакета(ов).
# pip list - список установленных пакетов.
# pip show package_name - показывает информацию об установленном пакете.
# pip search - поиск пакетов по имени.
# pip --proxy user:passwd@proxy.server:port - использование с прокси.
# pip install -U - обновление пакета(ов).
# pip install --force-reinstall - при обновлении, переустановить пакет, даже если он последней версии.

# def start_pip():
#     print("start")
#
#
# def help_pip():
#     print("help")
#
#
# def install_pip():
#     print("install")
#
#
# def uninstall_pip():
#     print("uninstall")
#
#
# def list_pip():
#     print("list")
#
#
# def show_pip():
#     print("show")
#
#
# def search_pip():
#     print("search")
#
#
# def upgrade_pip():
#     print("upgrade")
#
#
# def full_upgrade_pip():
#     print("full_upgrade")
#
#


import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import io


def load(url):
    with urllib.request.urlopen(url) as f:
        data = f.read()
        return data


def get_package_url(name):
    data = load('https://pypi.org/simple/%s/' % name)
    root = ET.fromstring(data)
    package_whl_url = None
    package_tar_gz_url = None
    for elem in root[1]:
        if elem.tag == 'a':
            url = elem.attrib['href']
            if '.whl#' in url:
                package_whl_url = url
            elif '.tar.gz#' in url:
                package_tar_gz_url = url
    if not package_whl_url:
        # return package_tar_gz_url
        return
    return package_whl_url


# tar = tarfile.open("filename.tar.gz", "r:gz")
# for member in tar.getmembers():
#      f = tar.extractfile(member)
#      if f is not None:
#          content = f.read()
#

def get_package_deps(url):
    data = load(url)
    obj = io.BytesIO(data)
    zipf = zipfile.ZipFile(obj)
    meta_pah = [s for s in zipf.namelist() if "METADATA" in s][0]
    with zipf.open(meta_pah) as f:
        meta = f.read().decode('utf-8')
    deps = []
    for line in meta.split('\n'):
        line = line.replace(';', ' ').split()
        if not line:
            break
        if line[0] == "Requires-Dist:" and "extra" not in line:
            deps.append(line[1])
    return deps


def get_package_graph(name):
    graph = {}
    def rec(name):
        print(name)
        graph[name] = set()
        url = get_package_url(name)
        if not url:
            return
        deps = get_package_deps(url)
        for d in deps:
            graph[name].add(d)
            if d not in graph:
                rec(d)
    rec(name)
    return graph


def gv(graph):
    lines = ["digraph G {"]
    for v1 in graph:
        for v2 in graph[v1]:
            lines.append('"%s" -> "%s"' % (v1, v2))
    lines.append("}")
    return "\n".join(lines)


if __name__ == '__main__':
    graph = get_package_graph("jupyter")
    gv = gv(graph)
    print(gv)
