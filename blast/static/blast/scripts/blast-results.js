$(function () { // document ready
    //////////////////
    // Prepare Data //
    //////////////////
    // convert arrays to objects
    //var results_db = _.map(results_data, function (row) { return _.object(results_col_names, row); });
    var col_idx = _.object(results_col_names, _.range(results_col_names.length));
    ///////////////////
    // Results Table //
    ///////////////////
    //$.fn.dataTable.TableTools.buttons.download = $.extend(
    //    true,
    //    $.fn.dataTable.TableTools.buttonBase,
    //    {
    //        'sAction': 'text',
    //        'sTag': 'default',
    //        'sFieldBoundary': '',
    //        'sFieldSeperator': '\t',
    //        'sNewLine': '<br>',
    //        'sToolTip': '',
    //        'sButtonClass': 'DTTT_button_text',
    //        'sButtonClassHover': 'DTTT_button_text_hover',
    //        'sButtonText': 'Download',
    //        'mColumns': 'all',
    //        'bHeader': true,
    //        'bFooter': true,
    //        'sDiv': '',
    //        'fnMouseover': null,
    //        'fnMouseout': null,
    //        'fnClick': function (nButton, oConfig) {
    //            var iframe = document.createElement('iframe');
    //            iframe.style.height = '0px';
    //            iframe.style.width = '0px';
    //            iframe.src = oConfig.sUrl;
    //            document.body.appendChild(iframe);
    //        },
    //        'fnSelect': null,
    //        'fnComplete': null,
    //        'fnInit': null
    //    }
    //);
    var toolbar_prefix = 'fg-toolbar ui-toolbar ui-widget-header ui-helper-clearfix ui-corner-';
    var task_path = '/media/' + task_id + '/' + task_id;
    var index_of_jbrowse = _.indexOf(results_col_names, 'jbrowse'); // -1 if not present
    var $results_table = $('#results-table').dataTable({
        scrollX: '100%',
        scrollY: '200px',
        dom:
            '<"' + toolbar_prefix + 'tl ui-corner-tr"Rifr>' +
            't' +
            '<"' + toolbar_prefix + 'bl ui-corner-br"<"btn-group dropup">>S',
        //dom: 'Rifrt<"btn-group dropup">S',
        //"dom": 'T<"clear">lfrtip',
        //deferRender: true,
        //bJQueryUI: true,
        //tableTools: {
        //    sSwfPath: '/static/blast/swf/copy_csv_xls_pdf.swf',
        //    aButtons: [
        //        'copy',
        //        {
        //            "sExtends": "print",
        //            "sInfo": "Press escape when done."
        //        },
        //        {
        //            sExtends:    'collection',
        //            sButtonText: 'Save',
        //            aButtons: [{
        //                sExtends: 'download',
        //                sButtonText: 'Pairwise',
        //                sUrl: task_path + '.0'
        //            }, {
        //                sExtends: 'download',
        //                sButtonText: 'Query-anchored showing identities',
        //                sUrl: task_path + '.1'
        //            }, {
        //                sExtends: 'download',
        //                sButtonText: 'Flat query-anchored, show identities',
        //                sUrl: task_path + '.3'
        //            }, {
        //                sExtends: 'download',
        //                sButtonText: 'XML',
        //                sUrl: task_path + '.xml'
        //            }, {
        //                sExtends: 'download',
        //                sButtonText: 'Tabular',
        //                sUrl: task_path + '.tsv'
        //            }, {
        //                sExtends: 'download',
        //                sButtonText: 'CSV',
        //                sUrl: task_path + '.csv'
        //            }, {
        //                sExtends: 'download',
        //                sButtonText: 'BLAST archive format (ASN.1)',
        //                sUrl: task_path + '.asn'
        //            }]
        //        }
        //    ]
        //},
        colReorder: {
            fixedColumns: 3,
            realtime: true,
            stateSave: true
        },
        order: [[ col_idx['qseqid'], 'asc' ]],
        //responsive: true,
        data: results_data,
        columns: _.map(results_col_names, function (name) {
            col = { 'title': results_col_names[col_idx[name]] };
            if (name == 'jbrowse')
                col['orderable'] = false;
            return col;
        }),
        "headerCallback": function (thead, data, start, end, display) {
            $(thead).find('th').each(function (index) {
                $(this).html('<a data-toggle="tooltip" data-placement="top" data-container="body" title="' + results_col_names_display[col_idx[$(this).text()]] + '"><span>' + results_col_names[col_idx[$(this).text()]] + '</span></a>');
                $(this).children().tooltip()
            });
        },
        rowCallback: function (row, data) {
            if (index_of_jbrowse > -1 && data[index_of_jbrowse] != '') {
                var sseqid = data[col_idx['sseqid']];
                if (/\|[^|_]+?_([^|]+)$/g.exec(sseqid) != null)
                    //>gnl|Ceratitis_capitata|cercap_Scaffold1
                    sseqid = /\|[^|_]+?_([^|]+)$/g.exec(sseqid)[1];
                else if (/\|([^|]+)\|/.exec(sseqid) != null)
                    //>diacit|scaffold149842.1|size221|ref0023013|ref0159280
                    sseqid = /\|([^|]+)\|/.exec(sseqid)[1];
                var start_pos = data[col_idx['sstart']];
                var end_pos = data[col_idx['send']];
                if (end_pos < start_pos)
                    end_pos = [start_pos, start_pos = end_pos][0];
                start_pos -= 200;
                if (start_pos < 0)
                    start_pos = 0;
                end_pos += 200;
                if (end_pos > data[col_idx['slen']])
                    end_pos = data[col_idx['slen']];
                var dbtitle = results_info['sseqid_db'][data[col_idx['sseqid']]];
                $('td', row).eq(index_of_jbrowse).addClass('center-cell').html('<a class="btn btn-primary btn-xs" target="_blank" href=\'' + results_info['db_url'][dbtitle] + '?loc=' + sseqid + ':' + start_pos + '..' + end_pos + '&addStores={"url":{"type":"JBrowse/Store/SeqFeature/GFF3","urlTemplate":"http://' + /http:\/\/([^\/]+)\//g.exec(document.URL)[1] + '/media/' + task_id + '/' + dbtitle + '.gff"}}&addTracks=[{"label":"BLAST+ Results","category":"0. Reference Assembly","type":"WebApollo/View/Track/DraggableHTMLFeatures","store":"url","style":{"renderClassName":"gray-center-10pct","subfeatureClasses":{"match_part":"blast-match_part"}}}]&tracks=BLAST+ Results\' role="button"><span class="glyphicon glyphicon-new-window"></span> ' + data[index_of_jbrowse] + '</a>');
                //http://gmod-dev.nal.usda.gov:8080/anogla/jbrowse/?loc=Scaffold1:107901..161900&addStores={"url":{"type":"JBrowse/Store/SeqFeature/GFF3","urlTemplate":"http://gmod-dev.nal.usda.gov/media/07b73d9a3dde4eac9faa9c4109f7cfb6/Agla_Btl03082013.genome_new_ids.fa.gff"}}&addTracks=[{"label":"BLAST+ Results","category":"0. Reference Assembly","type":"JBrowse/View/Track/CanvasFeatures","store":"url","glyph":"JBrowse/View/FeatureGlyph/ProcessedTranscript","subParts":"match_part","style":{"color":"blue","height":6,"connectorColor":"gray","connectorThickness":2}}]
            }
        }
    });
    var results_table_api = $('#results-table').DataTable();
    $('.ui-corner-br .btn-group').html('<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">\
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
    var $table_panel = $('#table-panel');
    var $ui_corner_tr = $('.ui-corner-tr');
    var $ui_corner_br = $('.ui-corner-br');
    var $dataTables_scrollHead = $('.dataTables_scrollHead');
    var $dataTables_scrollBody = $('.dataTables_scrollBody');
    function updateDataTableHeight() {
        // table_panel_div - top_bar - bottom_bar - table_header
        var h = $table_panel.height() - $ui_corner_tr.outerHeight() - $ui_corner_br.outerHeight() - $dataTables_scrollHead.outerHeight();
        $dataTables_scrollBody.css('height', h);
        // trigger dataTables.scroller to recalculate how many rows its showing
        $(window).trigger('resize.DTS');
    };
    // Draw initial graph with first row
    var row_data = results_table_api.row(0).data();
    // initial update, wait till core-splitter loads
    var report_panel_width = 820;
    var cm = null;
    $(window).on('polymer-ready', function () {
        var w = $(window).width() - report_panel_width
        w = w < report_panel_width ? $(window).width() / 2 : w
        $table_panel.width(w);
        updateDataTableHeight();
        var footer = $('<p class="nal-footer">2014 - National Agricultural Library</p>');
        $('.ui-corner-bl').append(footer);
        cm = $('code-mirror')[0].mirror;
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
    });
    $(window).resize(function () {
        var w = $(window).width() - report_panel_width
        w = w < report_panel_width ? $(window).width() / 2 : w
        $table_panel.width(w);
        updateDataTableHeight();
    });
    // only the horizontal-splitter changes height, track event defined by polymer
    $('#horizontal-splitter').on('track', function () {
        updateDataTableHeight();
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
            cm.curOp.cursorActivity = false; // don't fire event
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
    $(window).on('polymer-ready', function () {
        updateAlignmentGraph()
        results_table_api.draw();
    });
    $(window).resize(function () {
        updateAlignmentGraph()
    });
    $('#horizontal-splitter').on('track', function () {
        updateAlignmentGraph()
    });
    $('#graph-splitter').on('track', function () {
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
                    cm.curOp.cursorActivity = false; // don't fire event
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
            sliderDiv.style.margin = '32px 25px';
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
    /////////////////
    // Text Report //
    /////////////////
});
