#!/usr/bin/python

"""Client for interacting with qri repositories"""

import json
import os
import re

from .cmd_util import shell_exec, QriClientError
from . import dataset
from . import loader


def list():
    """list datasets in the user's repository"""
    cmd = 'qri list --format json'
    result, err = shell_exec(cmd)
    if err:
        raise QriClientError(err)
    raw_data = json.loads(result)
    datasets = dataset.DatasetList([dataset.Dataset(d) for d in raw_data])
    datasets.sort(key=lambda d: d.human_ref())
    return datasets


def get(ref):
    """get a dataset in the repository by reference"""
    cmd = 'qri get --format json %s' % ref
    result, err = shell_exec(cmd)
    if err:
        raise QriClientError(err)
    d = dataset.Dataset(json.loads(result))
    return d


def pull(ref):
    """pull a remote dataset from the registry to the user's repository"""
    cmd = 'qri pull %s' % ref
    print('Fetching from registry...')
    result, err = shell_exec(cmd)
    if err:
        raise QriClientError(err)
    return 'Pulled %s: %s' % (ref, result)


def add(ref):
    """add is an alias for pull"""
    return pull(ref)


def sql(query):
    """sql query run against a dataset"""
    cmd = f'qri sql --format "json" "{query}"'
    result, err = shell_exec(cmd)
    if err:
        raise QriClientError(err)
    return loader.from_json(result)
