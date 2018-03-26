#!/usr/bin/python
import sys
import json
import argparse
from subprocess import Popen, PIPE
import pandas as pd
import re
import os
import shlex
import sys
from collections import OrderedDict
import csv
import time

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO


_HASH_PATTERN = re.compile("^\/\w+\/(\w*)")
_TMP_PATH = "/tmp/qri/"
_MAX_ATTEMPTS = 10
_DELAY = .1

#------------------------------------------------------------------
class QriDatasetError(Exception):
    pass
class DataExportError(QriDatasetError):
    pass
#------------------------------------------------------------------

def _shell_exec_once(command):
	proc = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE)
	stdoutdata, err = proc.communicate()
	if err != "":
		raise Exception(err)
	return stdoutdata

def _shell_exec(command):
	stdoutdata = _shell_exec_once(command)
	for _ in range(_MAX_ATTEMPTS - 1):
		if "error" not in stdoutdata[:15]:
			break
		time.sleep(_DELAY)
		stdoutdata = _shell_exec_once(command)
	return stdoutdata

#------------------------------------------------------------------

def _list_ds():
	""" helper function for getting a list of datasets on your qri node"""
	command = "qri list -f json"
	stdoutdata = _shell_exec(command)
	names_and_hashes = [(ds['name'], ds['path']) for ds in json.loads(stdoutdata)]
	return names_and_hashes

def _export_to_disk(dsname):
    kwargs = dict(dsname=dsname, location=_TMP_PATH)
    command = "qri export -c -a -o {location} {dsname}".format(**kwargs)
    response = _shell_exec(command).split("\n")[:-1]
    if len(response) != 5:
        raise DataExportError("unable to load dataset")


    
def _load_ds(dsname):
    #save dataset to disk from export
    _export_to_disk(dsname)
    clean_name = dsname.split("/")[-1]
    if len(clean_name) <1:
        raise DataExportError("invalid dataset name")
    tmp_path = os.path.join(_TMP_PATH, clean_name)
    # paths to open
    data_path = os.path.join(tmp_path, "data.csv")
    meta_path = os.path.join(tmp_path, "meta.json")
    structure_path = os.path.join(tmp_path, "structure.json")
    dataset_path = os.path.join(tmp_path, "dataset.json")
    # load each of the files into python
    with open(meta_path, "r") as fp:
        meta = json.load(fp)
    with open(structure_path, "r") as fp:
        structure = json.load(fp)
    with open(dataset_path, "r") as fp:
        dataset = json.load(fp)
    data_format = structure.pop("format", dataset["structure"].pop("format", ""))
    if data_format == "":
        raise DataExportError("structure must specify data format")
    if data_format == "csv":
        df = pd.read_csv(data_path)
    elif data_format == "json":
        with open(meta_path, "r") as fp:
            df = json.load(fp)
    else:
        raise NotImplementedError("format '{}' not currently supported.  support for more types coming soon".format(data_format))
    #delete data
    _shell_exec("rm -rf {}".format(os.path.join(_TMP_PATH, clean_name)))
    return df, meta, structure, dataset, data_format


#------------------------------------------------------------------
#------------------------------------------------------------------
class QriDataset(object):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop("name", "")
        self.data = kwargs.pop("data", None)
        self.structure = kwargs.pop("structure", None)
        self.meta = kwargs.pop("meta", None)
        self.defn = kwargs.pop("defn", None)
        self.data_format = kwargs.pop("data_format", "")
        if self.name == "":
            raise QriDatasetError("name is required")
        if not isinstance(self.data, pd.DataFrame) and not isinstance(self.data, list):
            raise QriDatasetError("data is required. type {} not compatible", type(self.data))
        if not self.structure:
            raise QriDatasetError("structure is required")
    		# TODO: generalize for nested fields
        # self.fields = [item["title"] for item in self.structure["schema"]["items"]["items"]]
        if self.data_format == "":
        	raise QriDatasetError("structure.format is a required field")
        # format gets stripped from json.load, need to add back
        self.structure[u"format"] = self.data_format
        # self.defn[u"structure"][u"format"] = self.data_format
            
    def save(self, commit_msg=""):
        # save to disk temporarily
        # save structure
        structure_path = os.path.join(_TMP_PATH, "structure.json")
        with open(structure_path, "w") as fp:
            fp.write(json.dumps(self.structure))
        args = " --structure {}".format(structure_path)
        # save data
        data_path = os.path.join(_TMP_PATH, "data.{}".format(self.data_format))
        if self.data_format == "csv":
            self.data.to_csv(data_path, index=False)
        elif self.data_format == "json":
            with open(data_path, "w") as fp:
                fp.write(json.dumps(self.data))
        args += " --data {}".format(data_path)
        if self.meta:
            meta_path = os.path.join(_TMP_PATH, "meta.json")
            with open(meta_path, "w") as fp:
                fp.write(json.dumps(self.meta))
            args += " --meta {}".format(meta_path)
        #call qri cli
        command = """qri save -t "{}"{} {}""".format(commit_msg, args, self.name)
        out = _shell_exec(command)
        print out
        #delete data
        command = "rm -rf {}".format(os.path.join(_TMP_PATH, "*"))
        
    def save_as(self, name, commit_msg):
        raise NotImplementedError
    #TODO
    def rename_fields(self, name_dict):
        raise NotImplementedError

