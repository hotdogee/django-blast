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
        dom: 'Tlftip',
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
        $('#msg-approve').html('<span style="color:blue;">Processing...it may take a couple minutes. Patience is a virtue.</span>');
        $('#btn-approve-close').prop('disabled', true);;
        $('#approveModal').modal('show');
        var user_species = [];
        $.each(TableTools.fnGetInstance('pendings').fnGetSelectedData(), function(idx, val) {
            user_species.push({'username': val[5], 'species_name': val[6]});
        });
        $.post(path + "webapollo/bulk-approve", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'user_species': user_species, 'num': user_species.length}, function(data) {
            if (data.succeeded) {
                $.each(TableTools.fnGetInstance('pendings').fnGetSelectedData(), function(idx, val) {
                    var t = $("#annotators-" + val[6]).DataTable();
                    var rowNode = t.row.add([
                        val[1],
                        val[5],
                        val[2],
                        "<a href='#' class='link-remove'>Remove</a>"
                    ] ).draw().node(); 
                    $(rowNode).attr("id", "tr-" + val[5] + "-"  + val[6]);
                });
                $('#msg-approve').html('<span style="color:green;">Done! Please click Close to exit.</span>');
            }
            else {
                $('#msg-approve').html('<span style="color:red;">The user was probably approved by other coordinators. Please try again later. Click Close to exit.</span>');
            }
            $('#btn-approve-close').prop('disabled', false);
            $('#pendings').DataTable().row('.selected').remove().draw( false );
            TableTools.fnGetInstance('pendings').fnSelectNone();
            $('#pendings-count').text('0');
        }, "json");
    });

    $("#link-reject").click(function(event) {
        event.preventDefault();
        $('#pendings-action').fadeOut();
        $('#pendings-msg').html('<span style="color:blue;" >Processing...it may take a couple minutes.</span>');
        var user_species = [];
        $.each(TableTools.fnGetInstance('pendings').fnGetSelectedData(), function(idx, val) {
            user_species.push({'username': val[5], 'species_name': val[6]});
        });
        $.post(path + "webapollo/bulk-reject", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'user_species': user_species, 'num': user_species.length}, function(data) {
            if (data.succeeded) {
                $('#pendings-msg').html('<span style="color:green;" >Done!</span>');
                $('#pendings-action').fadeIn();
            }
            else {
                $('#pendings-msg').html('<span style="color:red;" >Some users were probably rejected by other coordinators. Please try again later.</span>');
            }
            $('#pendings').DataTable().row('.selected').remove().draw( false );
            TableTools.fnGetInstance('pendings').fnSelectNone();
            $('#pendings-count').text('0');
        }, "json");
    });

    // addUserModal
    $('#addUserModal').on('show.bs.modal', function(event) {
        $('#adduser-count').text('0');
        species_name = $(event.relatedTarget).data('whatever'); // ex. "agrpla"
        var t = $('#adduser-table').DataTable();
        t.clear();
        $.post(path + "webapollo/eligible", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name': species_name }, function(data) { 
            if (data.succeeded) {                
                $.each(data['users'], function(idx, val) {
                    var rowNode = t.row.add([
                        val['full_name'],
                        val['username'],
                        val['institution']
                    ]).draw().node();
                    //$(rowNode).attr("id", "tr-" + val['username'] + "-"  + species_name);
                });
                $('#hidden-addUserModal').val(species_name);
            }
            else {
                $('#addUserModal').children('.modal-dialog').children('.modal-content').children('.modal-body').text('Can not get eligible users. Please try again later.'); 
            }
        }, "json");
    });

    $('#adduser-table tbody').on('click', 'tr', function () {
        $('#adduser-count').text(TableTools.fnGetInstance('adduser-table').fnGetSelected().length);
    });

    $('#btn-addUserModal').click(function() {
        var species_name = $('#btn-addUserModal').next("input").val();
        var usernames = [];
        $.each(TableTools.fnGetInstance('adduser-table').fnGetSelectedData(), function(idx, val) {
            usernames.push(val[1]);
        });
        $('#btn-addUserModal').button('loading');
        $('#addUserMsg').text('Processing...it may take a couple minutes. Patience is a virtue.')
        $('#adduser-table_wrapper').fadeOut();
        $.post(path + "webapollo/adduser", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name': species_name, 'usernames': usernames,}, function(data) { 
            if (data.succeeded) {
                var t = $("#annotators-" + species_name).DataTable();
                $.each(TableTools.fnGetInstance('adduser-table').fnGetSelectedData(), function(idx, val) {
                    var rowNode = t.row.add([
                        val[0],
                        val[1],
                        val[2],
                        "<a href='#' class='link-remove'>Remove</a>"
                    ] ).draw().node(); 
                    $(rowNode).attr("id", "tr-" + val[1] + "-"  + species_name);
                });
                // remove and clear selected rows, reset counter, recover adding button
                $('#adduser-table tr.selected').fadeOut(500);
                $('#adduser-table').DataTable().row('.selected').remove().draw( false );
                TableTools.fnGetInstance('adduser-table').fnSelectNone();
                $('#adduser-count').text('0');
                $('#addUserMsg').text('Click to select users to be annotators')
                $('#adduser-table_wrapper').fadeIn();
                $('#btn-addUserModal').button('reset');
            }
            else {
               $('#addUserModal').children('.modal-dialog').children('.modal-content').children('.modal-body').text('Error occured when adding users. Please try again later.');
            }
        }, "json");
    });

    $(".well").on('click','.link-remove', function(event){
        event.preventDefault();
        var tr = $(this).parent('td').parent('tr');
        var v = tr.attr('id').split('-'); // ex. {"tr", "castman", "agrpla"}
        var species_name = v[v.length-1];
        var username = tr.attr('id').replace('-' + species_name, '');
        username = username.replace('tr-', '');
        $.post(path + "webapollo/remove", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name':species_name , 'username': username, }, function(data) { 
            if (data.succeeded) {
                var t = $("#annotators-" + species_name).DataTable();
                tr.fadeOut(500);
                t.row('#tr' + '-' + username + '-' + species_name).remove().draw( false );
            }
            else {
                alert('The user was probably removed by other coordinators. Please try again later.');
            }
        }, "json");
    });
    
});
