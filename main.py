import os
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import io

from pip._vendor import requests


def load(url):
    with urllib.request.urlopen(url) as f:
        data = f.read()
        return data


# Берем ссылку на пакет
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
        return package_tar_gz_url
    return package_whl_url


# Загружаем зависимости пакета
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


# Строим структуру зависимостей пакета
def get_package_graph(name):
    graph = {}
    def rec(name):
        print(name)
        graph[name] = set()
        url = get_package_url(name)
        if not url or ".tar.gz#" in url:
            return
        deps = get_package_deps(url)
        for d in deps:
            graph[name].add(d)
            if d not in graph:
                rec(d)
    rec(name)
    return graph


# Строим текст для файла GraphViz
def gv(graph):
    lines = ["digraph G {"]
    for v1 in graph:
        for v2 in graph[v1]:
            lines.append('"%s" -> "%s"' % (v1, v2))
    lines.append("}")
    return "\n".join(lines)


#################################################################
# Что ещё умеет делать pip
# Пробежимся по основным командам pip:

install_help = "pip install package_name - установка пакета(ов)\n" \
               "pip install -U - обновление пакета(ов).\n" \
               "pip install --force-reinstall - при обновлении, переустановить пакет, " \
               "даже если он последней версии.\n"

pip_help = "pip help - помощь по доступным командам.\n%s" \
       "pip uninstall package_name - удаление пакета(ов).\n" \
       "pip list - список установленных пакетов.\n" \
       "pip show package_name - показывает информацию об установленном пакете.\n" \
       "pip search - поиск пакетов по имени." % install_help

pip_commands = ["help", "install", "uninstall", "list", "show", "search", ]
install_arguments = ["-U", "--force-reinstall"]


def install_pip(packages):
    installed_packages = list_pip()
    if packages in installed_packages:
        to_do = input("Павет уже установлен, проверит на наличия зависимостей (Y/n): ")
        if not(to_do == 'y' or to_do == 'Y'):
            return
    packages_list = {}
    def rec(name):
        packages_list[name] = set()
        url = get_package_url(name)
        if not url or ".tar.gz#" in url:
            return
        deps = get_package_deps(url)
        for d in deps:
            packages_list[name].add(d)
            if d not in packages_list:
                rec(d)
    for i in packages:
        rec(i)
    for i in packages_list:
        if i not in installed_packages:
            url = get_package_url(i)
            print(i)
            data = requests.get(url)
            name = "" + url
            open('install_packages/%s' % name.split('#')[0].split('/')[-1].casefold(), 'wb').write(data.content)
        else:
            print(i + " уже установлен")


def uninstall_pip(package):
    packages = list_pip()
    package_not_found = True
    for i in package:
        for j in packages:
            if i in j:
                if os.path.exists('install_packages/%s' % j):
                    os.remove('install_packages/%s' % j)
                    print("Пакет был удалён!")
                    package_not_found = False
    if package_not_found:
        print("Пакет не найден!")


def list_pip():
    install_package = os.listdir('install_packages/')
    packages = []
    for i in install_package:
        packages.append(i)
    return packages


def show_pip(package):
    if os.path.exists('install_packages/%s.whl' % package):
        zipFile = zipfile.ZipFile('install_packages/%s.whl' % package)
        meta_pah = [s for s in zipFile.namelist() if "METADATA" in s][0]
        with zipFile.open(meta_pah) as f:
            meta = f.read().decode('utf-8')
        print(meta)
    elif os.path.exists('install_packages/%s.tar.gz' % package):
        tar = tarfile.open('install_packages/%s.tar.gz' % package, "r:gz")
        for member in tar.getnames():
            if "PKG-INFO" in member:
                f = tar.extractfile(member)
                if f is not None:
                    content = f.read().decode('utf-8')
                    print(content)
    else:
        print("Пакет '%s' не установлен\n" % package)


def search_pip(name):
    if name in list_pip():
        print("Пакет установлен. Для получения осползуйтейс командой: pip show %s" % name)
    else:
        print("Пакет не установлен. Для установки восползуйтейс командой: pip install %s" % name)

#
# def upgrade_pip():
#     print("upgrade")
#
#
# def full_upgrade_pip():
#     print("full_upgrade")
#
#


def do(command):
    i = 2
    packages = []
    while i < len(command.split()):
        packages.append(command.split()[i])
        i += 1
    if command.split()[1] == 'install':
        if command.split()[2] not in install_arguments:
            install_pip(packages)
        elif command.split()[2] == '-U' and len(command.split()) > 3:
            print("-U")
        elif command.split()[2] == '--force-reinstall' and len(command.split()) == 3:
            print('--force-reinstall')
        else:
            print(install_help)
    elif command.split()[1] == 'uninstall' and len(command.split()) >= 3:
        uninstall_pip(packages)
    elif command.split()[1] == 'list' and len(command.split()) == 2:
        packages_list = list_pip()
        for i in packages_list:
            print(i)
    elif command.split()[1] == 'show' and len(command.split()) == 3:
        show_pip(command.split()[2])
    elif command.split()[1] == 'search' and len(command.split()) == 3:
        search_pip(command.split()[2])


if __name__ == '__main__':
    def main():
        command = input(">>> ")
        if command.split()[0] == 'pip' and command.split()[1] in pip_commands:
            do(command)
            main()
        elif command.split()[0] == 'help':
            print(pip_help)
            main()
        elif command.split()[0] == 'exit':
            return
        else:
            print("Command is uncorrected")
            main()
    main()
