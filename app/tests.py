import os
import shutil
import sys
import tempfile
import unittest

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings

from .fields import MediaFile, MediaPathFormField, MediaPathWidget
from .models import Profile
from .templatetags.jsonify import jsonify


class AuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', 'alice@example.org', 'correct-horse')

    def test_login_page(self):
        response = self.client.get('/login/')
        self.assertContains(response, 'Log in')

    def test_login_and_logout(self):
        response = self.client.post('/login/', {'username': 'alice', 'password': 'correct-horse'})
        self.assertRedirects(response, '/home', fetch_redirect_response=False)
        self.assertEqual(self.client.get('/home').status_code, 200)
        response = self.client.get('/logout')
        self.assertRedirects(response, '/login/', fetch_redirect_response=False)
        self.assertEqual(self.client.get('/home').status_code, 302)

    def test_axes_locks_out_after_three_failures(self):
        for _ in range(3):
            response = self.client.post('/login/', {'username': 'alice', 'password': 'wrong'})
        self.assertTemplateUsed(response, 'app/login_lockout.html')
        response = self.client.post('/login/', {'username': 'alice', 'password': 'correct-horse'})
        self.assertTemplateUsed(response, 'app/login_lockout.html')

    def test_register(self):
        response = self.client.post('/register', {
            'username': 'bob', 'password1': 'a-long-password-1', 'password2': 'a-long-password-1',
            'first_name': 'Bob', 'last_name': 'Builder', 'email': 'bob@example.org', 'institution': 'NAL',
            'captcha_0': 'x', 'captcha_1': 'PASSED',
        })
        self.assertRedirects(response, '/blast/', fetch_redirect_response=False)
        bob = User.objects.get(username='bob')
        self.assertEqual(Profile.objects.get(user=bob).institution, 'NAL')
        self.assertEqual(int(self.client.session['_auth_user_id']), bob.id)

    def test_password_change_and_reset_pages(self):
        self.client.force_login(self.user)
        self.assertContains(self.client.get('/password_change'), 'password')
        response = self.client.post('/password_change', {'old_password': 'correct-horse', 'new_password1': 'another-password-2', 'new_password2': 'another-password-2'})
        self.assertRedirects(response, '/password_change_done', fetch_redirect_response=False)
        self.client.logout()
        response = self.client.post('/password_reset', {'email': 'alice@example.org'})
        self.assertRedirects(response, '/password_reset_done', fetch_redirect_response=False)
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/reset/', mail.outbox[0].body)

    def test_info_change(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get('/info_change'), '/set_institution', fetch_redirect_response=False)
        self.client.post('/set_institution', {'institution': 'NAL'})
        self.assertEqual(self.user.profile.institution, 'NAL')
        response = self.client.post('/info_change', {'first_name': 'Alice', 'last_name': 'A', 'email': 'a@example.org', 'institution': 'USDA'})
        self.assertContains(response, 'Your account info was updated.')
        self.user.refresh_from_db()
        self.assertEqual((self.user.first_name, self.user.profile.institution), ('Alice', 'USDA'))


class JsonifyTest(SimpleTestCase):
    def test_escapes_script_tags(self):
        self.assertEqual(jsonify({'a': '</script><b>&'}), '{"a": "\\u003C/script\\u003E\\u003Cb\\u003E\\u0026"}')


