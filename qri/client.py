#!/usr/bin/python
import sys
import json
import argparse
from subprocess import Popen, PIPE
import pandas as pd
import re
import shlex
import sys
from collections import OrderedDict
import csv

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO


_HASH_PATTERN = re.compile("^\/\w+\/(\w*)\/dataset\.json")
_TMP_TABLE_PATH = "/tmp/tmp.csv"
_TMP_META_PATH = "/tmp/meta_tmp.json"

def _shell_exec(command):
		proc = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE)
		stdoutdata, err = proc.communicate()
		if err != "":
			raise Exception(err)
		return stdoutdata

def _list_ds():
	""" helper function for getting a list of datasets on your qri node"""
	command = "qri list -f json"
	stdoutdata = _shell_exec(command)
	names_and_hashes = [(ds['name'], ds['path']) for ds in json.loads(stdoutdata)]
	return names_and_hashes

def _get_name_from_hash(_hash):
	""" Utility function to get a dataset's name from its hash"""
	names_and_hashes = _list_ds()
	full_hash_lookup = {h: n for n, h in names_and_hashes}
	partial_hash_lookup = dict()
	for n, h in names_and_hashes:
		matches = re.findall(_H, h)
		if len(matches) == 1:
			partial_hash = matches[0]
			partial_hash_lookup[partial_hash] = n
	if _hash in full_hash_lookup:
		return full_hash_lookup[_hash]
	if _hash in partial_hash_lookup:
		return partial_hash_lookup[_hash]

def _get_hash_from_name(dsname):
	""" Utility function to get a dataset's hash from its name"""
	names_and_hashes = _list_ds()
	name_lookup = {n: h for n, h in names_and_hashes}
	if dsname in name_lookup:
		return name_lookup[dsname]

def list_ds(name_only=True):
	"""get a listing of datasets on your qri node"""
	names_and_hashes = _list_ds()
	if name_only:
		return [items[0] for items in names_and_hashes]
	else:
		return names_and_hashes

def ds_info(dsname):
	""" get a dataset's metadata as a dict

	Args:
		dsname (str): name of the dataset of interest

	Returns:
		meta (dict): dictionary containing dataset metadata
	"""
	_hash = _get_hash_from_name(dsname)
	command = "qri info -f json {}".format(_hash)
	stdoutdata = _shell_exec(command)
	meta = json.loads(stdoutdata)
	return meta

class Structure(object):
	""" `Structure` objects are describe the structure of a `Dataset`

	Attributes:
		_format (str): the format of the qri `Dataset`
		formatConfig (dict): describes the formatConfig of the qri `Dataset`
		schema (dict): describes the schema of the qri `Dataset`
	"""
	def __init__(self,
							 format=None,
							 formatConfig=None,
							 schema=None,
							 **kwargs):
		self._format = format
		self.formatConfig = formatConfig
		self.schema = schema

	def fields(self, verbose):
		""" Gets a list of the dataset's fields

		Args:
			verbose (bool): flag to include just names or names, titles, 
				descriptions of each field

		Returns:
			list: If `verbose` is True, returns a list of dictionaries 
			including the name, title, and description for each field in 
			the dataset; if set to False, `fields` returns a list of field 
			names
		"""
		_fields = self.schema["fields"]
		if verbose:
			return _fields
		return [f["name"] for f in _fields]

class QriDataFrame(pd.DataFrame):
	""" TODO: docstring
	Attributes
		attr1 (type): desc
		attr2 (type): desc
	"""
	_metadata = [ "name", 
								"title", 
								"description", 
								"data_hash", 
								"timestamp", 
								"structure",
							]

	def __init__(self, *args, **kwargs):
		#self.new_thang = new_thang
		self.name = kwargs.pop('name', None)
		self.title = kwargs.pop('title', None)
		self.description = kwargs.pop('description', None)
		self.data_hash = kwargs.pop('data', None)
		structure_dict = kwargs.pop('structure', None)
		self.structure = Structure(**structure_dict)
		data_table = kwargs.pop('data_table', None)
		if data_table:
			df_table = data_table
		else:
			df_table = self._load_data()
		super(QriDataFrame, self).__init__(df_table)
		

	@property
	def _constructor(self):
		return QriDataFrame

	def fields(self, verbose=False):
		""" Gets a list of the dataset's fields by calling fields on its
		`structure` attribute

		Args:
			verbose (bool): flag to include just names or names, titles, 
				descriptions of each field; default=False

		Returns:
			list: If `verbose` is True, returns a list of dictionaries 
			including the name, title, and description for each field in 
			the dataset; if set to False, `fields` returns a list of field 
			names
		"""
		return self.structure.fields(verbose=verbose)

	def _load_data(self):
		""" Loads data into `Dataset`

		Returns:
			output (:obj: pd.DataFrame): pandas dataframe of Dataset with corresponding name

		"""
		command = """qri run -f csv "select * from {}" """.format(self.name)
		stdoutdata = _shell_exec(command)
		if stdoutdata[:3].lower() in ["csv", "txt"]:
			stdoutdata = stdoutdata[3:]
			output = pd.read_csv(StringIO(stdoutdata), header=None, names=self.fields())
		return output

