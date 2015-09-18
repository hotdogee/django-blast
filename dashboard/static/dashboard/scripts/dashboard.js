$(function() { // document ready
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
    var path = window.location.pathname.substring(0, window.location.pathname.lastIndexOf( "/" ) + 1);
    
    // data table initialization 
    $(".table-owner-annotators").DataTable({
        "paging":   false,
        "info":     false,
        "ordering": true,
        "searching": true,
        "aoColumnDefs": [
            { 'bSortable': false, 'aTargets': [ -1 ] }
        ],
    });
    
    $(".table-annotators").DataTable({
        "paging":   false,
        "info":     false,
        "ordering": true,
        "searching": true,
    });

    $('.table-adduser').DataTable( {
        dom: 'Tft',
        tableTools: {
            "sRowSelect": "multi",
            "aButtons": [],
        }
    });

    // BLAST queries
    var user_id = $('table[id^="queries-blast-"]')[0].id.split('-')[2];
    $('#queries-blast-' + user_id).dataTable( {
        "ajax": {
            "url": path + "blast/user-tasks/" + user_id,
            "dataSrc": ""
        },
        "columns": [
            { "data": "enqueue_date" },
            { "data": "result_status" },
            { "data": "task_id" },
        ],
        "aoColumnDefs": [
            {
                "aTargets": [2], // Column to target
                "mRender": function ( data, type, full ) {
                // 'full' is the row's data object, and 'data' is this column's data
                // e.g. 'full[0]' is the comic id, and 'data' is the comic title
                    return '<a href="' + path + 'blast/' + data  + '" target="_blank">' + data+ '</a>';
            }},
            {
                "aTargets": [0], // Column to target
                "mRender": function ( data, type, full ) {
                    return new Date(data).toUTCString();
            }}
        ],
        "order": [[ 0, "desc" ]],
    });

    $('#queries-hmmer-' + user_id).dataTable( {
        "ajax": {
            "url": path + "hmmer/user-tasks/" + user_id,
            "dataSrc": ""
        },
        "columns": [
            { "data": "enqueue_date" },
            { "data": "result_status" },
            { "data": "task_id" },
        ],
        "aoColumnDefs": [
            {
                "aTargets": [2], // Column to target
                "mRender": function ( data, type, full ) {
                // 'full' is the row's data object, and 'data' is this column's data
                // e.g. 'full[0]' is the comic id, and 'data' is the comic title
                    return '<a href="' + path + 'hmmer/' + data  + '" target="_blank">' + data+ '</a>';
            }},
            {
                "aTargets": [0], // Column to target
                "mRender": function ( data, type, full ) {
                    return new Date(data).toUTCString();
            }}
        ],
        "order": [[ 0, "desc" ]],
    });

     $('#queries-clustal-' + user_id).dataTable( {
        "ajax": {
            "url": path + "clustal/user-tasks/" + user_id,
            "dataSrc": ""
        },
        "columns": [
            { "data": "enqueue_date" },
            { "data": "result_status" },
            { "data": "task_id" },
        ],
        "aoColumnDefs": [
            {
                "aTargets": [2], // Column to target
                "mRender": function ( data, type, full ) {
                // 'full' is the row's data object, and 'data' is this column's data
                // e.g. 'full[0]' is the comic id, and 'data' is the comic title
                    return '<a href="' + path + 'clustal/' + data  + '" target="_blank">' + data+ '</a>';
            }},
            {
                "aTargets": [0], // Column to target
                "mRender": function ( data, type, full ) {
                    return new Date(data).toUTCString();
            }}
        ],
        "order": [[ 0, "desc" ]],
    });
});
