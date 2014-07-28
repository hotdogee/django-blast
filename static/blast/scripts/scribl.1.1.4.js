

/* Simple JavaScript Inheritance

 * By John Resig http://ejohn.org/
 
 * MIT Licensed.
 */
// Inspired by base2 and Prototype 

(function () {
    var initializing = false, fnTest = /xyz/.test(function () { xyz; }) ? /\b_super\b/ : /.*/;
    // The base Class implementation (does nothing)
    this.Class = function () { };

    // Create a new Class that inherits from this class
    Class.extend = function (prop) {
        var _super = this.prototype;

        // Instantiate a base class (but only create the instance,
        // don't run the init constructor)
        initializing = true;
        var prototype = new this();
        initializing = false;

        // Copy the properties over onto the new prototype
        for (var name in prop) {
            // Check if we're overwriting an existing function
            prototype[name] = typeof prop[name] == "function" &&
              typeof _super[name] == "function" && fnTest.test(prop[name]) ?
              (function (name, fn) {
                  return function () {
                      var tmp = this._super;

                      // Add a new ._super() method that is the same method
                      // but on the super-class
                      this._super = _super[name];

                      // The method only need to be bound temporarily, so we
                      // remove it when we're done executing
                      var ret = fn.apply(this, arguments);
                      this._super = tmp;

                      return ret;
                  };
              })(name, prop[name]) :
              prop[name];
        }

        // The dummy class constructor

        function Class() {
            // All construction is actually done in the init method
            if (!initializing && this.init)
                this.init.apply(this, arguments);
        }

        // Populate our constructed prototype object
        Class.prototype = prototype;

        // Enforce the constructor to be what we expect
        Class.constructor = Class;

        // And make this class extendable
        Class.extend = arguments.callee;

        return Class;
    };
})();/**
 * **Scribl Class**
 *
 * _sets defaults, defines how to add features
 * to chart/view and some methods to help
 * coordinate drawing_
 * 
 * Chase Miller 2011
 */

// globals
// if (SCRIBL == undefined) {
var SCRIBL = {};
SCRIBL.chars = {};
SCRIBL.chars.nt_color = 'white';
SCRIBL.chars.nt_A_bg = 'red';
SCRIBL.chars.nt_G_bg = 'blue';
SCRIBL.chars.nt_C_bg = 'green';
SCRIBL.chars.nt_T_bg = 'black';
SCRIBL.chars.nt_N_bg = 'purple';
SCRIBL.chars.nt_dash_bg = 'rgb(120,120,120)';
SCRIBL.chars.heights = [];
SCRIBL.chars.canvasHolder = document.createElement('canvas');
//}


