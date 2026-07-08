# PostgreSQL full-text search implementation

from django.db import connection, models
from django.db.models.query import QuerySet


class SearchQuerySet(QuerySet):
    DEFAULT = ''
    BOOLEAN = ' BOOLEAN'
    NATURAL_LANGUAGE = ''
    QUERY_EXPANSION = ''

    def __init__(self, fields=None, **kwargs):
        super(SearchQuerySet, self).__init__(**kwargs)
        self._search_fields = fields

    def _clone(self, *args, **kwargs):
        queryset = super(SearchQuerySet, self)._clone(*args, **kwargs)
        queryset._search_fields = self._search_fields
        return queryset

    def search(self, query, mode=DEFAULT):
        meta = self.model._meta

        # Get the column names from the model
        columns = [meta.get_field(name).column for name in self._search_fields]

        # Build PostgreSQL ts_vector expression from all search columns
        tsvector_parts = []
        for column in columns:
            col_ref = connection.ops.quote_name(column)
            tsvector_parts.append(f"COALESCE({col_ref}, '')")
        tsvector_expr = " || ' ' || ".join(tsvector_parts)

        # Build the full-text search query
        # Use plainto_tsquery for simple search, or to_tsquery for boolean mode
        if mode == self.BOOLEAN:
            # Convert MySQL boolean mode operators to PostgreSQL tsquery syntax
            # MySQL: +word -word word~ "phrase"
            # PostgreSQL: word & !word & word:* & 'phrase'
            pg_query = query
            pg_query = pg_query.replace('+', '')
            pg_query = pg_query.replace('-', '!')
            # Wrap remaining terms with :* for prefix matching
            terms = pg_query.split()
            processed = []
            for term in terms:
                if term.startswith('"') and term.endswith('"'):
                    processed.append(f"'{term[1:-1]}'")
                elif term.startswith('!'):
                    processed.append(f"!{term[1:]}:*")
                else:
                    processed.append(f"{term}:*")
            pg_query = ' & '.join(processed) if processed else "''"
            tsquery_expr = f"to_tsquery('english', {connection.ops.quote_value(pg_query)})"
        else:
            tsquery_expr = f"plainto_tsquery('english', {connection.ops.quote_value(query)})"

        # Calculate relevance score using ts_rank
        relevance_expr = f"ts_rank(to_tsvector('english', {tsvector_expr}), {tsquery_expr})"

        # Build the WHERE clause using tsvector @@ tsquery
        where_expr = f"to_tsvector('english', {tsvector_expr}) @@ {tsquery_expr}"

        # Add the extra SELECT and WHERE options
        return self.extra(select={'relevance': relevance_expr},
                          where=[where_expr])


class SearchManager(models.Manager):
    def __init__(self, fields=None):
        super(SearchManager, self).__init__()
        self._search_fields = fields

    def get_queryset(self):
        if self._search_fields is not None:
            return SearchQuerySet(model=self.model, fields=self._search_fields)
        return super(SearchManager, self).get_queryset()

    def search(self, *args, **kwargs):
        return self.get_queryset().search(*args, **kwargs)
