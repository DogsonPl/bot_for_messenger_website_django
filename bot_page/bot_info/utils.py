from django.core import serializers


def serialize(model, rows: int = False):
    if rows:
        # get last x rows from model queryset, if there are less rows than x get all rows
        try:
            model = model[len(model)-rows:]
        except AssertionError:
            pass
    model = serializers.serialize("json", model)
    return model