var Scribl = Class.extend({

    /** **init**
 
     * _ Constructor, call this with `new Scribl()`_
 
     * @param {Object} canvasHTML object
     * @param {Int} width of chart in pixels
     * @return {Object} Scribl object
     * @api public
     */
    init: function (canvas, width) {
        this.scrolled = false;
        // create canvas contexts		
        var ctx;
        if (canvas)
            ctx = canvas.getContext('2d');
        var chart = this;

        // chart defaults
        this.width = width;
        this.uid = _uniqueId('chart');
        this.laneSizes = 50;
        this.laneBuffer = 5;
        this.trackBuffer = 25;
        this.offset = undefined;
        this.canvas = canvas;
        this.ctx = ctx;

        // scale defaults
        this.scale = {};
        this.scale.pretty = true;
        this.scale.max = undefined;
        this.scale.min = undefined;
        this.scale.auto = true;
        this.scale.userControlled = false;
        this.scale.positions = [0]; // by default scale goes on top
        this.scale.off = false;
        this.scale.size = 15; // in pixels
        this.scale.font = {};
        this.scale.font.size = 15; // in pixels
        this.scale.font.color = 'black';
        this.scale.font.buffer = 10; // in pixels - buffer between two scale numbers
        // (e.g. 1k and 2k)

        // glyph defaults
        this.glyph = {};
        this.glyph.roundness = 6;
        this.glyph.borderWidth = 1; // in pixels
        this.glyph.color = ['#99CCFF', 'rgb(63, 128, 205)'];
        this.glyph.text = {};
        this.glyph.text.color = 'black';
        this.glyph.text.size = '13'; // in pixels
        this.glyph.text.font = 'arial';
        this.glyph.text.align = 'center';


        // initialize common types
        this.gene = {};
        this.gene.text = {};
        this.protein = {};
        this.protein.text = {};

        // event defaults
        this.events = {};
        this.events.hasClick = false;
        this.events.hasMouseover = false;
        this.events.clicks = new Array;
        this.events.mouseovers = new Array;
        this.events.added = false;
        this.mouseHandler = function (e) {
            chart.handleMouseEvent(e, 'mouseover')
        };
        this.clickHandler = function (e) { chart.handleMouseEvent(e, 'click') };

        // tick defaults
        this.tick = {};
        this.tick.auto = true;
        this.tick.major = {};
        this.tick.major.size = 10; // width between major ticks in nucleotides
        this.tick.major.color = 'black';
        this.tick.minor = {};
        this.tick.minor.size = 1; // width between minor ticks in nucleotides
        this.tick.minor.color = 'rgb(55,55,55)';
        this.tick.halfColor = 'rgb(10,10,10)';

        // tooltip defaults
        this.tooltips = {};
        this.tooltips.text = {}
        this.tooltips.text.font = 'arial';
        this.tooltips.text.size = 12; // in pixels
        this.tooltips.borderWidth = 1; // in pixels
        this.tooltips.roundness = 5;  // in pixels
        this.tooltips.fade = false;
        this.tooltips.style = 'light';  // also a 'dark' option
        this.lastToolTips = [];

        // scroll defaults
        this.scrollable = false;
        this.scrollValues = []; // values in nts where scroll

        this.chars = {};
        this.chars.drawOnBuild = [];

        // draw defaults
        this.drawStyle = 'expand';

        // draw hooks
        this.glyphHooks = [];
        this.trackHooks = [];

        // private variables
        this.myMouseEventHandler = new MouseEventHandler(this);
        this.tracks = [];
        var scaleSize = this.scale.size;
        var scaleFontSize = this.scale.font.size
    },

    /** **getScaleHeight**
   
    * _Get the height of the scale/ruler_
   
    * @return {Int} height in pixels
    * @api public
    */
    getScaleHeight: function () {
        return (this.scale.font.size + this.scale.size);
    },

    /** **getHeight**
   
    * _Get the height of the entire Scribl chart/view_
   
    * @return {Int} height in pixels
    * @api public
    */
    getHeight: function () {
        var wholeHeight = 0;

        if (!this.scale.off) wholeHeight += this.getScaleHeight();
        var numTracks = this.tracks.length

        for (var i = 0; i < numTracks; i++) {
            wholeHeight += this.trackBuffer;
            wholeHeight += this.tracks[i].getHeight();
        }

        return wholeHeight;
    },

    /** **getFeatures**
    
     * _Returns an array of features (e.g. gene)_
    
     * @return {Array} of features
     * @api public
     */

    getFeatures: function () {
        var features = [];
        for (var i = 0; i < this.tracks.length; i++) {
            for (var k = 0; k < this.tracks[i].lanes.length; k++) {
                features = features.concat(this.tracks[i].lanes[k].features);
            }
        }
        return features;
    },

    /** **setCanvas**
    
     * _Changes the canvas that Scribl draws to_
    
     * @param {Html Canvas Element} the canvas to draw to
     * @api public
     */
    setCanvas: function (canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        // this.registerEventListeners();
    },

    /** **addScale**
    
     * _Inserts a scale at the end of the last track currently added to the chart_
    
     * @api public
     */
    addScale: function () {
        if (this.scale.userControlled)
            this.scale.positions.push(this.tracks.length);
        else {
            this.scale.positions = [this.tracks.length];
            this.scale.userControlled = true;
        }
    },

    /** **addTrack**
   
    * _Creates a new track and adds it to the Scribl chart/view_
   
    * @return {Object} the new track
    * @api public
    */
    addTrack: function () {
        var track = new Track(this);
        if (this.tracks.length == 1 && this.tracks[0] == undefined)
            this.tracks = [];
        this.tracks.push(track);
        return track;
    },

    /** **removeTrack**
    
     * _removes a track_
    
     * @param {Object} the track to be removed
     * @api public
     */
    removeTrack: function (track) {
        var chart = this;

        for (var i = 0; i < chart.tracks.length; i++) {
            if (track.uid == chart.tracks[i].uid)
                chart.tracks.splice(i, 1);
        }
        delete track;
    },


    /** **loadGenbank**
   
    * _parses a genbank file and adds the features to the Scribl chart/view_
   
    * @param {String} genbank file as a string
    * @api public
    */
    loadGenbank: function (file) {
        genbank(file, this);
    },

    /** **loadBed**
   
    * _parses a bed file and adds the features to the Scribl chart/view_
   
    * @param {String} bed file as a string
    * @api public
    */
    loadBed: function (file) {
        bed(file, this);
    },

    /** **loadBam**
    
     * _parses a bam file and adds the features to the Scribl chart/view_
    
     * @param {File} bam file as a javascript file object
     * @param {File} bai (bam index) file as a javascript file object
     * @param {Int} start
     * @param {Int} end
     * @api public
     */
    loadBam: function (bamFile, baiFile, chr, start, end, callback) {
        var scribl = this;
        // scribl.scale.min = start;
        // scribl.scale.max = end;
        var track = scribl.addTrack();
        track.status = 'waiting';
        makeBam(new BlobFetchable(bamFile),
                new BlobFetchable(baiFile),
                function (bam, reader) {
                    scribl.file = bam;
                    bam.fetch(chr, start, end, function (r, e) {
                        if (r) {
                            for (var i = 0; i < r.length; i += 1) {
                                track.addFeature(new BlockArrow('bam', r[i].pos, r[i].lengthOnRef, '+', { 'seq': r[i].seq }))
                            }
                            track.status = "received";
                            if (track.drawOnResponse)
                                scribl.redraw();
                            //callback();
                        }
                        if (e) {
                            alert('error: ' + e);
                        }
                    });
                });
        return track;
    },

    /** **loadFeatures**
   
    * _adds the features to the Scribl chart/view_
   
    * @param {Array} features - array of features, which can be any of the derived Glyph classes (e.g. Rect, Arrow, etc..)
    * @api public
    */
    loadFeatures: function (features) {
        for (var i = 0; i < features.length; i++)
            this.addFeature(features[i]);
    },

    /** **addGene**
   
    * _syntactic sugar function to add a feature with the gene type_
   
    * @param {Int} position - start position of the feature
    * @param {Int} length - length of the feature
    * @param {String} strand - '+' or '-' strand
    * @param {Hash} [opts] - optional hash of options that can be applied to feature 
    * @return {Object} feature - a feature with the 'feature' type
    * @api public
    */
    addGene: function (position, length, strand, opts) {
        return (this.addFeature(
           new BlockArrow('gene', position, length, strand, opts)
        ));
    },

    /** **addProtein**
   
    * _syntactic sugar function to add a feature with the protein type_
   
    * @param {Int} position - start position of the protein
    * @param {Int} length - length of the protein
    * @param {String} strand - '+' or '-' strand
    * @param {Hash} [opts] - optional hash of options that can be applied to protein  
    * @return {Object} protein - a feature with the 'protein' type
    * @api public
    */
    addProtein: function (position, length, strand, opts) {
        return (this.addFeature(
           new BlockArrow('protein', position, length, strand, opts)
        ));
    },

    /** **addFeature**
   
    * _addFeature to Scribl chart/view and let Scribl manage track and lane placement to avoid overlaps_
    
    * example:
    * `chart.addFeature( new Rect('complex',3500, 2000) );`
   
    * @param {Object} feature - any of the derived Glyph classes (e.g. Rect, Arrow, etc..)
    * @return {Object} feature     
    * @api public        
    */
    addFeature: function (feature) {
        var track = this.tracks[0] || this.addTrack();
        track.addFeature(feature);
        return feature;
    },


    /** **slice**
   
    * _slices the Scribl chart/view at given places and returns a smaller chart/view_
   
    * @param {Int} from - nucleotide position to slice from
    * @param {Int} to - nucleotide position to slice to     
    * @param {String} type - _inclusive_ (defaulte) includes any feature that has any part in region, _exclusive_, includes only features that are entirely in the region, _strict_ if feature is partly in region, it'll cut that feature at the boundary and include the cut portion
    * @return {Object} Scribl   
    * @api public          
    */
    slice: function (from, to, type) {
        type = type || 'inclusive';
        var chart = this;
        var sliced_features = [];

        // iterate through tracks
        var numTracks = this.tracks.length;
        var newChart = new Scribl(this.canvas, this.width);

        // TODO: make this more robust
        newChart.scale.min = this.scale.min;
        newChart.scale.max = this.scale.max;
        newChart.offset = this.offset;
        newChart.scale.off = this.scale.off;
        newChart.scale.pretty = this.scale.pretty;
        newChart.laneSizes = this.laneSizes;
        newChart.drawStyle = this.drawStyle;
        newChart.glyph = this.glyph;
        newChart.glyphHooks = this.glyphHooks;
        newChart.trackHooks = this.trackHooks;
        //      newChart.mouseHandler = this.mouseHandler;
        //      newChart.clickHandler = this.clickHandler;
        newChart.previousDrawStyle = this.previousDrawStyle;

        // for ( var i in object.getOwnPropertyNames(this) ) {
        //    newChart[i] = this[i];
        // }

        // Aliases for the rather verbose methods on ES5
        // var descriptor  = Object.getOwnPropertyDescriptor
        //   , properties  = Object.getOwnPropertyNames
        //   , define_prop = Object.defineProperty

        // (target:Object, source:Object) → Object
        // Copies properties from `source' to `target'

        // properties(chart).forEach(function(key) {
        //     define_prop(newChart, key, descriptor(chart, key)) })


        for (var j = 0; j < numTracks; j++) {
            var track = this.tracks[j];
            var newTrack = newChart.addTrack();
            newTrack.drawStyle = track.drawStyle;
            var numLanes = track.lanes.length;
            for (var i = 0; i < numLanes; i++) {
                var newLane = newTrack.addLane();
                var s_features = track.lanes[i].features;
                for (var k = 0; k < s_features.length; k++) {
                    var end = s_features[k].position + s_features[k].length;
                    var start = s_features[k].position;
                    // determine if feature is in slice/region
                    if (type == 'inclusive') {
                        if (start >= from && start <= to)
                            newLane.addFeature(s_features[k].clone())
                        else if (end > from && end < to)
                            newLane.addFeature(s_features[k].clone())
                        else if (start < from && end > to)
                            newLane.addFeature(s_features[k].clone())
                        else if (start > from && end < to)
                            newLane.addFeature(s_features[k].clone())
                    } else if (type == 'strict') {
                        if (start >= from && start <= to) {
                            if (end > from && end < to)
                                newLane.addFeature(s_features[k].clone())
                            else {
                                // turn first half into rect to stop having two block arrows features    
                                if (s_features[k].glyphType == "BlockArrow" && s_features[k].strand == "+")
                                    var f = s_features[k].clone("Rect");
                                else
                                    var f = s_features[k].clone();

                                f.length = Math.abs(to - start);
                                newLane.addFeature(f);
                            }
                        } else if (end > from && end < to) {
                            // turn first half into rect to stop having two block arrows features    
                            if (s_features[k].glyphType == "BlockArrow" && s_features[k].strand == "-")
                                var f = s_features[k].clone("Rect");
                            else
                                var f = s_features[k].clone();

                            f.position = from;
                            f.length = Math.abs(end - from);
                            newLane.addFeature(f);
                        }
                        else if (start < from && end > to) {
                            // turn first half into rect to stop having two block arrows features    
                            if (s_features[k].glyphType == "BlockArrow")
                                var f = s_features[k].clone("Rect");
                            else
                                var f = s_features[k].clone();
                            f.position = from;
                            f.length = Math.abs(to - from);
                            newLane.addFeature(f);
                        }
                    } else if (type == 'exclusive') {
                        if (start >= from && start <= to && end > from && end < to)
                            newLane.addFeature(s_features[k].clone())
                    }

                }

            }
        }


        // for (var attr in this) {
        //    if (this.hasOwnProperty(attr)) copy[attr] = this[attr];
        // }

        return newChart;
    },

    /** **draw**
   
    * _draws everything_
    
    * @api public
    */

    draw: function () {
        // initalize variables
        var ctx = this.ctx;
        var tracks = this.tracks;
        // make scale pretty by starting and ending the scale
        // at major ticks and choosing best tick distances
        this.initScale();

        // check if scrollable
        if (this.scrollable == true) {
            this.initScrollable();
        }

        ctx.save();

        // fix offsets so scale will not be cut off on left side
        // check if offset is turned off and then set it to static '0'
        if (this.offset == undefined)
            this.offset = Math.ceil(ctx.measureText('0').width / 2 + 10);
			
        ctx.save();

        // draw tracks
        for (var i = 0; i < tracks.length; i++) {
            // draw scale
            if (!this.scale.off && this.scale.positions.indexOf(i) != -1)
                this.drawScale();
            tracks[i].draw();
        }

        // test if scale is drawn last
        if (!this.scale.off && this.scale.positions.indexOf(tracks.length) != -1)
            this.drawScale();

        ctx.restore();
        ctx.restore();

        // add events if haven't done so already
        if (!this.events.added)
            this.registerEventListeners();
    },

    /** **redraw**
 
     * _clears chart/view and draws it_
     
     * @api public
     */
    redraw: function () {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        if (this.tracks.length > 0)
            this.draw();
    },

    /** **initScale**
   
    * _initializes scale_
    
    * @api internal
    */
    initScale: function () {
        if (this.scale.pretty) {

            // determine reasonable tick intervals
            if (this.tick.auto) {
                // set major tick interval
                this.tick.major.size = this.determineMajorTick();

                // set minor tick interval
                this.tick.minor.size = Math.round(this.tick.major.size / 10);
            }

            // make scale end on major ticks
            if (this.scale.auto) {
                this.scale.min -= this.scale.min % this.tick.major.size;
                this.scale.max = Math.round(this.scale.max / this.tick.major.size + .4)
                   * this.tick.major.size;
            }
        }
    },

    /** **drawScale**
   
    * _draws scale_
    
    * @api public
    */
    drawScale: function (options) {
        var firstMinorTick;
        var ctx = this.ctx;
        var fillStyleRevert = ctx.fillStyle;

        if (options && options.init)
            this.initScale();

        // determine tick vertical sizes and vertical tick positions
        var tickStartPos = this.scale.font.size + this.scale.size;
        var majorTickEndPos = this.scale.font.size + 2;
        var minorTickEndPos = this.scale.font.size + this.scale.size * 0.66;
        var halfTickEndPos = this.scale.font.size + this.scale.size * 0.33;

        // set scale defaults
        ctx.font = this.scale.font.size + 'px arial';
        ctx.textBaseline = 'top';
        ctx.fillStyle = this.scale.font.color;

        if (this.offset == undefined)
            this.offset = Math.ceil(ctx.measureText('0').width / 2 + 10);

        // determine the place to start first minor tick
        if (this.scale.min % this.tick.minor.size == 0)
            firstMinorTick = this.scale.min
        else
            firstMinorTick = this.scale.min - (this.scale.min % this.tick.minor.size)
               + this.tick.minor.size;

        // draw
        for (var i = firstMinorTick; i <= this.scale.max; i += this.tick.minor.size) {
            ctx.beginPath();
            if (i == 187250)
                var h = 2;
            var curr_pos = this.pixelsToNts(i - this.scale.min) + this.offset;
            if (i % this.tick.major.size == 0) { // draw major tick
                // create text
                var tickText = this.getTickText(i);
                ctx.textAlign = 'center';
                ctx.fillText(tickText, curr_pos, 0);

                // create major tick
                ctx.moveTo(curr_pos, tickStartPos);
                ctx.lineTo(curr_pos, majorTickEndPos);
                ctx.strokeStyle = this.tick.major.color;
                ctx.stroke();

            } else { // draw minor tick
                ctx.moveTo(curr_pos, tickStartPos);

                // create half tick - tick between two major ticks
                if (i % (this.tick.major.size / 2) == 0) {
                    ctx.strokeStyle = this.tick.halfColor;
                    ctx.lineTo(curr_pos, halfTickEndPos);
                }
                    // create minor tick
                else {
                    ctx.strokeStyle = this.tick.minor.color;
                    ctx.lineTo(curr_pos, minorTickEndPos);
                }
                ctx.stroke();
            }
        }

        // restore fillstyle
        ctx.fillStyle = fillStyleRevert;

        // shift down size of scale
        ctx.translate(0, this.getScaleHeight() + this.laneBuffer);
    },

    /** **pixelsToNts**
   
    * _Get the number of nucleotides per the given pixels_
   
    * @param {Int} [pixels] optional - if not given, the ratio of pixels/nts will be returned
    * @return {Int} nucleotides or pixels/nts ratio
    * @api internal    
    */
    pixelsToNts: function (pixels) {
        if (pixels == undefined)
            return (this.width / (this.scale.max - this.scale.min));
        else
            return (this.width / (this.scale.max - this.scale.min) * pixels);
    },

    /** **ntsToPixels**
    
     * _Get the number of pixels shown per given nucleotides_
    
     * @param {Int} [nucleotides] optional - if not given, the ratio of nts/pixel will be returned
     * @return {Int} pixels or nts/pixel ratio
     * @api internal
     */
    ntsToPixels: function (nts) {
        if (nts == undefined)
            return (1 / this.pixelsToNts());
        else
            return (nts / this.width);
    },

    /** **initScrollable**
   
    * _turns static chart into scrollable chart_
   
    * @api internal
    */
    initScrollable: function () {
        var scroll_wrapper = this.canvas.parentNode;
        if (scroll_wrapper.className != 'scroll-wrapper') {
            var parent_node = scroll_wrapper;
            this.canvas.style.cssText = '';
            // Create slider
            var sliderDiv = document.createElement('div');
            sliderDiv.className = 'slider';
            sliderDiv.style.cssFloat = 'left';
            sliderDiv.style.margin = '32px 13px';
            sliderDiv.style.position = 'absolute';
            parent_node.replaceChild(sliderDiv, this.canvas);
            // Wrap canvas in scroll-wrapper
            scroll_wrapper = document.createElement('div');
            scroll_wrapper.style.width = '100%';
            scroll_wrapper.style.height = '100%';
            scroll_wrapper.style.overflow = 'auto';
            scroll_wrapper.className = 'scroll-wrapper';
            scroll_wrapper.appendChild(this.canvas);
            parent_node.appendChild(scroll_wrapper);
            // Make dragable
            jQuery(scroll_wrapper).dragscrollable({ dragSelector: 'canvas:first', acceptPropagatedEvent: false });
        }
        // At min zoom, this.canvas.width = $(scroll_wrapper).width()
        // At max zoom, let one Nt = 10px, this.canvas.width = (this.scale.max - this.scale.min) * 10 + this.offset * 2;
        // use this.scrollValues to calculate zoomValue
        // initialize this.scrollValues if empty
        if (this.scrollValues.length < 2) {
            // default to min zoom
            this.scrollValues = [this.scale.min, this.scale.max];
        }
        var full_range = this.scale.max - this.scale.min;
        var view_range = this.scrollValues[1] - this.scrollValues[0];
        var zoom_value = full_range / view_range;
        var scroll_wrapper_width = $(scroll_wrapper).width();
        var offset = this.offset;
        this.canvas.width = (scroll_wrapper_width - this.offset * 2) * zoom_value + this.offset * 2;
        this.width = this.canvas.width - this.offset * 2;
        scroll_wrapper.scrollLeft = (this.scrollValues[0] - this.scale.min) / full_range * this.width;
        var schart = this;
        var scroll_max = full_range * 10 + this.offset * 2;
        if (scroll_max < scroll_wrapper_width)
            scroll_max = scroll_wrapper_width;
        if (scroll_max > 32760) // nothing draws if > 32768
            scroll_max = 32760;
        jQuery(this.canvas.parentNode.previousElementSibling).slider({
            orientation: 'vertical',
            range: 'min',
            max: scroll_max,
            min: scroll_wrapper_width,
            value: this.width,
            slide: function (event, ui) {
                var ntPerPixel = full_range / (ui['value'] - offset * 2);
                var center = full_range * (scroll_wrapper.scrollLeft + scroll_wrapper_width / 2 - offset) / (schart.canvas.width - offset * 2);
                var left = center - (scroll_wrapper_width / 2 - offset) * ntPerPixel;
                var right = center + (scroll_wrapper_width / 2 - offset) * ntPerPixel;
                schart.scrollValues = [left, right];
                schart.ctx.clearRect(0, 0, schart.canvas.width, schart.canvas.height);
                schart.draw();
            }
        });
    },


    /** **determineMajorTick**
    
     * _intelligently determines a major tick interval based on size of the chart/view and size of the numbers on the scale_
    
     * @return {Int} major tick interval
     * @api internal
     */
    determineMajorTick: function () {
        this.ctx.font = this.scale.font.size + 'px arial';
        var numtimes = this.width / (this.ctx.measureText(this.getTickTextDecimalPlaces(this.scale.max)).width + this.scale.font.buffer);

        // figure out the base of the tick (e.g. 2120 => 2000)
        var irregularTick = (this.scale.max - this.scale.min) / numtimes;
        var baseNum = Math.pow(10, parseInt(irregularTick).toString().length - 1);
        this.tick.major.size = Math.ceil(irregularTick / baseNum) * baseNum;

        // round up to a 5* or 1* number (e.g 5000 or 10000)
        var digits = (this.tick.major.size + '').length;
        var places = Math.pow(10, digits);
        var first_digit = this.tick.major.size / places;

        if (first_digit > .1 && first_digit <= .5)
            first_digit = .5;
        else if (first_digit > .5)
            first_digit = 1;

        // return major tick interval
        return (first_digit * places);
    },


    /** **getTickText**
    
     * _abbreviates tick text numbers using 'k', or 'm' (e.g. 10000 becomes 10k)_
    
     * @param {Int} tickNumber - the tick number that needs to be abbreviated
     * @return {String} abbreviated tickNumber
     * @api internal
     */
    getTickText: function (tickNumber) {
        if (!this.tick.auto)
            return tickNumber;

        var tickText = tickNumber;
        if (tickNumber >= 1000000) {
            var decPlaces = 5;
            var base = Math.pow(10, decPlaces)
            tickText = Math.round(tickText / 1000000 * base) / base + 'm'; // round to decPlaces
        } else if (tickNumber >= 1000) {
            var decPlaces = 2;
            var base = Math.pow(10, decPlaces)
            tickText = Math.round(tickText / 1000 * base) / base + 'k';
        }

        return tickText;
    },

    /** **getTickTextDecimalPlaces**
    
     * _determines the tick text with decimal places_
    
     * @param {Int} tickNumber - the tick number that needs to be abbreviated
     * @return {String} abbreviated tickNumber
     * @api internal
     */
    getTickTextDecimalPlaces: function (tickNumber) {
        if (!this.tick.auto)
            return tickNumber;

        var tickText = tickNumber;
        if (tickNumber >= 1000000) {
            var decPlaces = 5;
            tickText = Math.round(tickText / (1000000 / Math.pow(10, decPlaces))) + 'm'; // round to 2 decimal places
        } else if (tickNumber >= 1000) {
            var decPlaces = 2;
            tickText = Math.round(tickText / (1000 / Math.pow(10, decPlaces))) + 'k';
        }

        return tickText;
    },

    /** **handleMouseEvent**
   
    * _handles mouse events_
   
    * @param {Object} event - triggered event
    * @param {String} type - type of event
    * @api internal
    */
    handleMouseEvent: function (e, type) {
        this.myMouseEventHandler.setMousePosition(e);
        var positionY = this.myMouseEventHandler.mouseY;
        var lane;

        for (var i = 0; i < this.tracks.length; i++) {
            for (var k = 0; k < this.tracks[i].lanes.length; k++) {
                var yt = this.tracks[i].lanes[k].getPixelPositionY();
                var yb = yt + this.tracks[i].lanes[k].getHeight();
                if (positionY >= yt && positionY <= yb) {
                    lane = this.tracks[i].lanes[k];
                    break;
                }
            }
        }

        // if mouse is not on any tracks then return
        if (!lane) return;

        var drawStyle = lane.track.getDrawStyle();

        if (drawStyle == 'collapse') {
            this.redraw();
        } else if (drawStyle == 'line') {
            // do nothing 
        } else {
            this.ctx.save();
            lane.erase();
            this.ctx.translate(0, lane.getPixelPositionY());
            lane.draw();
            var ltt;
            while (ltt = this.lastToolTips.pop()) {
                this.ctx.putImageData(ltt.pixels, ltt.x, ltt.y)
            }
            this.ctx.restore();
        }


        var chart = this;

        if (type == 'click') {
            var clicksFns = chart.events.clicks;
            for (var i = 0; i < clicksFns.length; i++)
                clicksFns[i](chart);
        } else {
            var mouseoverFns = chart.events.mouseovers;
            for (var i = 0; i < mouseoverFns.length; i++)
                mouseoverFns[i](chart);
        }

        this.myMouseEventHandler.reset(chart);


    },


    /** **addClickEventListener**
   
    * _add's function that will execute each time a feature is clicked_
   
    * @param {Function} func - function to be triggered
    * @api public
    */
    addClickEventListener: function (func) {
        this.events.clicks.push(func);
    },

    /** **addMouseoverEventListener**
   
    * _add's function that will execute each time a feature is mouseovered_
   
    * @param {Function} func - function to be triggered
    * @api public
    */
    addMouseoverEventListener: function (func) {
        this.events.mouseovers.push(func);
    },

    /** **removeEventListeners**
   
    * _remove event listerners_
   
    * @param {String} event-type - e.g. mouseover, click, etc...
    * @api internal
    */
    removeEventListeners: function (eventType) {
        if (eventType == 'mouseover')
            this.canvas.removeEventListener('mousemove', this.mouseHandler);
        else if (eventType == 'click')
            this.canvas.removeEventListener('click', this.clickHandler);
    },


    /** **registerEventListeners**
   
    * _adds event listerners_
   
    * @api internal
    */
    registerEventListeners: function () {
        var chart = this;

        if (this.events.mouseovers.length > 0) {
            this.canvas.removeEventListener('mousemove', chart.mouseHandler);
            this.canvas.addEventListener('mousemove', chart.mouseHandler, false);
        }
        if (this.events.clicks.length > 0) {
            //$(this.canvas).bind('click', function(e) {chart.handleMouseEvent(e, 'click')})
            this.canvas.removeEventListener('click', chart.clickHandler);
            this.canvas.addEventListener('click', chart.clickHandler, false);
        }
        this.events.added = true;
    }


});
/**
 * Scribl::Track
 *
 * _Tracks are used to segregrate different sequence data_
 *
 * Chase Miller 2011
 */


