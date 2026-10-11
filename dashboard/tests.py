from django.contrib.auth.models import User
from django.test import TestCase


class DashboardTest(TestCase):
    def test_requires_login(self):
        response = self.client.get('/home')
        self.assertRedirects(response, '/login/?next=/home', fetch_redirect_response=False)

    def test_dashboard(self):
        self.client.force_login(User.objects.create_user('alice', password='x'))
        response = self.client.get('/home')
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Launch application')
