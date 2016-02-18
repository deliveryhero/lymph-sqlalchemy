
class BulkInsert(object):

    """
    Usage:

        user_insert = BulkInsert(session)
        address_insert = BulkInsert(session, dependencies=[user_insert])

        for user in users:
            user_insert.add(user)
        from address in user_addresses:
            address_insert.add(address)

        address_insert.flush()
    """

    def __init__(self, session, count=250, dependencies=None):
        self.session = session
        self.count = count
        self._objects = []
        self.dependencies = dependencies or []

    def add(self, obj):
        self._objects.append(obj)
        if len(self._objects) >= self.count:
            self.flush()

    def flush(self):
        for dependency in self.dependencies:
            dependency.flush()
        self.session.bulk_save_objects(self._objects)
        self.session.flush()
        self._objects = []