var Track = Class.extend({
    /** **init**

    * _Constructor_
    *
    * This is called with `new Track()`, but to create new Tracks associated with a chart use `Scribl.addTrack()`
    *
    * @param {Object} ctx - the canvas.context object
    * @api internal
    */
    init: function (chart) {
        // defaults
        var track = this;
        this.chart = chart
        this.lanes = [];
        this.ctx = chart.ctx;
        this.uid = _uniqueId('track');
        this.drawStyle = undefined;
        this.hide = false;
        this.hooks = {};

        // add draw hooks
        for (var i = 0; i < chart.trackHooks.length; i++) {
            this.addDrawHook(chart.trackHooks[i]);
        }


        // coverage variables
        this.coverageData = [];  // number of features at any given pixel;
        this.maxDepth = 0; // highest depth for this track;
    },

    /** **addLane**

    * _creates a new Lane associated with this Track_

    * @return {Object} Lane - a Lane object
    * @api public
    */
    addLane: function () {
        var lane = new Lane(this.ctx, this);
        this.lanes.push(lane);
        return lane;
    },

    /** **addGene**
   
    * _syntactic sugar function to add a feature with the gene type to this Track_
   
    * @param {Int} position - start position of the gene
    * @param {Int} length - length of the gene
    * @param {String} strand - '+' or '-' strand
    * @param {Hash} [opts] - optional hash of options that can be applied to gene  
    * @return {Object} gene - a feature with the 'gene' type
    * @api public
    */
    addGene: function (position, length, strand, opts) {
        return (this.addFeature(new BlockArrow("gene", position, length, strand, opts)));
    },

    /** **addProtein**
   
    * _syntactic sugar function to add a feature with the protein type to this Track_
   
    * @param {Int} position - start position of the protein
    * @param {Int} length - length of the protein
    * @param {String} strand - '+' or '-' strand
    * @param {Hash} [opts] - optional hash of options that can be applied to protein  
    * @return {Object} protein - a feature with the 'protein' type
    * @api public
    */
    addProtein: function (position, length, strand, opts) {
        return (this.addFeature(new BlockArrow("protein", position, length, strand, opts)));
    },

    /** **addFeature**
   
    * _addFeature to this Track and let Scribl manage lane placement to avoid overlaps_
    
    * example:
    * `track.addFeature( new Rect('complex',3500, 2000) );`
   
    * @param {Object} feature - any of the derived Glyph classes (e.g. Rect, Arrow, etc..)
    * @return {Object} feature - new feature
    * @api public        
    */
    addFeature: function (feature) {

        var curr_lane;
        var new_lane = true;

        // try to add feature at lower lanes then move up
        for (var j = 0; j < this.lanes.length; j++) {
            var prev_feature = this.lanes[j].features[this.lanes[j].features.length - 1];

            // check if new lane is needed
            var spacer = 3 / this.chart.pixelsToNts() || 3;
            if (prev_feature != undefined && (feature.position - spacer) > (prev_feature.position + prev_feature.length)) {
                new_lane = false;
                curr_lane = this.lanes[j];
                break;
            }
        }

        // add new lane if needed
        if (new_lane)
            curr_lane = this.addLane();

        // add feature
        curr_lane.addFeature(feature);
        return feature;
    },

    /** **hide**
    
     * _hides the track so it doesn't get drawn_
        
     * @api public        
     */
    hide: function () {
        this.hide = true;
    },

    /** **unhide**
   
    * _unhides the track so it is drawn_
       
    * @api public        
    */
    unhide: function () {
        this.hide = false;
    },

    /** **getDrawStyle**
   
    * _returns the draw style associated with this track_
   
    * @return {String} drawStyle - the style this track will be drawn e.g. expand, collapse, line     
    * @api public        
    */
    getDrawStyle: function () {
        if (this.drawStyle)
            return this.drawStyle
        else
            return this.chart.drawStyle;
    },

    /** **getHeight**
   
    * _returns the height of this track in pixels_
   
    * @return {Int} height
    * @api public        
    */
    getHeight: function () {
        var wholeHeight = 0;

        var numLanes = this.lanes.length;
        var laneBuffer = this.chart.laneBuffer;
        var drawStyle = this.getDrawStyle();
        if (drawStyle == 'line' || drawStyle == 'collapse')
            numLanes = 1;

        for (var i = 0; i < numLanes; i++) {
            wholeHeight += laneBuffer;
            wholeHeight += this.lanes[i].getHeight();
        }
        // subtract 1 laneBuffer b\c laneBuffers are between lanes
        wholeHeight -= laneBuffer;

        return wholeHeight;
    },

    /** **getPixelPositionY**
   
    * _gets the number of pixels from the top of the chart to the top of this track_
   
    * @return {Int} pixelPositionY
    * @api public        
    */
    getPixelPositionY: function () {
        var track = this;
        var y;

        if (!track.chart.scale.off)
            y = track.chart.getScaleHeight() + track.chart.laneBuffer;
        else
            y = 0;

        for (var i = 0; i < track.chart.tracks.length; i++) {
            if (track.uid == track.chart.tracks[i].uid) break;
            y += track.chart.trackBuffer;
            y += track.chart.tracks[i].getHeight();
        }

        return y;
    },

    /** **calcCoverageData**
   
    * _calculates the coverage (the number of features) at each pixel_
    *
    * @api internal    
    */
    calcCoverageData: function () {
        var lanes = this.lanes
        var min = this.chart.scale.min;
        var max = this.chart.scale.max;

        // determine feature locations
        for (var i = 0; i < lanes.length; i++) {
            for (var k = 0; k < lanes[i].features.length; k++) {
                var feature = lanes[i].features[k];
                var pos = feature.position;
                var end = feature.getEnd();
                if ((pos >= min && pos <= max) || (end >= min && end <= max)) {
                    var from = Math.round(feature.getPixelPositionX());
                    var to = Math.round(from + feature.getPixelLength());
                    for (var j = from; j <= to; j++) {
                        this.coverageData[j] = this.coverageData[j] + 1 || 1;
                        this.maxDepth = Math.max(this.coverageData[j], this.maxDepth);
                    }
                }
            }
        }
    },

    /** **erase**
    
     * _erases this track_
     *
     * @api internal    
     */
    erase: function () {
        var track = this;
        track.chart.ctx.clearRect(0, track.getPixelPositionY(), track.chart.width, track.getHeight());
    },

    /** **draw**
   
    * _draws Track_
   
    * @api internal   
    */
    draw: function () {
        var track = this;

        // execute hooks
        var dontDraw = false;
        for (var i in track.hooks) {
            dontDraw = track.hooks[i](track) || dontDraw;
        }

        // check if track is waiting and if so do nothing
        if (track.status == 'waiting') {
            track.drawOnResponse = true;
            return;
        }

        // check if track shouldn't be drawn
        if (track.hide)
            return;

        var style = track.getDrawStyle();
        var laneSize = track.chart.laneSizes;
        var lanes = track.lanes;
        var laneBuffer = track.chart.laneBuffer;
        var trackBuffer = track.chart.trackBuffer;
        var y = laneSize + trackBuffer;
        var ctx = track.chart.ctx;

        if (!dontDraw) {

            // draw lanes

            // draw expanded/default style
            if (style == undefined || style == 'expand') {
                for (var i = 0; i < lanes.length; i++) {
                    lanes[i].y = y;
                    if (lanes[i].draw()) {
                        var height = lanes[i].getHeight();
                        ctx.translate(0, height + laneBuffer);
                        y = y + height + laneBuffer;
                    }
                }
            } else if (style == 'collapse') { // draw collapse style (i.e. single lane)
                var features = [];

                // concat all features into single array
                for (var i = 0; i < lanes.length; i++) {
                    features = features.concat(lanes[i].filterFeaturesByPosition(track.chart.scale.min, track.chart.scale.max));
                }
                // sort features so the minimal number of lanes are used
                features.sort(function (a, b) { return (a.position - b.position); });
                for (var j = 0; j < features.length; j++) {
                    var originalLength = features[j].length;
                    var originalName = features[j].name;
                    var m = undefined;
                    // for( m=j+1; m < features.length; m++) {
                    //    // if a feature is overlapping change length to draw as a single feature
                    //    if (features[j].getEnd() >= features[m].position) {
                    //       features[j].length = Math.max(features[j].getEnd(), features[m].getEnd()) - features[j].position;
                    //       features[j].name = "";
                    //    } else break;
                    // }               
                    // draw
                    features[j].draw();
                    // put length and name back to correct values
                    features[j].length = originalLength;
                    features[j].name = originalName;
                    // update j to skip features that were merged
                    //  j = m-1;
                }
                // translate down to next lane to draw
                if (lanes.length > 0)
                    ctx.translate(0, lanes[0].getHeight() + laneBuffer);

                // draw as a line chart of the coverage
            } else if (style == 'line') {
                track.coverageData = [];
                if (track.coverageData.length == 0) track.calcCoverageData();

                var normalizationFactor = this.maxDepth;

                ctx.beginPath();
                //         ctx.moveTo(this.chart.offset, laneSize);
                for (var k = this.chart.offset; k <= this.chart.width + this.chart.offset; k++) {
                    var normalizedPt = track.coverageData[k] / normalizationFactor * laneSize || 0;
                    normalizedPt = laneSize - normalizedPt;
                    ctx.lineTo(k, normalizedPt);
                }
                ctx.lineTo(this.chart.width + this.chart.offset, laneSize)
                //		   ctx.lineTo(this.chart.offset, laneSize);
                ctx.stroke();
                ctx.translate(0, lanes[0].getHeight() + laneBuffer);
            }
        }

        // add track buffer - extra laneBuffer
        ctx.translate(0, trackBuffer - laneBuffer);

    },

    /** **addDrawHook**
    
     * _add function that executes before the track is drawn_
     
     * @param {Function} function - takes track as param, returns true to stop the normal draw, false to allow
     * @return {Int} id - returns the uniqe id for the hook which is used to remove it
     * @api public 
     */

    addDrawHook: function (fn, hookId) {
        var uid = hookId || _uniqueId('drawHook');
        this.hooks[uid] = fn;
        return uid;
    },

    /** **removeDrawHook**
    
     * _removes function that executes before the track is drawn_
     
     * @param {Int} id - the id of drawHook function that will be removed
     * @api public 
     */

    removeDrawHook: function (uid) {
        delete this.hooks[uid];
    }

});
/**
 * **Scribl::Lane**
 *
 * _A lane is used to draw features on a single y position_
 *
 * Chase Miller 2011
 */


