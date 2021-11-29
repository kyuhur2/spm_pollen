from rpy2.rinterface import RRuntimeError
from rpy2.robjects.packages import importr


def r_checkpackage(
    package_name: str
):
    utils = importr('utils')
    try:
        importr(package_name)
    except RRuntimeError:
        utils.install_packages(package_name)
