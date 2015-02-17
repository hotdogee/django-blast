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
        var v = $(this).parent('td').parent('tr').attr('id').split('-'); // ex. {"tr", "castman", "agrpla"}
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
                $('#tr' + '-' + username + '-' + species_name).fadeOut(500, function() { $(this).remove(); });
                $(rowNode).attr("id", "tr-" + username + "-"  + species_name);
            }
            else {
                console.log('approve failed!');
            }
        }, "json");
    });
    
    $(".well").on('click','.link-remove', function(event){
        event.preventDefault();
        var v = $(this).parent('td').parent('tr').attr('id').split('-'); // ex. {"tr", "castman", "agrpla"}
        var username = v[1];
        var species_name = v[2];
        $.post(window.location.pathname + "/remove", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name':species_name , 'username': username, }, function(data) { 
            if (data.succeeded) {
                var t = $("#annotators-" + species_name).DataTable();
                $('#tr' + '-' + username + '-' + species_name).fadeOut(500, function() { $(this).remove(); });
            }
            else {
                console.log('remove failed!');
            }
        }, "json");
    });

    $('#rejectModal').on('show.bs.modal', function(event) {
        $('#hidden-rejectModal').val($(event.relatedTarget).data('whatever'));
    })

    $('#rejectModal').on('shown.bs.modal', function(event) {
        $('#decision_comment').focus();
    })

    $('#historyModal').on('show.bs.modal', function(event) {
        var v = $(event.relatedTarget).data('whatever').split('-'); // ex. ["castman", "agrpla"]
        //var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"').val();
        $.post(window.location.pathname + "/history", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name':v[1] , 'username': v[0], }, function(data) { 
            if (data.succeeded) {
                $('#history-table').children('tbody').children('tr').remove();
                $.each(data['apply_records'], function(idx, val) {
                    $('#history-table').children('tbody').append("<tr><td>" + val['submission_time'] + "</td><td>" + val['comment'] + "</td><td>" + val['status'] + "</td><td>" + val['msg']+ "</td></tr>");
                });
            }
            else {
                $('#history-table').parent('div').html('Error occurs. Please contact admin.'); 
            }
        }, "json");

        // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    })

    $('#btn-rejectModal').click(function() {
        var v = $(this).siblings("input").val().split('-'); // ex. ["castman", "agrpla"]
        //var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"').val();
        var comment = $('#decision_comment').val();
        $.post(window.location.pathname + "/reject", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name':v[1] , 'username': v[0], 'comment': comment}, function(data) { 
            if (data.succeeded) {
                $('#rejectModal').modal('hide');
                $('#tr-' + v[0] + '-' + v[1]).fadeOut();
                $('#tr-' + v[0] + '-' + v[1]).remove();
            }
            else {
               $('#btn-rejectModal').parent().prev('p').remove(); 
               $('#btn-rejectModal').parent().prev('p').html('Error occurs. Please contact admin.'); 
               $('#btn-rejectModal').prop('disabled', true);; 
            }
        }, "json");
    });
});
