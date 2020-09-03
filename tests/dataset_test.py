from qri import dataset
from qri import loader
import mock_loader
import unittest

# TODO - move these to a better place?
LIST_OBJ = {
    'username': 'me',
    'profileID': 'Qm.profileID',
    'name': 'first_dataset',
    'path': '/ipfs/Qm.path',
    'bodySize': 1,
    'bodyRows': 2,
    'numErrors': 3,
    'bodyFormat': 'json',
    'commitTime': '2020-08-24T20:00:32.171549113Z',
    'fsiPath': '/home/my_user/datasets/first_dataset'
}

GET_OBJ = {
    "bodyPath": "/ipfs/Qm.bodyPath",
    "commit": {
        "author": {"id": "Qm.commit.author.id"},
        "message": "commit.message",
        "timestamp": "2020-01-02T03:04:05.124963898Z",
    },
    "meta": {
        "description": "meta.description",
        "keywords": ["meta.keyword1", "meta.keyword2"],
    },
    "name": "first_dataset",
    "path": "/ipfs/Qm.path",
    "peername": "me",
    "previousPath": "/ipfs/Qm.previousPath",
    "readme": {
        "scriptBytes": "VEVTVCBSRUFETUUK",
    },
    "structure": {
        "checksum": "Qm.structure.checksum",
        "entries": 3,
        "format": "csv",
        "schema": {
            "items": {
                "items": [
                    {"title": "field1", "type": "string"},
                    {"title": "field2", "type": "integer"},
                ],
                "type": "array",
            },
            "type": "array",
        },
    },
}


class DatasetTests(unittest.TestCase):
    def test_init_from_list(self):
        loader.set_instance(mock_loader.DatasetMockLoader())
        ds = dataset.Dataset(LIST_OBJ)
        self.assertEqual(ds.username, 'me')
        self.assertEqual(ds.name, 'first_dataset')
        self.assertEqual(ds.profile_id, 'Qm.profileID')
        self.assertEqual(ds.path, '/ipfs/Qm.path')
        self.assertFalse(ds._is_populated)

    def test_init_from_get(self):
        loader.set_instance(mock_loader.DatasetMockLoader())
        ds = dataset.Dataset(GET_OBJ)
        self.assertEqual(ds.username, 'me')
        self.assertEqual(ds.name, 'first_dataset')
        self.assertEqual(ds.path, '/ipfs/Qm.path')

        self.assertEqual(ds.body_path_value, "/ipfs/Qm.bodyPath")
        self.assertEqual(ds.previous_path_value, "/ipfs/Qm.previousPath")

        # Checking a subset of the possible fields for brevity

        # TODO - should I test every field? I realized it would get pretty verbose but I can.
        # I figured I'd test set_fields and move on.
        # However if you want a super verbose and thorough comparison I can do that.
        self.assertIsInstance(ds.commit_component, dataset.Commit)
        self.assertEqual(ds.commit_component.author, {"id": "Qm.commit.author.id"})
        self.assertEqual(ds.commit_component.message, "commit.message")
        self.assertEqual(ds.commit_component.timestamp, "2020-01-02T03:04:05.124963898Z")

        self.assertIsInstance(ds.meta_component, dataset.Meta)
        self.assertEqual(ds.meta_component.description, 'meta.description')
        self.assertEqual(ds.meta_component.keywords, ['meta.keyword1', 'meta.keyword2'])

        self.assertIsInstance(ds.readme_component, dataset.Readme)
        self.assertEqual(ds.readme_component.script.strip(), "TEST README")

        self.assertIsInstance(ds.structure_component, dataset.Structure)
        self.assertEqual(ds.structure_component.entries, 3)
        self.assertEqual(ds.structure_component.format, 'csv')
        self.assertEqual(ds.structure_component.schema, {
            "items": {
                "items": [
                    {"title": "field1", "type": "string"},
                    {"title": "field2", "type": "integer"},
                ],
                "type": "array"
            },
            "type": "array"
        })

        self.assertIsNone(ds.body_component)

        self.assertTrue(ds._is_populated)

    def test_populate(self):
        loader.set_instance(mock_loader.DatasetMockLoader(get_responses={
            'me/first_dataset': GET_OBJ
        }))
        ds = dataset.Dataset(LIST_OBJ)
        self.assertFalse(ds._is_populated)
        self.assertFalse(hasattr(ds, 'meta_component'))
        ds.meta
        self.assertTrue(ds._is_populated)
        self.assertTrue(hasattr(ds, 'meta_component'))
        self.assertEqual(ds.meta.description, 'meta.description')

    def test_dont_populate_twice(self):
        loader.set_instance(mock_loader.DatasetMockLoader())
        ds = dataset.Dataset(GET_OBJ)
        self.assertTrue(ds._is_populated)
        self.assertTrue(hasattr(ds, 'meta_component'))
        ds.meta # The mock loader should complain if it calls "get"

    def test_body(self):
        loader.set_instance(mock_loader.DatasetMockLoader(get_body_responses={
            'me/first_dataset': 'dataframe standin'
        }))
        ds = dataset.Dataset(GET_OBJ)
        self.assertIsNone(ds.body_component)
        ds.body
        self.assertEqual(ds.body_component, 'dataframe standin')


if __name__ == '__main__':
  unittest.main()
