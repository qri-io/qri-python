#!/usr/bin/python
""" A python client for interacting with qri datasets"""
from subprocess import Popen, PIPE
import json
import os
import re
import shlex
import time

import pandas as pd


_HASH_PATTERN = re.compile(r'^\/\w+\/(\w*)')
_TMP_PATH = os.environ.get("HOME")
_MAX_ATTEMPTS = 10
_DELAY = .1


#---------------------------------------------------------------------
def _shell_exec_once(command, cwd=None):
  """ helper function to execute bash commands and return output"""
  if cwd:
    proc = Popen(shlex.split(command),
                 stdin=PIPE,
                 stdout=PIPE,
                 stderr=PIPE,
                 cwd=cwd)
    stdoutdata, err = proc.communicate()
    return stdoutdata, err
  # else
  proc = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE)
  stdoutdata, err = proc.communicate()
  return stdoutdata.decode(), err

def _shell_exec(command):
  """ helper function to deal with unreliable commands that may
      temporarily fail but succeed on a repeated attempt"""
  stdoutdata, _ = _shell_exec_once(command)
  for _ in range(_MAX_ATTEMPTS - 1):
    if "error" not in stdoutdata[:15]:
      break
    time.sleep(_DELAY)
    stdoutdata, _ = _shell_exec_once(command)
  return stdoutdata

#---------------------------------------------------------------------
def clean_up_files(paths):
  """ deletes the files listed in paths """
  for path in paths:
    cmd = "rm -rf {}".format(path)
    _shell_exec(cmd)

def strip_color(colored_text):
  """ strips color characters to return plaintext for when the
      global color flag cannot be overriden"""
  ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
  return ansi_escape.sub('', colored_text)
#---------------------------------------------------------------------

def shift_root_down(parent_dict):
  """ shifts the root key down to its child dict as a value with
      key 'root', making the child dict the top level dict"""
  keys = list(parent_dict.keys())
  if len(keys) > 1:
    print("error: dict must have single root")
  else:
    root = keys[0]
    child_dict = parent_dict[root]
    child_dict['root'] = root
    return child_dict

def shift_root_up(sibling_dict):
  """ reverses `shift_root_down()`"""
  if 'root' not in sibling_dict:
    print("error: no root key found")
  else:
    root_val = sibling_dict['root']
    del sibling_dict['root']
    parent_dict = {root_val: sibling_dict}
    return parent_dict

class QriDataset(object):
  """ QriDataset holds a qri dataset body as a dataframe and its head
      as a dictionary
  """
  def __init__(self, body, head, name):
    self.body = body
    self.head = head
    self.ds_name = name

  # TODO: implement
  # def _update_head_from_body(self):
  #  pass

  def save(self, commit_msg, publish=True):
    """ Saves a dataset back to user's repo
    """
    tmp_body_save_path = os.path.join(_TMP_PATH, "body.json")
    tmp_head_save_path = os.path.join(_TMP_PATH, "head.json")
    if is_csv(self.head):
      tmp_body_save_path = tmp_body_save_path.replace(".json", ".csv")
    body = self.body
    head = self.head
    head['bodyPath'] = tmp_body_save_path
    name = self.ds_name
    head['name'] = name
    # save body to temp file
    if is_csv(self.head):
      _ = body.where(
          (pd.notnull(body)),
          None).to_csv(tmp_body_save_path, index=False)
    else:
      with open(tmp_body_save_path, "w") as fp:
        body_as_dict = body.where(
            (pd.notnull(body)),
            None).to_dict(orient="records")
        json.dump(body_as_dict, fp, indent=2)
    # save head to temp file
    with open(tmp_head_save_path, "w") as fp:
      json.dump(head, fp, indent=2)
    flags = {"head_path": tmp_head_save_path,
             "commit_msg": commit_msg,
             "name": name,
             "publish": "-p " if publish else "",
            }

    cmd = ("qri save {publish}"
           "--file '{head_path}' "
           "-t '{commit_msg}' {name}").format(**flags)
    result = _shell_exec(cmd)
    print(result)
    # remove tmp files
    # clean_up_files([tmp_body_save_path, tmp_head_save_path])
    print("dataset saved")

#---------------------------------------------------------------------
def is_csv(head):
  """ helper function to check if qri says something is a csv"""
  if (('structure' in head) and
      ('format' in head['structure']) and
      (head['structure']['format'].lower() == "csv")):
    return True
  # (else)
  return False

def convert_csv(body):
  """ converts internal csv representation in qri to json
      representation"""
  field_names = body[0]
  data = body[1:]
  new_data = list()
  for row in data:
    kv_dict = dict()
    for key, value in zip(field_names, row):
      kv_dict[key] = value
    new_data.append(kv_dict)
  return new_data

#---------------------------------------------------------------------
def _load_ds_body(name, fix_csv=False):
  """ helper function, loads the data/ 'body' of the dataset """
  flags = {"name": name}
  cmd = "qri body -a {name}".format(**flags)
  result = _shell_exec(cmd)
  data = json.loads(result)
  if fix_csv:
    data = convert_csv(data)
  return pd.DataFrame.from_records(data)

def _load_ds_head(name):
  """ helper function, loads the metadata/ 'head' of the dataset"""
  flags = {"name": name}
  cmd = "qri get -f json {name}".format(**flags)
  result = _shell_exec(cmd)
  parent_dict = json.loads(result)
  return shift_root_down(parent_dict)

def load_ds(ds_name):
  """ loads a dataset in to a QriDataset object """
  if len(ds_name.split("/")) != 2:
    ds_name = u"me/{}".format(ds_name)
  head = _load_ds_head(ds_name)
  if is_csv(head):
    body = _load_ds_body(ds_name, fix_csv=True)
  else:
    body = _load_ds_body(ds_name, fix_csv=False)

  return QriDataset(body, head, ds_name)

#---------------------------------------------------------------------
def _list_ds(limit, offset):
  """ helper function for `list_ds()`"""
  flags = {"limit": limit, "offset": offset, "format": "json"}
  cmd = "qri -l {limit} -o {offset} -f {format} list".format(**flags)
  result = _shell_exec(cmd)
  return json.loads(result)

def list_ds(limit=25, offset=0, name_only=True):
  """ lists datasets currently in user repo """
  datasets = _list_ds(limit, offset)
  if name_only:
    return ["{}/{}".format(x["peername"], x["name"]) for x in datasets]
  # (else)
  return datasets
