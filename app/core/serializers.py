
class LocalCache(object):

    def __init__(self):
        self._cache = {}

    def __getitem__(self, key):
        return self._cache[key]

    def __setitem__(self, key, item):
        self._cache[key] = item

    def cached(self, key):
        if key in self._cache.keys():
            return True
        return False


class Serializer(object):
    """ Takes a SQLA object and a list of fields and returns a
    JSON serializable dictionary."""

    cache = LocalCache()

    def __init__(self, fields, debug=False):
        self.debug = debug

        self.date_format = '%Y-%m-%dT%H:%M:%SZ' # '%Y-%m-%dT%H:%M:%S%z' #  YYYY-MM-DDTHH:mm:ss.sssZ
        self.fields = fields
        self.fields.append('id')
        self.fields = list(set(self.fields))
        self.output = {}
        self.cache = self.__class__.cache
        self.logger = logging.getLogger('.'.join([__name__, self.__class__.__name__]))
        if self.debug:
            self.logger.setLevel(logging.DEBUG)

    def __call__(self, obj):
        self.build_output(obj)
        return self.output

    def is_list(self, item):
        return True if isinstance(item, list) else False

    def process_list(self, item):
        return [self.process_obj(subitem) for subitem in item]

    def process_non_recursive_list(self, item):
        return [subitem.id for subitem in item]

    def is_date(self, item):
        return True if isinstance(item, datetime.datetime) else False

    def process_date(self, item):
        return item.isoformat()

    def is_model(self, item):
        return True if isinstance(item, Base) else False

    def process_model(self, item):
        if isinstance(item, Writing):
            return { 'id': item.id, 'title': item.title}
        else:
            return item.serialize

    def jsonify(self):
        return json.dumps(self.output)

    def test_json(self, item):
        try:
            json.dumps(item)
            return True
        except TypeError:
            return False

    def build_output(self, obj):
        for field in self.fields:
            if hasattr(obj, field):
                item = getattr(obj, field, None)
                if item != None:
                    self.output[field] = self.process_obj(item)
            else:
                self.logger.debug('Skipping field - {}'.format(field))

    def process_obj(self, item):
        # pass on None objects
        if item is None:
            raise TypeError('NoneType Object passed to Serializer.process_obj')

        elif self.is_date(item):
            return self.process_date(item)

        elif self.is_model(item):
            return  self.process_model(item)

        elif self.is_list(item):
            return  self.process_list(item)

        elif self.test_json(item):
            return item
        else:
            raise TypeError("Could not process item {}".format(item))


class DeSerializer(object):
    """For the most part, SQLAlchemy makes updating a model
    from json straightforward. But we need to catch relationships."""

    def __init__(self, model):
        self.model = model
        self.json_mapper = {
            'tags': {
                'is_list': True,
                'model': Tag
                },
            'authors': {
                'is_list': True,
                'model': Author
                },
            'articles': {
                'is_list': True,
                'model': Article,
                },
            'responses': {
                'is_list': True,
                'model': Article,
                },
            'respondees': {
                'is_list': True,
                'model': Article,
                },
            'book_reviewed': {
                'is_list': False,
                'model': Book
                },
            'issue': {
                'is_list': False,
                'model': Issue
                }
            }

    def __call__(self, _json):
        self.build_output(_json)
        return self.model

    def is_submodel(self, key):
        return True if key in self.json_mapper.keys() else False

    def is_list(self, key):
        return self.json_mapper[key]['is_list']

    def query_submodel(self, submodel, qid):
        return db.session.query(submodel).get(qid)

    def build_output(self, _json):
        for key in _json:
            setattr(self.model, key, self.process_obj(_json(key)))

    def process_obj(self, key, value):
        if self.is_submodule(key):
            sub_model = self.json_mapper[key]['model']
            # if not self.is_list(key):
            # # Iterate through the keys of the submodel
            #     _id = None
            #     for subval in values:
            #         setattr(sub_model


            # if self.is_list(self, key):
            # pass

            # sub_json = _json[key]

            #     setattr(self.model, key, _json[key])
            # else:
            #     submodule_list = []
            #     for subjson in _json[key]:
            #         for subkey in subjson:
            #             setattr(submodel, subkey, subjson[key])
            #         submodule_list.append(
            # else:
            #     setattr(self.model, key, _json[key])