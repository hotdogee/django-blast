// Fill the path text box when a file is chosen for upload, so that
// dependent fields (e.g. the BLAST database title) can be suggested.
(function () {
    'use strict';
    document.addEventListener('change', function (event) {
        var upload = event.target;
        if (!upload.matches || !upload.matches('input[type=file][data-media-path-target]') || !upload.files.length) {
            return;
        }
        var input = document.getElementById(upload.getAttribute('data-media-path-target'));
        if (!input) {
            return;
        }
        var directory = (input.getAttribute('data-media-directory') || '').replace(/^\/+|\/+$/g, '');
        input.value = (directory ? directory + '/' : '') + upload.files[0].name;
        input.dispatchEvent(new Event('change', { bubbles: true }));
    });
})();
