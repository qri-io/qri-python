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

    def test_set_fields(self):
        class Component(object):
            pass
        component = Component()
        util.set_fields(component, {'a': 1, 'b': 2}, ['b', 'c'])
        self.assertFalse(hasattr(component, 'a'))
        self.assertEqual(component.b, 2)
        self.assertIsNone(component.c)

    def test_build_repr(self):
        class Subject(object):
            def __init__(self):
                self._fields = ['a', 'b', 'c']
                self.a = 'apple'
                self.b = 'berry'
                self.c = 'cherry'
        s = Subject()
        self.assertEqual(util.build_repr(s),
                         "{'a': 'apple', 'b': 'berry', 'c': 'cherry'}")

    def test_max_len(self):
        self.assertEqual(util.max_len('apples', 8), 'apples')
        self.assertEqual(util.max_len('apples', 6), 'apples')
        self.assertEqual(util.max_len('apples', 5), 'ap...')


if __name__ == '__main__':
  unittest.main()
