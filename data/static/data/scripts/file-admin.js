$(function () { // document ready
    window.id_file_change = function (value) {
        $('#id_name').val(value).change();
    }
    $('#id_name').change(function () {
        var file = $('#id_name').val().split('/').pop();
    });
});