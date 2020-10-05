#!/usr/bin/python

"""Client for interacting with qri repositories"""

from . import cmd_util, dataset, dsref, error, loader


def list(username=None):
    """list datasets in the user's repository"""
    try:
        objs = loader.instance().list_dataset_objects(username)
    except error.CloudMissingAPIError as e:
        cmd_util.write_missing_cloud_api()
        return None
    datasets = dataset.DatasetList([dataset.Dataset(d) for d in objs])
    datasets.sort(key=lambda d: d.human_ref())
    return datasets


def get(refstr):
    """get a dataset in the repository by reference"""
    ref = dsref.parse_ref(refstr)
    obj = loader.instance().get_dataset_object(ref)
    d = dataset.Dataset(obj)
    return d


def pull(refstr):
    """pull a remote dataset from the registry to the user's repository"""
    ref = dsref.parse_ref(refstr)
    print('Fetching from registry...')
    text = loader.instance().pull_dataset(ref)
    print('Pulled %s: %s' % (ref, text))
    return None


def add(refstr):
    """add is an alias for pull"""
    return pull(refstr)


def sql(query):
    """sql query run against a dataset"""
    cmd = ['qri', 'sql', '--format', 'json', query]
    result, err = cmd_util.shell_exec(cmd)
    if err:
        raise error.QriClientError(err)
    return loader.from_json(result)
