from django.core import serializers


def serialize_to_json(queryset, rows: int = 0):
    """
    :param queryset: django model queryset
    :param rows: if set to 0, get all rows from query
    :return serialized queryset to json
    """
    if rows:
        # get last x rows from model queryset, if there are less rows than x get all rows
        try:
            queryset = queryset[len(queryset)-rows:]
        except AssertionError:
            pass
    queryset = serializers.serialize("json", queryset)
    return queryset
