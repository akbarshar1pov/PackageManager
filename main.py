import os
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import io

from pip._vendor import requests

# Loading data from a link

def load(url):
    with urllib.request.urlopen(url) as f:
        data = f.read()
        return data


# We take a link to the package
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


# Download package dependencies
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


# Building the package dependency structure
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


# Building the text for the GraphViz file
def gv(graph):
    lines = ["digraph G {"]
    for v1 in graph:
        for v2 in graph[v1]:
            lines.append('"%s" -> "%s"' % (v1, v2))
    lines.append("}")
    return "\n".join(lines)


# Part of the code for the package manager
install_help = "pip install package_name - installing package(s)\n"

pip_help = "pip help - help with available commands.\n%s" \
           "pip uninstall package_name - removal of the package(s).\n" \
           "pip list - list of installed packages.\n" \
           "pip show package_name - shows information about the installed package.\n" \
           "pip search -search for packages by name.\n" \
           "pip mgvf - (make graph viz file) to create a file with " \
           "dependencies for GraphWiz" % install_help

pip_commands = ["help", "install", "uninstall", "list", "show", "search", "mgvf"]
install_arguments = ["-U", "--force-reinstall"]


#Installing (downloading) packages and their dependencies
def install_pip(packages):
    installed_packages = list_pip()
    for j in packages:
        for i in installed_packages:
            if j == i.split('-')[0]:
                to_do = input("Pavet already installed, check for dependencies (Y/n): ")
                if not (to_do == 'y' or to_do == 'Y'):
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
            data = requests.get(url)
            name = ("" + url).split('#')[0].split('/')[-1].casefold()
            open('install_packages/%s' % name, 'wb').write(data.content)
            print(name + '\t[%i bytes]' % os.path.getsize('install_packages/%s' % name))
        else:
            print(i + " already installed")


# Package removal
def uninstall_pip(package):
    packages = list_pip()
    package_not_found = True
    for i in package:
        for j in packages:
            if i in j:
                if os.path.exists('install_packages/%s' % j):
                    os.remove('install_packages/%s' % j)
                    print("The package has been removed!")
                    package_not_found = False
    if package_not_found:
        print("Package not found!")


# Listing installed packages
def list_pip():
    install_package = os.listdir('install_packages/')
    packages = []
    for i in install_package:
        packages.append(i)
    return packages


# Output metta data
def show_pip(package):
    packages = list_pip()
    for i in packages:
        if package in i.split('-'):
            package = i
            break
    if os.path.exists('install_packages/%s' % package) and (package.split('.')[-1] == "whl"):
        zipFile = zipfile.ZipFile('install_packages/%s' % package)
        meta_pah = [s for s in zipFile.namelist() if "METADATA" in s][0]
        with zipFile.open(meta_pah) as f:
            meta = f.read().decode('utf-8')
        print(meta)
    elif os.path.exists('install_packages/%s' % package):
        tar = tarfile.open('install_packages/%s' % package, "r:gz")
        for member in tar.getnames():
            if "PKG-INFO" in member:
                f = tar.extractfile(member)
                if f is not None:
                    content = f.read().decode('utf-8')
                    print(content)
    else:
        print("Package '%s' not installed\n" % package)


# Package search
def search_pip(name):
    packages = list_pip()
    for i in packages:
        if name in i.split('-'):
            print("The package is installed. To get run with the command: pip show %s" % name)
            return
    print("The package is not installed. To install, use the command: pip install %s" % name)


# File creation for Graph Wiz
def makeGraphVizFile(package):
    text = gv(get_package_graph(package))
    print(text)
    file = open('Graph Viz File.txt', 'w')
    file.write(text)


# To define a command
def do(command):
    i = 2
    packages = []
    while i < len(command.split()):
        packages.append(command.split()[i])
        i += 1
    if command.split()[1] == 'install':
        install_pip(packages)
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
    elif command.split()[1] == 'mgvf' and len(command.split()) == 3:
        makeGraphVizFile(command.split()[2])


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
