from qri import client, loader
import mock_loader
import unittest


class ClientTests(unittest.TestCase):
    def setUp(self):
        loader.set_instance(mock_loader.MockLoader())

    def test_client_list(self):
        dlist = client.list()
        expect = '[Dataset("my_peer/first_dataset"), Dataset("my_peer/second_dataset"), Dataset("other_peer/third_dataset")]'
        self.assertEqual(str(dlist), expect)

    def test_client_get(self):
        ds = client.get('me/first_dataset')
        expect = 'Dataset("my_peer/first_dataset")'
        self.assertEqual(str(ds), expect)
        self.assertEqual(ds.structure.format, 'csv')

    def test_client_get_readme(self):
        ds = client.get('me/first_dataset')
        readme = ds.readme
        self.assertEqual(str(readme), 'None')
        self.assertEqual(repr(readme), 'None')
        # Get a dataset with a readme
        ds = client.get('me/second_dataset')
        readme = ds.readme
        self.assertEqual(str(readme), '# Hello\n\ncontent')
        self.assertEqual(repr(readme), 'Readme("# Hello\n\ncontent")')


if __name__ == '__main__':
  unittest.main()