var Lane = Class.extend({
    /** **init**

    * _Constructor_
    *
    * This is called with `new Lane()`, but to create new Lanes associated with a chart use `track.addLane()`
    *
    * @param {Object} ctx - the canvas.context object
    * @param {Object} track - track that this lane belongs to
    * @api internal
    */
    init: function (ctx, track) {
        // defaults
        this.height = undefined;
        this.features = [];
        this.ctx = ctx;
        this.track = track;
        this.chart = track.chart;
        this.uid = _uniqueId('lane');
    },


    /** **addGene**
   
    * _syntactic sugar function to add a feature with the gene type to this Lane_
   
    * @param {Int} position - start position of the gene
    * @param {Int} length - length of the gene
    * @param {String} strand - '+' or '-' strand
    * @param {Hash} [opts] - optional hash of options that can be applied to gene  
    * @return {Object} gene - a feature with the 'gene' type      
    * @api public
    */
    addGene: function (position, length, strand, opts) {
        return (this.addFeature(new BlockArrow("gene", position, length, strand, opts)));
    },

    /** **addProtein**
   
    * _syntactic sugar function to add a feature with the protein type to this Lane_
   
    * @param {Int} position - start position of the protein
    * @param {Int} length - length of the protein
    * @param {String} strand - '+' or '-' strand
    * @param {Hash} [opts] - optional hash of options that can be applied to protein  
    * @return {Object} protein - a feature with the 'protein' type
    * @api public
    */
    addProtein: function (position, length, strand, opts) {
        return (this.addFeature(new BlockArrow("protein", position, length, strand, opts)));
    },

    /** **addFeature**
   
    * _addFeature to this Lane, allowing potential overlaps_
    
    * example:
    * `lane.addFeature( new Rect('complex',3500, 2000) );`
   
    * @param {Object} feature - any of the derived Glyph classes (e.g. Rect, Arrow, etc..)
    * @return {Object} feature - new feature
    * @api public        
    */
    addFeature: function (feature) {

        // create feature
        feature.lane = this;
        this.features.push(feature);

        // initialize hash containers for "type" level options
        if (!this.chart[feature.type]) {
            this.chart[feature.type] = { 'text': {} }
        }

        // determine chart absolute_min and absolute_max
        if (feature.length + feature.position > this.chart.scale.max || !this.chart.scale.max)
            this.chart.scale.max = feature.length + feature.position;
        if (feature.position < this.chart.scale.min || !this.chart.scale.min)
            this.chart.scale.min = feature.position;

        return feature;
    },

    /** **loadFeatures**
   
    * _adds the features to this Lane_
   
    * @param {Array} features - array of features, which can be any of the derived Glyph classes (e.g. Rect, Arrow, etc..)
    * @api public
    */
    loadFeatures: function (features) {
        var featureNum = features.length;
        for (var i = 0; i < featureNum; i++)
            this.addFeature(features[i]);
    },

    /** **getHeight**
   
    * _returns the height of this lane in pixels_
   
    * @return {Int} height
    * @api public        
    */
    getHeight: function () {
        if (this.height != undefined)
            return this.height;
        else
            return this.chart.laneSizes;
    },

    /** **getPixelPositionY**
   
    * _gets the number of pixels from the top of the chart to the top of this lane_
   
    * @return {Int} pixelPositionY
    * @api public        
    */
    getPixelPositionY: function () {
        var lane = this;
        var y = lane.track.getPixelPositionY();
        var laneHeight = lane.getHeight();
        for (var i = 0; i < lane.track.lanes.length; i++) {
            if (lane.uid == lane.track.lanes[i].uid) break;
            y += lane.track.chart.laneBuffer;
            y += laneHeight;
        }

        return y;
    },

    /** **erase**
    
     * _erases this lane_
     *
     * @api internal    
     */
    erase: function () {
        var lane = this;
        lane.chart.ctx.clearRect(0, lane.getPixelPositionY(), lane.track.chart.canvas.width, lane.getHeight());
    },

    /** **draw**
   
    * _draws lane_
   
    * @api internal
    */
    draw: function () {
        var min = this.track.chart.scale.min;
        var max = this.track.chart.scale.max;
        var hasGlyphs = false;
        for (var i = 0; i < this.features.length; i++) {
            var pos = this.features[i].position;
            var end = this.features[i].getEnd();
            if (pos >= min && pos <= max || end >= min && end <= max) {
                this.features[i].draw();
                hasGlyphs = true;
            }
        }
        return hasGlyphs;
    },

    /** **filterFeaturesByPosition**
    
    * _returns an array of features that fall inside a given range_
    
    * @param {Int} start - the start of the range
    * @param {Int} end - the end of the range
    * @return {Array} features - the features that any part of which fall inside that range
    * @api public
    */

    filterFeaturesByPosition: function (start, end) {
        var lane = this;
        var features = [];
        var numFeatures = lane.features.length;

        for (var i = 0; i < numFeatures; i++) {
            var ftStart = lane.features[i].position;
            var ftEnd = lane.features[i].getEnd();

            if ((ftStart >= start && ftStart <= end) || (ftEnd >= start && ftEnd <= end))
                features.push(lane.features[i]);
        }

        return features;
    }
});
/**
 * **Scribl::Tooltips**
 *
 * _Adds event support to Scribl_
 *
 * Chase Miller 2011
 */


var Tooltip = Class.extend({
    /** **init**
 
     * _Constructor, call this with `new tooltips()`_
 
     * @param {Object} chart - Scribl object
     * @return {Object} tooltip object
     * @api internal
     */
    init: function (text, placement, verticalOffset, opts) {
        var tt = this;
        tt.text = text;
        tt.placement = placement || 'above';
        tt.verticalOffset = verticalOffset || 0;
        // set option attributes if any
        for (var attribute in opts)
            tt[attribute] = opts[attribute];

        tt.horizontalOffset = tt.horizontalOffset || 0;
        tt.ntOffset = tt.ntOffset || 0;

    },

    /** **fire**

    * _fires the tooltip_

    * @param {Object} feature - any of the derived Glyph classes (e.g. Rect, Arrow, etc..)
    * @api internal
    */

    fire: function (ft) {
        // get curr opacity
        var feature = ft || this.feature;
        this.chart = feature.lane.track.chart;
        this.ctx = this.chart.ctx;

        this.draw(feature, 1);

    },

    /** **draw**

    * _draws tooltip_

    * @param {Object} feature - any of the derived Glyph classes (e.g. Rect, Arrow, etc..)
    * @param {Int} opacity
    * @api internal
    */
    draw: function (feature, opacity) {
        this.ctx.globalAlpha = opacity;

        // define attributes
        var roundness = this.chart.tooltips.roundness;
        var font = this.chart.tooltips.text.font;
        var fontSize = this.chart.tooltips.text.size;
        var text = this.text || feature.onMouseover;

        // Save
        this.ctx.save();

        this.ctx.font = fontSize + "px " + font;

        // determine properties of line
        var dim = this.ctx.measureText(text);
        var textlines = [text];
        var height = fontSize + 10;
        var length = dim.width + 10;
        var vertical_offset = height - 4;
        var fillStyle;
        var strokeStyle;

        // determine nt offset
        var ntOffsetPx = 0;
        if (feature.seq) {
            var lengthPx = feature.getPixelLength();
            ntOffsetPx = this.ntOffset * (lengthPx / feature.length);
        }

        // Get coordinates
        var x = feature.getPixelPositionX() + this.horizontalOffset + ntOffsetPx;
        var y;
        if (this.placement == 'below')
            y = feature.getPixelPositionY() + feature.getHeight() - this.verticalOffset;
        else
            y = feature.getPixelPositionY() - height - this.verticalOffset;




        // var x = feature.getPixelPositionX();
        // var y = feature.getPixelPositionY() + feature.getHeight();


        // linewrap text
        var geneLength = feature.getPixelLength();
        var mincols = 200;
        if (length > mincols) {
            var charpixel = this.ctx.measureText("s").width;
            var max = parseInt(mincols / charpixel);
            var formattedText = ScriblWrapLines(max, text);
            length = mincols + 10;
            height = formattedText[1] * fontSize + 10;
            textlines = formattedText[0];
        }

        // check if tooltip will run off screen
        if (length + x > this.chart.width)
            x = this.chart.width - length;

        // draw light style
        if (this.chart.tooltips.style == "light") {
            fillStyle = this.chart.ctx.createLinearGradient(x + length / 2, y, x + length / 2, y + height);
            fillStyle.addColorStop(0, 'rgb(253, 248, 196)');
            fillStyle.addColorStop(.75, 'rgb(253, 248, 196)');
            fillStyle.addColorStop(1, 'white');

            strokeStyle = this.chart.ctx.createLinearGradient(x + length / 2, y, x + length / 2, y + height);
            strokeStyle.addColorStop(0, 'black');
            strokeStyle.addColorStop(1, 'rgb(64, 64, 64)');

            this.chart.tooltips.text.color = "black";

            // draw dark style	
        } else if (this.chart.tooltips.style == "dark") {
            fillStyle = this.chart.ctx.createLinearGradient(x + length / 2, y, x + length / 2, y + height);
            fillStyle.addColorStop(0, 'rgb(64, 64, 64)');
            fillStyle.addColorStop(1, 'rgb(121, 121, 121)');

            strokeStyle = "white";
            this.chart.tooltips.text.color = "white";
        }

        this.chart.lastToolTips.push({
            'pixels': this.ctx.getImageData(x - 1, y - 1, length + 2, height + 2),
            'x': x - 1,
            'y': y - 1
        });

        this.ctx.fillStyle = fillStyle;

        this.ctx.beginPath();

        // calculate points

        // top left corner
        tlc_ctrl_x = x; 				// control point
        tlc_ctrl_y = y;
        tlc_lgth_x = x + roundness; 	// horizontal point
        tlc_lgth_y = y;
        tlc_wdth_x = x;				// vertical point
        tlc_wdth_y = y + roundness;

        // bottom left corner
        blc_ctrl_x = x; 				// control point
        blc_ctrl_y = y + height;
        blc_lgth_x = x + roundness; 	// horizontal point
        blc_lgth_y = y + height;
        blc_wdth_x = x;				// vertical point
        blc_wdth_y = y + height - roundness;

        // bottom right corner
        brc_ctrl_x = x + length; 				// control point
        brc_ctrl_y = y + height;
        brc_lgth_x = x + length - roundness; 	// horizontal point
        brc_lgth_y = y + height;
        brc_wdth_x = x + length;				// vertical point
        brc_wdth_y = y + height - roundness;

        // top right corner
        trc_ctrl_x = x + length; 				// control point
        trc_ctrl_y = y;
        trc_lgth_x = x + length - roundness; 	// horizontal point
        trc_lgth_y = y;
        trc_wdth_x = x + length;				// vertical point
        trc_wdth_y = y + roundness;


        // draw lines

        // top left corner
        this.ctx.moveTo(tlc_lgth_x, tlc_lgth_y);
        this.ctx.quadraticCurveTo(tlc_ctrl_x, tlc_ctrl_y, tlc_wdth_x, tlc_wdth_y);

        // bottom left corner
        this.ctx.lineTo(blc_wdth_x, blc_wdth_y);
        this.ctx.quadraticCurveTo(blc_ctrl_x, blc_ctrl_y, blc_lgth_x, blc_lgth_y);

        // bottom right corner
        this.ctx.lineTo(brc_lgth_x, brc_lgth_y);
        this.ctx.quadraticCurveTo(brc_ctrl_x, brc_ctrl_y, brc_wdth_x, brc_wdth_y);

        // top right corner
        this.ctx.lineTo(trc_wdth_x, trc_wdth_y);
        this.ctx.quadraticCurveTo(trc_ctrl_x, trc_ctrl_y, trc_lgth_x, trc_lgth_y);

        // top line
        this.ctx.lineTo(tlc_lgth_x, tlc_lgth_y);
        this.ctx.fill();
        this.ctx.lineWidth = this.chart.tooltips.borderWidth;
        this.ctx.strokeStyle = strokeStyle;
        this.ctx.stroke();

        // draw text;
        this.ctx.textBaseline = "middle";
        this.ctx.fillStyle = this.chart.tooltips.text.color;
        for (var i = 0; i < textlines.length; i++) {
            var dim = this.ctx.measureText(textlines[i]);
            this.ctx.fillText(textlines[i], x + 5, y + fontSize * (i + 1));
        }

        this.ctx.restore();

    }
});/**
 * **Scribl::Events**
 *
 * _Adds event support to Scribl_
 *
 * Chase Miller 2011
 */

var MouseEventHandler = Class.extend({
    /** **init**
 
     * _Constructor, call this with `new MouseEventHandler()`_
 
     * @param {Object} chart - Scribl object
     * @return {Object} MouseEventHandler object
     * @api internal
     */
    init: function (chart) {
        this.chart = chart;
        this.mouseX = null;
        this.mouseY = null;
        this.eventElement = undefined;
        this.isEventDetected = false;
        this.tooltip = new Tooltip("", 'above', -4);
    },

    /** **addEvents**
 
     * _registers event listeners if feature (or parent if part of complex feature) has mouse events associated with it_
 
     * @param {Object} feature - any of the derived Glyph classes (e.g. Rect, Arrow, etc..)
     * @api internal
     */
    addEvents: function (feature) {
        var chart = this.chart;
        var ctx = chart.ctx;
        var me = chart.myMouseEventHandler;

        // check if any features use onmouseover and if so register an event listener if not already done
        if (feature.onMouseover && !chart.events.hasMouseover) {
            chart.addMouseoverEventListener(chart.myMouseEventHandler.handleMouseover);
            chart.events.hasMouseover = true;
        }
        else if (feature.tooltips.length > 0 && !chart.events.hasMouseover) {
            chart.addMouseoverEventListener(chart.myMouseEventHandler.handleMouseover);
            chart.events.hasMouseover = true;
        }
        else if (feature.parent && feature.parent.tooltips.length > 0 && !chart.events.hasMouseover) {
            chart.addMouseoverEventListener(chart.myMouseEventHandler.handleMouseover);
            chart.events.hasMouseover = true;
        }
        else if (feature.parent && feature.parent.onMouseover && !chart.events.hasMouseover) {
            chart.addMouseoverEventListener(chart.myMouseEventHandler.handleMouseover);
            chart.events.hasMouseover = true;
        }

        // check if any features use onclick and if so register event listeners if not already done
        if (feature.onClick && !chart.events.hasClick) {
            chart.addClickEventListener(chart.myMouseEventHandler.handleClick);
            chart.addMouseoverEventListener(chart.myMouseEventHandler.handleMouseStyle);
            chart.events.hasClick = true;
        } else if (feature.parent && feature.parent.onClick && !chart.events.hasClick) {
            chart.addClickEventListener(chart.myMouseEventHandler.handleClick);
            chart.addMouseoverEventListener(chart.myMouseEventHandler.handleMouseStyle);
            chart.events.hasClick = true;
        }

        // determine if cursor is currently in a drawn object (feature)
        if (!me.isEventDetected && ctx.isPointInPath_mozilla(me.mouseX, me.mouseY)) {
            me.eventElement = feature;
            me.isEventDetected = true;
        }
    },

    /** **setMousePosition**
 
     * _sets the mouse position relative to the canvas_
 
     * @param {Object} e - event
     * @api internal
     */
    setMousePosition: function (e) {
        if (e != null) {
            var rect = this.chart.canvas.getBoundingClientRect();
            this.mouseX = e.clientX - rect.left;
            this.mouseY = e.clientY - rect.top;
        }
    },

    /** **handleClick**

    * _gets called when there is a click and determines how to handle it_

    * @param {Object} chart - Scribl object
    * @api internal
    */
    handleClick: function (chart) {
        var me = chart.myMouseEventHandler;
        var clicked = me.eventElement;
        var onClick;

        // check if the click occured on a feature/object with an onClick property
        if (clicked != undefined && clicked.onClick != undefined)
            onClick = clicked.onClick
        else if (clicked && clicked.parent && clicked.parent.onClick)
            onClick = clicked.parent.onClick

        if (onClick) {
            // open window if string
            if (typeof (onClick) == "string") { window.open(onClick); }
                // if function run function with feature as argument
            else if (typeof (onClick) == "function") { onClick(clicked); }
        }
    },

    /** **handleMouseover**

    * _gets called when there is a mouseover and fires tooltip if necessary_

    * @param {Object} chart - Scribl object
    * @api internal
    */
    handleMouseover: function (chart) {
        var me = chart.myMouseEventHandler;
        var clicked = me.eventElement;

        // handle mouseover tooltips
        if (clicked && clicked.onMouseover == undefined && clicked.parent && clicked.parent.onMouseover) {
            clicked.onMouseover = clicked.parent.onMouseover
        }

        if (clicked && clicked.onMouseover) {
            // open window if string
            if (typeof (clicked.onMouseover) == "string") { me.tooltip.fire(clicked); }
                // if function run function with feature as argument
            else if (typeof (clicked.onMouseover) == "function") { clicked.onMouseover(clicked); }
        }

        // handle tooltip object tooltips
        if (clicked && clicked.tooltips.length > 0)
            clicked.fireTooltips();
    },

    /** **handleMouseStyle**

    * _changes cursor to pointer if the feature the mouse is over can be clicked_

    * @param {Object} chart - Scribl object
    * @api internal
    */
    handleMouseStyle: function (chart) {
        var me = chart.myMouseEventHandler;
        var obj = me.eventElement;
        var ctx = chart.ctx;

        if (obj && obj.onClick != undefined)
            ctx.canvas.style.cursor = 'pointer';
        else if (obj && obj.parent && obj.parent.onClick != undefined)
            ctx.canvas.style.cursor = 'pointer';
        else
            ctx.canvas.style.cursor = 'auto';
    },

    /** **reset**
 
     * _resets the state of the mouseEventHandler_
 
     * @param {Object} chart - Scribl object
     * @api internal
     */
    reset: function (chart) {
        var me = chart.myMouseEventHandler;
        me.mouseX = null;
        me.mouseY = null;
        me.eventElement = undefined;
        me.isEventDetected = null;
        me.elementIndexCounter = 0;
    }

});

