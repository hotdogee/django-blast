from django.core.serializers import serialize
from django.db.models.query import QuerySet
import json
from django.utils.safestring import mark_safe
from django.template import Library

register = Library()

# keep the output safe inside <script> elements
_SCRIPT_ESCAPES = {ord('<'): '\\u003C', ord('>'): '\\u003E', ord('&'): '\\u0026'}

def jsonify(object):
    if isinstance(object, QuerySet):
        return mark_safe(serialize('json', object).translate(_SCRIPT_ESCAPES))
    return mark_safe(json.dumps(object).translate(_SCRIPT_ESCAPES))

register.filter('jsonify', jsonify)
jsonify.is_safe = True