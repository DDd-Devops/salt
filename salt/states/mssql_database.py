"""
Management of Microsoft SQLServer Databases
===========================================

The mssql_database module is used to create
and manage SQL Server Databases

.. code-block:: yaml

    yolo:
      mssql_database.present
"""

import collections


def __virtual__():
    """
    Only load if the mssql module is present
    """
    if "mssql.version" in __salt__:
        return True
    return (False, "mssql module could not be loaded")


def _normalize_options(options):
    if type(options) in [dict, collections.OrderedDict]:
        return [f"{k}={v}" for k, v in options.items()]
    if type(options) is list and (not options or type(options[0]) is str):
        return options
    # Invalid options
    if type(options) is not list or type(options[0]) not in [
        dict,
        collections.OrderedDict,
    ]:
        return []
    return [o for d in options for o in _normalize_options(d)]


def present(name, containment="NONE", options=None, **kwargs):
    """
    Ensure that the named database is present with the specified options

    name
        The name of the database to manage
    containment
        Defaults to NONE
    options
        Can be a list of strings, a dictionary, or a list of dictionaries
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    if __salt__["mssql.db_exists"](name, **kwargs):
        ret["comment"] = (
            "Database {} is already present (Not going to try to set its options)".format(
                name
            )
        )
        return ret
    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = f"Database {name} is set to be added"
        return ret

    db_created = __salt__["mssql.db_create"](
        name,
        containment=containment,
        new_database_options=_normalize_options(options),
        **kwargs,
    )
    if (
        db_created is not True
    ):  # Non-empty strings are also evaluated to True, so we cannot use if not db_created:
        ret["result"] = False
        ret["comment"] += "Database {} failed to be created: {}".format(
            name, db_created
        )
        return ret
    ret["comment"] += f"Database {name} has been added"
    ret["changes"][name] = "Present"
    return ret


def absent(name, **kwargs):
    """
    Ensure that the named database is absent

    name
        The name of the database to remove
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    if not __salt__["mssql.db_exists"](name):
        ret["comment"] = f"Database {name} is not present"
        return ret
    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = f"Database {name} is set to be removed"
        return ret
    if __salt__["mssql.db_remove"](name, **kwargs):
        ret["comment"] = f"Database {name} has been removed"
        ret["changes"][name] = "Absent"
        return ret
    # else:
    ret["result"] = False
    ret["comment"] = f"Database {name} failed to be removed"
    return ret
