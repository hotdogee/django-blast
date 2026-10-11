from unittest import mock

from django.contrib.auth.models import Permission, User
from django.core import mail
from django.test import TestCase

from app.models import Profile
from .models import Registration, Species
from .views import do_reject

AJAX = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}


def create_species(name='anogla'):
    return Species.objects.create(name=name, full_name='Anoplophora glabripennis', host='localhost', db_name='web_apollo_' + name,
                                  db_acct='apollo', url='https://apollo.example.org/' + name)


class SpeciesTest(TestCase):
    def test_species_permissions(self):
        species = create_species()
        self.assertEqual(sorted(Permission.objects.filter(codename__startswith='anogla_').values_list('codename', flat=True)),
                         ['anogla_admin', 'anogla_owner', 'anogla_publish', 'anogla_read', 'anogla_write'])
        species.delete()
        self.assertFalse(Permission.objects.filter(codename__startswith='anogla_').exists())

    @mock.patch('webapollo.models.psycopg.connect', side_effect=OSError('no server'))
    def test_db_exists_without_a_server(self, connect):
        self.assertFalse(create_species().db_exists())


class RegistrationFlowTest(TestCase):
    def setUp(self):
        self.species = create_species()
        self.owner = User.objects.create_user('owner', 'owner@example.org', 'x', first_name='Olga')
        self.applicant = User.objects.create_user('alice.b', 'alice@example.org', 'x', first_name='Alice', last_name='B')
        Profile.objects.create(user=self.applicant, institution='NAL')
        # webapollo writes permissions with raw SQL to bypass its m2m_changed handler
        from django.db import connection
        with connection.cursor() as c:
            c.execute('INSERT INTO auth_user_user_permissions (user_id, permission_id) VALUES (%s, %s)',
                      [self.owner.id, Permission.objects.get(codename='anogla_owner').id])

    def test_apply_and_reject(self):
        self.client.force_login(self.applicant)
        self.assertEqual(self.client.get('/webapollo/panel').status_code, 200)
        response = self.client.post('/webapollo/apply', {'species_name': 'anogla', 'comment': '<script>x</script>'}, **AJAX)
        self.assertTrue(response.json()['succeeded'])
        registration = Registration.objects.get()
        self.assertEqual((registration.status, registration.submission_comment), ('Pending', '&lt;script&gt;x&lt;/script&gt;'))
        self.assertEqual(len(mail.outbox), 2)  # applicant and owner

        # rejecting with a comment used to fail with a NameError
        self.assertTrue(do_reject('anogla', 'alice.b', 'Not yet', 'owner'))
        registration.refresh_from_db()
        self.assertEqual((registration.status, registration.decision_comment), ('Rejected', 'from owner: Not yet'))
        self.assertIn('/webapollo/panel', mail.outbox[-1].body)

    def test_requests_must_be_ajax(self):
        self.client.force_login(self.applicant)
        response = self.client.post('/webapollo/apply', {'species_name': 'anogla', 'comment': ''})
        self.assertFalse(response.json()['succeeded'])
        self.assertFalse(Registration.objects.exists())

    def test_ajax_requires_login(self):
        response = self.client.post('/webapollo/apply', {'species_name': 'anogla', 'comment': ''}, **AJAX)
        self.assertEqual(response.json(), {'invalid_request': True})

    def test_dashboard_lists_pending_requests_for_owner(self):
        Registration.objects.create(user=self.applicant, species=self.species, status='Pending')
        self.client.force_login(self.owner)
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pendings']), 1)

    def test_admin_pages(self):
        admin = User.objects.create_superuser('admin', 'admin@example.org', 'x')
        self.client.force_login(admin)
        for url in ('/webapollo/admin/manage', '/webapollo/admin/species/anogla', '/webapollo/admin/user/%d' % self.applicant.id,
                    '/admin/webapollo/registration/', '/admin/webapollo/speciespassword/'):
            self.assertEqual(self.client.get(url).status_code, 200, url)
