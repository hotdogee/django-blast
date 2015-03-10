$(function() { // document ready

    $("#table-user-permission").DataTable( {
        "dom": "Tlftip",
        "order": [[ 1, "asc" ]],
        "aoColumnDefs": [{ "bSortable": false, "aTargets": [0,2,3,4,5,6] }],
        tableTools: {
            "sRowSelect": "multi",
            "sRowSelector": "td:first-child",
            "aButtons": [],
        }
    });


    $("input[name=owner]").click(function() {
        if (this.checked) {
            $(this).parent("td").siblings().find("input").each(function() {
                $(this).attr("checked", true);
                $(this).attr("disabled", true);
            });
        }
        else {
            $(this).parent("td").siblings().find("input").each(function() {
                $(this).attr("checked", false);
                $(this).attr("disabled", false);
            });
        }
    });


    $("#select-all").click(function() {
        $(this).parent("tr").toggleClass("selected");
        if ( $(this).parent("tr").hasClass("selected") ) {
            TableTools.fnGetInstance("table-user-permission").fnSelectAll();
        }
        else {
            TableTools.fnGetInstance("table-user-permission").fnSelectNone();
        }
    });


    $('#btn-update').click(function() {
        var species_permissions = [];
        $.each(TableTools.fnGetInstance('table-user-permission').fnGetSelectedData(), function(idx, val) {
            /* example:
             * ["", "cataqu (Catajapyx aquilonaris)", "<input type="checkbox" name="read" value="1" checked="">", 
             * "<input type="checkbox" name="write" value="2" checked="">", "<input type="checkbox" name="publist" value="4">", 
             * "<input type="checkbox" name="admin" value="8">", "<input type="checkbox" name="owner" value="0">"]
            */
            var species_name = val[1].split(" ")[0]
            var permission = 0;
            var is_owner = false;
            if ($("#" + species_name).children("td")[2].children[0].checked) permission += 1;
            if ($("#" + species_name).children("td")[3].children[0].checked) permission += 2;
            if ($("#" + species_name).children("td")[4].children[0].checked) permission += 4;
            if ($("#" + species_name).children("td")[5].children[0].checked) permission += 8;
            if ($("#" + species_name).children("td")[6].children[0].checked) is_owner = true;
            species_permissions.push({
                'species_name': species_name,
                'permission': permission,
                'is_owner': is_owner,
            });
        });
        console.log(species_permissions);
        /*$.post(window.location.pathname + "/reject", {'csrfmiddlewaretoken': csrfmiddlewaretoken, 'species_name':v[1] , 'username': v[0], 'comment': comment}, function(data) { 
            if (data.succeeded) {
            }
            else {
            }
        }, "json");*/
    });
});

