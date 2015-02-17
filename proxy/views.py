import requests
from django.http import HttpResponse, HttpResponseRedirect

def proxy_view(request, url, requests_args=None):
    if request.method == 'GET':
        if not 'http://' in url:
            url = url.replace('http:/', 'http://')
        if not 'https://' in url:
            url = url.replace('https:/', 'http:s//')
        for safe_url in ['//golr.berkeleybop.org', '//a2-proxy1.stanford.edu:8080/solr/']:
            if safe_url in url:
                param = request.GET.urlencode()
                response = requests.get(url + '?' + param)
                proxy_response = HttpResponse(
                    response.content,
                    status=response.status_code)
                excluded_headers = set([
                    # Hop-by-hop headers
                    # ------------------
                    # Certain response headers should NOT be just tunneled through.  These
                    # are they.  For more info, see:
                    # http://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.5.1
                    'connection', 'keep-alive', 'proxy-authenticate', 
                    'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 
                    'upgrade', 
            
                    # Although content-encoding is not listed among the hop-by-hop headers,
                    # it can cause trouble as well.  Just let the server set the value as
                    # it should be.
                    'content-encoding',
            
                    # Since the remote server may or may not have sent the content in the
                    # same encoding as Django will, let Django worry about what the length
                    # should be.
                    'content-length',
                ])
                for key, value in response.headers.iteritems():
                    if key.lower() in excluded_headers:
                        continue
                    proxy_response[key] = value        
                return proxy_response
        return HttpResponseRedirect('https://i5k.nal.usda.gov')
    else:
        return HttpResponse('Not Supported')
