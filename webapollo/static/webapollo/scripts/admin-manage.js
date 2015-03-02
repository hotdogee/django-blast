$(function() { // document ready

    $.fn.dataTable.moment('MMM D YYYY');
    $('#table-pendings').DataTable( {
        'dom': 'Tlftip',
        "order": [[ 2, "asc" ]],
        'tableTools': {
            "sRowSelect": "os",
            "aButtons": [],
        },
    });
    $('#table-pendings tbody').on('click', 'tr', function () {
        $('#remind-count').text(TableTools.fnGetInstance('table-pendings').fnGetSelected().length);
    });

    $('#btn-admin-remind').click(function(event) {
        event.preventDefault();
        $("#alert-remind-success").fadeIn();
        $("#alert-remind-fail").fadeIn();
    });

});