class MediaPathFieldTest(SimpleTestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp(prefix='django-blast-media-')
        self.addCleanup(shutil.rmtree, self.media_root, True)
        override = override_settings(MEDIA_ROOT=self.media_root, MEDIA_URL='/media/')
        override.enable()
        self.addCleanup(override.disable)
        os.makedirs(os.path.join(self.media_root, 'blast', 'db', 'sub'))
        for name in ('a.fa', 'b.txt', os.path.join('sub', 'c.FASTA')):
            with open(os.path.join(self.media_root, 'blast', 'db', name), 'w') as f:
                f.write('>x\nACGT\n')
        self.field = MediaPathFormField(directory='blast/db/', extensions=['.fa', '.fasta'], max_length=100)

    def test_media_file(self):
        f = MediaFile('/blast/db/a b.fa')
        self.assertEqual(f.path_relative, 'blast/db/a b.fa')
        self.assertEqual(f.url, '/media/blast/db/a%20b.fa')
        self.assertEqual(f.filename, 'a b.fa')
        self.assertFalse(f.exists)
        self.assertTrue(MediaFile('blast/db/a.fa').exists)

    def test_paths_stored_by_filebrowser(self):
        # FileBrowseField stored MEDIA_URL + path; databases upgraded from the
        # old version must keep pointing at their FASTA files
        self.assertEqual(MediaFile('/media/blast/db/a.fa').path_relative, 'blast/db/a.fa')
        self.assertTrue(MediaFile('/media/blast/db/a.fa').exists)
        self.assertEqual(MediaFile('/blast/db/a.fa').path_relative, 'blast/db/a.fa')  # the shipped fixtures
        with self.settings(MEDIA_URL='https://files.example.org/webapp/media/'):
            for value in ('https://files.example.org/webapp/media/blast/db/a.fa', '/webapp/media/blast/db/a.fa', 'blast/db/a.fa'):
                self.assertEqual(MediaFile(value).path_relative, 'blast/db/a.fa', value)

    def test_widget_lists_matching_files(self):
        context = MediaPathWidget('blast/db/', ['.fa', '.fasta']).get_context('fasta_file', 'blast/db/missing.fa', {'id': 'id_fasta_file'})
        self.assertEqual(context['widget']['choices'], ['blast/db/a.fa', 'blast/db/sub/c.FASTA'])
        self.assertTrue(context['widget']['missing'])

    def test_clean_path(self):
        self.assertEqual(self.field.clean(('blast\\db\\a.fa', None)), 'blast/db/a.fa')
        with self.assertRaisesMessage(ValidationError, 'inside the media directory'):
            self.field.clean(('../outside.fa', None))
        with self.assertRaisesMessage(ValidationError, 'Allowed extensions'):
            self.field.clean(('blast/db/b.txt', None))

    def test_upload(self):
        upload = SimpleUploadedFile('new genome.fa', b'>s\nACGT\n')
        self.assertEqual(self.field.clean(('', upload)), 'blast/db/new_genome.fa')
        with open(os.path.join(self.media_root, 'blast', 'db', 'new_genome.fa'), 'rb') as f:
            self.assertEqual(f.read(), b'>s\nACGT\n')
        # the same file again (e.g. after another field failed validation) is fine
        self.assertEqual(self.field.clean(('', SimpleUploadedFile('new genome.fa', b'>s\nACGT\n'))), 'blast/db/new_genome.fa')

    def test_upload_errors_are_reported(self):
        with self.assertRaisesMessage(ValidationError, 'already exists'):
            self.field.clean(('', SimpleUploadedFile('a.fa', b'>other\nAAAAAAAA\n')))
        with self.assertRaisesMessage(ValidationError, 'allowed extensions'):
            self.field.clean(('', SimpleUploadedFile('notes.txt', b'hi')))
        with self.settings(MEDIA_UPLOAD_MAX_SIZE=3):
            with self.assertRaisesMessage(ValidationError, 'larger than'):
                self.field.clean(('', SimpleUploadedFile('big.fa', b'>s\nACGT\n')))

    @unittest.skipIf(sys.platform == 'win32' or (hasattr(os, 'geteuid') and os.geteuid() == 0), 'needs POSIX permissions and a non-root user')
    def test_permission_error_is_reported(self):
        target = os.path.join(self.media_root, 'blast', 'db')
        os.chmod(target, 0o555)
        self.addCleanup(os.chmod, target, 0o755)
        with self.assertRaisesMessage(ValidationError, 'Permission denied'):
            self.field.clean(('', SimpleUploadedFile('denied.fa', b'>s\nACGT\n')))


class MigrationsTest(TestCase):
    def test_models_and_migrations_are_in_sync(self):
        call_command('makemigrations', check=True, dry_run=True, verbosity=0)
