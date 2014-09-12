(function () {
    function decimalAdjust(type, value, exp) {
        // If the exp is undefined or zero...
        if (typeof exp === 'undefined' || +exp === 0) {
            return Math[type](value);
        }
        value = +value;
        exp = +exp;
        // If the value is not a number or the exp is not an integer...
        if (isNaN(value) || !(typeof exp === 'number' && exp % 1 === 0)) {
            return NaN;
        }
        // Shift
        value = value.toString().split('e');
        value = Math[type](+(value[0] + 'e' + (value[1] ? (+value[1] - exp) : -exp)));
        // Shift back
        value = value.toString().split('e');
        return +(value[0] + 'e' + (value[1] ? (+value[1] + exp) : exp));
    }
    // Decimal round
    if (!Math.round10) {
        Math.round10 = function (value, exp) {
            return decimalAdjust('round', value, exp);
        };
    }
    // Decimal floor
    if (!Math.floor10) {
        Math.floor10 = function (value, exp) {
            return decimalAdjust('floor', value, exp);
        };
    }
    // Decimal ceil
    if (!Math.ceil10) {
        Math.ceil10 = function (value, exp) {
            return decimalAdjust('ceil', value, exp);
        };
    }
})();
$(function () { // document ready
    //////////////////
    // Prepare Data //
    //////////////////
    // convert arrays to objects
    //var results_db = _.map(results_data, function (row) { return _.object(results_col_names, row); });
    var col_idx = _.object(results_col_names, _.range(results_col_names.length));
    ////////////
    // Layout //
    ////////////
    $("#top-side-by-side-container").kendoSplitter({
        panes: [
            { collapsible: false, size: '50%' },
            { collapsible: true }
        ]
    });
    ////////////////
    // CodeMirror //
    ////////////////
    var code_mirror = CodeMirror($('#text-report')[0], {
        value: results_detail,
        theme: 'xq-light',
        tabSize: 2,
        lineNumbers: true,
        styleActiveLine: true,
        readOnly: true,
        viewportMargin: 15,
        gutters: ["CodeMirror-linenumbers"]
    });
    ///////////////////
    // Results Table //
    ///////////////////
    var toolbar_prefix = 'fg-toolbar ui-toolbar ui-widget-header ui-helper-clearfix ui-corner-';
    var index_of_blastdb = col_idx['blastdb']; // -1 if not present
    var index_of_sseqid = col_idx['sseqid']; // -1 if not present
    var fixedColumns = 2;
    // add header and footer for jbrowse if index != -1
    if (index_of_blastdb != -1) {
        $('#results-table thead tr').append('<th></th>');
        $('#results-table tfoot tr').append('<th></th>');
        fixedColumns = 3;
    }
    var $results_table = $('#results-table').dataTable({
        scrollX: '100%',
        scrollY: '200px',
        dom:
            '<"' + toolbar_prefix + 'tl ui-corner-tr"Rifr>' +
            't' +
            '<"' + toolbar_prefix + 'bl ui-corner-br"<"btn-download btn-group dropup">T>S',
        //dom: 'Rifrt<"btn-group dropup">S',
        //"dom": 'T<"clear">lfrtip',
        //deferRender: true,
        //bJQueryUI: true,
        tableTools: {
            sRowSelect: "os",
            aButtons: [],
        },
        colReorder: {
            fixedColumns: fixedColumns,
            realtime: true,
            stateSave: true
        },
        order: [[ col_idx['qseqid'], 'asc' ]],
        //responsive: true,
        data: results_data,
        columns: _.map(results_col_names, function (name) {
            col = {
                'title': name,
                'name': name.toLowerCase().replace(' ', '-')
            };
            if (name == 'blastdb') {
                col['orderable'] = false;
                col['type'] = 'choice';
                col['className'] = 'center-cell';
                col['render'] = function (dbtitle, type, row, meta) {
                    if (type == "display") {
                        var sseqid = row[index_of_sseqid];
                        if (/\|\w\w\w\w\w\w_([^|]+)$/g.exec(sseqid) != null)
                            //>gnl|Ceratitis_capitata|cercap_Scaffold1
                            sseqid = /\|[^|_]+?_([^|]+)$/g.exec(sseqid)[1];
                        else if (/\|([^|]+)$/.exec(sseqid) != null)
                            //>gnl|Drosophila_ficusphila_transcript_v0.5.3|DFIC013799-RA
                            sseqid = /\|([^|]+)$/.exec(sseqid)[1];
                        if (dbtitle in results_info['db_url']) {
                            var start_pos = row[col_idx['sstart']];
                            var end_pos = row[col_idx['send']];
                            if (end_pos < start_pos)
                                end_pos = [start_pos, start_pos = end_pos][0];
                            start_pos -= 200;
                            if (start_pos < 0)
                                start_pos = 0;
                            end_pos += 200;
                            if (end_pos > row[col_idx['slen']])
                                end_pos = row[col_idx['slen']];
                            return '<a class="btn btn-primary btn-xs" data-toggle="tooltip" data-placement="right" data-container="body" title="' + dbtitle + '\nClick to view in genome browser" target="_blank" href=\'' + results_info['db_url'][dbtitle] + '?loc=' + sseqid + ':' + start_pos + '..' + end_pos + '&addStores={"url":{"type":"JBrowse/Store/SeqFeature/GFF3","urlTemplate":"' + /^(https?:\/\/)/g.exec(results_info['db_url'][dbtitle])[1] + /https?:\/\/(.+)\/blast/g.exec(document.URL)[1] + '/media/blast/task/' + task_id + '/' + dbtitle + '.gff"}}&addTracks=[{"label":"BLAST+ Results","category":"0. Reference Assembly","type":"WebApollo/View/Track/DraggableHTMLFeatures","store":"url","style":{"renderClassName":"gray-center-10pct","subfeatureClasses":{"match_part":"blast-match_part"}}}]&tracks=BLAST+ Results\' role="button"><span class="glyphicon glyphicon-new-window"></span> ' + results_info['db_organism'][dbtitle] + '</a>';
                            //http://gmod-dev.nal.usda.gov:8080/anogla/jbrowse/?loc=Scaffold1:107901..161900&addStores={"url":{"type":"JBrowse/Store/SeqFeature/GFF3","urlTemplate":"http://gmod-dev.nal.usda.gov/media/07b73d9a3dde4eac9faa9c4109f7cfb6/Agla_Btl03082013.genome_new_ids.fa.gff"}}&addTracks=[{"label":"BLAST+ Results","category":"0. Reference Assembly","type":"JBrowse/View/Track/CanvasFeatures","store":"url","glyph":"JBrowse/View/FeatureGlyph/ProcessedTranscript","subParts":"match_part","style":{"color":"blue","height":6,"connectorColor":"gray","connectorThickness":2}}]
                        } else {
                            return '<span data-toggle="tooltip" data-placement="right" title="' + dbtitle + '">' + results_info['db_organism'][dbtitle] + '</span>';
                        }
                    }
                    return dbtitle;
                }
            } else if (name == 'sseqid') {
                col['render'] = function (sseqid, type, row, meta) {
                    if (type == "display") {
                        if (/\|\w\w\w\w\w\w_([^|]+)$/g.exec(sseqid) != null)
                            //>gnl|Ceratitis_capitata|cercap_Scaffold1
                            sseqid = /\|[^|_]+?_([^|]+)$/g.exec(sseqid)[1];
                        else if (/\|([^|]+)$/.exec(sseqid) != null)
                            //>gnl|Drosophila_ficusphila_transcript_v0.5.3|DFIC013799-RA
                            sseqid = /\|([^|]+)$/.exec(sseqid)[1];
                        var idx = meta.row;
                        //if (idx == 1)
                        //    console.log('col["render"](' + sseqid + ')');
                        return sseqid;
//                        return '<span>' + sseqid + '\
//<button class="btn btn-primary btn-xs btn-fasta pull-right" data-toggle="modal" data-target="#fasta-model-' + idx + '" data-remote="">\
//    <span class="glyphicon glyphicon-chevron-right"></span> FASTA\
//</button></span>\
//<div class="modal fade" id="fasta-model-' + idx + '" tabindex="-1" role="dialog" aria-labelledby="fasta-model-' + idx + '-label" aria-hidden="true">\
//  <div class="modal-dialog">\
//    <div class="modal-content">\
//      <div class="modal-header">\
//        <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>\
//        <h4 class="modal-title" id="fasta-model-' + idx + '-label">FASTA Sequences</h4>\
//      </div>\
//      <div class="modal-body">\
//        Fetching FASTA Sequence...\
//      </div>\
//      <div class="modal-footer">\
//        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>\
//      </div>\
//    </div>\
//  </div>\
//</div>\
//';
                    }
                    return sseqid;
                }
            }
            return col;
        }),
        headerCallback: function (thead, data, start, end, display) {
            $(thead).find('th').each(function (index) {
                $(this).children().tooltip('destroy'); // remove old tooltip
                $(this).html('<a data-toggle="tooltip" data-placement="top" data-container="body" title="' + results_col_names_display[col_idx[$(this).text()]] + '"><span>' + results_col_names[col_idx[$(this).text()]] + '</span></a>');
                $(this).children().tooltip();
            });
        },
        rowCallback: function (row, data) {
            var $blastdb_td = $('td', row).eq(index_of_blastdb); // .addClass('center-cell')
            $blastdb_td.children().tooltip();
        }
    });
    var results_table_api = $results_table.api(); // $('#results-table').DataTable()
    //results_table_api.columns.adjust().draw();
    // Download button menu
    var task_path = /(https?:\/\/.+)\/blast/g.exec(document.URL)[1] + '/media/blast/task/' + task_id + '/' + task_id;
    $('.btn-download').html('<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">\
<span class="glyphicon glyphicon-download"></span> Download <span class="caret"></span>\
</button>\
<ul class="dropdown-menu" role="menu">\
    <li><a href="' + task_path + '.0"><span class="glyphicon glyphicon-file"></span> Pairwise</a></li>\
    <li><a href="' + task_path + '.1"><span class="glyphicon glyphicon-file"></span> Query-anchored showing identities</a></li>\
    <li><a href="' + task_path + '.3"><span class="glyphicon glyphicon-file"></span> Flat query-anchored, show identities</a></li>\
    <li><a href="' + task_path + '.xml"><span class="glyphicon glyphicon-file"></span> XML</a></li>\
    <li><a href="' + task_path + '.tsv"><span class="glyphicon glyphicon-file"></span> Tabular</a></li>\
    <li><a href="' + task_path + '.csv"><span class="glyphicon glyphicon-file"></span> CSV</a></li>\
    <li><a href="' + task_path + '.asn"><span class="glyphicon glyphicon-file"></span> BLAST archive format (ASN.1)</a></li>\
</ul>')
    var filters = {};
    // Add per column filter input elements to tfoot
    $('.dataTables_scrollFoot tfoot th').each(function (i) {
        var col_setting = results_table_api.settings()[0].aoColumns[i];
        var type = col_setting.sType
        var id = 'results-table-' + i + '-filter';
        var title = col_setting.sName || id;
        if (type == 'choice') { // blastdb
            var db_list = results_table_api.column(i).data().unique().sort();
            var select = $('<select id="' + id + '" class="selectpicker dropup show-menu-arrow" data-style="btn-sm btn-default" data-width="91px" multiple data-live-search="true" data-actions-box="true" multiple data-selected-text-format="count" data-count-selected-text="{0} of {1}" title="Filter" data-icon="icon-filter" data-size="10"></select>')
            .appendTo($(this).empty())
            .on('change', function () {
                // build search string '|'.join
                var $toggle = $('#' + id + '+.bootstrap-select .dropdown-toggle');
                var $title = $('#' + id + '+.bootstrap-select .title');
                var selected_options = $('#' + id + ' option:selected').map(function () { return this.value; }).get();
                $title.text(selected_options.length + ' of ' + db_list.length);
                if (selected_options.length == db_list.length) {
                    $toggle.removeClass('btn-success');
                    results_table_api.column(i).search('', true, false).draw();
                } else {
                    $toggle.addClass('btn-success');
                    results_table_api.column(i).search(selected_options.join('|') || '^$', true, false).draw();
                }
            });
            db_list.each(function (d, j) {
                select.append('<option selected value="' + d + '">' + d + '</option>')
            });
            select.selectpicker();
        } else if (title == 'evalue') {
            //var is_last_col = i == col_idx.length - 1;
            // use log slider for evalue
            var data = results_table_api.column(i).data();
            var min = _.min(data);
            var max = _.max(data);
            var min_log = min;
            var max_log = max;
            // remove 0
            if (max == 0) { // all 0
                min_log = -324;
                max_log = -324; // Math.pow(10, -324) == 0
            } else if (min == 0) {
                //Math.ceil(Math.log(1e-323) / Math.log(10))
                min_log = _.min(_.filter(data, function (num) { return num != 0; }));
                min_log = Math.ceil(Math.log(min_log) / Math.log(10)) - 1;
                max_log = Math.ceil(Math.log(max) / Math.log(10));
            } else {
                min_log = Math.ceil(Math.log(min) / Math.log(10)) - 1;
                max_log = Math.ceil(Math.log(max) / Math.log(10));
            }
            min = 0;
            max = Math.round10(Math.pow(10, max_log), max_log);
            var input = $('<div class="btn-group dropup show-menu-arrow">\
<button id="' + id + '-toggle" type="button" class="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown">\
<span class="glyphicon glyphicon-filter">\
</span>\
<span class="caret">\
</span>\
<span class="sr-only">Toggle Dropdown</span>\
</button>\
<div class="dropdown-menu range-filter" role="menu"><div class="arrow"></div>\
<div class="popover-title">' + title + ' filter</div>\
<div class="input-group label-row">\
<label for="' + id + '-input-min">Min</label>\
<div class="input-group-addon"></div>\
<label for="' + id + '-input-max">Max</label></div>\
<div class="input-group">\
<input id="' + id + '-input-min" type="text" class="form-control col-search-input-min ' + title + '" placeholder="Min"/>\
<div class="input-group-addon">-</div>\
<input id="' + id + '-input-max" type="text" class="form-control col-search-input-max ' + title + '" placeholder="Max"/>\
</div><br>\
<div id="' + id + '-slider" class="slider"></div>\
</div></div>').appendTo($(this).empty());
            var $toggle = $('#' + id + '-toggle');
            var $slider = $('#' + id + '-slider');
            var $input_min = $('#' + id + '-input-min');
            var $input_max = $('#' + id + '-input-max');
            filters['min_' + i] = {
                'enabled': false,
                'filter': function (rd) {
                    var i_min = $input_min.val() * 1;
                    var val = rd[i] * 1;
                    if (!_.isNaN(val) && (_.isNaN(i_min) || i_min <= val))
                        return true;
                    else
                        return false;
                }
            };
            filters['max_' + i] = {
                'enabled': false,
                'filter': function (rd) {
                    var i_max = $input_max.val() * 1;
                    var val = rd[i] * 1;
                    if (!_.isNaN(val) && (_.isNaN(i_max) || i_max >= val))
                        return true;
                    else
                        return false;
                }
            };
            var draw_table = function () {
                if ($input_min.val() == min)
                    filters['min_' + i]['enabled'] = false;
                else
                    filters['min_' + i]['enabled'] = true;
                if ($input_max.val() == max)
                    filters['max_' + i]['enabled'] = false;
                else
                    filters['max_' + i]['enabled'] = true;
                if ($input_min.val() == min && $input_max.val() == max) {
                    $toggle.removeClass('btn-success');
                } else {
                    $toggle.addClass('btn-success');
                }
                results_table_api.draw();
            }
            $slider.slider({
                range: true,
                min: min_log,
                max: max_log,
                values: [min_log, max_log],
                change: function (event, ui) {
                    draw_table();
                },
                slide: function (event, ui) {
                    // check for 0
                    if (ui.values[0] == min_log)
                        $input_min.val(0);
                    else
                        $input_min.val(Math.round10(Math.pow(10, ui.values[0]), ui.values[0]));
                    $input_max.val(Math.round10(Math.pow(10, ui.values[1]), ui.values[1]));
                    //console.log(ui.values[0], Math.round10(Math.pow(10, ui.values[0]), ui.values[0]), ui.values[1], Math.round10(Math.pow(10, ui.values[1]), ui.values[1]));
                }
            });
            $input_min.val(min);
            $input_max.val(max);
            $input_min.on('keyup', function () {
                var i_min = $input_min.val() * 1;
                var i_max = $input_max.val() * 1;
                if (!_.isNaN(i_min) && min <= i_min && i_max >= i_min) {
                    $slider.slider("values", 0, Math.log(i_min) / Math.log(10));
                }
            });
            $input_min.on('change', function () {
                var i_min = $input_min.val() * 1;
                var i_max = $input_max.val() * 1;
                if (!_.isNaN(i_min) && $input_min.val() != '') {
                    if (i_min > i_max)
                        i_min = i_max;
                    else if (i_min < min)
                        i_min = min;
                    $input_min.val(i_min);
                    $slider.slider("values", 0, Math.log(i_min) / Math.log(10));
                } else {
                    $input_min.val(min);
                    $slider.slider("values", 0, min_log);
                }
            });
            $input_max.on('keyup', function () {
                var i_min = $input_min.val() * 1;
                var i_max = $input_max.val() * 1;
                if (!_.isNaN(i_max) && i_min <= i_max && max >= i_max) {
                    $slider.slider("values", 1, Math.log(i_max) / Math.log(10));
                }
            });
            $input_max.on('change', function () {
                var i_min = $input_min.val() * 1;
                var i_max = $input_max.val() * 1;
                if (!_.isNaN(i_max) && $input_max.val() != '') {
                    if (i_max < i_min)
                        i_max = i_min;
                    else if (i_max > max)
                        i_max = max;
                    $input_max.val(i_max);
                    $slider.slider("values", 1, Math.log(i_max) / Math.log(10));
                } else {
                    $input_max.val(max);
                    $slider.slider("values", 1, max_log);
                }
            });
        } else if (type == 'num') {
            //var is_last_col = i == col_idx.length - 1;
            var data = results_table_api.column(i).data();
            var min = Math.floor(_.min(data));
            var max = Math.ceil(_.max(data));
            var input = $('<div class="btn-group dropup show-menu-arrow">\
<button id="' + id + '-toggle" type="button" class="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown">\
<span class="glyphicon glyphicon-filter">\
</span>\
<span class="caret">\
</span>\
<span class="sr-only">Toggle Dropdown</span>\
</button>\
<div class="dropdown-menu range-filter" role="menu"><div class="arrow"></div>\
<div class="popover-title">' + title + ' filter</div>\
<div class="input-group label-row">\
<label for="' + id + '-input-min">Min</label>\
<div class="input-group-addon"></div>\
<label for="' + id + '-input-max">Max</label></div>\
<div class="input-group">\
<input id="' + id + '-input-min" type="number" min="' + min + '" max="' + max + '" class="form-control col-search-input-min ' + title + '" placeholder="Min" />\
<div class="input-group-addon">-</div>\
<input id="' + id + '-input-max" type="number" min="' + min + '" max="' + max + '" class="form-control col-search-input-max ' + title + '" placeholder="Max" />\
</div><br>\
<div id="' + id + '-slider" class="slider"></div>\
</div></div>').appendTo($(this).empty());
            var $toggle = $('#' + id + '-toggle');
            var $slider = $('#' + id + '-slider');
            var $input_min = $('#' + id + '-input-min');
            var $input_max = $('#' + id + '-input-max');
            filters['min_' + i] = {
                'enabled': false,
                'filter': function (rd) {
                    var i_min = $input_min.val() * 1;
                    var val = rd[i] * 1;
                    if (!_.isNaN(val) && (_.isNaN(i_min) || i_min <= val))
                        return true;
                    else
                        return false;
                }
            };
            filters['max_' + i] = {
                'enabled': false,
                'filter': function (rd) {
                    var i_max = $input_max.val() * 1;
                    var val = rd[i] * 1;
                    if (!_.isNaN(val) && (_.isNaN(i_max) || i_max >= val))
                        return true;
                    else
                        return false;
                }
            };
            var draw_table = function () {
                if ($input_min.val() == min)
                    filters['min_' + i]['enabled'] = false;
                else
                    filters['min_' + i]['enabled'] = true;
                if ($input_max.val() == max)
                    filters['max_' + i]['enabled'] = false;
                else
                    filters['max_' + i]['enabled'] = true;
                if ($input_min.val() == min && $input_max.val() == max) {
                    $toggle.removeClass('btn-success');
                } else {
                    $toggle.addClass('btn-success');
                }
                results_table_api.draw();
            }
            $slider.slider({
                range: true,
                min: min,
                max: max,
                values: [min, max],
                change: function (event, ui) {
                    draw_table();
                },
                slide: function (event, ui) {
                    $input_min.val(ui.values[0]);
                    $input_max.val(ui.values[1]);
                }
            });
            $input_min.val(min);
            $input_max.val(max);
            $input_min.on('keyup', function () {
                var i_min = $input_min.val() * 1;
                var i_max = $input_max.val() * 1;
                if (!_.isNaN(i_min) && min <= i_min && i_max >= i_min) {
                    $slider.slider("values", 0, i_min);
                }
            });
            $input_min.on('change', function () {
                var i_min = $input_min.val() * 1;
                var i_max = $input_max.val() * 1;
                if (!_.isNaN(i_min) && $input_min.val() != '') {
                    if (i_min > i_max)
                        i_min = i_max;
                    else if (i_min < min)
                        i_min = min;
                    $input_min.val(i_min);
                    $slider.slider("values", 0, i_min);
                } else {
                    $input_min.val(min);
                    $slider.slider("values", 0, min);
                }
            });
            $input_max.on('keyup', function () {
                var i_min = $input_min.val() * 1;
                var i_max = $input_max.val() * 1;
                if (!_.isNaN(i_max) && i_min <= i_max && max >= i_max) {
                    $slider.slider("values", 1, i_max);
                }
            });
            $input_max.on('change', function () {
                var i_min = $input_min.val() * 1;
                var i_max = $input_max.val() * 1;
                if (!_.isNaN(i_max) && $input_max.val() != '') {
                    if (i_max < i_min)
                        i_max = i_min;
                    else if (i_max > max)
                        i_max = max;
                    $input_max.val(i_max);
                    $slider.slider("values", 1, i_max);
                } else {
                    $input_max.val(max);
                    $slider.slider("values", 1, max);
                }
            });
        } else {
            var input = $('<div id="' + id + '" class="input-group"><div class="input-group-addon input-sm"><span class="glyphicon glyphicon-search"></div><input type="text" class="form-control input-sm col-search-input ' + title + '" placeholder="' + title + ' filter" /></div></div>').appendTo($(this).empty());
            $('input', input).on('keyup change', function () {
                //console.log(colIdx);
                if (this.value == '') {
                    $('#' + id).removeClass('has-success');
                } else {
                    $('#' + id).addClass('has-success');
                }
                results_table_api.column(i).search(this.value).draw();
            });
        }
        $(this).addClass('center-cell');
    });
    $("#result-container").kendoSplitter({
        orientation: "vertical",
        panes: [
            { collapsible: true, size: '38%' },
            { collapsible: false }
        ]
    });
    $results_table.dataTableExt.afnFiltering.push(
        function (oSettings, aData, iDataIndex) {
            return _.every(_.map(_.filter(filters, function (f) { return f['enabled']; }), function (f, key) { return f['filter'](this); }, aData));
        }
    );
    // Fix input element click problem
    $('.dropdown-menu.range-filter').click(function (e) {
        e.stopPropagation();
    });
    //}).yadcf([{
    //    column_number: 0,
    //    filter_type: "multi_select"
    //}, {
    //    column_number: 1,
    //    filter_type: "multi_select"
    //}, {
    //    column_number: 2,
    //    filter_type: "range_number"
    //}]);
    /*
     * Table resize events
     */
    // Calculate dataTables_scrollBody height
    var $table_container = $('#table-container');
    var $ui_corner_tr = $('.ui-corner-tr');
    var $ui_corner_br = $('.ui-corner-br');
    var $dataTables_scrollHead = $('.dataTables_scrollHead');
    var $dataTables_scrollBody = $('.dataTables_scrollBody');
    var $dataTables_scrollFoot = $('.dataTables_scrollFoot');
    function updateDataTableHeight() {
        // table_panel_div - top_bar - bottom_bar - table_header
        var h = $table_container.height() - $ui_corner_tr.outerHeight() - $ui_corner_br.outerHeight() - $dataTables_scrollHead.outerHeight() - $dataTables_scrollFoot.outerHeight();
        $dataTables_scrollBody.css('height', h);
        // trigger dataTables.scroller to recalculate how many rows its showing
        $(window).trigger('resize.DTS');
    };
    // Draw initial graph with first row
    var row_data = results_table_api.row(0).data();
    // initial update, wait till core-splitter loads
    var cm = code_mirror;
    // text result event setup
    cm.on('cursorActivity', function () {
        //console.log('cm.getCursor() = ' + cm.getCursor().line);
        var filtered = results_info['line_num_list'].filter(function (i) { return i <= cm.getCursor().line + 3 });
        var i = 0;
        if (filtered.length > 0)
            i = filtered.length - 1;
        //console.log(i);
        // get row
        var row = results_table_api.row(i);
        row_data = row.data();
        renderAlignmentGraph('query-canvas', row_data);
        renderAlignmentGraph('subject-canvas', row_data);
        // is filtered?
        // Get data as ordered and filtered in datatable
        var table_data = results_table_api.rows({ search: 'applied' }).data();
        var i = _.indexOf(table_data, row_data);
        results_table_api.scroller().scrollToRow(i, false);
        $(results_table_api.rows().nodes()).removeClass('highlight');
        var $row = $(results_table_api.rows({ search: 'applied' }).nodes()[i]);
        $row.addClass('highlight');
    })
    // only the horizontal-splitter changes height, track event defined by polymer
    $("#result-container").data("kendoSplitter").bind('resize', function () {
        updateDataTableHeight();
    });
    // Active rows
    var oTT = TableTools.fnGetInstance('results-table');
    var active_rows = [];
    $results_table.on('click', 'tr', function () {
        active_rows = oTT.fnGetSelectedIndexes();
        console.log(active_rows);
    });
    /*
     * data row mouse over event
     */
    $results_table.addClass('table-hover');
    $results_table.on('mouseover', 'tr', function () {
        $(results_table_api.rows().nodes()).removeClass('highlight');
        // get row data and convert to object
        //row_data = _.object(results_col_names, results_table_api.row(this).data());
        var this_row = results_table_api.row(this);
        row_data = this_row.data();
        //console.log('mouseover: row_data = ' + row_data);
        renderAlignmentGraph('query-canvas', row_data);
        renderAlignmentGraph('subject-canvas', row_data);
        cm.operation(function () {
            cm.scrollIntoView({ line: results_info['line_num_list'][this_row.index()], ch: 0 }, cm.getScrollInfo().clientHeight / 2)
            cm.setCursor({ line: results_info['line_num_list'][this_row.index()], ch: 0 })
            cm.curOp.cursorActivityHandlers = false; // don't fire event
        });
        cm.operation(function () {
            //$('.CodeMirror')[0].CodeMirror.scrollTo(0, 2976+551/2-42)
            var info = cm.getScrollInfo();
            cm.scrollTo(0, info.top + info.clientHeight / 2 - 42);
            cm.curOp.cursorActivityHandlers = false; // don't fire event
        });
    });
    // Order event
    var order = results_table_api.order();
    $results_table.on('order.dt', function () {
        //console.log('order.dt');
        //if (_.isEqual(order, results_table_api.order()))
        //    return;
        //renderAlignmentGraph('query-canvas', row_data);
        //renderAlignmentGraph('subject-canvas', row_data);
    });
    // Search event
    $results_table.on('search.dt', function () {
        //console.log('search.dt');
    });
    $results_table.on('draw.dt', function () {
        //console.log('draw.dt');
        renderAlignmentGraph('query-canvas', row_data);
        renderAlignmentGraph('subject-canvas', row_data);
    });
    //$('td').mouseover(function () {
    //    $(this).siblings().css('background-color', '#EAD575');
    //    var ind = $(this).index();
    //    $('td:nth-child(' + (ind + 1) + ')').css('background-color', '#EAD575');
    //});
    //$('td').mouseleave(function () {
    //    $(this).siblings().css('background-color', '');
    //    var ind = $(this).index();
    //    $('td:nth-child(' + (ind + 1) + ')').css('background-color', '');
    //});
    $results_table.on('click', '.btn-fasta', function () {
        $($(this).data("target") + ' .modal-body').html($(this).data("target"));
    });
        
    /////////////////////
    // Alignment Graph //
    /////////////////////
    // Fit canvas to container width and height
    // .width and .height needs to be in pixels
    // .style.width and .style.height only streches the rendered image and doesn't change the render dimensions
    // initial update, wait till core-splitter loads
    var $query_canvas = $('#query-canvas');
    //$query_canvas.width('100%');
    //$query_canvas.height('100%');
    var $query_canvas_container = $query_canvas.parent();
    var $subject_canvas = $('#subject-canvas');
    //$subject_canvas.width('100%');
    //$subject_canvas.height('100%');
    var $subject_canvas_container = $subject_canvas.parent();
    function updateAlignmentGraph() {
        //$query_canvas.attr({ width: $query_canvas_container.outerWidth(), height: $query_canvas_container.outerHeight() });
        //$subject_canvas.attr({ width: $subject_canvas_container.outerWidth(), height: $subject_canvas_container.outerHeight() });
        document.getElementById('query-canvas').height = $query_canvas_container.outerHeight() - 25;
        document.getElementById('subject-canvas').height = $subject_canvas_container.outerHeight() - 25;
        //console.log($query_canvas.outerHeight());
        renderAlignmentGraph('query-canvas', row_data);
        renderAlignmentGraph('subject-canvas', row_data);
    };
    $("#result-container").data("kendoSplitter").bind('resize', function () {
        updateAlignmentGraph()
    });
    $("#top-side-by-side-container").data("kendoSplitter").bind('resize', function () {
        updateAlignmentGraph()
    });
    function renderAlignmentGraph(canvas_name, row_data) {
        // Get Canvas and Create Chart
        var canvas = document.getElementById(canvas_name);
        // Remove all previous events
        var canvasClone = canvas.cloneNode(true);
        canvas.parentNode.replaceChild(canvasClone, canvas);
        canvas = canvasClone;
        // clear canvas
        var ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        var chart = new Scribl(canvas, canvas.width);
        var offset = 45; // so scale text won't get cutoff
        var chart = new Scribl(canvas, canvas.width - offset * 2);
        chart.offset = offset;
        chart.scrollable = true;
        // Change laneSizes and buffers
        chart.laneSizes = 20;
        chart.laneBuffer = 0;
        chart.trackBuffer = 0;
        // change text color		
        chart.glyph.text.color = 'white';

        // Get data indexes
        var other_canvas = canvas_name == 'query-canvas' ? 'subject-canvas' : 'query-canvas';
        var rseqid = canvas_name == 'query-canvas' ? col_idx['qseqid'] : col_idx['sseqid'];
        var rstart = canvas_name == 'query-canvas' ? col_idx['qstart'] : col_idx['sstart'];
        var rend = canvas_name == 'query-canvas' ? col_idx['qend'] : col_idx['send'];
        var sstart = col_idx['sstart'];
        var send = col_idx['send'];
        var bitscore = col_idx['bitscore'];
        // Get data as ordered and filtered in datatable
        var table_data = results_table_api.rows({ search: 'applied' }).data();
        // Filter data, only keep rows associated with the reference given by row_data
        // Set name text
        $('#' + canvas_name + '-name').text(row_data[rseqid]);
        var aligned_data = _.filter(table_data, function (row) {
            // only draw HSPs within the range of 32000nt(+-16000nt)
            var position = row[rend] < row[rstart] ? row[rend] : row[rstart];
            var center_position = row_data[rend] < row_data[rstart] ? row_data[rend] : row_data[rstart];
            return row[rseqid] == row_data[rseqid] && Math.abs(center_position - position) < 16000;
        });
        // draw at most 100 alignments, partition aligned_data if length > 100
        var start = Math.floor(_.indexOf(aligned_data, row_data) / 100) * 100;
        aligned_data = aligned_data.slice(start, start + 100);
        // Sort data ascending by coordinate for draw order
        //var sorted_data = _.sortBy(filtered_data, function (row) { return -row['bitscore']; });

        // draw each hsp row
        _.each(aligned_data, function (row, index, list) {
            var position = row[rend] < row[rstart] ? row[rend] : row[rstart];
            var length = row[rend] < row[rstart] ? row[rstart] - row[rend] : row[rend] - row[rstart];
            var strand = row [send] < row[sstart] ? '-' : '+';
            // Current row color
            var feature = chart.addFeature(new BlockArrow('gene', position, length, strand));
            if (_.isEqual(row, row_data)) {
                feature.setColorGradient(
                    'rgb(252, 213, 181)',
                    'rgb(228, 108, 10)'
                );
            } else {
                // color according to score
                var min_score = 50;
                var max_score = 200;
                var color_bitscore = Math.max(min_score, Math.min(max_score, row[bitscore]));
                var color_scale = (color_bitscore - min_score) / (max_score - min_score);
                // max_color = rgb(30, 74, 117), min_color = rgb(170, 178, 187)
                var r = Math.round(29 - (29 - 22) * color_scale);
                var g = Math.round(114 - (114 - 52) * color_scale);
                var b = Math.round(54 - (54 - 82) * color_scale);
                feature.setColorGradient(
                    ' #99CCFF',
                    'rgb(' + r + ', ' + g + ', ' + b + ')'
                );
            }
            feature.onMouseover = function () {
                renderAlignmentGraph('query-canvas', row);
                renderAlignmentGraph('subject-canvas', row);
                var i = _.indexOf(table_data, row);
                //console.log(i);
                // highlight row
                //.ui-state-highlight
                // scroll to row
                results_table_api.scroller().scrollToRow(i, false);
                $(results_table_api.rows().nodes()).removeClass('highlight');
                var $row = $(results_table_api.rows({ search: 'applied' }).nodes()[i]);
                $row.addClass('highlight');
                cm.operation(function () {
                    cm.scrollIntoView({ line: results_info['line_num_list'][$row.index()], ch: 0 }, cm.getScrollInfo().clientHeight / 2)
                    cm.setCursor({ line: results_info['line_num_list'][$row.index()], ch: 0 })
                    cm.curOp.cursorActivityHandlers = false; // don't fire event
                });
                cm.operation(function () {
                    //$('.CodeMirror')[0].CodeMirror.scrollTo(0, 2976+551/2-42)
                    var info = cm.getScrollInfo();
                    cm.scrollTo(0, info.top + info.clientHeight / 2 - 42);
                    cm.curOp.cursorActivityHandlers = false; // don't fire event
                });
            };
        });
        // Calculate optimal lane size according to current canvas height
        // canvas.height = canvas.getScaleHeight() + canvas.tracks[0].lanes.length * (chart.laneSizes + chart.laneBuffer) + chart.trackBuffer;
        optimal_lane_size = (canvas.height - chart.getScaleHeight() - chart.trackBuffer) / chart.tracks[0].lanes.length - chart.laneBuffer;
        optimal_lane_size = optimal_lane_size < 5 ? 5 : optimal_lane_size > 20 ? 20 : optimal_lane_size;
        chart.laneSizes = optimal_lane_size;
        canvas.height = chart.getHeight();

        // create lane size slider on top right
        var lane_size_slider_id = canvas_name + '-lane-size-slider';
        if (!document.getElementById(lane_size_slider_id)) {
            // Create slider
            var sliderDiv = document.createElement('div');
            sliderDiv.id = lane_size_slider_id;
            sliderDiv.style.margin = '32px 19px'; // avoid overlapping with scrollbars
            sliderDiv.style.position = 'absolute';
            sliderDiv.style.top = '0';
            sliderDiv.style.right = '0';
            canvas.parentNode.insertBefore(sliderDiv, canvas);
        }
        jQuery('#' + lane_size_slider_id).slider({
            orientation: 'vertical',
            range: 'min',
            max: 20,
            min: 5,
            value: chart.laneSizes,
            slide: function (event, ui) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                chart.laneSizes = ui['value'];
                canvas.height = chart.getHeight();
                chart.draw();
            }
        });
        // calculate needed height
        //canvas.height = chart.getHeight();
        // Draw Chart
        chart.draw();
    }
    ////////////
    // Resize //
    ////////////
    var report_panel_width = 777;
    var lazyLayout = _.throttle(function () {
        var w = $(window).width() - report_panel_width
        w = w < report_panel_width ? $(window).width() / 2 : w
        $("#bottom-side-by-side-container").data("kendoSplitter").size(".k-pane:first", w)
        //$table_container.width(w);
        updateDataTableHeight();
        updateAlignmentGraph()
        results_table_api.columns.adjust().draw();
    }, 200, { leading: false });
    $(window).resize(lazyLayout);
    var w = $(window).width() - report_panel_width
    w = w < report_panel_width ? $(window).width() / 2 : w
    $("#bottom-side-by-side-container").kendoSplitter({
        panes: [
            { collapsible: false, size: w },
            { collapsible: true }
        ]
    });
    $table_container.width(w);
    updateDataTableHeight();
    updateAlignmentGraph()
    results_table_api.columns.adjust().draw();
    var footer = $('<p class="nal-footer">2014 - National Agricultural Library</p>');
    $('.ui-corner-bl').append(footer);
    //console.log('checkpoint!');
});
