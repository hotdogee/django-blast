$(function() { // document ready
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
    var path = window.location.pathname.substring(0, window.location.pathname.lastIndexOf( "/" ) + 1);

    // BLAST queries
    var user_id = $('table[id^="queries-"]')[0].id.split('-')[1];
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

    // pendings table
    $('#pendings').DataTable( {
        dom: 'Tft',
        "columnDefs": [
            {
                "targets": [ 5 ],   // username
                "visible": false,
                "searchable": false
            },
            {
                "targets": [ 6 ],   // species short name
                "visible": false,
                "searchable": false
            }
        ],
        tableTools: {
            "sRowSelect": "multi",
            "aButtons": [],
        }           
    });
    $('#pendings-count').text('0');
    $('#pendings tbody').on('click', 'tr', function () {
        $('#pendings-count').text(TableTools.fnGetInstance('pendings').fnGetSelected().length);
    });
    $("#link-approve").click(function(event) {
        event.preventDefault();
        $('#pendings-action').fadeOut();
        $('#pendings-msg').html('<span style="color:blue;" >Processing...it may take a couple minutes.</span>');
        var user_species = [];
        //var done = true;
        $.each(TableTools.fnGetInstance('pendings').fnGetSelectedData(), function(idx, val) {
            //var uname = val[5];
            //var sname = val[6];
            user_species.push({'username': val[5], 'species_name': val[6]});
            /*$.post(path + "webapollo/aprove", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name': val[6] , 'username': val[5], }, function(data) {
                if (!data.succeeded) {
                    done = false;
                }
            }, "json");
            if (!done) return false;  // break loop*/
        });
        /*if (done) {
            $('#pendings-msg').html('<span style="color:green;" >Done!</span>');
            $('#pendings-action').fadeIn();            
        }
        else {
            $('#pendings-msg').html('<span style="color:red;" >Some users were probably approved by other coordinators. Please try again later.</span>');
        }
        $('#pendings').DataTable().row('.selected').remove().draw( false );
        TableTools.fnGetInstance('pendings').fnSelectNone();
        $('#pendings-count').text('0');*/
        
        $.post(path + "webapollo/bulk-approve", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'user_species': user_species, 'num': user_species.length}, function(data) {
            if (data.succeeded) {
                $('#pendings-msg').html('<span style="color:green;" >Done!</span>');
                $('#pendings-action').fadeIn();
            }
            else {
                $('#pendings-msg').html('<span style="color:red;" >Some users were probably approved by other coordinators. Please try again later.</span>');
            }
            $('#pendings').DataTable().row('.selected').remove().draw( false );
            TableTools.fnGetInstance('pendings').fnSelectNone();
            $('#pendings-count').text('0');
        }, "json");

    });

});
