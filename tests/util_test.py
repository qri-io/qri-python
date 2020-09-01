from qri import util
import unittest


class UtilTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_to_snake_case(self):
        self.assertEqual(util.to_snake_case('bodyFormat'), 'body_format')
        self.assertEqual(util.to_snake_case('downloadURL'), 'download_url')
        self.assertEqual(util.to_snake_case('SomeNameLotsOfCaps'),
                         'some_name_lots_of_caps')


if __name__ == '__main__':
  unittest.main()
