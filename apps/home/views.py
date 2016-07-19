import json
import requests

from collections import OrderedDict
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from .utils import ERROR_CODE_LIST, error_status, pretty_json

SERVER_LIST = [("1","http://52.72.172.54:8080/fhir/baseDstu2/"),]
DEFAULT_FHIR_SERVER = "http://52.72.172.54:8080/fhir/baseDstu2/"

def authenticated_home(request):
    if request.user.is_authenticated():
        name = _('Authenticated Home')
        # this is a GET
        context = {'name': name}
        template = 'authenticated-home.html'
    else:
        name = ('home')
        context = {'name': name}
        template = 'index.html'
    return render(request, template, context)


def show_result(request, srvr, resource, hi_fld, *args, **kwargs):
    """ display a results page with json code embedded """

    print("We made it to the result page:%s / %s / %s" % (srvr,
                                                          resource,
                                                          hi_fld))

    server_url = DEFAULT_FHIR_SERVER
    for num, server in SERVER_LIST:
        if srvr == num:
            server_url = server
    search_p = ""
    if "GET" in request.method:
        for key, val in request.GET.items():
            search_p += key
            search_p += "="
            search_p += val
            search_p += "&"

    if "_format" in search_p:
        pass
    else:
        search_p += "_format=json&"

    if search_p.endswith("&"):
        search_p = search_p[:-1]

    call_url = server_url + resource + "?" + search_p

    r = requests.get(call_url)

    text_out = json.loads(r.text, object_pairs_hook=OrderedDict)
    highlighted = ""
    if hi_fld in text_out:
        highlighted = text_out[hi_fld]
    context =  {"additional_info": pretty_json(text_out, indent=4),
                "subname": resource,
                "highlight_field": hi_fld,
                "highlight": highlighted,
                "url_parm": call_url}
    template = "output.html"
    return render(request, template, context)


def request_call(request, call_url, fail_redirect="/"):
    """  call to request or redirect on fail"""
    try:
        r = requests.get(call_url)

    except requests.ConnectionError:
        # logger.debug('Problem connecting to FHIR Server')
        messages.error(request, 'FHIR Server is unreachable.')
        return HttpResponseRedirect(fail_redirect)

    if r.status_code in ERROR_CODE_LIST:
        return error_status(r, r.status_code)

    return r

