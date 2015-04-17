$(function() { // document ready
    var user_id = $('table[id^="queries-"]')[0].id.split('-')[1];
    var path = window.location.pathname.substring(0, window.location.pathname.lastIndexOf( "/" ) + 1);
    if ( $.fn.dataTable.isDataTable('#queries-' + user_id) ) {
        var table = $('#queries-' + user_id).DataTable();
        table.ajax.reload();
    }
    else {
        $('#queries-' + user_id).dataTable( {
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
                    return '<a href="' + path + 'blast/' + data  + '" target="_blank">' + data + '</a>';
                }},
                {
                "aTargets": [0], // Column to target
                "mRender": function ( data, type, full ) {
                    return new Date(data).toUTCString();
                }}
            ],
            "order": [[ 0, "desc" ]],
        });
    }
});