// FIX FOR FIREFOX BUG in ctx.isPointInPath() function
CanvasRenderingContext2D.prototype.isPointInPath_mozilla = function (x, y) {
    if (navigator.userAgent.indexOf('Firefox') != -1) {
        this.save();
        this.setTransform(1, 0, 0, 1, 0, 0);
        var ret = this.isPointInPath(x, y);
        this.restore();
    } else
        var ret = this.isPointInPath(x, y);

    return ret;
}
/**
 * **Scribl::Utils**
 *
 * Chase Miller 2011
 */

/** **ScriblWrapLines**

* _transforms text to fit in a column of given width_

* @param {Int} max - column width in letters
* @param {String} text
* @return {String} formatted text
* @api internal
*/
function ScriblWrapLines(max, text) {
    var lines = [];
    text = "" + text;
    var temp = "";
    var chcount = 0;
    var linecount = 0;
    var words = text.split(" ");

    for (var i = 0; i < words.length; i++) {
        if ((words[i].length + temp.length) <= max)
            temp += " " + words[i]
        else {
            // word is bigger than line break
            if (temp == "") {
                trunc1 = words[i].slice(0, max - 1);
                temp += " " + trunc1 + "-"
                trunc2 = words[i].slice(max, words[i].length);
                words.splice(i + 1, 0, trunc2);
                lines.push(temp);
                temp = "";
                linecount++;
            }
            else {
                i--;
                lines.push(temp);
                linecount++;
                temp = "";
            }
        }
    }
    linecount++;
    lines.push(temp)
    return ([lines, linecount]); // sends value of temp back
}


/** create unique ids */
var idCounter = 0;
_uniqueId = function (prefix) {
    var id = idCounter++;
    return prefix ? prefix + id : id;
};

// polyfill for older browsers
Object.keys = Object.keys || function (o, k, r) { r = []; for (k in o) r.hasOwnProperty.call(o, k) && r.push(k); return r }


/** add indexOf if not implemented for compatibility
    with older browsers
*/
if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function (searchElement /*, fromIndex */) {
        "use strict";
        if (this === void 0 || this === null) {
            throw new TypeError();
        }
        var t = Object(this);
        var len = t.length >>> 0;
        if (len === 0) {
            return -1;
        }
        var n = 0;
        if (arguments.length > 0) {
            n = Number(arguments[1]);
            if (n !== n) { // shortcut for verifying if it's NaN  
                n = 0;
            } else if (n !== 0 && n !== Infinity && n !== -Infinity) {
                n = (n > 0 || -1) * Math.floor(Math.abs(n));
            }
        }
        if (n >= len) {
            return -1;
        }
        var k = n >= 0 ? n : Math.max(len - Math.abs(n), 0);
        for (; k < len; k++) {
            if (k in t && t[k] === searchElement) {
                return k;
            }
        }
        return -1;
    }
}/** 
 * utility functions for converting canvas to svg
 */


var CanvasToSVG = {
    idCounter: 0,
    convert: function (sourceCanvas, targetSVG, x, y) {
        var svgNS = "http://www.w3.org/2000/svg";
        var xlinkNS = "http://www.w3.org/1999/xlink";

        // get base64 encoded png from Canvas
        var image = sourceCanvas.toDataURL();

        // must be careful with the namespaces
        var svgimg = document.createElementNS(svgNS, "image");

        svgimg.setAttribute('id', 'importedCanvas_' + this.idCounter++);
        svgimg.setAttributeNS(xlinkNS, 'xlink:href', image);

        svgimg.setAttribute('x', x ? x : 0);
        svgimg.setAttribute('y', y ? y : 0);
        svgimg.setAttribute('width', sourceCanvas.width);
        svgimg.setAttribute('height', sourceCanvas.height);

        // pixel data needs to be saved because of firefox data:// url bug:
        // http://markmail.org/message/o2kd3bnnv3vcbwb2
        svgimg.imageData = sourceCanvas.toDataURL();

        targetSVG.appendChild(svgimg);
    }
}


var toXml = function (str) {
    return $('<p/>').text(str).html();
};

// Function: svgCanvasToString
// Main function to set up the SVG content for output 
//
// Returns: 
// String containing the SVG image for output

var svgToString = function (svgcontent) {
    // keep calling it until there are none to remove
    while (removeUnusedDefElems() > 0) { };

    pathActions.clear(true);

    // Keep SVG-Edit comment on top
    $.each(svgcontent.childNodes, function (i, node) {
        if (i && node.nodeType == 8 && node.data.indexOf('Created with') >= 0) {
            svgcontent.insertBefore(node, svgcontent.firstChild);
        }
    });

    // Move out of in-group editing mode
    if (current_group) {
        leaveContext();
        selectOnly([current_group]);
    }

    var naked_svgs = [];

    // Unwrap gsvg if it has no special attributes (only id and style)
    $(svgcontent).find('g:data(gsvg)').each(function () {
        var attrs = this.attributes;
        var len = attrs.length;
        for (var i = 0; i < len; i++) {
            if (attrs[i].nodeName == 'id' || attrs[i].nodeName == 'style') {
                len--;
            }
        }
        // No significant attributes, so ungroup
        if (len <= 0) {
            var svg = this.firstChild;
            naked_svgs.push(svg);
            $(this).replaceWith(svg);
        }
    });

    var output = svgToString(svgcontent, 0);

    // Rewrap gsvg
    if (naked_svgs.length) {
        $(naked_svgs).each(function () {
            groupSvgElem(this);
        });
    }

    return output;
}

// Function: svgToString
// Sub function ran on each SVG element to convert it to a string as desired
// 
// Parameters: 
// elem - The SVG element to convert
// indent - Integer with the amount of spaces to indent this tag
//
// Returns: 
// String with the given element as an SVG tag
var svgToString = function (elem, indent) {
    var out = new Array();//, toXml;// = Utils.toXml;

    if (elem) {
        //cleanupElement(elem);
        var attrs = elem.attributes,
			attr,
			i,
			childs = elem.childNodes;

        for (var i = 0; i < indent; i++) out.push(" ");
        out.push("<"); out.push(elem.nodeName);
        if (elem.id == 'svgcontent') {
            // Process root element separately
            var res = getResolution();
            out.push(' width="' + res.w + '" height="' + res.h + '" xmlns="' + svgns + '"');

            var nsuris = {};

            // Check elements for namespaces, add if found
            $(elem).find('*').andSelf().each(function () {
                var el = this;
                $.each(this.attributes, function (i, attr) {
                    var uri = attr.namespaceURI;
                    if (uri && !nsuris[uri] && nsMap[uri] !== 'xmlns' && nsMap[uri] !== 'xml') {
                        nsuris[uri] = true;
                        out.push(" xmlns:" + nsMap[uri] + '="' + uri + '"');
                    }
                });
            });

            var i = attrs.length;
            while (i--) {
                attr = attrs.item(i);
                var attrVal = toXml(attr.nodeValue);

                // Namespaces have already been dealt with, so skip
                if (attr.nodeName.indexOf('xmlns:') === 0) continue;

                // only serialize attributes we don't use internally
                if (attrVal != "" &&
					['width', 'height', 'xmlns', 'x', 'y', 'viewBox', 'id', 'overflow'].indexOf(attr.localName) == -1) {

                    if (!attr.namespaceURI || nsMap[attr.namespaceURI]) {
                        out.push(' ');
                        out.push(attr.nodeName); out.push("=\"");
                        out.push(attrVal); out.push("\"");
                    }
                }
            }
        } else {
            for (var i = attrs.length - 1; i >= 0; i--) {
                attr = attrs.item(i);
                var attrVal = toXml(attr.nodeValue);
                //remove bogus attributes added by Gecko
                if (['-moz-math-font-style', '_moz-math-font-style'].indexOf(attr.localName) >= 0) continue;
                if (attrVal != "") {
                    if (attrVal.indexOf('pointer-events') === 0) continue;
                    if (attr.localName === "class" && attrVal.indexOf('se_') === 0) continue;
                    out.push(" ");
                    if (attr.localName === 'd') attrVal = pathActions.convertPath(elem, true);
                    //if(!isNaN(attrVal)) {
                    //	attrVal = shortFloat(attrVal);
                    //}

                    // Embed images when saving 
                    // if(save_options.apply
                    //    && elem.nodeName === 'image' 
                    //    && attr.localName === 'href'
                    //    && save_options.images
                    //    && save_options.images === 'embed') 
                    // {
                    //    var img = encodableImages[attrVal];
                    //    if(img) attrVal = img;
                    // }

                    // map various namespaces to our fixed namespace prefixes
                    // (the default xmlns attribute itself does not get a prefix)
                    //	if(!attr.namespaceURI || attr.namespaceURI == svgns || nsMap[attr.namespaceURI]) {
                    out.push(attr.nodeName); out.push("=\"");
                    out.push(attrVal); out.push("\"");
                    //	}
                }
            }
        }

        if (elem.hasChildNodes()) {
            out.push(">");
            indent++;
            var bOneLine = false;

            for (var i = 0; i < childs.length; i++) {
                var child = childs.item(i);
                switch (child.nodeType) {
                    case 1: // element node
                        out.push("\n");
                        out.push(svgToString(childs.item(i), indent));
                        break;
                    case 3: // text node
                        var str = child.nodeValue.replace(/^\s+|\s+$/g, "");
                        if (str != "") {
                            bOneLine = true;
                            out.push(toXml(str) + "");
                        }
                        break;
                    case 8: // comment
                        out.push("\n");
                        out.push(new Array(indent + 1).join(" "));
                        out.push("<!--");
                        out.push(child.data);
                        out.push("-->");
                        break;
                } // switch on node type
            }
            indent--;
            if (!bOneLine) {
                out.push("\n");
                for (var i = 0; i < indent; i++) out.push(" ");
            }
            out.push("</"); out.push(elem.nodeName); out.push(">");
        } else {
            out.push("/>");
        }
    }
    return out.join('');
}; // end svgToString()


/**
 * **Scribl::Glyph**
 *
 * _Generic glyph class that should not be used directly. 
 * All feature classes (e.g. Rect, arrow, etc..) inherit
 * from this class_
 *
 * Chase Miller 2011
 *
 */

