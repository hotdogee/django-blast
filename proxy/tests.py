from django.test import TestCase
from django.core.urlresolvers import reverse

class Proxy_viewTest(TestCase):
    def test_url_and_args(self):
        response = self.client.get('/proxy/http://golr.berkeleybop.org/select?defType=edismax&qt=standard&indent=on&wt=json&rows=10&start=0&fl=*,score&facet=true&facet.mincount=1&facet.sort=count&json.nl=arrarr&facet.limit=25&fq=document_category:%22ontology_class%22&fq=source:(biological_process%20OR%20molecular_function%20OR%20cellular_component)&facet.field=annotation_class&facet.field=synonym&facet.field=alternate_id&q=go:&qf=annotation_class%5E5&qf=annotation_class_label_searchable%5E5&qf=synonym_searchable%5E1&qf=alternate_id%5E1&json.wrf=jQuery171018561481428332627_1420660818198&_=1420660827771')
        #response = self.client.get('/proxy/http://tw.yahoo.com')
        print response.content
        self.assertEquals(response.status_code, 200)
