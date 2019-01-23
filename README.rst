lsm-db-extras
=============

.. image:: https://coveralls.io/repos/github/mosquito/lsm-db-extras/badge.svg?branch=master
    :target: https://coveralls.io/github/mosquito/lsm-db-extras
    :alt: Coveralls

.. image:: https://cloud.drone.io/api/badges/mosquito/lsm-db-extras/status.svg
    :target: https://cloud.drone.io/mosquito/lsm-db-extras/
    :alt: Drone CI

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


    from lsm_extras import Shelf, LSMDict, LSMTree

    with Shelf("/tmp/test.ldb") as shelf:
        shelf["foo"] = True


    with Shelf("/tmp/test.ldb") as shelf:
        print(shelf["foo"])


    with LSMDict("/tmp/test-dict.ldb") as storage:
        storage[1] = True


    with LSMDict("/tmp/test-dict.ldb") as storage:
        print(storage[1])


    with LSMTree("/tmp/test-tree.ldb") as storage:
        with tree.transaction():
            for i in range(10):
                tree['numbers', i] = i * 2
                tree['strings', i] = str(i)

        print(list(tree.find('strings')))
