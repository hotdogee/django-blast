"""A small replacement for django-filebrowser's FileBrowseField.

``MediaPathField`` stores a file path relative to ``MEDIA_ROOT`` in a plain
varchar column (the same column type FileBrowseField used, so no data
migration is needed). In forms it renders as a text box with a list of the
matching files that already exist below ``directory``, plus an upload input.
Upload problems (permissions, disk space, name clashes, ...) are reported as
form errors instead of failing silently.
"""
import os
from urllib.parse import urlsplit

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query_utils import DeferredAttribute
from django.utils.encoding import iri_to_uri
from django.utils.text import get_valid_filename

MAX_LISTED_FILES = 2000


def media_url_prefixes():
    '''MEDIA_URL and, for an absolute MEDIA_URL, its path (longest first).'''
    media_url = settings.MEDIA_URL or ''
    prefixes = [media_url, urlsplit(media_url).path]
    return [p for p in prefixes if p and p != '/']


class MediaFile(str):
    """A path relative to MEDIA_ROOT, as stored by MediaPathField.

    Provides the handful of attributes that the code base used from
    filebrowser's FileObject.
    """

    @property
    def path(self):
        return str(self)

    @property
    def path_relative(self):
        value = self.replace('\\', '/')
        # FileBrowseField stored URLs (MEDIA_URL + path), e.g. /media/blast/db/x.fa
        for prefix in media_url_prefixes():
            if value.startswith(prefix):
                value = value[len(prefix):]
                break
        return value.lstrip('/')

    @property
    def path_full(self):
        return os.path.join(settings.MEDIA_ROOT, *self.path_relative.split('/'))

    @property
    def filename(self):
        return os.path.basename(self.path_relative)

    @property
    def url(self):
        return iri_to_uri(settings.MEDIA_URL + self.path_relative)

    @property
    def exists(self):
        return bool(self) and os.path.isfile(self.path_full)


class MediaPathDescriptor(DeferredAttribute):
    """Wrap every assigned value in MediaFile."""

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, MediaFile):
            value = MediaFile(value)
        instance.__dict__[self.field.attname] = value


def list_media_files(directory='', extensions=None):
    """Paths (relative to MEDIA_ROOT) of the files below ``directory``."""
    root = os.path.join(settings.MEDIA_ROOT, directory)
    extensions = tuple(e.lower() for e in extensions or ())
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for filename in sorted(filenames):
            if extensions and not filename.lower().endswith(extensions):
                continue
            rel = os.path.relpath(os.path.join(dirpath, filename), settings.MEDIA_ROOT)
            found.append(rel.replace(os.sep, '/'))
            if len(found) >= MAX_LISTED_FILES:
                return found
    return found


def resolve_extensions(extensions):
    """Accept a list of extensions or a key of settings.MEDIA_FILE_EXTENSIONS."""
    if isinstance(extensions, str):
        return list(settings.MEDIA_FILE_EXTENSIONS.get(extensions, [extensions]))
    return list(extensions or [])


class MediaPathWidget(forms.Widget):
    template_name = 'app/widgets/media_path.html'
    needs_multipart_form = True

    class Media:
        js = ('app/scripts/media-path-widget.js',)

    def __init__(self, directory='', extensions=None, attrs=None):
        self.directory = directory
        self.extensions = extensions or []
        super().__init__(attrs)

    def upload_name(self, name):
        return name + '_upload'

    def format_value(self, value):
        if isinstance(value, (list, tuple)):
            value = value[0]
        return value or ''

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        widget = context['widget']
        widget['upload_name'] = self.upload_name(name)
        widget['directory'] = self.directory
        widget['accept'] = ','.join(self.extensions)
        widget['choices'] = list_media_files(self.directory, self.extensions)
        current = MediaFile(widget['value'])
        widget['missing'] = bool(current) and not current.exists
        return context

    def value_from_datadict(self, data, files, name):
        return (data.get(name, ''), files.get(self.upload_name(name)))

    def value_omitted_from_data(self, data, files, name):
        return name not in data and self.upload_name(name) not in files


