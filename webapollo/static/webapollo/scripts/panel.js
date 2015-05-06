$(function() { // document ready

    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
    var path = window.location.pathname.substring(0, window.location.pathname.lastIndexOf( "/" ) + 1);

    $(".table-apply-records").DataTable({
        "paging":   false,
        "ordering": false,
        "info":     false,
        "searching": false,
    });
    
    $(".well").on('click','.btn-new', function(){
        $(this).addClass('disabled');   // prevent double submissions
        var species_name = this.id.replace("btn_","");
        var comment = $(this).parent('p').prev('p').find('textarea').val();
        //var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"').val();
        var apply_btn = $("#collapse-" + species_name).prev('table.species-table').find('tr td:nth-child(2) .btn');
        var div_well = $("#collapse-" + species_name).children('div.well');
        var apply_records = $(this).parent('p').parent('div').next('div').children('table');
        $.post(path + "apply", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name': species_name, 'comment': comment}, function(data) { 
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

    $(".well").on('click','.link-remind', function(event){
        event.preventDefault();
        var msg_span = $(this).parent('span');
        var sname = msg_span.parent('p').parent('div').parent('div').attr('id').replace('collapse-','');
        $.post(path + "remind", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'sname':sname, }, function(data) { 
            if (data.succeeded) {
                msg_span.html('<span style="color:green;" >A reminder was sent!!</span>');
            }
            else {
                msg_span.html('<span style="color:red;" >Errors occured. Please try again later.</span>');
            }
        }, "json");
        
    });

    $(".well").on('click','.link-reapply', function(event){
        event.preventDefault();
        var species_name = $(this).siblings("input").val();
        $(this).parent('p').remove();
        $("#collapse-"+ species_name + " div.well div").fadeIn();
    });

});
