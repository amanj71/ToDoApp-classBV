from django.db.backends.postgresql import base  # if using another database like MySQL, import from it
class DatabaseWrapper(base.DatabaseWrapper):
    schema_name = None
