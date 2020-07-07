#!/usr/bin/python

"""Client for interacting with qri repositories"""

import json
import os
import re

from .cmd_util import shell_exec


class Dataset(object):
  def __init__(self, obj):
    self.username = obj.get('username')
    self.name = obj.get('name')
    self.profileID = obj.get('profileID')
    self.path = obj.get('path')
    self.bodySize = obj.get('bodySize')
    self.bodyRows = obj.get('bodyRows')
    self.bodyFormat = obj.get('bodyFormat')
    # TODO(dustmop): Remove me.
    if 'bodyFromat' in obj:
      self.bodyFormat = obj.get('bodyFromat')
    self.numErrors = obj.get('numErrors')
    self.commitTime = obj.get('commitTime')

  def humanRef(self):
    return '%s/%s' % (self.username, self.name)

  def __repr__(self):
    return '#<Dataset>'

  def __str__(self):
    return 'Dataset(%s)' % self.humanRef()


def list():
  """list datasets in the user's repository"""
  cmd = 'qri list --format json'
  result, err = shell_exec(cmd)
  datasets = [Dataset(d) for d in json.loads(result)]
  datasets.sort(key=lambda d: d.humanRef())
  return datasets
