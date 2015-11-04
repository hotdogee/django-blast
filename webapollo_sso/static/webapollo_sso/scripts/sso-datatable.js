/**
 * Created by yu-yu.lin on 11/4/2015.
 */
$(document).ready(function() {

    //implement callback for datatable after drawing
    var timer_userTable;
    var timer_groupTable;
    var is_usertable_finish_load = false;
    var is_grouptable_finish_load = false;

    //error alert
    function errorAlert(text){
        BootstrapDialog.alert({
            title: 'ERROR',
            message: text,
            type: BootstrapDialog.TYPE_DANGER,
        });
    }

    //pre-load data
    var availableUsers = [];
    function loadAllGroups(){
        $.getJSON("http://10.11.210.63:8000/sso/get_all_groups", function(data){
            $('#all-groups').val(data);
        });
    }

    //jumpToData func and two timer to simulate callback func of datatable
    jQuery.fn.dataTable.Api.register( 'page.jumpToData()', function ( data, column, DomTable ) {
        var pos = this.column(column, {order:'current'}).data().indexOf( data );

        if ( pos >= 0 ) {
            var page = Math.floor( pos / this.page.info().length );
            this.page( page ).draw( false );

            var idx = pos - page * this.page.info().length;

            $(DomTable).DataTable().$('tr.selected').removeClass('selected');
            $(DomTable.rows[idx+1]).addClass('selected');
            $(DomTable.rows[idx+1]).click();
        }
        return this;
    } );

    function func_timer_userTable(userName){
        if(is_usertable_finish_load){
            $('#userTable').DataTable().page.jumpToData( userName, 0 , $('#userTable')[0]);
            for(i=0; i<9999; i++){clearInterval(i);}
        }
    };

    function func_timer_groupTable(groupName){
        if(is_grouptable_finish_load){
            $('#groupTable').DataTable().page.jumpToData( groupName, 0 , $('#groupTable')[0]);
            for(i=0; i<9999; i++){clearInterval(i);}
        }
    };

    //cookie handlers
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var table;
    var is_myUser_loaded = false;

    $('#myUserTab').on('click',function(){
        if(is_myUser_loaded == true)return;
        is_myUser_loaded = true;

        table = $('#userTable').DataTable({
            "processing":true,
            "paging":true,
            "deferRender": true,
            "ajax": {
                "url" : 'http://10.11.210.63:8000/sso/get_users',
                "dataSrc": ""
            },
            "columns": [
                {"data":"username"},
                {"data":"firstName"},
                {"data":"lastName"},
                {"data":"role"},
                {"data":"groups[,].name"},
                {"data":"groups[,].name"},
                {"data":"userId"},
                //{"data":"availableGroups[,].name"},
                {"data":"djangoUser"},
                //{"data":"organismPermissions[,].permissions"},
            ],
            "columnDefs": [{
                "aTargets": [4], // Column to target
                "mRender": function ( data, type, full ) {
                    text = '';
                    var str = data.split(",");
                    for (i = 0; i < str.length; i++){
                        var patt = /GROUP_(\w+)_ADMIN/g;
                        if(patt.test(str[i]) == true){
                            var organism = str[i].split("_")[1];
                            text += organism + ",";
                        }
                    }
                    return '<a href="' + data  + '" target="_blank">' + text + '</a>';
                }},{
                "aTargets": [5], // Column to target
                "mRender": function ( data, type, full ) {
                    text = '';
                    var str = data.split(",");
                    for (i = 0; i < str.length; i++){
                        var patt = /GROUP_(\w+)_USER/g;
                        if(patt.test(str[i]) == true){
                            var organism = str[i].split("_")[1];
                            text += organism + ",";
                        }
                    }
                    return '<a href="' + data  + '" target="_blank">' + text + '</a>';
                }},
            ],
            "order": [[ 6, "asc" ]],
            "fnInitComplete": function (oSettings) {
                loadAllGroups();
                $('#user-reset-button').click();
                //$('#myGroupTab').click();
                //pre-load data of user list
                for (i = 0; i < table.column(0, {order:'current'}).data().length; i++){
                    availableUsers[i] = table.column(0, {order:'current'}).data()[i];
                }
                availableUsers.sort();

            },
            "fnDrawCallback": function (oSettings) {
                is_usertable_finish_load = true;
            },
        });
    });

    $('a.toggle-vis').on( 'click', function (e) {
            e.preventDefault();
            var column = table.column( $(this).attr('data-column') );
            column.visible( ! column.visible() );
    });

    $('#userTable').delegate('tbody tr','click',function() {
        if ( $(this).hasClass('selected') ) {
            //$(this).removeClass('selected');
        }
        else {
            table.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }

        $('#user-name').val(table.cell(table.row(this).index(),0).data());
        $('#first-name').val(table.cell(table.row(this).index(),1).data());
        $('#last-name').val(table.cell(table.row(this).index(),2).data());
        $('#user-role').val(table.cell(table.row(this).index(),3).data());
        $('#django-user-name').val('');
        $('#user-password').val('');

        text = "";
        str = table.cell(table.row(this).index(),4).data().split(",");
        if(str != ""){
            for (i = 0; i < str.length; i++){
                text += "<button type='button' class='btn btn-success user-group-button' value='" + str[i] + "'>" + str[i] + "</button> ";
            }
        }
        $('#user-group-now-group').html(text);

        text = "";
        var str = $('#all-groups').val().split(",");
        var groupin = table.cell(table.row(this).index(),4).data().split(",");

        for (i = 0; i < str.length; i++){
            if($.inArray(str[i], groupin) == -1){
                text += "<button type='button' class='btn btn-gray user-group-button' value='" + str[i] + "'>" + str[i] + "</button> ";
            }
        }
        $('#user-group-avaiable-group').html(text);
    } );


    $('#user-group').delegate('.user-group-button','click',function(){
        if(typeof(table.row(table.$('tr.selected')).index()) == 'undefined'){
            return;
        }
        userId = table.cell(table.row(table.$('tr.selected')).index(),6).data();
        userName = table.cell(table.row(table.$('tr.selected')).index(),0).data();
        groupName = $(this).val();
        $('.user-group-button').addClass('disabled');
        if($(this).hasClass('btn-success') == true){
            $(this).removeClass('btn-success');
            $(this).addClass('btn-gray');

            $.ajax({
                type: "POST",
                url: 'http://10.11.210.63:8000/sso/remove_user_from_group',
                data: { groupName: groupName ,userId: userId},
                success: function(data){
                    is_usertable_finish_load = false;
                    table.ajax.reload();
                    timer_userTable = setInterval(function(){func_timer_userTable(userName)}, 10);
                }
            });

        }else if($(this).hasClass('btn-gray') == true){
            $(this).removeClass('btn-gray');
            $(this).addClass('btn-success');

            $.ajax({
                type: "POST",
                url: 'http://10.11.210.63:8000/sso/add_user_to_group',
                data: { groupName: groupName , user: userName, userId: userId},
                success: function(data){
                    is_usertable_finish_load = false;
                    table.ajax.reload();
                    timer_userTable = setInterval(function(){func_timer_userTable(userName)}, 10);
                }
            });

        }
    });

    //myGroup
    var table_group;
    var is_myGroup_load = false;
    $('#myGroupTab').on('click',function(){
        if(is_myGroup_load == true)return;
        is_myGroup_load = true;

        table_group = $('#groupTable').DataTable({
            "ajax": {
                "url" : 'http://10.11.210.63:8000/sso/get_groups',
                "dataSrc": ""
            },
            "columns": [
                {"data":"name"},
                {"data":"numberOfUsers"},
                {"data":"public"},
                {"data":"id"},
                {"data":"users[,].email"},
                {"data":"permission.permissions"}
            ],
            "order": [[ 0, "desc" ]],
            "fnDrawCallback": function (oSettings) {
                is_grouptable_finish_load = true;
            },
        });
        table_group.column(4).visible(false);
    });

    $('#groupTable').delegate('tbody tr','click',function(){

        if ( $(this).hasClass('selected') ) {
            //$(this).removeClass('selected');
        }else {
            table_group.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
        groupName = table_group.cell(table_group.row(this).index(),0).data();
        var organism = '';
        var patt = /GROUP_(\w+)_USER|GROUP_(\w+)_ADMIN/g;
        if(patt.test(groupName) == true){
            organism = groupName.split("_")[1];
        }

        $('#group-name').val(organism);
        $('#group-admin-name').text("GROUP_" + organism + "_ADMIN");
        $('#group-user-name').text("GROUP_" + organism + "_USER");

        text = "";
        str = table_group.cell(table_group.row(this).index(),4).data().split(",");
        if(str != ""){
            for (i = 0; i < str.length; i++){
                text += "<button type='button' class='btn btn-success group-member-button' value='" + str[i] + "'>" + str[i] + "</button> ";
            }
        }
        $('#group-member-now-member').html(text);

        text = "";
        permissons = table_group.cell(table_group.row(this).index(),5).data();
        perms = ['READ','WRITE','EXPORT'];
        for (i = 0; i < perms.length; i++){
            if(permissons.indexOf(perms[i]) > -1){
                text += "<button type='button' class='btn btn-success group-permission-button' value='" + str[i] + "'>" + perms[i] + "</button> ";
            }else{
                text += "<button type='button' class='btn btn-gray group-permission-button' value='" + str[i] + "'>" + perms[i] + "</button> ";
            }
        }

        $('#group-permissions').html(text);
    });

    $('#group-member').delegate('.group-member-button','click',function(){
        if(typeof(table_group.row(table_group.$('tr.selected')).index()) == 'undefined'){return;}

        groupName = table_group.cell(table_group.row(table_group.$('tr.selected')).index(),0).data();
        userName = $(this).val();
        $('.group-member-button').addClass('disabled');
        if($(this).hasClass('btn-success') == true){
            $(this).removeClass('btn-success');
            $(this).addClass('btn-gray');

            $.ajax({
                type: "POST",
                url: 'http://10.11.210.63:8000/sso/remove_user_from_group',
                data: { groupName: groupName ,userName: userName},
                success: function(data){
                    is_grouptable_finish_load = false;
                    table_group.ajax.reload();
                    timer_groupTable = setInterval(function(){func_timer_groupTable(groupName)}, 10);
                }
            });
        }
    });

    //myOrganism
    var is_myOrganism_loaded = false;
    $('#myOrganismTab').on('click',function(){
        if(is_myOrganism_loaded == true)return;
        is_myOrganism_loaded = true;

        $.getJSON("http://10.11.210.63:8000/sso/get_my_organism", function(data){
            var items = [];
            $.each( data, function( key, val ) {
                if(val[0] == true){
                    box = ""
                    if(val[1] == true){
                        box = "<i class='fa fa-envelope-o'></i>"
                        $('#myOrganismTab').html("My Organism <i class='fa fa-envelope-o'></i>");
                    }
                    name = key.split("_")[0]
                    oid  = key.split("_")[1]
                    items.push( "<legend style='font-size:20px; padding-top:20px'>" + name +
                        " <button type='button' class='btn btn-primary' onclick='myFunction()'>Owner</button>" +
                        " <button type='button' class='btn btn-success'>Launch</button>" +
                        "</legend>" +
                        "<p><a href='#" + name + "-user-collapse' data-toggle='collapse' id='" + name + "' class='userlink'>User Collapsible</a>" +
                        "<div id='" + name + "-user-collapse' class='collapse'>" +
                        "<table id='table" + name + "' class='display' cellspacing='0' width='100%' load='none' id='" + name + "' oid = '" + oid + "' oname='" + name + "'><thead><tr>" +
                        "<th>UserName</th><th>FirstName</th><th>LastName</th><th>Role</th><th>Species_Admin</th><th>Species_User</th><th>Organism</th><th>Permission</th><th>UserId</th><th>action</th>" +
                        "</tr></thead></table></div>" +
                        "<a href='#" + name + "-pending-request-collapse' data-toggle='collapse' id='" + name + "' oid = '" + oid + "' class='pendinglink'>Pending Request Collapsible</a> " + box +
                        " <div id='" + name + "-pending-request-collapse' class='collapse'>" +
                        "<table id='tableRequest" + name + "' class='display tableRequest' cellspacing='0' width='100%' load='none' oid='" + oid + "' oname='" + name + "'><thead><tr>" +
                        "<th>UserName</th><th>FirstName</th><th>LastName</th><th>Role</th><th>Species_Admin</th><th>Species_User</th><th>userID</th><th>Action</th>" +
                        "</tr></thead></table></div>"
                        );
                }else{
                     name = key.split("_")[0]
                     items.push( "<legend style='font-size:20px; padding-top:20px'>" + name +
                        " <button type='button' class='btn btn-info'>Info</button>" +
                        " <button type='button' class='btn btn-success'>Launch</button>" +
                        "</legend>" +
                        "<a href='#" + name + "-owner-info-collapse' data-toggle='collapse' id='test'>Info Collapsible</a>" +
                        "<div id='" + name + "-owner-info-collapse' class='collapse'></div>"
                        );
                }
            });

            $( items.join( "" )
            ).appendTo( $("#myOrganism") );

        })
    });

    //myRequest
    var table_request;
    var is_myRequest_loaded = false;
    $('#myRequestTab').on('click',function(){
        if(is_myRequest_loaded == true)return;
        is_myRequest_loaded = true;

        table_request = $('#requestTable').DataTable({
            "processing":true,
            //"serverSide": true,
            "ajax": {
                "url" : 'http://10.11.210.63:8000/sso/get_my_request',
                "dataSrc": ""
            },
            "columns": [
                {"data":"commonName"},
                {"data":"species"},
                {"data":"genus"},
                {"data":"valid"},
                {"data":"id"},
                {"data":"admin"},
                {"data":"action"},
            ],
            "columnDefs": [{
                "aTargets": [6], // Column to target
                "mRender": function ( data, type, full ) {
                    if(data == 'REQUEST'){
                        return '<button type="button" class="btn btn-primary action">request</button>'
                    }else if(data == 'RELEASE'){
                        return '<button type="button" class="btn btn-danger action">release</button>'
                    }else if(data == 'W_REQUEST'){
                        return '<button type="button" class="btn btn-primary action">requesting</button>'
                    }else if(data == 'W_RELEASE'){
                        return '<button type="button" class="btn btn-danger action">releaseing</button>'
                    }else{
                        return ''
                    }

                }}
            ],
        });
    });


    $('#myOrganism').delegate('.userlink','click',function(){

        tablename = "table" + $(this).attr('id');

        if($('#' + tablename).attr("load") == "none"){

            $('#' + tablename).attr("load","OK");

            var table = $('#' + tablename).DataTable({
                "processing":true,
                //"serverSide": true,
                "ajax": {
                    "url" : 'http://10.11.210.63:8000/sso/get_users?organism=' + $(this).attr('id'),
                    "dataSrc": ""
                },
                "columns": [
                    {"data":"username"},
                    {"data":"firstName"},
                    {"data":"lastName"},
                    {"data":"role"},
                    {"data":"groups[,].name"},
                    {"data":"groups[,].name"},
                    {"data":"organismPermissions[,].organism"},
                    {"data":"organismPermissions[,].permissions"},
                    {"data":"userId"},
                    {"data":"admin"}
                ],
                "columnDefs": [{
                    "aTargets": [4], // Column to target
                    "mRender": function ( data, type, full ) {
                        text = '';
                        var str = data.split(",");
                        for (i = 0; i < str.length; i++){
                            var patt = /GROUP_(\w+)_ADMIN/g;
                            if(patt.test(str[i]) == true){
                                var organism = str[i].split("_")[1];
                                text += organism + ",";
                            }
                        }
                        return '<a href="' + data  + '" target="_blank">' + text + '</a>';
                    }},{
                    "aTargets": [5], // Column to target
                    "mRender": function ( data, type, full ) {
                        text = '';
                        var str = data.split(",");
                        for (i = 0; i < str.length; i++){
                            var patt = /GROUP_(\w+)_USER/g;
                            if(patt.test(str[i]) == true){
                                var organism = str[i].split("_")[1];
                                text += organism + ",";
                            }
                        }
                        return '<a href="' + data  + '" target="_blank">' + text + '</a>';
                    }},{
                    "aTargets": [9], // Column to target
                    "mRender": function ( data, type, full ) {
                        if(data == false){
                            return '<button type="button" class="btn btn-danger user-manage-button">release</button>'
                        }else{
                            return ''
                        }
                    }},
                ],
                "order": [[ 8, "asc" ]],
            });
        }
    })

    //event handler for myOrganism
    $('#myOrganism').delegate('.pendinglink','click',function(){

        tablename = "tableRequest" + $(this).attr('id');

        if($('#' + tablename).attr("load") == "none"){

            $('#' + tablename).attr("load","OK");

                var table = $('#' + tablename).DataTable({
                "processing":true,
                //"serverSide": true,
                "ajax": {
                    "url" : 'http://10.11.210.63:8000/sso/get_pending_request?oid=' + $(this).attr('oid'),
                    "dataSrc": ""
                },
                "columns": [
                    {"data":"username"},
                    {"data":"firstName"},
                    {"data":"lastName"},
                    {"data":"role"},
                    {"data":"groups[,].name"},
                    {"data":"groups[,].name"},
                    {"data":"userId"},
                    {"data":"action"}
                ],
                "columnDefs": [{
                    "aTargets": [4], // Column to target
                    "mRender": function ( data, type, full ) {
                        text = '';
                        var str = data.split(",");
                        for (i = 0; i < str.length; i++){
                            var patt = /GROUP_(\w+)_ADMIN/g;
                            if(patt.test(str[i]) == true){
                                var organism = str[i].split("_")[1];
                                text += organism + ",";
                            }
                        }
                        return '<a href="' + data  + '" target="_blank">' + text + '</a>';
                    }},{
                    "aTargets": [5], // Column to target
                    "mRender": function ( data, type, full ) {
                        text = '';
                        var str = data.split(",");
                        for (i = 0; i < str.length; i++){
                            var patt = /GROUP_(\w+)_USER/g;
                            if(patt.test(str[i]) == true){
                                var organism = str[i].split("_")[1];
                                text += organism + ",";
                            }
                        }
                        return '<a href="' + data  + '" target="_blank">' + text + '</a>';
                    }},{
                    "aTargets": [7], // Column to target
                    "mRender": function ( data, type, full ) {
                        if(data == 'REQUEST'){
                            return '<button type="button" class="btn btn-primary pending-request-button" action="ACCEPT">request-accept</button>' + ' <button type="button" class="btn btn-primary pending-request-button" action="REFUSE">request-refuse</button>'
                        }else if(data == 'RELEASE'){
                            return '<button type="button" class="btn btn-danger pending-request-button" action="ACCEPT">release-accept</button>' + ' <button type="button" class="btn btn-danger pending-request-button"action="REFUSE">release-refuse</button>'
                        }else{
                            return ''
                        }
                    }}
                ],
            });
        }
    })

    $('#myOrganism').delegate('.pending-request-button','click',function(){
        var current_column = this.parentElement;
        var current_row = current_column.parentElement;
        var table_name = current_row.parentElement.parentElement.id;
        var oid = $(current_row.parentElement.parentElement).attr("oid");
        var oname = $(current_row.parentElement.parentElement).attr("oname");
        var action = $(this).attr("action");
        var table = $('#'+table_name).DataTable();

        var idx = table.row(current_row).index();
        var name  = table.cell(idx,0).data();
        var userId = table.cell(idx,6).data();

        BootstrapDialog.confirm({
            title: 'Are you sure you want to do that?',
            message: $('<textarea class="form-control" maxlength="100" placeholder="Type the reason that you do this here... (<100 words)"></textarea>'),
            type: BootstrapDialog.TYPE_WARNING,
            closable: true,
            draggable: true,
            btnOKClass: 'btn-warning',
            callback: function(result) {
                if(result) {
                    $.ajax({
                    type: "POST",
                    url: 'http://10.11.210.63:8000/sso/handle_request',
                    data: { action: action, oid : oid , oname: oname , user: name, userId: userId, reply_desc : $('.form-control').val()},
                    success: function(data){
                        table.ajax.reload();
                        }
                    });
                }
            }
        });
    })

    $('#myOrganism').delegate('.user-manage-button','click',function(){
        var current_column = this.parentElement;
        var current_row = current_column.parentElement;
        var table_name = current_row.parentElement.parentElement.id;
        var table = $('#'+table_name).DataTable();
        var oid = $(current_row.parentElement.parentElement).attr("oid");
        var oname = $(current_row.parentElement.parentElement).attr("oname");

        var idx = table.row(current_row).index();
        var userId = table.cell(idx,8).data();
        var name  = table.cell(idx,0).data();

        BootstrapDialog.confirm({
            title: 'Are you sure you want to do that?',
            message: $('<textarea class="form-control"  maxlength="100" placeholder="Type the reason that you do this here... (<100 words)"></textarea>'),
            type: BootstrapDialog.TYPE_WARNING,
            closable: true,
            draggable: true,
            btnOKClass: 'btn-warning',
            callback: function(result) {
                if(result) {
                    $.ajax({
                    type: "POST",
                    url: 'http://10.11.210.63:8000/sso/remove_user_from_group',
                    data: { groupName: "GROUP_" + oname + "_USER", userId: userId, reason : $('.form-control').val()},
                    success: function(data){
                        table.ajax.reload();
                        }
                    });
                }
            }
        });
    })


    $('#myRequest').delegate('.action','click',function(){
        var action = table_request.cell(this.parentElement).data();
        var idx = table_request.row(this.parentElement.parentElement).index();
        var oid  = table_request.cell(idx,4).data();

        BootstrapDialog.confirm({
            title: 'Are you sure you want to do that?',
            message: $('<textarea class="form-control" maxlength="100" placeholder="Type the reason that you do this here... (<100 words)"></textarea>'),
            type: BootstrapDialog.TYPE_WARNING,
            closable: true,
            draggable: true,
            btnOKClass: 'btn-warning',
            callback: function(result) {
                if(result) {
                    $.ajax({
                    type: "POST",
                    url: 'http://10.11.210.63:8000/sso/make_request',
                    data: { oid: oid , action: action, apply_desc : $('.form-control').val()},
                    success: function(data){
                        if(jQuery.isEmptyObject(data)){
                            table_request.ajax.reload();
                        }else if('error' in data){
                            errorAlert(data['error']);
                        }
                        }
                    });
                }
            }
        });
    })

    //event handler for user management
    $('#user-create-button').on('click', function(){
        if($('#user-create-button').val() == 'Create'){
            $('#user-cancel-button').click();
            $('#user-create-button').val('Save');
            $('#user-cancel-button').removeClass('hide');
            disableUserButtons();
            $('#user-create-button').prop('disabled', false);
            $('#user-cancel-button').prop('disabled', false);
        }else if($('#user-create-button').val() == 'Save'){
            firstName = $('#first-name').val();
            lastName  = $('#last-name').val();
            userName  = $('#user-name').val();
            password  = $('#user-password').val();
            djangoUserName = $('#django-user-name').val();

            BootstrapDialog.confirm({
                message: 'You\'re going to create user ' + userName + ', are you sure?',
                type: BootstrapDialog.TYPE_WARNING,
                callback : function(result){
                    if(result) {
                        $.ajax({
                            type: "POST",
                            url: 'http://10.11.210.63:8000/sso/create_user',
                            data: {firstName : firstName, lastName : lastName, userName : userName, password : password, djangoUserName : djangoUserName},
                            success: function(data){
                                if(jQuery.isEmptyObject(data)){
                                    BootstrapDialog.alert("Create user " + userName +  " success!");
                                    table.ajax.reload();
                                    $('#user-cancel-button').click();
                                }else if('error' in data){
                                    errorAlert(data['error']);
                                }
                            }
                        });
                    }
                }
            });

            $('#user-create-button').val('Create');
            $('#user-cancel-button').addClass('hide');
            $('#user-update-button').prop('disabled', false);
            $('#user-delete-button').prop('disabled', false);
            $('#user-disconnect-button').prop('disabled', false);
        }
    });

    $('#user-cancel-button').on('click', function(){
        $('#user-name').val('');
        $('#first-name').val('');
        $('#last-name').val('');
        $('#user-role').prop('selectedIndex', 0);
        $('#django-user-name').val('');
        $('#user-create-button').val('Create');
        $('#user-cancel-button').addClass('hide');
        $('#check-django-user-icon').removeClass();
        $('#user-password').val('');
        enableUserButtons();
    });


    $('#user-delete-button').on('click', function(){
        if(typeof(table.row(table.$('tr.selected')).index()) == 'undefined'){
            return;
        }

        userId = table.cell(table.row(table.$('tr.selected')).index(),6).data();
        BootstrapDialog.confirm({
            message: 'You\'re going to delete user ' + userId + ', are you sure?',
            type: BootstrapDialog.TYPE_WARNING,
            callback : function(result){
                if(result) {
                    $.ajax({
                        type: "POST",
                        url: 'http://10.11.210.63:8000/sso/delete_user',
                        data: {userId : userId},
                        success: function(data){
                            if(jQuery.isEmptyObject(data)){
                                table.ajax.reload();
                                $('#user-cancel-button').click();
                            }else if('error' in data){
                                errorAlert(data['error']);
                            }
                        }
                    });
                }
            }
        });

   });

    $('#user-update-button').on('click', function(){
        if(typeof(table.row(table.$('tr.selected')).index()) == 'undefined') return;

        userId = table.cell(table.row(table.$('tr.selected')).index(),6).data();
        firstName = $('#first-name').val();
        lastName  = $('#last-name').val();
        userName  = $('#user-name').val();
        role      = $('#user-role').val();
        password  = $('#user-password').val();
        djangoUserName = $('#django-user-name').val();

        BootstrapDialog.confirm({
            message: 'You\'re going to update user ' + userId + ', are you sure?',
            type: BootstrapDialog.TYPE_WARNING,
            callback : function(result){
                if(result) {
                    $.ajax({
                        type: "POST",
                        url: 'http://10.11.210.63:8000/sso/update_user',
                        data: {userId : userId, firstName : firstName, lastName : lastName, userName : userName, role : role, password : password, djangoUserName : djangoUserName},
                        success: function(data){
                            if(jQuery.isEmptyObject(data)){
                                BootstrapDialog.alert("Update user " + userName +  " success!");
                                table.ajax.reload();
                                $('#user-cancel-button').click();
                            }else if('error' in data){
                                errorAlert(data['error']);
                            }
                        }
                    });
                }
            }
        });
    });

    $('#user-disconnect-button').on('click', function(){
        if(typeof(table.row(table.$('tr.selected')).index()) == 'undefined')return;

        userId = table.cell(table.row(table.$('tr.selected')).index(),6).data();
        firstName = $('#first-name').val();
        lastName  = $('#last-name').val();
        userName  = $('#user-name').val();
        role      = $('#user-role').val();

        BootstrapDialog.confirm({
            message: 'You\'re going to disconnect user ' + userId + ', are you sure?',
            type: BootstrapDialog.TYPE_WARNING,
            callback : function(result){
                if(result) {
                    $.ajax({
                        type: "POST",
                        url: 'http://10.11.210.63:8000/sso/disconnect_user',
                        data: {userId : userId},
                        success: function(data){
                            if(jQuery.isEmptyObject(data)){
                                BootstrapDialog.alert("Disconnect user " + userName +  " success!");
                                table.ajax.reload();
                                $('#user-cancel-button').click();
                            }else if('error' in data){
                                errorAlert(data['error']);
                            }
                        }
                    });
                }
            }
        });
    });

    $('#user-reset-button').on('click', function(){
        enableUserButtons();
        $('#user-cancel-button').click();
    });

    function disableUserButtons(){
        $('.user-button').prop('disabled', true);
    }

    function enableUserButtons(){
        $('.user-button').prop('disabled', false);
    }

    function disableGroupButtons(){
        $('.group-button').prop('disabled', true);
    }

    function enableGroupButtons(){
        $('.group-button').prop('disabled', false);
    }

    //evnet handlers for group management
    $('#group-create-button').on('click', function(){
        if($('#group-create-button').val() == 'Create'){
            $('#group-cancel-button').click();
            $('#group-create-button').val('Save');
            $('#group-cancel-button').removeClass('hide');
            $('#group-delete-button').prop('disabled', true);
        }else if($('#group-create-button').val() == 'Save'){
            BootstrapDialog.confirm({
                message: 'You\'re going to create group ' + $('#group-name').val() + ', are you sure?',
                type: BootstrapDialog.TYPE_WARNING,
                callback : function(result){
                    if(result) {
                        $.ajax({
                            type: "POST",
                            url: 'http://10.11.210.63:8000/sso/create_group_for_organism',
                            data: {oname : $('#group-name').val()},
                            success: function(data){
                                if(jQuery.isEmptyObject(data)){
                                    table_group.ajax.reload();
                                    loadAllGroups();
                                }else if('error' in data){
                                    errorAlert(data['error']);
                                }
                            }
                        });
                    }
                }
            });
        }
    });

    $('#group-cancel-button').on('click', function(){
        $('#group-name').val('');
        $('#group-create-button').val('Create');
        $('#group-cancel-button').addClass('hide');
        enableGroupButtons();
        $('#group-admin-name').text('');
        $('#group-user-name').text('');
        $('#check-organism-icon').removeClass();
    });

    $('#group-reset-button').on('click', function(){
        $('#group-organism-icon')
        $('#group-cancel-button').click();
    });

    $('#group-delete-button').on('click', function(){
        if(typeof(table_group.row(table_group.$('tr.selected')).index()) == 'undefined')return;

        oid = table_group.cell(table_group.row(table_group.$('tr.selected')).index(),3).data();
        BootstrapDialog.confirm({
            message: 'You\'re going to delete group ' + oid + ', are you sure?',
            type: BootstrapDialog.TYPE_WARNING,
            callback : function(result){
                if(result) {
                    $.ajax({
                        type: "POST",
                        url: 'http://10.11.210.63:8000/sso/delete_group_for_organism',
                        data: {oname : $('#group-name').val(), oid : oid},
                        success: function(data){
                            if(jQuery.isEmptyObject(data)){
                                table_group.ajax.reload();
                                $('#group-cancel-button').click();
                                loadAllGroups();
                            }else if('error' in data){
                                errorAlert(data['error']);
                            }
                        }
                    });
                }
            }
        });
    });


    $('#group-adduser-button').on('click', function(){
        if($('#tags').val() == ''){return;}
        if(typeof(table_group.row(table_group.$('tr.selected')).index()) == 'undefined')return;
        userName = $('#tags').val();
        groupName = table_group.cell(table_group.row(table_group.$('tr.selected')).index(),0).data();
        $('.group-member-button').addClass('disabled');
        BootstrapDialog.confirm({
            message: 'You\'re going to grant user ' + userName + 'into  group ' + groupName + ', are you sure?',
            type: BootstrapDialog.TYPE_WARNING,
            callback : function(result){
                if(result) {
                    $.ajax({
                        type: "POST",
                        url: 'http://10.11.210.63:8000/sso/add_user_to_group',
                        data: {groupName : groupName, userName : userName},
                        success: function(data){
                            is_grouptable_finish_load = false;
                            table_group.ajax.reload();
                            timer_groupTable = setInterval(function(){func_timer_groupTable(groupName)}, 10);

                            if(jQuery.isEmptyObject(data)){
                                $('#tags').val('');
                                $('#group-adduser-button').prop('disabled', true);
                                $('.group-member-button').removeClass('disabled');
                            }else if('error' in data){
                                errorAlert(data['error']);
                            }
                        }
                    });
                }
            }
        });

    });


    //debounce setting
    var checkDjangoUserProgram = _.debounce(function () {
        disableUserButtons();
        if($('#django-user-name').val() == ''){
            enableUserButtons();
            if($('#group-create-button').val('') == 'Create'){
                $('#user-update-button').prop('disabled', false);
                $('#user-delete-button').prop('disabled', false);
                $('#user-disconnect-button').prop('disabled', false);
            }
            $('#check-django-user-icon').removeClass();
            return true;
        }

        $.ajax({
            type: "POST",
            url: 'http://10.11.210.63:8000/sso/check_django_user_available',
            data: {userName : $('#django-user-name').val()},
            success: function(data){
                $('#check-django-user-icon').removeClass();
                if(jQuery.isEmptyObject(data)){
                    $('#check-django-user-icon').addClass("fa fa-check");
                    enableUserButtons();
                }else if('error' in data){
                    $('#check-django-user-icon').addClass("fa fa-close");
                }
            }
        });
    }, 200);

    $('#django-user-name').keyup(checkDjangoUserProgram);

    var organismToGroups = _.debounce(function () {
        disableGroupButtons();
        if($('#group-name').val() == ''){
            enableGroupButtons();
            $('#check-organism-icon').removeClass();
            return true;
        }

        $.ajax({
            type: "POST",
            url: 'http://10.11.210.63:8000/sso/check_organism_exist',
            data:{oname : $('#group-name').val()},
            success: function(data){
                $('#check-organism-icon').removeClass();
                if(jQuery.isEmptyObject(data)){
                    var organismName = $('#group-name').val().toUpperCase();
                    $('#group-admin-name').text('GROUP_'+organismName+'_ADMIN');
                    $('#group-user-name').text('GROUP_'+organismName+'_USER');
                    $('#check-organism-icon').addClass("fa fa-check");
                    enableGroupButtons();
                    $('#group-delete-button').prop('disabled', true);
                }else if('error' in data){
                    $('#group-admin-name').text('');
                    $('#group-user-name').text('');
                    $('#check-organism-icon').addClass("fa fa-close");
                }
            }
        });
    }, 200);

    $('#group-name').keyup(organismToGroups);

    var checkApolloUserProgram = _.debounce(function () {
        $('#group-adduser-button').prop('disabled', true);
        if((availableUsers.indexOf($('#tags').val()) > -1)){
            $('#group-adduser-button').prop('disabled', false);
        }
    }, 30);

    $('#tags').keyup(checkApolloUserProgram);

    $( "#tags" ).autocomplete({
        source: function(request, response) {
            var results = $.ui.autocomplete.filter(availableUsers, request.term);
            response(results.slice(0, 10));
        }
    });

    $.ui.autocomplete.filter = function (array, term) {
        var matcher = new RegExp("^" + $.ui.autocomplete.escapeRegex(term), "i");
        return $.grep(array, function (value) {
                return matcher.test(value.label || value.value || value);
        });
    };
} );
