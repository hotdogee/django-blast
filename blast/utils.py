import json
import os
import shutil
import sys

from django.conf import settings

BLAST_PROGRAMS = ('blastn', 'tblastn', 'tblastx', 'blastp', 'blastx')


def blast_bin(name):
    """Return the path of a BLAST+ executable such as ``blastn`` or ``makeblastdb``.

    ``settings.BLAST_BIN_DIR`` wins when set. Otherwise the executable is
    looked up on PATH, falling back to the copies bundled in ``blast/bin_linux``
    or ``blast/bin_win`` (BLAST+ 2.2.29).
    """
    exe = name + '.exe' if sys.platform == 'win32' else name
    if settings.BLAST_BIN_DIR:
        return os.path.join(settings.BLAST_BIN_DIR, exe)
    found = shutil.which(name)
    if found:
        return found
    bin_name = 'bin_win' if sys.platform == 'win32' else 'bin_linux'
    return os.path.join(settings.PROJECT_ROOT, 'blast', bin_name, exe)


def program_name(path):
    """'/usr/bin/blastn' or 'C:\\blast\\blastn.exe' -> 'blastn'"""
    return os.path.splitext(os.path.basename(path))[0]


_SCRIPT_ESCAPES = {ord('<'): '\\u003C', ord('>'): '\\u003E', ord('&'): '\\u0026'}


def escape_json_for_script(json_text):
    """Make a JSON document safe to embed in an inline <script> element.

    BLAST results contain user supplied FASTA deflines, so a defline such as
    ``</script><script>...`` must not be able to close the script tag.
    """
    return json_text.translate(_SCRIPT_ESCAPES)


def json_for_script(obj):
    return escape_json_for_script(json.dumps(obj))
