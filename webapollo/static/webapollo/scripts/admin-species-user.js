$(function() { // document ready

    $("#table-users").DataTable( {
        "dom": "Tlftip",
        tableTools: {
            "sRowSelect": "multi",
            "aButtons": [],
        }
    });


    $("#table-candidates").DataTable( {
        "dom": "Tlftip",
        tableTools: {
            "sRowSelect": "multi",
            "aButtons": [],
        }
    });


    $("#table-users tbody").on("click", "tr", function () {
        $("#users-count").text(TableTools.fnGetInstance("table-users").fnGetSelected().length);        
    });


    $("#table-candidates tbody").on("click", "tr", function () {
        $("#candidates-count").text(TableTools.fnGetInstance("table-candidates").fnGetSelected().length);        
    });


    $(".btn-users").click(function(event) {
        var $btn = $(this).button('loading');
        if ($(this).attr("id") == "btn-update") {
            $("#users-operation").val("update");
        }
        else {
            $("#users-operation").val("remove");
        }
        try {
            usernames = [];
            $.each(TableTools.fnGetInstance('table-users').fnGetSelectedData(), function(idx, val) {
                usernames.push(val[1]);
            });
            $("#input-users").val(usernames.join());
        }
        catch(err) {
            $('#alert-danger').text('Exceptions when locating users').fadeIn();
            $btn.button('reset');
            event.preventDefault();
        }
    });



    $(".btn-candidates").click(function(event) {
        var $btn = $(this).button('loading')
        if ($(this).attr("id") == "btn-adduser") {
            $("#candidates-operation").val("adduser");
        }
        else {
            $("#candidates-operation").val("addowner");
        }
        try {
            usernames = [];
            $.each(TableTools.fnGetInstance('table-candidates').fnGetSelectedData(), function(idx, val) {
                usernames.push(val[1]);
            });
            $("#input-candidates").val(usernames.join());
        }
        catch(err) {
            $('#alert-danger').text('Exceptions when locating users').fadeIn();
            $btn.button('reset');
            event.preventDefault();
        }
    });
});