var Glyph = Class.extend({
    /** **init**
 
     * _Constructor, call this with `new Glyph()`_
     * This method must be called in all feature subclasses like so `this._super(type, pos, length, strand, opts)` 
     
     * @param {String} type - a tag to associate this glyph with
     * @param {Int} position - start position of the glyph
     * @param {Int} length - length of the glyph
     * @param {String} strand - '+' or '-' strand
     * @param {Hash} [opts] - optional hash of attributes that can be applied to glyph
     * @api internal
     */
    init: function (type, pos, length, strand, opts) {
        var glyph = this;

        // set unique id
        this.uid = _uniqueId('feature');

        // set variables
        glyph.position = pos;
        glyph.length = length;
        glyph.strand = strand;
        // this is used for all attributes at the chart level (e.g. chart.gene.color = "blue" )
        this.type = type;
        glyph.opts = {};

        glyph.name = "";
        glyph.borderColor = "none";
        glyph.borderWidth = undefined;
        glyph.ntLevel = 4; // in pixels - sets the level at which glyphs are rendered as actual nucleotides instead of icons
        glyph.tooltips = [];
        glyph.hooks = {};

        // add seq hook
        glyph.addDrawHook(function (theGlyph) {
            if (theGlyph.ntLevel != undefined && theGlyph.seq && theGlyph.lane.chart.ntsToPixels() < theGlyph.ntLevel) {
                var s = new Seq(theGlyph.type, theGlyph.position, theGlyph.length, theGlyph.seq, theGlyph.opts);
                s.lane = theGlyph.lane;
                s.ctx = theGlyph.ctx;
                s._draw();
                // return true to stop normal drawing of glyph
                return true;
            }
            // return false to allow normal draing of glyph
            return false;
        }, "ntHook");

        // initialize font variables
        glyph.text = {};
        // unset defaults that can be used to override chart defaults for specific glyphs
        glyph.text.font = undefined; // default: 'arial'
        glyph.text.size = undefined;  // default: '15' in pixels 
        glyph.text.color = undefined; // default: 'black'
        glyph.text.align = undefined; // default: 'middle'		

        glyph.onClick = undefined;
        glyph.onMouseover = undefined;

        // set option attributes if any
        for (var attribute in opts) {
            glyph[attribute] = opts[attribute];
            glyph.opts[attribute] = opts[attribute];
        }

    },

    /** **setColorGradient**
 
     * _creates a gradient given a list of colors_
     
     * @param {List} colors - takes as many colors as you like
     * @api public
     */
    setColorGradient: function () {
        if (arguments.length == 1) {
            this.color = arguments[0];
            return;
        }
        var lineargradient = this.lane.ctx.createLinearGradient(this.length / 2, 0, this.length / 2, this.getHeight());
        var color;
        for (var i = 0; color = arguments[i], i < arguments.length; i++) {
            lineargradient.addColorStop(i / (arguments.length - 1), color);
        }
        this.color = lineargradient;
    },

    /** **getPixelLength**
   
    * _gets the length of the glyph/feature in pixels_
   
    * @return {Int} length - in pixels
    * @api public        
    */
    getPixelLength: function () {
        var glyph = this;
        return (glyph.lane.chart.pixelsToNts(glyph.length) || 1);
    },


    /** **getPixelPositionx**
    
     * _gets the number of pixels from the left of the chart to the left of this glyph/feature_
    
     * @return {Float} positionX - in pixels
     * @api public        
     */
    getPixelPositionX: function () {
        var glyph = this;
        var offset = parseInt(glyph.lane.track.chart.offset) || 0;
        if (glyph.parent)
            var position = glyph.position + glyph.parent.position - glyph.lane.track.chart.scale.min;
        else
            var position = glyph.position - glyph.lane.track.chart.scale.min;
        return (glyph.lane.track.chart.pixelsToNts(position) + offset);
    },

    /** **getPixelPositionY**
   
    * _gets the number of pixels from the top of the chart to the top of this glyph/feature_
   
    * @return {Float} positionY - in pixels
    * @api public        
    */
    getPixelPositionY: function () {
        var glyph = this;
        return (glyph.lane.getPixelPositionY());
    },

    /** **getEnd**
    
     * _gets the nucleotide/amino acid end point of this glyph/feature_
    
     * @return {Int} end - in nucleotides/amino acids
     * @api public        
     */
    getEnd: function () {
        return (this.position + this.length);
    },

    /** **clone**
   
    * _shallow copy_
   
    * @return {Object} copy - shallow copy of this glyph/feature
    * @api public        
    */
    clone: function (glyphType) {
        var glyph = this;
        var newFeature;

        glyphType = glyphType || glyph.glyphType;

        if (glyphType == "Rect" || glyphType == "Line")
            glyph.strand = undefined

        if (glyph.strand) {
            var str = 'new ' + glyphType + '("' + glyph.type + '",' + glyph.position + ',' + glyph.length + ',"' + glyph.strand + '",' + JSON.stringify(glyph.opts) + ')';
            newFeature = eval(str);
            var attrs = Object.keys(glyph);
            for (var i = 0; i < attrs.length; i++) {
                newFeature[attrs[i]] = glyph[attrs[i]];
            }
        } else {
            var str = 'new ' + glyphType + '("' + glyph.type + '",' + glyph.position + ',' + glyph.length + ',' + JSON.stringify(glyph.opts) + ')';
            newFeature = eval(str);
            var attrs = Object.keys(glyph);
            for (var i = 0; i < attrs.length; i++) {
                newFeature[attrs[i]] = glyph[attrs[i]];
            }
        }

        newFeature.tooltips = glyph.tooltips;
        newFeature.hooks = glyph.hooks;
        return (newFeature);

    },

    /** **getAttr**
   
    * _determine and retrieve the appropriate value for each attribute, checks parent, default, type, and glyph levels in the appropriate order_
    
    * @param {*} attribute
    * @return {*} attribute
    * @api public        
    */
    getAttr: function (attr) {
        var glyph = this;
        var attrs = attr.split('-');

        // glyph level
        var glyphLevel = glyph;
        for (var k = 0; k < attrs.length; k++) { glyphLevel = glyphLevel[attrs[k]]; }
        if (glyphLevel) return glyphLevel

        // parent level
        if (glyph.parent) {
            var parentLevel = glyph.parent;
            for (var k = 0; k < attrs.length; k++) { parentLevel = parentLevel[attrs[k]]; }
            if (parentLevel) return parentLevel;
        }

        // type level
        var typeLevel = this.lane.chart[glyph.type];
        if (typeLevel) {
            for (var k = 0; k < attrs.length; k++) { typeLevel = typeLevel[attrs[k]]; }
            if (typeLevel) return typeLevel;
        }

        // chart level
        var chartLevel = glyph.lane.chart.glyph;
        for (var k = 0; k < attrs.length; k++) { chartLevel = chartLevel[attrs[k]]; }
        if (chartLevel) return chartLevel;

        // nothing
        return undefined;
    },

    /** **drawText**
   
    * _draws the text for a glyph/feature
    _    
    * @param {String} text
    * @api internal 
    */
    drawText: function (text) {
        // initialize
        var glyph = this;
        var ctx = glyph.lane.chart.ctx;
        var padding = 5;
        var length = glyph.getPixelLength();
        var height = glyph.getHeight();
        var fontSize = glyph.getAttr('text-size');
        var fontSizeMin = 8;
        var fontStyle = glyph.getAttr('text-style');
        // set ctx
        ctx.font = fontSize + "px " + fontStyle;
        ctx.textBaseline = "middle";
        ctx.fillStyle = glyph.getAttr('text-color');


        // align text properly
        var placement = undefined

        // handle relative text alignment based on glyph orientation
        var align = glyph.getAttr('text-align');
        if (align == "start")
            if (glyph.strand == '+')
                align = 'left';
            else
                align = 'right';
        else if (align == "end")
            if (glyph.strand == '+')
                align = 'right';
            else
                align = 'left';

        // handle absolute text alignment	
        ctx.textAlign = align;
        if (align == 'left')
            placement = 0 + padding;
        else if (align == 'center')
            placement = length / 2;
        else if (align == "right")
            placement = length - padding;

        // test if text size is too big and if so make it smaller
        var dim = ctx.measureText(text);
        if (text && text != "") {
            while ((length - dim.width) < 4) {
                fontSize = /^\d+/.exec(ctx.font);
                fontSize--;
                dim = ctx.measureText(text);
                ctx.font = fontSize + "px " + fontStyle;

                // Check if font is getting too small
                if (fontSize <= fontSizeMin) {
                    text = "";  // set name to blank if glyph is too small to display text
                    break;
                }
            }

            // handle special case
            if (glyph.glyphType == "Complex") {
                var offset = 0;
                var fontsize = /^\d+/.exec(ctx.font);
                if (align == "center")
                    offset = -(ctx.measureText(text).width / 2 + padding / 2);
                ctx.clearRect(placement + offset, height / 2 - fontsize / 2, ctx.measureText(text).width + padding, fontsize);
            }
            ctx.fillText(text, placement, height / 2);
        }
    },

    /** **calcRoundness**
   
    * _determines a roundness value based on the height of the glyph feature, so roundness looks consistent as lane size changes_    

    * @return {Int} roundness
    * @api internal
    */
    calcRoundness: function () {
        var roundness = this.getHeight() * this.getAttr('roundness') / 100;
        // round roundness to the nearest 0.5
        roundness = ((roundness * 10 % 5) >= 2.5 ? parseInt(roundness * 10 / 5) * 5 + 5 : parseInt(roundness * 10 / 5) * 5) / 10;
        return (roundness);
    },

    /** **isContainedWithinRect**
   
    * _determines if this glyph/feature is contained within a box with the given coordinates_    
    
    * @param {Int} selectionTlX - top left X coordinate of bounding box
    * @param {Int} selectionTlY - top left Y coordinate of bounding box
    * @param {Int} selectionBrX - bottom right X coordinate of bounding box
    * @param {Int} selectionBrY - bottom right Y coordinate of bounding box
    * @return {Boolean} isContained
    * @api public        
    */
    isContainedWithinRect: function (selectionTlX, selectionTlY, selectionBrX, selectionBrY) {
        var glyph = this;
        var y = glyph.getPixelPositionY();
        var tlX = glyph.getPixelPositionX();
        var tlY = y
        var brX = glyph.getPixelPositionX() + glyph.getPixelLength();
        var brY = y + glyph.getHeight();
        return tlX >= selectionTlX
           && brX <= selectionBrX
           && tlY >= selectionTlY
           && brY <= selectionBrY;
    },

    /** **getHeight**
   
    * _returns the height of this glyph/feature in pixels_
   
    * @return {Int} height
    * @api public        
    */
    getHeight: function () {
        var glyph = this;
        return (glyph.lane.getHeight());
    },

    /** **getFillStyle**
   
    * _converts glyph.color into the format taken by canvas.context.fillStyle_
   
    * @return {Sting/Object} fillStyle
    * @api public        
    */
    getFillStyle: function () {
        var glyph = this;
        var color = glyph.getAttr('color');

        if (color instanceof Array) {
            var lineargradient = this.lane.track.chart.ctx.createLinearGradient(this.length / 2, 0, this.length / 2, this.getHeight());
            var currColor;
            for (var i = 0; currColor = color[i], i < color.length; i++)
                lineargradient.addColorStop(i / (color.length - 1), currColor);
            return lineargradient
        } else if (color instanceof Function) {
            var lineargradient = this.lane.track.chart.ctx.createLinearGradient(this.length / 2, 0, this.length / 2, this.getHeight());
            return color(lineargradient);
        } else
            return color;
    },

    /** **getStrokeStyle**
   
    * _converts glyph.borderColor into the format taken by canvas.context.fillStyle_
   
    * @return {Sting/Object} fillStyle
    * @api public        
    */
    getStrokeStyle: function () {
        var glyph = this;
        var color = glyph.getAttr('borderColor');

        if (typeof (color) == "object") {
            var lineargradient = this.lane.ctx.createLinearGradient(this.length / 2, 0, this.length / 2, this.getHeight());
            var currColor;
            for (var i = 0; currColor = color[i], i < color.length; i++)
                lineargradient.addColorStop(i / (color.length - 1), currColor);
            return lineargradient
        } else
            return color;
    },

    /** **isSubFeature**
   
    * _checks if glyph/feature has a parent_
   
    * @return {Boolean} isSubFeature? 
    * @api public        
    */
    isSubFeature: function () {
        return (this.parent != undefined);
    },

    /** **erase**
   
    * _erase this glyph/feature_
   
    * @api public 
    */
    erase: function () {
        var glyph = this;
        glyph.ctx.save();
        glyph.ctx.setTransform(1, 0, 0, 1, 0, 0);
        glyph.ctx.clearRect(glyph.getPixelPositionX(), glyph.getPixelPositionY(), glyph.getPixelLength(), glyph.getHeight());
        glyph.ctx.restore();
    },

    /** **addDrawHook**
    
     * _add function to glyph that executes before the glyph is drawn_
     
     * @param {Function} function - takes glyph as param, returns true to stop the normal draw, false to allow
     * @return {Int} id - returns the uniqe id for the hook which is used to remove it
     * @api public 
     */

    addDrawHook: function (fn, hookId) {
        var uid = hookId || _uniqueId('drawHook');
        this.hooks[uid] = fn;
        return uid;
    },

    /** **removeDrawHook**
    
     * _removes function to glyph that executes before the glyph is drawn_
     
     * @param {Int} id - the id of drawHook function that will be removed
     * @api public 
     */

    removeDrawHook: function (uid) {
        delete this.hooks[uid];
    },

    /** **addTooltip**
    
     * _add tooltip to glyph. Can add multiple tooltips_
     
     * @param {Int} placement - two options 'above' glyph or 'below' glyph
     * @param {Int} verticalOffset - + numbers for up, - for down
     * @param {Hash} options - optional attributes, horizontalOffset and ntOffset (nucleotide)
     * @return {Object} tooltip   
     * @api public 
     */

    addTooltip: function (text, placement, verticalOffset, opts) {
        var glyph = this;
        var tt = new Tooltip(text, placement, verticalOffset, opts);
        tt.feature = glyph;
        glyph.tooltips.push(tt);
    },

    /** **fireTooltips**

     * _draws the tooltips associated with this feature_

     * @api public 
     */
    fireTooltips: function () {
        for (var i = 0; i < this.tooltips.length; i++)
            this.tooltips[i].fire()
    },

    /** **draw**
   
    * _draws the glyph_
   
    * @api internal        
    */
    draw: function () {
        var glyph = this;

        // set ctx
        glyph.ctx = glyph.lane.chart.ctx;
        glyph.ctx.beginPath();

        // intialize
        var fontSize = /^\d+/.exec(glyph.ctx.font);
        var font = /\S+$/.exec(glyph.ctx.font);
        var fontSizeMin = 10;
        glyph.onClick = glyph.getAttr('onClick');
        glyph.onMouseover = glyph.getAttr('onMouseover');
        glyph.ctx.fillStyle = glyph.getFillStyle();
        var fillStyle = glyph.ctx.fillStyle;
        var position = glyph.getPixelPositionX();
        var height = glyph.getHeight();

        (height < fontSizeMin) ? glyph.ctx.font = fontSizeMin + "px " + font : glyph.ctx.font = height * .9 + "px " + font;

        // setup ctx position and orientation
        glyph.ctx.translate(position, 0);
        if (glyph.strand == '-' && !glyph.isSubFeature())
            glyph.ctx.transform(-1, 0, 0, 1, glyph.getPixelLength(), 0);

        var dontDraw = false;
        for (var i in glyph.hooks) {
            dontDraw = glyph.hooks[i](glyph) || dontDraw;
        }
        if (!dontDraw) {
            // draw glyph with subclass specific draw
            glyph._draw();
        }


        // draw border color
        if (glyph.borderColor != "none") {
            if (glyph.color == 'none' && glyph.parent.glyphType == 'Complex') {
                glyph.erase();
            }
            var saveStrokeStyle = glyph.ctx.strokeStyle;
            var saveLineWidth = glyph.ctx.lineWidth;
            glyph.ctx.strokeStyle = glyph.getStrokeStyle();
            glyph.ctx.lineWidth = glyph.getAttr('borderWidth');
            glyph.ctx.stroke();
            glyph.ctx.strokeStyle = saveStrokeStyle;
            glyph.ctx.lineWidth = saveLineWidth;
        }

        // draw fill color
        if (glyph.color != "none") glyph.ctx.fill();

        // explicity change transformation matrix back -- it's faster than save restore!
        if (glyph.strand == '-' && !glyph.isSubFeature())
            glyph.ctx.transform(-1, 0, 0, 1, glyph.getPixelLength(), 0);

        // draw text
        glyph.drawText(glyph.getAttr('name'));

        // explicity change transformation matrix back -- it's faster than save restore!
        glyph.ctx.translate(-position, 0);
        glyph.ctx.fillStyle = fillStyle;

        // setup mouse events if need be
        glyph.lane.chart.myMouseEventHandler.addEvents(this);

    },

    /** **redraw**
    
     * _erases this specific glyph and redraws it_
    
     * @api internal        
     */
    redraw: function () {
        var glyph = this;
        glyph.lane.ctx.save();
        glyph.erase;
        var y = glyph.getPixelPositionY();
        glyph.lane.ctx.translate(0, y);
        glyph.draw();
        glyph.lane.ctx.restore();
    }

});
/**
 * **Scribl::Glyph::BlockArrow**
 *
 * _Glyph used to draw any blockarrow shape_
 *
 * Chase Miller 2011
 */

