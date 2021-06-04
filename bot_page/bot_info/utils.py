from django.core import serializers


def serialize(model, rows: int = False):
    if rows:
        try:
            model = model[len(model)-rows:]
        except AssertionError:
            pass
    model = serializers.serialize("json", model)
    return model
