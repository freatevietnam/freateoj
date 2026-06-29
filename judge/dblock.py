from django.db import connection, transaction


class LockModel(object):
    def __init__(self, write, read=()):
        self.write_tables = [model._meta.db_table for model in write]
        self.read_tables = [model._meta.db_table for model in read]

    def __enter__(self):
        self.atomic = transaction.atomic()
        self.atomic.__enter__()
        self.cursor = connection.cursor()
        for table in self.write_tables:
            self.cursor.execute('LOCK TABLE %s IN ACCESS EXCLUSIVE MODE' % connection.ops.quote_name(table))
        for table in self.read_tables:
            self.cursor.execute('LOCK TABLE %s IN SHARE MODE' % connection.ops.quote_name(table))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        return self.atomic.__exit__(exc_type, exc_val, exc_tb)