#------------------------------------------------------------------
def load_data(ds_name):
    if len(ds_name.split("/")) != 2:
        ds_name = u"me/{}".format(ds_name)
    d, m, s, defn, data_format = _load_ds(ds_name)
    ds_params = dict(
        name=ds_name,
        data=d,
        structure=s,
        meta=m,
        defn=defn,
        data_format=data_format,
    )
    return QriDataset(**ds_params)

#------------------------------------------------------------------
#------------------------------------------------------------------

# def _get_name_from_hash(_hash):
# 	""" helper function to get a dataset's name from its hash"""
# 	names_and_hashes = _list_ds()
# 	full_hash_lookup = {h: n for n, h in names_and_hashes}
# 	partial_hash_lookup = dict()
# 	for n, h in names_and_hashes:
# 		matches = re.findall(_H, h)
# 		if len(matches) == 1:
# 			partial_hash = matches[0]
# 			partial_hash_lookup[partial_hash] = n
# 	if _hash in full_hash_lookup:
# 		return full_hash_lookup[_hash]
# 	if _hash in partial_hash_lookup:
# 		return partial_hash_lookup[_hash]

# def _get_hash_from_name(name):
# 	""" Utility function to get a dataset's hash from its name"""
# 	names_and_hashes = _list_ds()
# 	name_lookup = {n: h for n, h in names_and_hashes}
# 	if name in name_lookup:
# 		return name_lookup[name]

# def _run_select_all(name):
# 	""" helper function for getting data from qri commandline"""
# 	command = """qri run -f csv "select * from {}" """.format(name)
# 	stdoutdata = _shell_exec(command)
# 	if stdoutdata[:3].lower() in ["csv", "txt"]:
# 		stdoutdata = stdoutdata[3:]
# 	return StringIO(stdoutdata)

# def _get_ds_info(name):
# 	""" helper function for getting a dataset's info from qri node"""
# 	_hash = _get_hash_from_name(name)
# 	command = """qri info -f json {}""".format(_hash)
# 	stdoutdata = _shell_exec(command)
# 	info = json.loads(stdoutdata)
# 	return info

# def _get_ds_fields(name, verbose=False):
# 	""" helper function for getting a dataset's fields from qri node"""
# 	info = _get_ds_info(name)
# 	if verbose:
# 		return info["structure"]["schema"]["fields"]
# 	else:
# 		return [f["name"] for f in info["structure"]["schema"]["fields"]]


# #------------------------------------------------------------------
def ds_list(name_only=True):
	""" get a listing of datasets on a qri node"""
	names_and_hashes = _list_ds()
	if name_only:
		return [items[0] for items in names_and_hashes]
	else:
		return names_and_hashes


# class QriDataset(object):
# 	""" QriDataset consists of a pandas DataFrame with additional 
# 	qri-related attributes and methods

# 	Attributes:
# 		name (str): name of qri dataset
# 		title (str): title of qri dataset
# 		description (str): description of qri dataset
# 		path (stro): hash of datset representing its unique address
# 			based on the files's content
# 		structure (dict): metadat containint the dataset's fields and schema
# 		timestamp (str): timestamp indicating when the dataset was created
# 		df (:obj: pd.DataFrame): data table
# 	"""

# 	def __init__(self, *args, **kwargs):
# 		self.name = kwargs.pop("name", "")
# 		self.title = kwargs.pop("title", "")
# 		self.description = kwargs.pop("description", "")
# 		self.path = kwargs.pop("data", "")
# 		self.structure = kwargs.pop("structure", None)
# 		df_table = kwargs.pop("df_table", None)
# 		if df_table:
# 			self.df = df_table
# 		else:
# 			self.df = self._load_data_table(self.name)
# 		del df_table

# 	def _load_data_table(self, name):
# 		""" gets data and headers and loads into dataframe """
# 		fields = _get_ds_fields(name)
# 		data_table = _run_select_all(name)
# 		return pd.read_csv(data_table, header=None, names=fields)

