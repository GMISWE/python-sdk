import subprocess


def get_installed_packages():
    """
    Get a list of currently installed packages using pip freeze.
    """
    result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)
    return set(result.stdout.splitlines())


def get_required_packages(file_path):
    """
    Get a list of required packages from the requirements file.
    """
    with open(file_path, 'r') as file:
        return {line.strip() for line in file}


def uninstall_packages(packages):
    """
    Uninstall the given packages using pip.
    """
    for package in packages:
        subprocess.run(['pip', 'uninstall', '-y', package])


if __name__ == '__main__':
    # Get the list of installed packages
    installed_packages = get_installed_packages()

    # Get the list of required packages from the requirements file
    required_packages = get_required_packages('../../requirements.txt')

    # Determine the packages that need to be uninstalled
    packages_to_uninstall = installed_packages - required_packages

    # Uninstall the packages that are not required
    uninstall_packages(packages_to_uninstall)