class MediaPathFormField(forms.CharField):
    """Text path below MEDIA_ROOT, or an uploaded file saved into ``directory``."""

    def __init__(self, directory='', extensions=None, **kwargs):
        self.directory = directory
        self.extensions = extensions or []
        kwargs.setdefault('widget', MediaPathWidget(directory=directory, extensions=self.extensions))
        super().__init__(**kwargs)

    def clean(self, value):
        path, upload = value if isinstance(value, (list, tuple)) else (value, None)
        if upload is not None:
            path = self.save_upload(upload)
        return super().clean(path)

    def has_changed(self, initial, data):
        path, upload = data if isinstance(data, (list, tuple)) else (data, None)
        return upload is not None or super().has_changed(initial, path)

    def to_python(self, value):
        value = super().to_python(value)
        return MediaFile(value.strip().replace('\\', '/')) if value else value

    def validate(self, value):
        super().validate(value)
        if not value:
            return
        normalized = os.path.normpath(value.path_relative)
        if normalized.startswith('..') or os.path.isabs(normalized):
            raise ValidationError('The path must be inside the media directory (%s).' % settings.MEDIA_ROOT)
        if self.extensions and not value.lower().endswith(tuple(e.lower() for e in self.extensions)):
            raise ValidationError('Unsupported file type. Allowed extensions: %s' % ', '.join(self.extensions))

    def save_upload(self, upload):
        """Save an uploaded file to MEDIA_ROOT/directory, reporting any problem as a form error."""
        filename = get_valid_filename(os.path.basename(upload.name))
        if self.extensions and not filename.lower().endswith(tuple(e.lower() for e in self.extensions)):
            raise ValidationError('"%s" was not uploaded: allowed extensions are %s.' % (filename, ', '.join(self.extensions)))
        max_size = getattr(settings, 'MEDIA_UPLOAD_MAX_SIZE', None)
        if max_size and upload.size > max_size:
            raise ValidationError('"%s" was not uploaded: it is larger than the %d byte limit (MEDIA_UPLOAD_MAX_SIZE).' % (filename, max_size))
        rel_path = '/'.join(p for p in (self.directory.strip('/'), filename) if p)
        target = MediaFile(rel_path).path_full
        target_dir = os.path.dirname(target)
        if os.path.exists(target):
            if os.path.isfile(target) and os.path.getsize(target) == upload.size:
                return rel_path  # same file uploaded again, e.g. after another field failed validation
            raise ValidationError('"%s" was not uploaded: a different file with that name already exists in %s. '
                                  'Rename the file, or select the existing file instead.' % (filename, target_dir))
        try:
            os.makedirs(target_dir, mode=0o755, exist_ok=True)
            with open(target, 'xb') as destination:
                for chunk in upload.chunks():
                    destination.write(chunk)
            os.chmod(target, getattr(settings, 'FILE_UPLOAD_PERMISSIONS', None) or 0o644)
        except OSError as e:
            if os.path.isfile(target) and os.path.getsize(target) != upload.size:
                try:
                    os.remove(target)
                except OSError:
                    pass
            raise ValidationError('"%s" could not be saved to %s: %s. Check that the web server user can write to this '
                                  'directory and that the disk is not full.' % (filename, target_dir, e.strerror or e))
        return rel_path


class MediaPathField(models.CharField):
    """Model field storing a path relative to MEDIA_ROOT (replaces filebrowser's FileBrowseField)."""

    descriptor_class = MediaPathDescriptor

    def __init__(self, *args, directory='', extensions=None, format=None, **kwargs):
        self.directory = directory
        self.extensions = resolve_extensions(extensions or format)
        kwargs.setdefault('max_length', 100)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None or isinstance(value, MediaFile):
            return value
        return MediaFile(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': MediaPathFormField,
            'directory': self.directory,
            'extensions': self.extensions,
        }
        defaults.update(kwargs)
        # The admin passes its own widget for CharFields; keep ours.
        if not isinstance(defaults.get('widget'), MediaPathWidget):
            defaults.pop('widget', None)
        return super().formfield(**defaults)
