from setuptools import setup, find_packages


setup(
    name='lsm-db-extras',
    version='0.1',
    author='Dmitry Orlov',
    author_email='me@mosquito.su',
    description='Thread/Process safe shelves and other lam-db helpers',
    long_description=open("README.rst"),
    license="Apache 2",
    packages=find_packages(".", exclude=['tests', 'doc']),
    install_requires=[
        "lsm-db",
    ],
)
