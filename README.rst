lsm-db-extras
=============

.. image:: https://coveralls.io/repos/github/mosquito/lsm-db-extras/badge.svg?branch=master
    :target: https://coveralls.io/github/mosquito/lsm-db-extras
    :alt: Coveralls

.. image:: https://travis-ci.org/mosquito/lsm-db-extras.svg
    :target: https://travis-ci.org/mosquito/lsm-db-extras
    :alt: Travis CI

.. image:: https://img.shields.io/pypi/v/lsm-db-extras.svg
    :target: https://pypi.python.org/pypi/lsm-db-extras/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/wheel/lsm-db-extras.svg
    :target: https://pypi.python.org/pypi/lsm-db-extras/

.. image:: https://img.shields.io/pypi/pyversions/lsm-db-extras.svg
    :target: https://pypi.python.org/pypi/lsm-db-extras/

.. image:: https://img.shields.io/pypi/l/lsm-db-extras.svg
    :target: https://pypi.python.org/pypi/lsm-db-extras/


Thread/Process safe shelves and other lam-db helpers


Installation
------------

.. code-block:: shell

    pip install lsm-db-extras


Usage example
-------------

.. code-block:: python


    from lsm_extras import Shelf, LSMDict

    with Shelf("/tmp/test.ldb") as shelf:
        shelf["foo"] = True

    with Shelf("/tmp/test.ldb") as shelf:
        print(shelf["foo"])


    with LSMDict("/tmp/test-dict.ldb") as storage:
        storage[1] = True

    with LSMDict("/tmp/test-dict.ldb") as storage:
        print(storage[1])
