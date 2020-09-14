from qri import error
import unittest


class ErrorsTests(unittest.TestCase):
    def test_string_error(self):
        err = error.QriClientError('text')
        self.assertEqual(str(err), 'text')

    def test_bytes_error(self):
        err = error.QriClientError(b'binary')
        self.assertEqual(str(err), 'binary')

    def test_remove_color_from_error(self):
        err = error.QriClientError(b'\x1b[0;34mERROR')
        self.assertEqual(str(err), 'ERROR')


if __name__ == '__main__':
  unittest.main()
