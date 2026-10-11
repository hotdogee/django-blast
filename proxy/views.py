import requests
from urllib.parse import urlsplit
from django.http import HttpResponse, HttpResponseRedirect

# Only these services may be fetched through the proxy: (scheme-less host[:port], path prefix)
SAFE_URLS = [
    ('golr.berkeleybop.org', '/'),
    ('a2-proxy1.stanford.edu:8080', '/solr/'),
    ('golr.geneontology.org', '/solr'),
]

def is_safe_url(url):
    '''Compare the parsed host and path with the allow list, so that the
    allowed host name cannot just appear somewhere else in the URL.'''
    parts = urlsplit(url)
    if parts.scheme not in ('http', 'https') or parts.username or parts.password:
        return False
    return any(parts.netloc.lower() == host and parts.path.startswith(prefix) for host, prefix in SAFE_URLS)

def proxy_view(request, url, requests_args=None):
    if request.method == 'GET':
        if not 'http://' in url:
            url = url.replace('http:/', 'http://')
        if not 'https://' in url:
            url = url.replace('https:/', 'https://')
        if is_safe_url(url):
            param = request.GET.urlencode()
            response = requests.get(url + '?' + param, timeout=30)
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
            for key, value in response.headers.items():
                if key.lower() in excluded_headers:
                    continue
                proxy_response[key] = value        
            return proxy_response
        return HttpResponseRedirect('https://i5k.nal.usda.gov')
    else:
        return HttpResponse('Not Supported')
