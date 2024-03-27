"""Install pytest-rerunclassfailures"""

from setuptools import setup

setup(
    name="pytest-rerunclassfailures",
    entry_points={
        "pytest11": [
            "pytest_rerunclassfailures = pytest_rerunclassfailures:pytest_rerunclassfailures",
        ],
    },
)