def load_ds(dsname):
	""" Loads a dataset from your qri node
	"""
	info = ds_info(dsname)
	info["name"] = dsname
	#info["data_table"] = None
	qdf = QriDataFrame(**info)
	return qdf

def _save_tmp_table(ds):
	ds.to_csv(_TMP_TABLE_PATH, index=False, quoting=csv.QUOTE_NONNUMERIC)

def _remove_tmp_table():
	command = """rm -f {}""".format(_TMP_TABLE_PATH)
	_shell_exec(command)

def _remove_tmp_meta():
	command = """rm -f {}""".format(_TMP_META_PATH)
	_shell_exec(command)

def _save_tmp_meta(meta_dict):
	with open(_TMP_META_PATH, "w") as fp:
		fp.write(json.dumps(meta_dict))

def _get_flat_metadata(ds):
	d = OrderedDict()
	d["title"] = ds.title
	d["description"] = ds.description
	d["fields"] = ds.fields(verbose=True)
	return d

def save_ds(dataset, name, metadata={}, transfer_meta=True):
	""" Save a dataset as a new dataset

	Args
		dataset (:obj: qri.Dataset): dataset object to save
		name (str): name to give to dataset
		metadata (dict): a flat dictionary of metadata to specify the 
			title, description, column names and descriptions, etc.
		transfer_meta (bool): if True, if a metadata field is not
			provided `save_ds` will attempt to transfer values from the 
			source dataset
	"""
	existing_names = _list_ds()
	if name in existing_names:
		raise Exception("name '{}' already exists, name must be unique".format(name))
	if not transfer_meta and metadata == {}:
		_save_tmp_table(dataset)
		command = """qri add -f {} -n {}""".format(_TMP_TABLE_PATH, name)
		stdoutdata = _shell_exec(command)
		print stdoutdata
		_remove_tmp_table()
		return
	else:
		# ensure consistent field structure
		if "fields" in metadata and type(metadata["fields"][0]) == str:
			metadata["fields"] = [{"name": val} for val in metadata["fields"]]
		if transfer_meta:
			old_fields = _get_flat_metadata(dataset)
			for k in old_fields:
				metadata[k] = metadata.get(k, old_fields[k])
		#update metadata
		structured_metadata = OrderedDict()
		structured_metadata["title"] = metadata.get("title", "")
		structured_metadata["description"] = metadata.get("description", "")
		ordered_col_names = list(dataset.columns)
		if "fields" in metadata and metadata["fields"][0]["name"] != "field_1":
			field_lookup = {f["name"]: f for f in metadata["fields"]}
			fields = list()
			for col_name in ordered_col_names:
				f = {"name": col_name}
				if col_name in field_lookup:
					if "description" in field_lookup[col_name]:
						f["description"] = field_lookup[col_name]["description"]
					if "title" in field_lookup[col_name]:
						f["title"] = field_lookup[col_name]["title"]
				fields.append(f)
			structured_metadata["structure"] = OrderedDict()
			structured_metadata["structure"]["schema"] = OrderedDict()
			structured_metadata["structure"]["schema"]["fields"] = fields
			_save_tmp_meta(structured_metadata)
			_save_tmp_table(dataset)
			command = """qri add -f {} -m {} -n {}""".format(_TMP_TABLE_PATH, _TMP_META_PATH, name)
			stdoutdata = _shell_exec(command)
			print stdoutdata
			_remove_tmp_table()
			_remove_tmp_meta()
			return


def install_qri(cmd_only=False):
	"""Utility to install qri if it's not already installed"""
	#install qri cmd
	command1 = "go get github.com/qri-io/qri"
	command2 = "brew install qri"
	print u"attempting to install qri cli"
	_shell_exec(command1)
	print "qri cli installation complete"
	if not cmd_only:
		_shell_exec(command2)
		print "qri desktop installation complete"
	


def main():
	# TODO
	print("please use the qri commandline client @ github.com/qri-io/qri")

if __name__ == "__main__":
	main()