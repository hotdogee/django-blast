$(function () { // document ready
    // Suggest short name from display name
    // text change event
    $('#id_display_name').keyup(function () {
        var name = $('#id_display_name').val().toLowerCase().replace(/^\s+|\s+$/g, '');
        if (name.length == 0)
            return;
        var tokens = name.split(/\s+/);
        var token_count = tokens.length;
        var short_name = '';
        if (token_count == 1) {
            short_name = tokens[0].substr(0, 6);
        } else if (token_count > 1) {
            short_name = tokens[0].substr(0, 3) + tokens.pop().substr(0, 3);
        }
        if (!$('#id_short_name').data('userModified'))
            $('#id_short_name').val(short_name);
    });
    $('#id_short_name').keyup(function () {
        if ($('#id_short_name').val().length > 0) {
            $('#id_short_name').data('userModified', true);
        } else {
            $('#id_short_name').data('userModified', false);
        }
    });
    // Get NCBI taxonomy id
    $('#id_display_name').change(function () {
        var name = $('#id_display_name').val().toLowerCase().replace(/^\s+|\s+$/g, '');
        $.ajax({
            url: 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi',
            data: {
                db: 'taxonomy',
                term: name,
                retmode: 'json',
            }
        }).done(function (data) {
            //console.log(data['esearchresult']['idlist']);
            $('#id_tax_id').val(data['esearchresult']['idlist'][0])
        });
    });
    // Get description from wikipedia
    $('#id_display_name').change(function () {
        var name = $('#id_display_name').val().toLowerCase().replace(/^\s+|\s+$/g, '');
        $.getJSON('http://en.wikipedia.org/w/api.php?action=query&list=search&srprop=snippet&srlimit=1&format=json&callback=?&srsearch=' + name, function (data) {
            //console.log(data['query']['search']);
            if (data['query']['search'].length > 0) {
                $.getJSON('http://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&exintro=true&callback=?&titles=' + data['query']['search'][0]['title'], function (data) {
                    //console.log(data['query']['pages']);
                    var keys = Object.keys(data['query']['pages']);
                    if (keys.length > 0) {
                        $('#id_description').val($(data['query']['pages'][keys[0]]['extract']).text());
                        // data['query']['search'][keys(data['query']['pages'])[0]]['extract']
                    }
                });
            }
        });
        //$.ajax({
        //    url: 'https://en.wikipedia.org/w/api.php',
        //    data: { // action=query&list=search&srprop=snippet&srlimit=1&format=json&srsearch=Anoplophora%20glabripennis
        //        action: 'query',
        //        list: 'search',
        //        srsearch: name,
        //        srprop: '',
        //        srlimit: '1',
        //        format: 'json'
        //    }
        //}).done(function (data) {
        //    console.log(data['query']['search']);
        //    if (data['query']['search'].length > 0) {
        //        $.ajax({ // action=query&prop=extracts&format=json&exintro=true&titles=Asian%20long-horned%20beetle
        //            url: 'https://en.wikipedia.org/w/api.php',
        //            data: {
        //                action: 'query',
        //                prop: 'extracts',
        //                format: 'json',
        //                exintro: '',
        //                titles: data['query']['search'][0]['title']
        //            }
        //        }).done(function (data) {
        //            console.log(data['query']['search']);
        //            if (keys(data['query']['pages']).length > 0) {
        //                $('#id_description').val(data['query']['search'][keys(data['query']['pages'])[0]]['extract']);
        //                // data['query']['search'][keys(data['query']['pages'])[0]]['extract']
        //            }
        //        });
        //    }
        //});
    });
});