# 	def fields(self, verbose=False):
# 		""" get the fields of the dataset from the datset object """
# 		if not self.structure:
# 			info = _get_ds_info(self.name)
# 			self.structure = info["structure"]
# 		if verbose:
# 			return self.structure["schema"]["fields"]
# 		else:
# 			return [f["name"] for f in self.structure["schema"]["fields"]]

# def load_ds(name):
# 	""" Loads a dataset from a qri node """
# 	info = _get_ds_info(name)
# 	# if err != "":
# 	# 	raise Exception("error: {}".format(err))
# 	info["name"] = name
# 	return QriDataset(**info)

# #------------------------------------------------------------------

# def _save_tmp_table(ds):
# 	ds.df.to_csv(_TMP_TABLE_PATH, index=False, quoting=csv.QUOTE_NONNUMERIC)

# def _remove_tmp_table():
# 	command = """rm -f {}""".format(_TMP_TABLE_PATH)
# 	_shell_exec(command)

# def _remove_tmp_meta():
# 	command = """rm -f {}""".format(_TMP_META_PATH)
# 	_shell_exec(command)

# def _save_tmp_meta(meta_dict):
# 	with open(_TMP_META_PATH, "w") as fp:
# 		fp.write(json.dumps(meta_dict))

# def _get_flat_metadata(ds):
# 	d = OrderedDict()
# 	d["title"] = ds.title
# 	d["description"] = ds.description
# 	d["fields"] = ds.fields(verbose=True)
# 	return d

# #------------------------------------------------------------------

# def save_ds(dataset, name, metadata={}, transfer_meta=True):
# 	""" Save a QriDataset as a new QriDataset

# 	Args:
# 		dataset (:obj: QriDataset): dataset object to save
# 		name (str): name to give dataset
# 		metadata (dict): a flat dictionary of metdata to specify the 
# 			title, description, column names and descriptions, etc.
# 		transfer_meta (bool): if True, if a metadata field is not 
# 			provided `save_ds` will attempt to tranfer values from the 
# 			source datset
# 	"""
# 	#check to make sure there isn't a name conflict
# 	existing_names = _list_ds()
# 	if name in existing_names:
# 		raise Exception("name '{}' already exists, name must be unique".format(name))
# 	if not transfer_meta and metadata == {}:
# 		_save_tmp_table(dataset)
# 		command = """qri add -f {} -n {}""".format(_TMP_TABLE_PATH, name)
# 		stdoutdata = _shell_exec(command)
# 		print stdoutdata
# 		_remove_tmp_table()
# 		return
# 	else:
# 		# ensure consistent field structure
# 		if "fields" in metadata and type(metadata["fields"][0]) == str:
# 			metadata["fields"] = [{"name": val} for val in metadata["fields"]]
# 		if transfer_meta:
# 			old_fields = _get_flat_metadata(dataset)
# 			# use old value where there is no value in metadata
# 			for k in old_fields:
# 				metadata[k] = metadata.get(k, old_fields[k])
# 		#update metadata
# 		structured_metadata = OrderedDict()
# 		structured_metadata["title"] = metadata.get("title", "")
# 		structured_metadata["description"] = metadata.get("description", "")
# 		ordered_col_names = list(dataset.df.columns)
# 		if "fields" in metadata and metadata["fields"][0]["name"] != "field_1":
# 			field_lookup = {f["name"]: f for f in metadata["fields"]}
# 			fields = list()
# 			for col_name in ordered_col_names:
# 				f = {"name": col_name}
# 				if col_name in field_lookup:
# 					if "description" in field_lookup[col_name]:
# 						f["description"] = field_lookup[col_name]["description"]
# 					if "title" in field_lookup[col_name]:
# 						f["title"] = field_lookup[col_name]["title"]
# 				fields.append(f)
# 			structured_metadata["structure"] = OrderedDict()
# 			structured_metadata["structure"]["schema"] = OrderedDict()
# 			structured_metadata["structure"]["schema"]["fields"] = fields
# 			_save_tmp_meta(structured_metadata)
# 			_save_tmp_table(dataset)
# 			command = """qri add -f {} -m {} -n {}""".format(_TMP_TABLE_PATH, _TMP_META_PATH, name)
# 			stdoutdata = _shell_exec(command)
# 			print stdoutdata
# 			_remove_tmp_table()
# 			_remove_tmp_meta()
# 			return

# def remove_ds(name):
# 	""" removes a dataset from your qri node """
# 	all_datasets = ds_list()
# 	if name not in all_datasets:
# 		raise Exception("no datset named '{}' to delete".format(name))
# 	command = """qri remove {}""".format(name)
# 	stdoutdata = _shell_exec(command)
# 	print(stdoutdata)


def main():
	print("please use the qri commandline client @ `github.com/qri-io/qri`")

if __name__ == "__main__":
	main()