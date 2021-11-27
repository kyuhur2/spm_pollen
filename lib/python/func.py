from rpy2.rinterface import RRuntimeWarning
from rpy2.robjects.packages import importr


def r_checkpackage(
    package_name: str,
    url: str = "https://cloud.r-project.org"
):
    utils = importr('utils')
    try:
        importr(package_name)
    except RRuntimeWarning:
        utils.install_packages(package_name, contriburl=url)
