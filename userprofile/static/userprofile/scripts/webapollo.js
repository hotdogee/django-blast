$("#more-organism-show").click(function( event ) {
    event.preventDefault();
    $("#more-organism").hide();
    $("#other-organism").fadeIn();
});

$("#more-organism-hide").click(function( event ) {
    event.preventDefault();
    $("#other-organism").hide();
    $("#more-organism").fadeIn();
});

$(".well").on('click','.btn-new', function(){
    var species_name = this.id.replace("btn_","");
    var comment = $(this).parent('p').prev('p').find('textarea').val();
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"').val();
    var apply_btn = $(this).closest('div.well').parent('div').prev('table.species-table').find('tr td:nth-child(2) .btn');
    var div_well = $(this).parent('p').parent('div');
    $.post(window.location.pathname + "/apply", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name': species_name, 'comment': comment}, function(data) { 
        if (typeof data.invalid == 'undefined') {
            apply_btn.fadeOut(100).fadeIn().text('Applied');
            var content = "<p>You have applied for annotating this organism on " + data['submission_time'] + ". Please wait for the approval from the community contact.</p>"
            div_well.fadeOut(100).fadeIn().html(content);
        }
        else {
            div_well.fadeOut(100).fadeIn().html('Error occurs. Please contact admin.');
        }
    }, "json");
});
