from unittest import mock

from django.test import SimpleTestCase

from .views import is_safe_url


class SafeUrlTest(SimpleTestCase):
    def test_allowed_urls(self):
        self.assertTrue(is_safe_url('http://golr.berkeleybop.org/select'))
        self.assertTrue(is_safe_url('https://golr.geneontology.org/solr/select'))
        self.assertTrue(is_safe_url('http://a2-proxy1.stanford.edu:8080/solr/select'))

    def test_lookalike_urls_are_rejected(self):
        for url in [
            'http://evil.example.com/?//golr.berkeleybop.org',
            'http://evil.example.com//golr.berkeleybop.org/select',
            'http://golr.berkeleybop.org.evil.example.com/select',
            'http://user:pass@golr.berkeleybop.org/select',
            'http://a2-proxy1.stanford.edu:8080/admin/',
            'file:///etc/passwd',
        ]:
            self.assertFalse(is_safe_url(url), url)


class ProxyViewTest(SimpleTestCase):
    @mock.patch('proxy.views.requests.get')
    def test_proxies_allowed_url(self, get):
        get.return_value = mock.Mock(content=b'{"ok": 1}', status_code=200,
                                     headers={'Content-Type': 'application/json', 'Connection': 'keep-alive'})
        response = self.client.get('/proxy/http://golr.berkeleybop.org/select', {'q': 'go:', 'wt': 'json'})
        get.assert_called_once_with('http://golr.berkeleybop.org/select?q=go%3A&wt=json', timeout=30)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"ok": 1}')
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertFalse(response.has_header('Connection'))

    @mock.patch('proxy.views.requests.get')
    def test_other_urls_are_redirected(self, get):
        response = self.client.get('/proxy/http://evil.example.com/?x=//golr.berkeleybop.org')
        self.assertEqual(response.status_code, 302)
        get.assert_not_called()
