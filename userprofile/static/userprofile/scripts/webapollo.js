$(function() { // document ready

    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();

    $(".table-apply-records").DataTable({
        "paging":   false,
        "ordering": false,
        "info":     false,
        "searching": false,
    });
    
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
            "sRowSelect": "os",
            "aButtons": [],
        }
    });

    $("#more-organism-show").click(function(event) {
        event.preventDefault();
        $("#more-organism").hide();
        $("#other-organism").fadeIn();
    });

    $("#more-organism-hide").click(function(event) {
        event.preventDefault();
        $("#other-organism").hide();
        $("#more-organism").fadeIn();
    });

    $(".well").on('click','.btn-new', function(){
        $(this).addClass('disabled');   // prevent double submissions
        var species_name = this.id.replace("btn_","");
        var comment = $(this).parent('p').prev('p').find('textarea').val();
        //var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"').val();
        var apply_btn = $("#collapse-" + species_name).prev('table.species-table').find('tr td:nth-child(2) .btn');
        var div_well = $("#collapse-" + species_name).children('div.well');
        var apply_records = $(this).parent('p').parent('div').next('div').children('table');
        $.post(window.location.pathname + "/apply", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name': species_name, 'comment': comment}, function(data) { 
            if (data.succeeded) {
                apply_btn.fadeOut(100).fadeIn().text('Applied');
                var content = "<p>You have applied for annotation. Please wait for the approval from the community contacts.</p>"
                if (! apply_records.length) { // if apply_record doesn't exists
                    content += "<table class='table table-apply-record display compact'><thead><tr><th>Submission time</th><th>Comment</th><th>Status</th><th>Msg from contacts</th></tr></thead><tbody><tr><td>" + data['submission_time'] + "</td><td>" + data['comment'] + "</td><td>Pending</td><td></td></tr></tbody></table>";
                    div_well.fadeOut(100).fadeIn().html(content);
                    div_well.children('table').DataTable({
                        "paging":   false,
                        "ordering": false,
                        "info":     false,
                        "searching": false,
                    });
                    // move to request div section, hold off
                    //$('#interested-organism').children('p').after($('#collapse-' + species_name).parent('div'));
                    //$('#collapse-' + species_name).parent('div').fadeOut(100).fadeIn();
                }
                else {
                    div_well.children("div:first-child").remove();
                    apply_records.children('tbody').children('tr:first').before("<tr><td>" + data['submission_time'] + "</td><td>" + data['comment'] + "</td><td>Pending</td><td></td></tr>");
                    div_well.prepend(content);
                    apply_records.fadeOut(100).fadeIn();
                }
            }
            else {
                div_well.fadeOut(100).fadeIn().html('Error occurs. Please contact admin.');
            }
        }, "json");
    });

    $(".well").on('click','.link-reapply', function(event){
        event.preventDefault();
        var species_name = $(this).siblings("input").val();
        $(this).parent('p').remove();
        $("#collapse-"+ species_name + " div.well div").fadeIn();
    });

    $(".well").on('click','.link-approve', function(event){
        event.preventDefault();
        var tr = $(this).parent('td').parent('tr');
        var v = tr.attr('id').split('-'); // ex. {"tr", "castman", "agrpla"}
        var username = v[1];
        var species_name = v[2];
        $.post(window.location.pathname + "/approve", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name':species_name , 'username': username, }, function(data) { 
            if (data.succeeded) {
                var t = $("#annotators-" + species_name).DataTable();
                var rowNode = t.row.add([
                    $("#tr" + "-" + username + "-" + species_name).children("td:nth-child(1)").text(),
                    username,
                    $("#tr" + "-" + username + "-" + species_name).children("td:nth-child(2)").text(),
                    "<a href='#' class='link-remove'>Remove</a>"
                ] ).draw().node();                                                                                     
                $(rowNode).attr("id", "tr-" + username + "-"  + species_name);
            }
            else {
                alert('The user was probably approved by other coordinators. Please try again later.');
            }
            tr.fadeOut(500, function() { $(this).remove(); });
        }, "json");
    });
    
    $(".well").on('click','.link-remove', function(event){
        event.preventDefault();
        var tr = $(this).parent('td').parent('tr');
        var v = tr.attr('id').split('-'); // ex. {"tr", "castman", "agrpla"}
        var username = v[1];
        var species_name = v[2];
        $.post(window.location.pathname + "/remove", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name':species_name , 'username': username, }, function(data) { 
            if (data.succeeded) {
                var t = $("#annotators-" + species_name).DataTable();
                //$('#tr' + '-' + username + '-' + species_name).fadeOut(500, function() { $(this).remove(); });
                //tr.fadeOut(500, function() { $(this).remove(); });
                tr.fadeOut(500);
                t.row('#tr' + '-' + username + '-' + species_name).remove().draw( false );
            }
            else {
                alert('The user was probably removed by other coordinators. Please try again later.');
            }
        }, "json");
    });

    $('#rejectModal').on('show.bs.modal', function(event) {
        $('#hidden-rejectModal').val($(event.relatedTarget).data('whatever'));
    });

    $('#rejectModal').on('shown.bs.modal', function(event) {
        $('#decision_comment').focus();
    });

    $('#historyModal').on('show.bs.modal', function(event) {
        var v = $(event.relatedTarget).data('whatever').split('-'); // ex. ["castman", "agrpla"]
        //var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"').val();
        $.post(window.location.pathname + "/history", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name':v[1] , 'username': v[0], }, function(data) { 
            if (data.succeeded) {
                $('#history-table').children('tbody').children('tr').remove(); // flush the table
                $.each(data['apply_records'], function(idx, val) {
                    $('#history-table').children('tbody').append("<tr><td>" + val['submission_time'] + "</td><td>" + val['comment'] + "</td><td>" + val['status'] + "</td><td>" + val['msg']+ "</td></tr>");
                });
            }
            else {
                $('#historyModal').children('.modal-dialog').children('.modal-content').children('.modal-body').text('Can not get application records. Please try again later.'); 
                //$('#history-table').parent('div').html('Can not get application records. Please try again later.'); 
            }
        }, "json");
    });
    
    $('#addUserModal').on('show.bs.modal', function(event) {
        $('#adduser-count').text('0');
        species_name = $(event.relatedTarget).data('whatever'); // ex. "agrpla"
        var t = $('#adduser-table').DataTable();
        t.clear();
        $.post(window.location.pathname + "/eligible", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name': species_name }, function(data) { 
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

    $('#btn-rejectModal').click(function() {
        var v = $(this).siblings("input").val().split('-'); // ex. ["castman", "agrpla"]
        var comment = $('#decision_comment').val();
        $.post(window.location.pathname + "/reject", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name':v[1] , 'username': v[0], 'comment': comment}, function(data) { 
            if (data.succeeded) {
                $('#rejectModal').modal('hide');
            }
            else {
               $('#rejectModal').children('.modal-dialog').children('.modal-content').children('.modal-body').text('The user was probably rejected by other coordinators. Please try again later.'); 
            }
            $('#tr-' + v[0] + '-' + v[1]).fadeOut(500, function() { $(this).remove(); });
        }, "json");
    });

    $('#btn-addUserModal').click(function() {
        var species_name = $('#btn-addUserModal').next("input").val();
        var usernames = [];
        $.each(TableTools.fnGetInstance('adduser-table').fnGetSelectedData(), function(idx, val) {
            usernames.push(val[1]);
        });
        $('#btn-addUserModal').button('loading');
        $.post(window.location.pathname + "/adduser", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name': species_name, 'usernames': usernames,}, function(data) { 
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
                // remove and ckear selected rows, reset counter, recover adding button
                $('#adduser-table tr.selected').fadeOut(500);
                $('#adduser-table').DataTable().row('.selected').remove().draw( false );
                TableTools.fnGetInstance('adduser-table').fnSelectNone();
                $('#adduser-count').text('0');
                $('#btn-addUserModal').button('reset');
            }
            else {
               $('#addUserModal').children('.modal-dialog').children('.modal-content').children('.modal-body').text('Error occured when adding users. Please try again later.');
            }
        }, "json");
    });
});