var BlockArrow = Glyph.extend({
    /** **init**

     * _Constructor, call this with `new BlockArrow()`_

     * @param {String} type - a tag to associate this glyph with
     * @param {Int} position - start position of the glyph
     * @param {Int} length - length of the glyph
     * @param {String} strand - '+' or '-' strand
     * @param {Hash} [opts] - optional hash of attributes that can be applied to glyph
     * @api public
     */
    init: function (type, position, length, strand, opts) {
        // call super init method to initialize glyph
        this._super(type, position, length, strand, opts);
        this.slope = 1;
        this.glyphType = "BlockArrow";
    },

    /** **_draw**

       * _private blockarrow specific draw method that gets called by this._super.draw()_

       * @param [context] - optional canvas.context 
       * @param [length] - optional length of glyph/feature
       * @param [height] - optional height of lane
       * @param [roundness] - optional roundness of glyph/feature      
       * @api internal 
       */
    _draw: function (ctx, length, height, roundness) {

        // Initialize
        var blockarrow = this;

        // see if optional parameters are set and get chart specific info
        var ctx = ctx || blockarrow.ctx;
        var length = length || blockarrow.getPixelLength();
        var height = height || blockarrow.getHeight();
        var roundness = roundness + 1 || blockarrow.calcRoundness();
        if (roundness != undefined) roundness -= 1;

        var side = length * .75;


        // set start x and y draw locations to 0
        x = y = 0;

        // calculate points

        // top corner
        tc_ctrl_x = x; 				// control point
        tc_ctrl_y = y;
        tc_lgth_x = x + roundness; 	// horizontal point
        tc_lgth_y = y;
        tc_wdth_x = x;				// vertical point
        tc_wdth_y = y + roundness;

        // bottom corner
        bc_ctrl_x = x; 				// control point
        bc_ctrl_y = y + height;
        bc_lgth_x = x + roundness; 	// horizontal point
        bc_lgth_y = y + height;
        bc_wdth_x = x;				// vertical point
        bc_wdth_y = y + height - roundness;

        // arrow x and control coords
        a_b_x = x + length - roundness;  // bottom x coord					
        a_t_x = x + length - roundness; // top point x coord
        a_max_x = x + length;  // the furthest point of the arrow
        // use bezier quadratic equation to calculate control point x coord
        t = .5  // solve for end of arrow
        a_ctrl_x = Math.round(((a_max_x - (1 - t) * (1 - t) * a_b_x - t * t * a_t_x) / (2 * (1 - t) * t)) * 10) / 10;
        a_ctrl_y = y + height / 2;

        // arrow slope and intercept
        bs_slope = blockarrow.slope;
        bs_intercept = (-a_ctrl_y) - bs_slope * a_ctrl_x;
        ts_slope = -blockarrow.slope;
        ts_intercept = (-a_ctrl_y) - ts_slope * a_ctrl_x;

        // arrow y coords
        a_b_y = -(Math.round((bs_slope * a_b_x + bs_intercept) * 10) / 10);
        a_t_y = -(Math.round((ts_slope * a_t_x + ts_intercept) * 10) / 10);


        // bottom slope
        bs_ctrl_y = y + height;
        bs_ctrl_x = ((-bs_ctrl_y - bs_intercept) / blockarrow.slope); 	// control point
        if (bs_ctrl_x < x) {
            var r = new Rect(blockarrow.type, 0, length);
            r._draw(ctx, length, height, roundness);
            return;
        }

        bs_lgth_y = y + height; 	// horizontal point
        bs_lgth_x = bs_ctrl_x - roundness;
        bs_slpe_x = bs_ctrl_x + roundness;		// slope point
        bs_slpe_y = -(Math.round((bs_slope * bs_slpe_x + bs_intercept) * 10) / 10);

        // top slope					
        ts_ctrl_y = y;
        ts_ctrl_x = (ts_ctrl_y + ts_intercept) / blockarrow.slope; 	// control point      
        ts_lgth_y = y; 	// horizontal point
        ts_lgth_x = ts_ctrl_x - roundness;
        ts_slpe_x = ts_ctrl_x + roundness;		// slope point
        ts_slpe_y = -(Math.round((ts_slope * ts_slpe_x + ts_intercept) * 10) / 10);


        // draw lines
        ctx.beginPath();

        // top left corner
        ctx.moveTo(tc_lgth_x, tc_lgth_y);
        ctx.quadraticCurveTo(tc_ctrl_x, tc_ctrl_y, tc_wdth_x, tc_wdth_y);

        // bottom left corner
        ctx.lineTo(bc_wdth_x, bc_wdth_y);
        ctx.quadraticCurveTo(bc_ctrl_x, bc_ctrl_y, bc_lgth_x, bc_lgth_y);

        // bottom right slope
        ctx.lineTo(bs_lgth_x, bs_lgth_y);
        ctx.quadraticCurveTo(bs_ctrl_x, bs_ctrl_y, bs_slpe_x, bs_slpe_y);

        // arrow
        ctx.lineTo(a_b_x, a_b_y);
        ctx.quadraticCurveTo(a_ctrl_x, a_ctrl_y, a_t_x, a_t_y);

        // top right slope
        ctx.lineTo(ts_slpe_x, ts_slpe_y);
        ctx.quadraticCurveTo(ts_ctrl_x, ts_ctrl_y, ts_lgth_x, ts_lgth_y);

        // top line
        ctx.lineTo(tc_lgth_x, tc_lgth_y);
    }

});



/**
 * **Scribl::Glyph::Rect**
 *
 * _Glyph used to draw any rectangle shape_
 *
 * Chase Miller 2011
 */
var Rect = Glyph.extend({
    /** **init**

     * _Constructor, call this with `new Rect()`_

     * @param {String} type - a tag to associate this glyph with
     * @param {Int} position - start position of the glyph
     * @param {Int} length - length of the glyph
     * @param {Hash} [opts] - optional hash of attributes that can be applied to glyph
     * @api public
       */
    init: function (type, position, length, opts) {
        this._super(type, position, length, undefined, opts);
        //this._super(type, position, length, '+', opts);
        this.glyphType = "Rect";
    },

    /** **_draw**

       * _private rect specific draw method that gets called by this._super.draw()_

       * @param [context] - optional canvas.context 
       * @param [length] - optional length of glyph/feature
       * @param [height] - optional height of lane
       * @param [roundness] - optional roundness of glyph/feature      
       * @api internal 
       */
    _draw: function (ctx, length, height, roundness) {

        // initialize
        var rect = this;

        // see if optional parameters are set
        var ctx = ctx || rect.ctx;
        var length = length || rect.getPixelLength();
        var height = height || rect.getHeight();
        var roundness = roundness + 1 || rect.calcRoundness();
        if (roundness != undefined) roundness -= 1

        // Set starting draw position
        x = y = 0;


        ctx.beginPath();

        // calculate points

        // top left corner
        tlc_ctrl_x = x; 				// control point
        tlc_ctrl_y = y;
        tlc_lgth_x = x + roundness; 	// horizontal point
        tlc_lgth_y = y;
        tlc_wdth_x = x;				// vertical point
        tlc_wdth_y = y + roundness;

        // bottom left corner
        blc_ctrl_x = x; 				// control point
        blc_ctrl_y = y + height;
        blc_lgth_x = x + roundness; 	// horizontal point
        blc_lgth_y = y + height;
        blc_wdth_x = x;				// vertical point
        blc_wdth_y = y + height - roundness;

        // bottom right corner
        brc_ctrl_x = x + length; 				// control point
        brc_ctrl_y = y + height;
        brc_lgth_x = x + length - roundness; 	// horizontal point
        brc_lgth_y = y + height;
        brc_wdth_x = x + length;				// vertical point
        brc_wdth_y = y + height - roundness;

        // top right corner
        trc_ctrl_x = x + length; 				// control point
        trc_ctrl_y = y;
        trc_lgth_x = x + length - roundness; 	// horizontal point
        trc_lgth_y = y;
        trc_wdth_x = x + length;				// vertical point
        trc_wdth_y = y + roundness;

        // draw lines

        // top left corner
        ctx.moveTo(tlc_lgth_x, tlc_lgth_y);
        ctx.quadraticCurveTo(tlc_ctrl_x, tlc_ctrl_y, tlc_wdth_x, tlc_wdth_y);

        // bottom left corner
        ctx.lineTo(blc_wdth_x, blc_wdth_y);
        ctx.quadraticCurveTo(blc_ctrl_x, blc_ctrl_y, blc_lgth_x, blc_lgth_y);

        // bottom right corner
        ctx.lineTo(brc_lgth_x, brc_lgth_y);
        ctx.quadraticCurveTo(brc_ctrl_x, brc_ctrl_y, brc_wdth_x, brc_wdth_y);

        // top right corner
        ctx.lineTo(trc_wdth_x, trc_wdth_y);
        ctx.quadraticCurveTo(trc_ctrl_x, trc_ctrl_y, trc_lgth_x, trc_lgth_y);

        // top line
        ctx.lineTo(tlc_lgth_x, tlc_lgth_y);
    }
});/**
 * **Scribl::Glyph::Seq**
 *
 * _Glyph used to letters e.g nucleotides or proteins_
 *
 * Chase Miller 2011
 */

var Seq = Glyph.extend({
    /** **init**

     * _Constructor, call this with `new seq()`_

     * @param {String} type - a tag to associate this glyph with
     * @param {Int} position - start position of the glyph
     * @param {Int} length - length of the glyph
     * @param {Hash} [opts] - optional hash of attributes that can be applied to glyph
     * @api public
     */
    init: function (type, position, length, seq, opts) {
        this.seq = seq;
        this.insertions = [];
        // used to show bar chart like information; range 0.0 - 1.0
        this.fraction = 1;
        this.fractionLevel = 0.3; // level where seq shows as fraction (in pixels)           
        this.glyphType = "Seq";

        this.font = "8px courier";
        this.chars = {};
        this.chars.width = undefined;
        this.chars.height = undefined;
        this.chars.list = ['A', 'G', 'T', 'C', 'N', '-'];

        this._super(type, position, length, undefined, opts);
    },

    /** **_draw**

       * _private letter specific draw method that gets called by this._super.draw()_

       * @param [context] - optional canvas.context 
       * @param [length] - optional length of glyph/feature
       * @param [height] - optional height of lane
       * @api internal 
       */
    _draw: function (ctx, length, height) {

        // initialize
        var seq = this;
        var fraction = 1;

        if (seq.lane.chart.ntsToPixels() <= seq.fractionLevel)
            fraction = this.fraction

        // see if optional parameters
        var ctx = ctx || seq.ctx;
        var length = length || seq.getPixelLength();
        var height = height || seq.getHeight();

        // get coords
        var left = seq.getPixelPositionX();
        var top = seq.getPixelPositionY();

        // check if nts images have been built
        var chars = SCRIBL.chars;

        // check if image chars need to be built for this height
        if (!chars.heights[height]) {
            // build nt images
            chars.heights[height] = [];
            for (var i = 0; i < this.chars.list.length; i++) {
                var nt = this.chars.list[i];
                var ntName = nt;
                if (nt == '-') { ntName = 'dash'; }
                var charName = "nt_" + ntName + '_bg';
                this.createChar(nt, chars.nt_color, chars[charName], height);
            }
        }

        // Set starting draw position
        x = y = 0;


        if (seq.imgCanvas) {
            ctx.drawImage(seq.imgCanvas, left, top - height * fraction, length, height * fraction);
        } else {
            ctx.save();
            ctx.beginPath();
            ctx.textBaseline = "middle";
            var origFont = ctx.font;
            var size = /[\d+px]/.exec(origFont) + 'px';
            ctx.font = size + " courier";
            ctx.fillStyle = 'black';
            ctx.textAlign = 'left';
            var seqPx = this.seq.length * chars.heights[height].width;

            // draw text;
            seq.imgCanvas = document.createElement('canvas');
            seq.imgCanvas.width = seqPx;
            seq.imgCanvas.height = height;
            var tmpCtx = seq.imgCanvas.getContext('2d');

            var pos = 0;
            var k = 0;
            for (var i = 0; i < this.seq.length; i++) {
                if (!chars.heights[height][this.seq[i]]) {
                    this.createChar(this.seq[i], 'black', 'white', height);
                }
                var charGlyph = this.seq[i];
                if (this.insertions.length > 1) {
                    var h = 2;
                }
                if (this.insertions[k] && this.insertions[k]['pos'] != undefined) {
                    if (this.insertions[k]['pos'] - 1 == i) {
                        charGlyph += 'rightInsert';
                    } else if (this.insertions[k] && this.insertions[k]['pos'] == i) {
                        charGlyph += 'leftInsert';
                        k++;
                    }
                }

                tmpCtx.drawImage(chars.heights[height][charGlyph], pos, y);
                pos += chars.heights[height].width;
            }

            ctx.drawImage(seq.imgCanvas, x, height - height * fraction, length, height * fraction);
            //ctx.drawImage(seq.imgCanvas, x, y, length, height);
            ctx.font = origFont;

            ctx.restore();
        }

        // this is horrible
        // have to draw an outline around the nucleotides
        // so that the mousehover will work b\c mousehover
        // only works with drawn Paths and not drawn Images :(            
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(length, y);
        ctx.lineTo(length, y + height);
        ctx.lineTo(x, y + height);
        ctx.lineTo(x, y);
        ctx.fillStyle = 'rgba(0,0,0,0)';
        if (seq.lane.chart.ntsToPixels() <= seq.fractionLevel)
            ctx.strokeStyle = 'rgba(0,0,0,1)';
        else
            ctx.strokeStyle = 'rgba(0,0,0,0)';

        ctx.stroke();
        ctx.closePath();
    },

    /** **_createChar**

    * _creates glyphs of a given character_

    * @param {Char} - the char to create glyph of
    * @param {String} - string of char color in rgb or hex
    * @param {String} - string of char background color in rgb or hex
    * @param {Int} - height of glyph
    * @api internal 
    */
    createChar: function (theChar, color, backgroundColor, height) {
        var seq = this;
        var chart = seq.lane.track.chart;
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        var buffer = 2;
        var fontsize = height - buffer;
        ctx.font = fontsize + 'px courier';
        var width = ctx.measureText(theChar).width + buffer;
        canvas.height = height;
        canvas.width = width;
        SCRIBL.chars.heights[height].width = width;

        // draw standard nt
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        ctx.font = fontsize + 'px courier';
        canvas.height = height;
        canvas.width = width;
        var fillStyle = ctx.fillStyle;
        ctx.fillStyle = backgroundColor;
        ctx.fillRect(0, 0, width, height);
        ctx.fillStyle = color;
        ctx.textAlign = 'center';
        ctx.textBaseline = "middle";
        ctx.fillText(theChar, width / 2, height / 2);
        // store canvas with glyph in global variable
        SCRIBL.chars.heights[height][theChar] = canvas;
        ctx.fillStyle = fillStyle;

        // draw nt with insert to the right
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        ctx.font = fontsize + 'px courier';
        canvas.height = height;
        canvas.width = width;
        var fillStyle = ctx.fillStyle;
        ctx.fillStyle = backgroundColor;
        ctx.fillRect(0, 0, width, height);
        ctx.fillStyle = 'yellow';
        ctx.beginPath();
        ctx.moveTo(0, height);
        ctx.arcTo(width, height, width, 0, height / 2);
        ctx.lineTo(width, height);
        ctx.lineTo(0, height)
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = color;
        ctx.textAlign = 'center';
        ctx.textBaseline = "middle";
        ctx.fillText(theChar, width / 2, height / 2);
        // store canvas with glyph in global variable
        SCRIBL.chars.heights[height][theChar + 'rightInsert'] = canvas;
        ctx.fillStyle = fillStyle;

        // draw nt with insertion to the left
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        ctx.font = fontsize + 'px courier';
        canvas.height = height;
        canvas.width = width;
        var fillStyle = ctx.fillStyle;
        ctx.fillStyle = backgroundColor;
        ctx.fillRect(0, 0, width, height);
        ctx.fillStyle = 'yellow';
        ctx.beginPath();
        ctx.moveTo(width, height);
        ctx.arcTo(0, height, 0, 0, height / 2);
        ctx.lineTo(0, height);
        ctx.lineTo(width, height)
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = color;
        ctx.textAlign = 'center';
        ctx.textBaseline = "middle";
        ctx.fillText(theChar, width / 2, height / 2);
        // store canvas with glyph in global variable
        SCRIBL.chars.heights[height][theChar + 'leftInsert'] = canvas;
        ctx.fillStyle = fillStyle;

    }
});/**
 * **Scribl::Glyph::Line**
 *
 * _Glyph used to draw any line shape_
 *
 * Chase Miller 2011
 */

