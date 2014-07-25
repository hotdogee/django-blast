$(function () { // document ready
    //////////////////
    // Prepare Data //
    //////////////////
    // convert arrays to objects
    var results_db = _.map(results_data, function (row) { return _.object(results_col, row); });
    ///////////////////
    // Results Table //
    ///////////////////
    $('#example').dataTable({
        'data': results_data
    });
    /////////////////////
    // Alignment Graph //
    /////////////////////
    function renderAlignmentGraph(canvas_name, data) {
        // Get Canvas and Create Chart
        //var canvas = $('query-canvas');
        var canvas = document.getElementById(canvas_name);

        // Create Chart
        //chart = new Scribl(canvas, canvas.width());
        var chart = new Scribl(canvas, 1000);

        // Change laneSizes and buffers
        chart.laneSizes = 20;
        chart.laneBuffer = 0;
        chart.trackBuffer = 0;

        // change text color		
        chart.glyph.text.color = 'white';

        // Create Track 1
        var track1 = chart.addTrack();

        // Add Genes to Track 1
        var gene1 = track1.addFeature(new BlockArrow('track1', 5, 750, '-'));
        var gene2 = track1.addFeature(new BlockArrow('track1', 3500, 2500, '+'));
        //gene4 = track1.addFeature( new BlockArrow('track1', 6200, 1500, '+') );
        var gene3 = track1.addFeature(new BlockArrow('track1', 8100, 1000, '-'));
        //chart.track1.name = 'track 11';

        // Create Track 2
        var track2 = chart.addTrack();

        // Add Genes to Track 2
        var gene5 = track2.addFeature(new BlockArrow('track2', 100, 1000, '-'));
        var gene6 = track2.addFeature(new BlockArrow('track2', 3500, 1500, '-'));
        var gene10 = track2.addFeature(new BlockArrow('track2', 35000, 1000, '+'));
        //chart.track2.name = 'track 2';

        // create Lane1 of Track2

        // Create Track with 1 lane
        var track3Lane1 = chart.addTrack().addLane();

        // Add Genes to single lane
        var gene7 = track3Lane1.addFeature(new BlockArrow('track3', 2230, 1000, '+'));
        var gene8 = track3Lane1.addFeature(new BlockArrow('track3', 3300, 1500, '+'));
        var gene9 = track3Lane1.addFeature(new BlockArrow('track3', 4800, 1000, '-'));
        //chart.track3.name = 'track 3';

        // Draw Chart
        chart.draw();
    }
    function buildGraphData(data, seqid) {
        // data = _.object(['seqid', 'start', 'end', 'bitscore'], ['Contig1', 1341, 1432, 110])
    }
    var query_data = [];
    renderAlignmentGraph('query-canvas', query_data);
    var subject_data = [];
    renderAlignmentGraph('subject-canvas', subject_data);
});