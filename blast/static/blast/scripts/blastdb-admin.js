$(function () { // document ready
    window.id_file_change = function (value) {
        $('#id_fasta_file').val(value).change();
    }
    $('#id_fasta_file').change(function () {
        var file = $('#id_fasta_file').val().split('/').pop();
        //console.log(file);
        if (!$('#id_title').data('userModified'))
            $('#id_title').val(file)
    });
    // don't overwrite user input
    $('#id_title').keyup(function () {
        if ($('#id_title').val().length > 0) {
            $('#id_title').data('userModified', true);
        } else {
            $('#id_title').data('userModified', false);
        }
    });
});