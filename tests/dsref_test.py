from qri import dsref, error
import unittest


class DsrefTests(unittest.TestCase):
    def test_parse_ref(self):
        r = dsref.parse_ref('peer/my_ds')
        self.assertEqual(r.username, 'peer')
        self.assertEqual(r.name, 'my_ds')

    def test_parse_ref_failure(self):
        with self.assertRaises(error.QriClientError):
            dsref.parse_ref('peer/my+ds')


if __name__ == '__main__':
  unittest.main()
