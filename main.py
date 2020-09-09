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

def start_pip():
    print("start")


def help_pip():
    print("help")


def install_pip():
    print("install")


def uninstall_pip():
    print("uninstall")


def list_pip():
    print("list")


def show_pip():
    print("show")


def search_pip():
    print("search")


def upgrade_pip():
    print("upgrade")


def full_upgrade_pip():
    print("full_upgrade")


if __name__ == '__main__':
    start_pip()
