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
    /////////////////////////
    // Hover and Selection //
    /////////////////////////
    // State variables
    var last_focus_row_index = 0;
    var State = Backbone.Model.extend({
        defaults: {
            'hover': null,
            'selected': []
        },
        focus_row_index: function() {
            var focus_row_index = this.get('hover');
            if (focus_row_index == null) {
                selected = this.get('selected');
                if (selected.length > 0)
                    focus_row_index = selected[0];
                else
                    focus_row_index = last_focus_row_index;
            }
            last_focus_row_index = focus_row_index;
            return focus_row_index;
        }
    });
    var s = new State;
    s.on('change:hover', function (model, value, options) {
        //console.log('change:hover - ' + value);
    });
    s.on('change:selected', function (model, value, options) {
        //console.log('change:selected - ' + value);
    });
    //////////////////
    // BLAST Report //
    //////////////////
    var cm_blast_report = CodeMirror($('#blast-report')[0], {
        value: results_detail,
        theme: 'xq-light',
        tabSize: 2,
        lineNumbers: true,
        styleActiveLine: true,
        readOnly: true,
        viewportMargin: 15,
        gutters: ["CodeMirror-linenumbers"]
    });
    $('#text-tabs a[href="#blast-report"]').on('shown.bs.tab', function (e) {
        cm_blast_report.refresh();
    })
    // Selected line changed event
    cm_blast_report.on('cursorActivity', function (instance) {
        //console.log('cm_blast_report.getCursor() = ' + cm_blast_report.getCursor().line);
        var filtered = results_info['line_num_list'].filter(function (i) { return i <= cm_blast_report.getCursor().line + 3 });
        var i = 0;
        if (filtered.length > 0)
            i = filtered.length - 1;
        s.set({ 'selected': [i] }, { 'set_by': instance });
    })
    function cm_blast_report_select_hsp(row_idx) {
        cm_blast_report.operation(function () {
            cm_blast_report.scrollIntoView({ line: results_info['line_num_list'][row_idx], ch: 0 }, cm_blast_report.getScrollInfo().clientHeight / 2);
            cm_blast_report.setCursor({ line: results_info['line_num_list'][row_idx], ch: 0 });
            cm_blast_report.curOp.cursorActivityHandlers = false; // don't fire event
        });
        cm_blast_report.operation(function () {
            //$('.CodeMirror')[0].CodeMirror.scrollTo(0, 2976+551/2-42)
            var info = cm_blast_report.getScrollInfo();
            cm_blast_report.scrollTo(0, info.top + info.clientHeight / 2 - 42);
            cm_blast_report.curOp.cursorActivityHandlers = false; // don't fire event
        });
    }
    s.on('change:hover', function (model, value, options) {
        if (options.set_by == this)
            return;
        if (value != null)
            cm_blast_report_select_hsp(value);
        else {
            selected = s.get('selected')
            if (selected.length > 0)
                cm_blast_report_select_hsp(selected[0]);
        }
    }, cm_blast_report);
    s.on('change:selected', function (model, value, options) {
        if (options.set_by == this)
            return;
        if (value.length > 0)
            cm_blast_report_select_hsp(value[0]);
    }, cm_blast_report);

    //////////////////
    // FASTA Viewer //
    //////////////////
    var empty_fasta_hint = 'Select one or more rows in the table on the left to display its FASTA sequence.';
    var cm_fasta_viewer = CodeMirror($('#fasta-viewer')[0], {
        value: empty_fasta_hint,
        theme: 'xq-light',
        tabSize: 2,
        lineNumbers: true,
        styleActiveLine: true,
        readOnly: true,
        viewportMargin: 15,
        gutters: ["CodeMirror-linenumbers"],
        lineWrapping: true,
    });
    $('#text-tabs a[href="#fasta-viewer"]').on('shown.bs.tab', function (e) {
        cm_fasta_viewer.refresh();
    })
    // Check if an ajax call is already done or underway, prevent duplicate calls to server
    // Cache FASTA sequences
    var fasta_cache = {};
    // Flag ongoing ajax calls
    var fasta_loading = {};
    var url_root = /(https?:\/\/.*(?:blast)*)\//g.exec(document.URL)[1];
    function get_fasta(sseqid) {
        // Returns a jqXHR or true if already in cache, for use with $.when
        //http://localhost:8000/api/seq/gnl%7CLoxosceles_reclusa_transcript_v0.5.3%7CLREC000002-RA/?format=fasta
        if (sseqid in fasta_cache)
            return true;
        else if (sseqid in fasta_loading)
            return fasta_loading[sseqid];
        else {
            fasta_loading[sseqid] = $.get(url_root + '/api/seq/' + sseqid + '/?format=fasta', function (data) {
                fasta_cache[sseqid] = data;
            });
            return fasta_loading[sseqid];
        }
    }
    s.on('change:hover', function (model, value, options) {
        //if (options.set_by == this)
        //    return;
        //if (value != null)
        //    cm_fasta_viewer_load_fasta(value);
        //else {
        //    selected = s.get('selected')
        //    if (selected.length > 0)
        //        cm_fasta_viewer_load_fasta(selected[0]);
        //}
    }, cm_fasta_viewer);
    s.on('change:selected', function (model, row_indexes, options) {
        if (options.set_by == this)
            return;
        if (row_indexes.length > 0) {
            sseqids = _.uniq(row_indexes.map(function (row_index) { return results_data[row_index][col_idx['sseqid']]; }));
            $.when.apply(null, sseqids.map(get_fasta)).then(function () {
                //check if row_indexes in fasta_cache, row_indexes might have already changed when this is called
                if (sseqids.length > 0 && _.all(sseqids.map(function (sseqid) { return sseqid in fasta_cache; }))) {
                    var fasta = '';
                    for (var i = 0; i < sseqids.length; i++) { // faster than array.join('')
                        fasta += fasta_cache[sseqids[i]];
                    }
                    cm_fasta_viewer.setValue(fasta);
                }
            });
        } else {
            cm_fasta_viewer.setValue(empty_fasta_hint);
        }
    }, cm_fasta_viewer);

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
                            return '<a class="btn btn-primary btn-xs" data-toggle="tooltip" data-placement="right" data-container="body" title="' + dbtitle + '\nClick to view in genome browser" target="_blank" href=\'' + results_info['db_url'][dbtitle] + '?loc=' + sseqid + ':' + start_pos + '..' + end_pos + '&addStores={"url":{"type":"JBrowse/Store/SeqFeature/GFF3","urlTemplate":"' + /^(https?:\/\/)/g.exec(results_info['db_url'][dbtitle])[1] + /https?:\/\/(.*?)\/(?:blast)*/g.exec(document.URL)[1] + '/media/blast/task/' + task_id + '/' + dbtitle + '.gff"}}&addTracks=[{"label":"BLAST+ Results","category":"0. Reference Assembly","type":"WebApollo/View/Track/DraggableHTMLFeatures","store":"url","style":{"renderClassName":"gray-center-10pct","subfeatureClasses":{"match_part":"blast-match_part"}}}]&tracks=BLAST+ Results\' role="button"><span class="glyphicon glyphicon-new-window"></span> ' + results_info['db_organism'][dbtitle] + '</a>';
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
    ///////////////////
    // Download Menu //
    ///////////////////
    var task_path = /(https?:\/\/.*?)\/(?:blast)*/g.exec(document.URL)[1] + '/media/blast/task/' + task_id + '/' + task_id;
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
    ///////////////////
    // Table Filters //
    ///////////////////
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
            var input = $('<div id="' + id + '" class="input-group input-group-sm"><div class="input-group-addon"><span class="glyphicon glyphicon-search"></div><input type="text" class="form-control col-search-input ' + title + '" placeholder="' + title + ' filter" /></div></div>').appendTo($(this).empty());
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
    //////////////////
    // Resize Event //
    //////////////////
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
    // only the horizontal-splitter changes height
    $("#result-container").data("kendoSplitter").bind('resize', function () {
        updateDataTableHeight();
    });
    // Draw initial graph with first row
    var row_data = results_table_api.row(0).data();
    // Selected
    var oTT = TableTools.fnGetInstance('results-table');
    $results_table.on('click', 'tr', function () {
        s.set({ 'selected': oTT.fnGetSelectedIndexes() }, { 'set_by': $results_table });
    });
    // Hover
    $results_table.on('mouseover', 'tr', function () {
        var this_row = results_table_api.row(this);
        s.set({ 'hover': this_row.index() }, { 'set_by': $results_table });
    });
    $('.dataTables_scrollBody').mouseleave(function () {
        s.set({ 'hover': null }, { 'set_by': $results_table });
    });
    s.on('change:hover', function (model, hover_index, options) {
        $(results_table_api.rows().nodes()).removeClass('highlight');
        if (options.set_by == this)
            return;
        // scroll to
        var scroll_index = s.focus_row_index();
        // get row
        var row = results_table_api.row(scroll_index);
        var row_data = row.data();
        // is filtered?
        // Get data as ordered and filtered in datatable
        var table_data = results_table_api.rows({ search: 'applied' }).data();
        var i = _.indexOf(table_data, row_data);
        results_table_api.scroller().scrollToRow(i, false);
        // highlight row
        if (hover_index != null) {
            var $row = $(results_table_api.rows({ search: 'applied' }).nodes()[i]);
            $row.addClass('highlight');
        }
    }, $results_table);
    s.on('change:selected', function (model, selected_indexes, options) {
        if (options.set_by == this)
            return;
        if (selected_indexes.length > 0) {
            // get row
            var row = results_table_api.row(selected_indexes[0]);
            var row_data = row.data();
            // is filtered?
            // Get data as ordered and filtered in datatable
            var table_data = results_table_api.rows({ search: 'applied' }).data();
            var i = _.indexOf(table_data, row_data);
            results_table_api.scroller().scrollToRow(i, false);
        }
        oTT.fnSelectNone();
        $.each(selected_indexes, function (key, value) {
            oTT.fnSelect(results_table_api.row(value).node());
        });
    }, $results_table);
    //////////////////////////////
    // Order, Search and Filter //
    //////////////////////////////
    var order = results_table_api.order();
    $results_table.on('order.dt', function () {
        //console.log('order.dt');
    });
    // Search event
    $results_table.on('search.dt', function () {
        //console.log('search.dt');
    });
    $results_table.on('draw.dt', function () {
        //console.log('draw.dt');
        var focus_row_index = s.get('hover')
        if (focus_row_index == null) {
            selected = s.get('selected')
            if (selected.length > 0)
                focus_row_index = selected[0];
            else
                focus_row_index = 0;
        }
        renderAlignmentGraph('query-canvas', focus_row_index);
        renderAlignmentGraph('subject-canvas', focus_row_index);
    });
        
    /////////////////////
    // Alignment Graph //
    /////////////////////
    function num_asc(a, b) { return (a - b); }
    var sorted_score_data = results_table_api.column(col_idx['bitscore']).data().sort(num_asc);
    var dynamic_min_score = Math.round(sorted_score_data[Math.round((sorted_score_data.length - 1) * 0.1)]);
    var dynamic_max_score = Math.round(sorted_score_data[Math.round((sorted_score_data.length - 1) * 0.9)]);
    var light_color_list = ['#fc9272', '#bcbddc', '#a1d99b', '#9ecae1', '#bdbdbd'].reverse();
    var dark_color_list = ['#7f0000', '#4d004b', '#004529', '#081d58', '#000000'].reverse();
    var selected_color_gradient = ['#fee6ce', '#f8bb5d', '#ee7d45']; // orange
    var hover_color_gradient = ['#f1e5bf', '#ffcc00', '#d4af37']; // yellow
    var min_score = dynamic_min_score;
    var max_score = dynamic_max_score;
    // #fc9272, #bcbddc, #a1d99b, #9ecae1, #bdbdbd
    var light_color_interpolator = chroma.scale(light_color_list).domain([min_score, max_score], 50);
    // #7f0000, #4d004b, #004529, #081d58, #000000
    var dark_color_interpolator = chroma.scale(dark_color_list).domain([min_score, max_score], 50);
    // build color lookup tables
    var score_to_color_light = {};
    var score_to_color_dark = {};
    for (var i = min_score; i <= max_score; i++) {
        score_to_color_light[i] = light_color_interpolator(i).hex();
        score_to_color_dark[i] = dark_color_interpolator(i).hex();
    }

    // Graph legend
    var legend_dim = { width: 300, height: 30, top: 0, right: 20, bottom: 0, left: 20 }
    document.getElementById('score-color-canvas').width = legend_dim.width;
    document.getElementById('score-color-canvas').height = legend_dim.height;
    var legend_svg = d3.select('#score-color-d3').append('svg')
        .attr('width', legend_dim.width)
        .attr('height', legend_dim.height);

    function hex_to_rgb(hex) {
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    function draw_bilinear(canvas, legend_dim, top_color_list, bottom_color_list, offsetX) {
        canvas.width = legend_dim.width;
        canvas.height = legend_dim.height;
        var ctx = canvas.getContext('2d');
        // setup x color interpolators
        var top_color_interpolator = chroma.scale(top_color_list).domain([legend_dim.left, legend_dim.width - legend_dim.right]);
        var bottom_color_interpolator = chroma.scale(bottom_color_list).domain([legend_dim.left, legend_dim.width - legend_dim.right]);
        if (offsetX) {
            var g = ctx.createLinearGradient(0, 0, 0, legend_dim.height);
            g.addColorStop(0, top_color_interpolator(offsetX).hex());
            g.addColorStop(1, bottom_color_interpolator(offsetX).hex());
            ctx.fillStyle = g;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        } else {
            var imageData = ctx.getImageData(0, 0, legend_dim.width, legend_dim.height);
            var pixels = imageData.data;
            var inner_width = legend_dim.width - legend_dim.left - legend_dim.right;
            var y_domain = [0, legend_dim.height];
            var x_offset = legend_dim.width * 4;
            for (var x = 0; x < legend_dim.width; x++) {
                // setup y color interpolator
                var y_color_list = [top_color_interpolator(x).hex(), bottom_color_interpolator(x).hex()]
                var y_color_interpolator = chroma.scale(y_color_list).domain(y_domain);
                for (var y = 0; y < legend_dim.height; y++) {
                    var color = y_color_interpolator(y).rgb();
                    pixels[y * x_offset + x * 4] = color[0];
                    pixels[y * x_offset + x * 4 + 1] = color[1];
                    pixels[y * x_offset + x * 4 + 2] = color[2];
                    pixels[y * x_offset + x * 4 + 3] = 255;
                }
            }
            ctx.putImageData(imageData, 0, 0);
        }
    }

    function draw_legend_continuous(color_list, li_text) {
        // draw background
        var canvas = $('#score-color-canvas')[0];
        draw_bilinear(canvas, legend_dim, light_color_list, dark_color_list);
        // draw axis
        var range_max = legend_svg.attr('width') - legend_dim.left - legend_dim.right;
        var x = d3.scale.linear().range([0, range_max]).domain([min_score, max_score]);
        var xAxis = d3.svg.axis().scale(x).orient('bottom').tickValues(d3.range(min_score, max_score + 1, (max_score - min_score) / (color_list.length - 1)));
        legend_svg.select("g").remove();
        legend_svg.append("g").attr("class", "x axis")
            .attr("transform", "translate(" + legend_dim.left + "," + legend_dim.top + ")")
            .call(xAxis);
    }

    // mouse over events
    $('#score-color-canvas').mousemove(function (e) {
        $('#score-color-rule').css('left', e.offsetX);
        var x = d3.scale.linear().range([min_score, max_score]).domain([legend_dim.left, legend_dim.width - legend_dim.left]);
        $('#score-color-rule-text').text(Math.round(x(e.offsetX)));
        // draw background
        var canvas = $('#score-color-canvas')[0];
        draw_bilinear(canvas, legend_dim, light_color_list, dark_color_list, Math.round(e.offsetX));
    });
    $('#score-color-rule').hide();
    $('#score-color-map').mouseleave(function (e) {
        $('#score-color-rule').hide();
        // draw background
        var canvas = $('#score-color-canvas')[0];
        draw_bilinear(canvas, legend_dim, light_color_list, dark_color_list);
    });
    $('#score-color-map').mouseenter(function (e) {
        $('#score-color-rule').show();
        //console.log(e.offsetX);
    });

    $('#score-to-color-checkbox').bootstrapSwitch({
        onText: 'Dynamic', offText: 'Static', onInit: function (event, state) {
            $('.bootstrap-switch-id-score-to-color-checkbox').popover({
                title: 'Dynamic / Static Switch',
                content: '<b>Dynamic</b> color keys help visualize <i>relative</i> scores between all BLAST hits.<br><b>Static</b> color keys help visualize the <i>absolute</i> scores of each BLAST hit.',
                html: true,
                trigger: 'hover',
                placement: 'bottom',
            });
        }, onSwitchChange: function (event, state) {
            if (state) {
                // dynamic
                min_score = dynamic_min_score;
                max_score = dynamic_max_score;
                // #fc9272, #bcbddc, #a1d99b, #9ecae1, #bdbdbd
                light_color_interpolator = chroma.scale(light_color_list).domain([min_score, max_score], 50);
                // #7f0000, #4d004b, #004529, #081d58, #000000
                dark_color_interpolator = chroma.scale(dark_color_list).domain([min_score, max_score], 50);
                // build color lookup tables
                score_to_color_light = {};
                score_to_color_dark = {};
                for (var i = min_score; i <= max_score; i++) {
                    score_to_color_light[i] = light_color_interpolator(i).hex();
                    score_to_color_dark[i] = dark_color_interpolator(i).hex();
                }
                color_scale = d3.scale.quantize().domain([min_score, max_score]).range(_.zip(light_color_list, dark_color_list));
                draw_legend_continuous(color_scale.range(), function (c) {
                    var r = color_scale.invertExtent(c);
                    return Math.round(r[0]);
                });
                //$('.score-to-color-text').text('Dynamic');
                updateAlignmentGraph();
            } else {
                // static
                min_score = 40;
                max_score = 200;
                // #fc9272, #bcbddc, #a1d99b, #9ecae1, #bdbdbd
                light_color_interpolator = chroma.scale(light_color_list).domain([min_score, max_score], 5);
                // #7f0000, #4d004b, #004529, #081d58, #000000
                dark_color_interpolator = chroma.scale(dark_color_list).domain([min_score, max_score], 5);
                // build color lookup tables
                score_to_color_light = {};
                score_to_color_dark = {};
                for (var i = min_score; i <= max_score; i++) {
                    score_to_color_light[i] = light_color_interpolator(i).hex();
                    score_to_color_dark[i] = dark_color_interpolator(i).hex();
                }
                color_scale = d3.scale.quantize().domain([min_score, max_score]).range(_.zip(light_color_list, dark_color_list));
                draw_legend_continuous(color_scale.range(), function (c) {
                    var r = color_scale.invertExtent(c);
                    return Math.round(r[0]);
                });
                //$('.score-to-color-text').text('Static');
                updateAlignmentGraph();
            }
        }
    });
    function draw_legend(legend_id, color_list, li_text) {
        d3.select(legend_id).selectAll('div').remove();
        var legend = d3.select(legend_id).selectAll('div').data(color_list).enter().append('div').attr('class', 'color-key')
            .style('background', function (c) {
                return c[0];
            })
            /*
    linear-gradient(60deg, rgba(30,87,153,1) 0%,rgba(0,0,0,0) 100%), 
    linear-gradient(120deg, rgba(131,179,211,1) 0%,rgba(0,0,0,0) 100%), 
    linear-gradient(60deg, rgba(0,0,0,0) 0%,rgba(136,216,144,1) 100%),
    linear-gradient(120deg, rgba(0,0,0,0) 0%,rgba(0,109,7,1) 100%);
             */
            .style('background', function (c) {
                return '-moz-linear-gradient(top, ' + c[0] + ' 0%, ' + c[1] + ' 100%)';
            }) //-moz-linear-gradient(top, #1e5799 0%, #7db9e8 100%);
            .style('background', function (c) {
                return '-webkit-gradient(linear, left top, left bottom, color-stop(0%,' + c[0] + '), color-stop(100%,' + c[1] + '))';
            }) //-webkit-gradient(linear, left top, left bottom, color-stop(0%,#1e5799), color-stop(100%,#7db9e8))
            .style('background', function (c) {
                return '-webkit-linear-gradient(top, ' + c[0] + ' 0%,' + c[1] + ' 100%)';
            }) //-webkit-linear-gradient(top, #1e5799 0%,#7db9e8 100%)
            .style('background', function (c) {
                return '-o-linear-gradient(top, ' + c[0] + ' 0%,' + c[1] + ' 100%)';
            }) //-o-linear-gradient(top, #1e5799 0%,#7db9e8 100%)
            .style('background', function (c) {
                return '-ms-linear-gradient(top, ' + c[0] + ' 0%,' + c[1] + ' 100%)';
            }) //-ms-linear-gradient(top, #1e5799 0%,#7db9e8 100%)
            .style('background', function (c) {
                return 'linear-gradient(to bottom, ' + c[0] + ' 0%,' + c[1] + ' 100%)';
            }) //linear-gradient(to bottom, #1e5799 0%,#7db9e8 100%)
            .style('background', function (c) {
                return 'progid:DXImageTransform.Microsoft.gradient( startColorstr="' + c[0] + '", endColorstr="' + c[1] + '",GradientType=0 )';
            }) //progid:DXImageTransform.Microsoft.gradient( startColorstr='#1e5799', endColorstr='#7db9e8',GradientType=0 )
            .text(li_text || String);
    }
    var color_scale = d3.scale.quantize().domain([min_score, max_score]).range(_.zip(light_color_list, dark_color_list));
    draw_legend_continuous(color_scale.range(), function (c) {
        var r = color_scale.invertExtent(c);
        return Math.round(r[0]);
    });
    draw_legend('#selected-hsp-color', [selected_color_gradient.slice(1)], function (c) { return ''; });
    draw_legend('#mouseover-hsp-color', [hover_color_gradient.slice(1)], function (c) { return ''; });

    // ctrl and shift detection
    var ctrl_down = false;
    var shift_down = false;
    $(document).keydown(function (event) {
        if (event.which == '17')
            ctrl_down = true;
        else if (event.which == '16')
            shift_down = true;
    });
    $(document).keyup(function (event) {
        if (event.which == '17')
            ctrl_down = false;
        else if (event.which == '16')
            shift_down = false;
    });

    function renderAlignmentGraph(canvas_name, focus_row_index) {
        // Get Canvas and Create Chart
        var canvas = document.getElementById(canvas_name);
        var canvas_parent = canvas.parentNode;
        // Remove all previous events
        var canvas_clone = canvas.cloneNode(true);
        // Copy jquery data
        var $canvas = $(canvas);
        var $canvas_clone = $(canvas_clone);
        $canvas_clone.data('lane_size', $canvas.data('lane_size'));
        //canvas = canvas_clone;
        //$canvas = $canvas_clone;
        // Clear canvas
        var ctx = canvas_clone.getContext('2d');
        ctx.clearRect(0, 0, canvas_clone.width, canvas_clone.height);
        //var chart = new Scribl(canvas_clone, canvas_clone.width);
        var offset = 45; // so scale text won't get cutoff
        var chart = new Scribl(canvas_clone, canvas_clone.width - offset * 2);
        chart.offset = offset;
        chart.scrollable = true;
        // Change laneSizes and buffers
        chart.laneSizes = 20;
        chart.laneBuffer = 0;
        chart.trackBuffer = 0;
        // Change text color		
        chart.glyph.text.color = 'white';

        var focus_row_data = results_table_api.row(focus_row_index).data();
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
        // Filter data, only keep rows associated with the reference given by focus_row_data
        var hsp_nt_range = 16000;
        var center_position = focus_row_data[rend] < focus_row_data[rstart] ? focus_row_data[rend] : focus_row_data[rstart];
        var filtered_rows = results_table_api.rows({ search: 'applied' }).eq(0).filter(function (row_index) {
            var row_data = results_table_api.row(row_index).data();
            // Only draw HSPs within the range of 32000nt(+-16000nt)
            var position = row_data[rend] < row_data[rstart] ? row_data[rend] : row_data[rstart];
            return row_data[rseqid] == focus_row_data[rseqid] && Math.abs(center_position - position) < hsp_nt_range;
        });
        // Draw at most 100 alignments, partition aligned_data if length > 100
        var graph_page_size = 50;
        var start = Math.floor(filtered_rows.indexOf(focus_row_index) / graph_page_size) * graph_page_size;
        var paged_filtered_rows = filtered_rows.toArray().slice(start, start + graph_page_size);
        // Sort data ascending by coordinate for draw order
        //var sorted_data = _.sortBy(filtered_data, function (row) { return -row['bitscore']; });
        // Set name text
        $('#' + canvas_name + '-name').text(focus_row_data[rseqid] + ', BLAST Hits ' + (start + 1) + '-' + (start + paged_filtered_rows.length));

        // Draw each hsp row
        _.each(paged_filtered_rows, function (row_index, paged_filtered_index) {
            var row_data = results_table_api.row(row_index).data();
            // Add glyph
            var position = row_data[rend] < row_data[rstart] ? row_data[rend] : row_data[rstart];
            var length = row_data[rend] < row_data[rstart] ? row_data[rstart] - row_data[rend] : row_data[rend] - row_data[rstart];
            var strand = row_data[send] < row_data[sstart] ? '-' : '+';
            var feature;
            // Set color
            // Default color this.glyph.color = ['#99CCFF', 'rgb(63, 128, 205)'];
            if (row_index == s.get('hover')) {
                feature = chart.addFeature(new BlockArrow('hover', position, length, strand));
            } else if (_.indexOf(s.get('selected'), row_index) != -1) {
                feature = chart.addFeature(new BlockArrow('selected', position, length, strand));
            } else {
                feature = chart.addFeature(new BlockArrow('hsp', position, length, strand));
                // Color according to score
                var color_bitscore = Math.max(min_score, Math.min(max_score, Math.round(row_data[bitscore])));
                feature.setColorGradient(
                    score_to_color_light[color_bitscore],
                    score_to_color_dark[color_bitscore]
                );
            }
            // Handle events
            feature.onMouseover = function () {
                s.set({ 'hover': row_index }, { 'set_by': 'graph' });
            };
            feature.onClick = function () {
                if (ctrl_down) {
                    var selected = s.get('selected').slice(0);
                    if (_.indexOf(selected, row_index) != -1) {
                        // remove row_index from selected
                        s.set({ 'selected': _.without(selected, row_index) }, { 'set_by': 'graph' });
                    } else {
                        selected.push(row_index);
                        s.set({ 'selected': selected}, { 'set_by': 'graph' });
                    }
                } else {
                    s.set({ 'selected': [row_index] }, { 'set_by': 'graph' });
                }
            };
        });
        // Set glyph type colors
        if ('hover' in chart)
            chart.hover.color = hover_color_gradient;
        if ('selected' in chart)
            //chart.selected.color = ['#fee6ce', '#f16913']; // orange
            chart.selected.color = selected_color_gradient; // orange
        // Calculate optimal lane size according to current canvas height
        // canvas.height = canvas.getScaleHeight() + canvas.tracks[0].lanes.length * (chart.laneSizes + chart.laneBuffer) + chart.trackBuffer;
        // only calculate if the user didn't touch the lane-size-slider
        if (!$canvas_clone.data('lane_size')) {
            optimal_lane_size = (canvas_clone.height - chart.getScaleHeight() - chart.trackBuffer) / chart.tracks[0].lanes.length - chart.laneBuffer;
            optimal_lane_size = optimal_lane_size < 5 ? 5 : optimal_lane_size > 20 ? 20 : optimal_lane_size;
            chart.laneSizes = optimal_lane_size;
        } else {
            chart.laneSizes = $canvas_clone.data('lane_size');
        }
        canvas_clone.height = chart.getHeight();

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
            canvas_parent.insertBefore(sliderDiv, canvas);
        }
        jQuery('#' + lane_size_slider_id).slider({
            orientation: 'vertical',
            range: 'min',
            max: 20,
            min: 5,
            value: chart.laneSizes,
            slide: function (event, ui) {
                ctx.clearRect(0, 0, canvas_clone.width, canvas_clone.height);
                chart.laneSizes = ui['value'];
                $canvas_clone.data('lane_size', chart.laneSizes);
                canvas_clone.height = chart.getHeight();
                chart.draw();
            }
        });
        // calculate needed height
        //canvas.height = chart.getHeight();
        // Draw Chart
        canvas_parent.replaceChild(canvas_clone, canvas);
        chart.draw();
    }
    // Fit canvas to container width and height
    // .width and .height needs to be in pixels
    // .style.width and .style.height only streches the rendered image and doesn't change the render dimensions
    // initial update, wait till core-splitter loads
    var $query_canvas = $('#query-canvas');
    var $query_canvas_container = $query_canvas.parent();
    var $subject_canvas = $('#subject-canvas');
    var $subject_canvas_container = $subject_canvas.parent();
    function updateAlignmentGraph() {
        //$query_canvas.attr({ width: $query_canvas_container.outerWidth(), height: $query_canvas_container.outerHeight() });
        //$subject_canvas.attr({ width: $subject_canvas_container.outerWidth(), height: $subject_canvas_container.outerHeight() });
        document.getElementById('query-canvas').height = $query_canvas_container.outerHeight() - 25;
        document.getElementById('subject-canvas').height = $subject_canvas_container.outerHeight() - 25;
        document.getElementById('query-canvas').width = $query_canvas_container.outerWidth();
        document.getElementById('subject-canvas').width = $subject_canvas_container.outerWidth();
        //console.log($query_canvas.outerHeight());
        var focus_row_index = s.focus_row_index();
        renderAlignmentGraph('query-canvas', focus_row_index);
        renderAlignmentGraph('subject-canvas', focus_row_index);
    };
    // Events
    s.on('change:hover', function (model, hover_index, options) {
        updateAlignmentGraph();
    }, 'graph');
    s.on('change:selected', function (model, selected_indexes, options) {
        updateAlignmentGraph();
    }, 'graph');
    $('.graph-canvas-container').mouseleave(function () {
        s.set({ 'hover': null }, { 'set_by': 'graph' });
    });
    ////////////
    // Layout //
    ////////////
    $('#top-side-by-side-container').kendoSplitter({
        panes: [
            { collapsible: false },
            { collapsible: true, size: '50%' }
        ]
    });
    $('#result-container').data('kendoSplitter').bind('resize', function () {
        updateAlignmentGraph();
    });
    $('#top-side-by-side-container').data('kendoSplitter').bind('resize', function () {
        updateAlignmentGraph();
    });
    ////////////
    // Resize //
    ////////////
    var report_panel_width = 777;
    var lazyLayout = _.throttle(function () {
        var w = $(window).width() - report_panel_width;
        w = w < report_panel_width ? $(window).width() / 2 : w;
        $('#bottom-side-by-side-container').data('kendoSplitter').size('.k-pane:first', w);
        //$table_container.width(w);
        updateDataTableHeight();
        updateAlignmentGraph();
        results_table_api.columns.adjust().draw();
    }, 200, { leading: false });
    $(window).resize(lazyLayout);
    var w = $(window).width() - report_panel_width
    w = w < report_panel_width ? $(window).width() / 2 : w
    $('#bottom-side-by-side-container').kendoSplitter({
        panes: [
            { collapsible: false, size: w },
            { collapsible: true }
        ]
    });
    $table_container.width(w);
    updateDataTableHeight();
    updateAlignmentGraph();
    results_table_api.columns.adjust().draw();
    var footer = $('<p class="nal-footer">2014 - National Agricultural Library</p>');
    $('.ui-corner-bl').append(footer);
    //console.log('checkpoint!');
});
