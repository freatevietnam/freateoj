from django.db import connection, transaction


class LockModel(object):
    def __init__(self, write, read=()):
        self.write_tables = [model._meta.db_table for model in write]
        self.read_tables = [model._meta.db_table for model in read]
        self.cursor = connection.cursor()

    def __enter__(self):
        for table in self.write_tables:
            self.cursor.execute('LOCK TABLE %s IN ACCESS EXCLUSIVE MODE' % connection.ops.quote_name(table))
        for table in self.read_tables:
            self.cursor.execute('LOCK TABLE %s IN SHARE MODE' % connection.ops.quote_name(table))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            transaction.commit()
        else:
            transaction.rollback()
        self.cursor.close()
