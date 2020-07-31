#!/usr/bin/python

"""Client for interacting with qri repositories"""

import json
import os
import re
import pandas as pd

from .cmd_util import shell_exec
from . import dataset


def list():
  """list datasets in the user's repository"""
  cmd = 'qri list --format json'
  result, err = shell_exec(cmd)
  if err:
    raise RuntimeError(err)
  datasets = dataset.DatasetList([dataset.Dataset(d) for d in json.loads(result)])
  datasets.sort(key=lambda d: d.human_ref())
  return datasets


def get(ref):
  """get a dataset in the repository by reference"""
  cmd = 'qri get --format json %s' % ref
  result, err = shell_exec(cmd)
  if err:
    raise RuntimeError(err)
  d = dataset.Dataset(json.loads(result))
  return d


def add(ref):
  """adds a remote dataset from the registry to the user's repository"""
  cmd = 'qri add %s' % ref
  print('Fetching from registry...')
  result, err = shell_exec(cmd)
  return 'Added %s: %s' % (ref, result)

def sql(query):
  cmd = f'qri sql --format "json" "{query}"'
  result, err = shell_exec(cmd)
  return pd.read_json(result)
