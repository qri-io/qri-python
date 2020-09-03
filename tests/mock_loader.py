MOCK_DATASET_LIST = [
    {
        'peername': 'my_peer',
        'name': 'first_dataset',
        'bodyPath': '/mem/SomeBodyPath',
        'structure': {
            'format': 'csv',
        },
    },
    {
        'username': 'my_peer',
        'name': 'second_dataset',
        'bodyPath': '/mem/AnotherBodyPath',
        'structure': {
            'format': 'csv',
        },
        'readme': {
            'scriptBytes': 'IyBIZWxsbwoKY29udGVudA=='
        }
    },
    {
        'peername': 'other_peer',
        'name': 'third_dataset',
        'bodyPath': '/mem/TheirBodyPath',
        'structure': {
            'format': 'csv',
        },
    },
]

MOCK_DATASET_REFS = {
    'my_peer/first_dataset': 0,
    'my_peer/second_dataset': 1,
    'other_peer/third_dataset': 2,
}


class MockLoader(object):
    def list_dataset_objects(self, username=None):
        return MOCK_DATASET_LIST

    def get_dataset_object(self, ref):
        ref = ref.clone()
        if ref.username == 'me':
            ref.username = 'my_peer'
        index = MOCK_DATASET_REFS.get(ref.human())
        if index is None:
            raise RuntimeError('dataset ref not found: "{}"'.format(ref))
        return MOCK_DATASET_LIST[index]

class DatasetMockLoader(object): # TODO - better name and place
    def __init__(self, list_response=None, get_responses=None, get_body_responses=None):
        self.list_response = list_response
        self.get_responses = get_responses or {}
        self.get_body_responses = get_body_responses or {}

    def list_dataset_objects(self, username=None):
        if self.list_response is None:
            raise RuntimeError('Got unexpected call to list_dataset_objects')
        return self.list_response

    def get_dataset_object(self, ref):
        try:
            return self.get_responses[ref.human()]
        except KeyError:
            raise RuntimeError('Got unexpected call to get_dataset_object')

    def load_body(self, ref, structure):
        try:
            return self.get_body_responses[ref.human()]
        except KeyError:
            raise RuntimeError('Got unexpected call to load_body')
