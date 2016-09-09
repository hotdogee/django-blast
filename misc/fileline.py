#
#  Functions to print current file name and line number.
#  and format http request.
#
from django.views.debug import get_exception_reporter_filter
import inspect
import sys

def line():
     return inspect.currentframe().f_back.f_lineno

def file():
     return inspect.currentframe().f_back.f_code.co_filename

def request(request):
    filter = get_exception_reporter_filter(request)
    request_repr = '\n{0}'.format(filter.get_request_repr(request))
    return request_repr