var Line = Glyph.extend({
    /** **init**

     * _Constructor, call this with `new Line()`_

     * @param {String} type - a tag to associate this glyph with
     * @param {Int} position - start position of the glyph
     * @param {Int} length - length of the glyph
     * @param {Hash} [opts] - optional hash of attributes that can be applied to glyph
     * @api public
     */
    init: function (type, position, length, opts) {
        this.thickness = 2;
        this._super(type, position, length, undefined, opts);
        this.glyphType = "Line";
    },

    /** **_draw**

       * _private line specific draw method that gets called by this._super.draw()_

       * @param [context] - optional canvas.context 
       * @param [length] - optional length of glyph/feature
       * @param [height] - optional height of lane
       * @param [roundness] - optional roundness of glyph/feature      
       * @api internal 
       */
    _draw: function (ctx, length, height, roundness) {

        // initialize
        var line = this;

        // see if optional parameters
        var ctx = ctx || line.ctx;
        var length = length || line.getPixelLength();
        var height = height || line.getHeight();

        // Set starting draw position
        x = y = 0;

        ctx.beginPath();
        ctx.moveTo(x, height / 2 - line.thickness / 2);
        ctx.lineTo(x, height / 2 + line.thickness / 2);
        ctx.lineTo(x + length, height / 2 + line.thickness / 2);
        ctx.lineTo(x + length, height / 2 - line.thickness / 2);
        //			ctx.fill();			
        //			ctx.fillRect(x, height/2 - line.thickness/2, length, line.thickness);
    }
});/**
 * **Scribl::Glyph::Complex**
 *
 * _Complex is used to draw any feature that has splices
 * (e.g gene with subFeatures and introns, etc) Or
 * any feature that should be made up of other features_
 *
 * Chase Miller 2011
 */

var Complex = Glyph.extend({
    /** **init**

     * _Constructor, call this with `new Complex()`_

     * @param {String} type - a tag to associate this glyph with
     * @param {Int} position - start position of the glyph
     * @param {Int} length - length of the glyph
     * @param {Array} subFeatures - array of derived Glyph objects (e.g Rect, Arrow, etc...)
     * @param {Hash} [opts] - optional hash of attributes that can be applied to glyph
     * @api public
       */
    init: function (type, position, length, strand, subFeatures, opts) {
        // call super init method to initialize glyph
        this._super(type, position, length, strand, opts);

        // instantiate and set defaults
        this.slope = 1;
        this.glyphType = "Complex";
        this.subFeatures = subFeatures;

        // instantiate connector line and set default attributes
        this.line = new Line(type, 0, length);
        this.line.parent = this;
        this.line.color = "black";
        this.line.thickness = 2;
    },

    /** **addSubFeature**

   * _adds subFeature to complex glyph/feature_

   * @param subFeature - a derived Glyph object (e.g. Rect, Arrow, etc..) 
   * @api public
   */
    addSubFeature: function (subFeature) {
        this.subFeatures.push(subFeature);
    },

    /** **_draw**

       * _private complex specific draw method that gets called by this._super.draw()_

       * @param [context] - optional canvas.context 
       * @param [length] - optional length of glyph/feature
       * @param [height] - optional height of lane
       * @param [roundness] - optional roundness of glyph/feature      
       * @api internal 
       */
    _draw: function (ctx, length, height, roundness) {

        // Initialize
        var complex = this;


        // see if optional parameters are set and get chart specific info
        var ctx = ctx || complex.ctx;
        var length = length || complex.getPixelLength();
        var height = height || complex.getHeight();
        var roundness = roundness + 1 || complex.calcRoundness();
        if (roundness != undefined) roundness -= 1;

        // set start x and y draw locations to 0
        x = y = 0;

        // translate back the length of the complex glyph
        // so sub glyphs will be placed correctly
        ctx.translate(-complex.getPixelPositionX(), 0);

        // draw connector line
        complex.line.lane = this.lane;
        complex.line.draw();

        // draw subFeatures
        var numsubFeatures = complex.subFeatures.length
        for (var i = 0; i < numsubFeatures; i++) {
            // set subFeature to same lane and draw
            complex.subFeatures[i].parent = complex;
            complex.subFeatures[i].lane = complex.lane;
            complex.subFeatures[i].draw();
        }

        // redo translate so the next glyphs will be placed correctly
        ctx.translate(complex.getPixelPositionX(), 0);

        // end path so it doesn't get redrawn when parent tries to draw
        ctx.beginPath();
    }

});


/**
 * **Scribl::Glyph::Arrow**
 *	
 * _Glyph used to draw any arrow shape_
 *
 * Chase Miller 2011
 */


var Arrow = Glyph.extend({
    /** **init**

     * _Constructor, call this with `new Arrow()`_

     * @param {String} type - a tag to associate this glyph with
     * @param {Int} position - start position of the glyph
     * @param {Int} length - length of the glyph
     * @param {String} strand - '+' or '-' strand
     * @param {Hash} [opts] - optional hash of attributes that can be applied to glyph
     * @api public
     */
    init: function (type, position, strand, opts) {
        // call base class glyph init method to initialize glyph
        this._super(type, position, 0, strand, opts);

        // set defaults
        this.slope = 1;
        this.glyphType = "Arrow";
        this.thickness = 4.6
    },

    /** **getPixelThickness**

   * _gets pixel thickness_

   * @preturn {Int} pixelThickness
   * @api internal
   */
    getPixelThickness: function () {
        var arrow = this;
        var height = arrow.getHeight();
        var arrowLength = height / 2 / Math.tan(Math.atan(arrow.slope))
        return (arrow.thickness / 10 * arrowLength);
    },

    /** **erase**

       * _erase this glyph/feature_

       * @api public 
       */
    erase: function () {
        var arrow = this;
        var thickness = arrow.getPixelThickness();
        arrow.ctx.clearRect(-thickness, 0, thickness, arrow.getHeight());
    },

    /** **_draw**

       * _private arrow specific draw method that gets called by this._super.draw()_

       * @param [context] - optional canvas.context 
       * @param [length] - optional length of glyph/feature
       * @param [height] - optional height of lane
       * @param [roundness] - optional roundness of glyph/feature      
       * @api internal 
       */
    _draw: function (ctx, length, height, roundness) {

        // Initialize
        var arrow = this;

        // see if optional parameters are set and get chart specific info
        var ctx = ctx || arrow.ctx;
        var height = height || arrow.getHeight();
        var roundness = roundness + 1 || arrow.calcRoundness();
        if (roundness != undefined) roundness -= 1;
        var thickness = arrow.getPixelThickness();
        var arrowLength = 0;

        // set start x and y draw locations to 0
        x = y = 0;

        // arrow x and control coords
        a_b_x = x - arrowLength - roundness;  // bottom x coord					
        a_t_x = x - arrowLength - roundness; // top point x coord
        a_max_x = x - arrowLength;  // the furthest point of the arrow

        // use bezier quadratic equation to calculate control point x coord
        t = .5  // solve for end of arrow
        a_ctrl_x = (a_max_x - (1 - t) * (1 - t) * a_b_x - t * t * a_t_x) / (2 * (1 - t) * t)
        a_ctrl_y = y + height / 2;

        // arrow slope and intercept
        bs_slope = arrow.slope;
        bs_intercept = (-a_ctrl_y) - bs_slope * a_ctrl_x;
        ts_slope = -arrow.slope;
        ts_intercept = (-a_ctrl_y) - ts_slope * a_ctrl_x;

        // arrow y coords
        a_b_y = -(bs_slope * a_b_x + bs_intercept);
        a_t_y = -(ts_slope * a_t_x + ts_intercept);

        // draw lines
        ctx.beginPath();


        // bottom slope
        bs_ctrl_y = y + height;
        bs_ctrl_x = ((-bs_ctrl_y - bs_intercept) / arrow.slope); 	// control point
        bs_slpe_x = bs_ctrl_x + roundness + roundness;		// slope point
        bs_slpe_y = -(bs_slope * bs_slpe_x + bs_intercept);

        ctx.moveTo(bs_slpe_x, bs_slpe_y);

        // bottom outer-line
        ctx.lineTo(a_b_x, a_b_y);

        // front part of arrow
        ctx.quadraticCurveTo(a_ctrl_x, a_ctrl_y, a_t_x, a_t_y);

        // top outer-line
        // top slope					
        ts_ctrl_y = y;
        ts_ctrl_x = (ts_ctrl_y + ts_intercept) / arrow.slope; 	// control point      
        ts_slpe_x = ts_ctrl_x + roundness + roundness;		// slope point
        ts_slpe_y = -(ts_slope * ts_slpe_x + ts_intercept);
        ctx.lineTo(ts_slpe_x, ts_slpe_y);


        // top u-turn
        // angle needed to get the x, y position of a point on the inner line perpendicular to a point on the outer line
        var theta = (Math.PI - Math.abs(Math.atan(arrow.slope))) - Math.PI / 2;
        var dX = Math.sin(theta) * thickness;
        var dY = Math.cos(theta) * thickness;
        var arcTX = ts_slpe_x - dX;
        var arcTY = ts_slpe_y + dY;
        ctx.bezierCurveTo(ts_ctrl_x, ts_ctrl_y, ts_ctrl_x - dX, ts_ctrl_y + dY, arcTX, arcTY);

        // inner top-line
        ctx.lineTo(a_max_x - thickness, y + height / 2);


        // inner bottom-line
        var arcBX = bs_slpe_x - dX;
        var arcBY = bs_slpe_y - dY;
        ctx.lineTo(arcBX, arcBY);

        // bottom uturn
        ctx.bezierCurveTo(bs_ctrl_x - dX, bs_ctrl_y - dY, bs_ctrl_x, bs_ctrl_y, bs_slpe_x, bs_slpe_y);
        // ctx.fill();	
    }

});


/**
 * Genbank parser
 */
function genbank(file, bchart) {

    var lines = file.split("\n");
    var re = new RegExp(/\s+gene\s+([a-z]*)\(?(\d+)\.\.(\d+)/);
    var genes = [];
    var max = undefined;
    var min = undefined;

    // parse genes
    for (var j = 0; j < lines.length; j++) {

        var gene_info;
        if (gene_info = lines[j].match(re)) {
            gene_info.shift();
            genes.push(gene_info);

            // determine scale dimensions
            var end = gene_info[2];
            if (max == undefined || max > end)
                max = end;
            var position = gene_info[1];
            if (min == undefined || min < position)
                min = position;
        }
    }


    // set scale dimensions
    bchart.scale.max = max;
    bchart.scale.min = min;

    // add genes to chart
    for (var i = 0; i < genes.length; i++) {

        // get positional values
        var strand = '+';
        if (genes[i][0] == "complement")
            strand = '-';

        var position = genes[i][1];
        var end = genes[i][2];
        position = position - 1 + 1;  // force to be integer - TODO make bChart catch non-ints automatically and gracefully fail
        var length = end - position;

        bchart.addGene(position, length, strand);

    }

}/**
 * Bed parser
 */
function bed(file, chart) {
    var lines = file.split("\n");
    var features = [];
    var max = undefined;
    var min = undefined;

    // 	track name=pairedReads description="Clone Paired Reads" useScore=1
    var trackInfo = lines[0];

    // parse genes
    numFeatures = lines.length
    for (var j = 1; j < numFeatures; j++) {
        if (lines[j] == "") break;

        var fields = lines[j].split(" ");

        //chrom chromStart chromEnd name score strand thickStart thickEnd itemRgb blockCount blockSizes blockStarts
        var chromStart = parseInt(fields[1]);
        var chromEnd = parseInt(fields[2]);
        var name = fields[0] + ": " + fields[3];
        var orientation = fields[5];
        var itemRgb = fields[8];
        var blockLengths = fields[10].split(',');
        var blockStarts = fields[11].split(',');

        var complex = chart.addFeature(new Complex('complex', chromStart, chromEnd, orientation, [], { 'color': itemRgb, 'name': name }));

        for (var k = 0; k < blockLengths.length; k++) {
            if (blockLengths[k] == "") break;
            complex.addSubFeature(new BlockArrow('complex', parseInt(blockStarts[k]), parseInt(blockLengths[k]), orientation));
        }
    }
}