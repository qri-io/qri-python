import pytest
import qri
import pandas as pd

def test_ds_list():
	l = qri.ds_list()
	assert(type(l) == list)
	assert(len(l) > 0)

def test_load_ds():
	name = "movies"
	ds = qri.load_ds(name)
	assert(type(ds.df) == pd.DataFrame)
	assert(ds.name == "movies")
	assert (ds.fields() == list(ds.df.columns))
