// for IE6,7,8
if (!Array.prototype.indexOf) {
  Array.prototype.indexOf = function (obj, fromIndex) {
    if (fromIndex == null) {
        fromIndex = 0;
    } else if (fromIndex < 0) {
        fromIndex = Math.max(0, this.length + fromIndex);
    }
    for (var i = fromIndex, j = this.length; i < j; i++) {
        if (this[i] === obj)
            return i;
    }
    return -1;
  };
}

$(function() { // document ready

	// load file into textarea
	$('.query-file').change(function (evt) {
		if (window.File && window.FileReader) {
			var f = evt.target.files[0];
			console.log(f.type);
			if (f && (f.type.match('text.*') || f.type == '')) {
				var r = new FileReader();
				r.onload = function (e) {
					var contents = e.target.result;
					$('#query-textarea').val(contents);
					$('#query-textarea').keyup();
				}
				r.readAsText(f);
			}
		}
	});

	function sum(obj) {
		var sum = 0;
		for(var el in obj) {
			if(obj.hasOwnProperty(el)) {
				sum += parseFloat(obj[el]);
			}
		}
		return sum;
	}

	function filter_key(obj, test) {
		var result = {}, key;
		for (key in obj) {
			if (obj.hasOwnProperty(key) && test(key)) {
				result[key] = obj[key];
			}
		}
		return result;
	}

	function validateFasta(fasta) {

		if (!fasta) { // check there is something first of all
			return false;
		}

		// immediately remove trailing spaces
		fasta = fasta.trim();

		// split on newlines...
		var lines = fasta.split('\n');

		// check for header
		var fasta_count = 0;
		for (i = 0; i < lines.length; i++){
			if(i + 1 == lines.length){
				//only one fasta
				if(fasta_count == 1){return 4;}
			}else if(lines[i][0] == '>'){
				lines[i] = '';
				//no content
				if(lines[i+1][0] == '>'){return 4;}
				fasta_count = fasta_count + 1;
			}
		}

		// join the array back into a single string without newlines and
		// trailing or leading spaces
		fasta = lines.join('').trim();

		if (!fasta) { // is it empty whatever we collected ? re-check not efficient
			return false;
		}

		// note that the empty string is caught above
		// allow for Selenocysteine (U)
		if(/^[ATCGU*\s]+$/i.test(fasta)){return 1;}
		if(/^[ACDEFGHIKLMNPQRSTUVWY*\s]+$/i.test(fasta)){return 2;}
		return 3;
	}

	function setQueryType(qtype) {
		query_type = qtype;
		if($('#texterror').length){
			$('#texterror').remove();
		}
        $('.sequenceType').attr('disabled', false).removeClass('disabled-radio');
		if (qtype == '') {
			$('.enter-query-text').before("<label id='texterror' class=\"error\">No sequence found!</label>");
			$('.enter-query-text').html('Enter sequence below in <a href="docs/fasta.html">FASTA</a> format:');
		} else if (qtype == 'invalid') {
			$('.enter-query-text').before("<label id='texterror' class=\"error\">Your sequence is invalid:</label>");
			$('.enter-query-text').html('Enter sequence below in <a href="docs/fasta.html">FASTA</a> format:');
		} else if (qtype == 'not_multiple') {
            $('.enter-query-text').before("<label id='texterror' class=\"error\">You must provide 2+ sequence</label>");
			$('.enter-query-text').html('Enter sequence below in <a href="docs/fasta.html">FASTA</a> format:');
		} else if (qtype == 'nucleotide') {
			$('.enter-query-text').html('Your sequence is detected as nucleotide:');
			$('.sequenceType.protein').attr('disabled', 'disabled').addClass('disabled-radio');
			$('.sequenceType.dna').prop('checked', true);
			$('.sequenceType.dna').change();
		} else if (qtype == 'peptide') {
			$('.enter-query-text').html('Your sequence is detected as peptide:');
			$('.sequenceType.dna').attr('disabled', 'disabled').addClass('disabled-radio');
			$('.sequenceType.protein').prop('checked', true);
			$('.sequenceType.protein').change();
		}
	}

	function checktxt() {
		if ($('#query-textarea').val() == '') {
			setQueryType('');
			return false;
		}else if(validateFasta($('#query-textarea').val()) == 1) {
			setQueryType('nucleotide');
			return true;
		}else if(validateFasta($('#query-textarea').val()) == 2) {
			setQueryType('peptide');
			return true;
		}else if(validateFasta($('#query-textarea').val()) == 4) {
			setQueryType('not_multiple');
			return true;
		}else{
			setQueryType('invalid');
			return false;
		}
	}

	var parseTextarea = _.debounce(checktxt, 30);
	$('#query-textarea').keyup(parseTextarea);

	$('.sequenceType').change(function (){
		if($('.sequenceType:checked').val() == 'dna'){
			$('#fieldset-protein-multi').css('display','none');
			$('#fieldset-dna-multi').css('display','inline');
			if($('.pairwise:checked').val() == 'full'){
				$('#fieldset-protein-full').css('display','none');
				$('#fieldset-dna-full').css('display','inline');
			}
		}else if($('.sequenceType:checked').val() == 'protein'){
			$('#fieldset-dna-multi').css('display','none');
			$('#fieldset-protein-multi').css('display','inline');
			if($('.pairwise:checked').val() == 'full') {
				$('#fieldset-dna-full').css('display', 'none');
				$('#fieldset-protein-full').css('display', 'inline');
			}
		}
	});

	$('.pairwise').change(function (){
		if($('.pairwise:checked').val() == 'fast'){
			$('#fieldset-protein-full').css('display','none');
			$('#fieldset-dna-full').css('display','none');
			$('#fieldset-fast').css('display','inline');
		}else if($('.pairwise:checked').val() == 'full'){
			$('#fieldset-fast').css('display','none');
			if($('.sequenceType:checked').val() == 'protein'){
				$('#fieldset-protein-full').css('display','inline');
			}else if($('.sequenceType:checked').val() == 'dna'){
				$('#fieldset-dna-full').css('display','inline');
			}
		}
	});



	// Validate MainClustalForm form on keyup and submit
	$("#MainClustalForm").validate({
		rules: {
			'query-sequence': {
				//'textarea_valid':'',
				required: true
			},
			'dna-PWGAPOPEN': {
				number: true
			},
			'dna-PWGAPEXT': {
				number: true
			},
			'protein-PWGAPOPEN': {
				number: true
			},
			'protein-PWGAPEXT': {
				number: true
			},
			'KTUPLE': {
				number: true
			},
			'WINDOW': {
				number: true
			},
			'PAIRGAP': {
				number: true
			},
			'TOPDIAGS': {
				number: true
			},
			'dna-GAPOPEN': {
				number: true
			},
			'dna-GAPEXT': {
				number: true
			},
			'dna-GAPDIST': {
				number: true
			},
			'dna-NUMITER': {
				number: true
			},
			'protein-GAPOPEN': {
				number: true
			},
			'protein-GAPEXT': {
				number: true
			},
			'protein-GAPDIST': {
				number: true
			},
			'protein-NUMITER': {
				number: true
			},
		},
		messages: {
			'query-sequence': {
				required: "No sequence found!"
			},
			'dna-PWGAPOPEN': {
				number: "<br>Please enter a valid number"
			},
			'dna-PWGAPEXT': {
				number: "<br>Please enter a valid number"
			},
			'protein-PWGAPOPEN': {
				number: "<br>Please enter a valid number"
			},
			'protein-PWGAPEXT': {
				number: "<br>Please enter a valid number"
			},
			'KTUPLE': {
				number: "<br>Please enter a valid number"
			},
			'WINDOW': {
				number: "<br>Please enter a valid number"
			},
			'PAIRGAP': {
				number: "<br>Please enter a valid number"
			},
			'TOPDIAGS': {
				number: "<br>Please enter a valid number"
			},
			'dna-GAPOPEN': {
				number: "<br>Please enter a valid number"
			},
			'dna-GAPEXT': {
				number: "<br>Please enter a valid number"
			},
			'dna-GAPDIST': {
				number: "<br>Please enter a valid number"
			},
			'dna-NUMITER': {
				number: "<br>Please enter a valid number"
			},
			'protein-GAPOPEN': {
				number: "<br>Please enter a valid number"
			},
			'protein-GAPEXT': {
				number: "<br>Please enter a valid number"
			},
			'protein-GAPDIST': {
				number: "<br>Please enter a valid number"
			},
			'protein-NUMITER': {
				number: "<br>Please enter a valid number"
			},
		},
		errorPlacement: function (error, element) {
			switch (element.attr('name').toString()) {
				case 'query-sequence':
					error.insertAfter('#legend-sequence');
					break;
				default:
					error.insertAfter(element);
			}
		}
	});

    $('#queries-tab').click(function() {
        user_id = $('table[id^="queries-"]')[0].id.split('-')[1];
        if ( $.fn.dataTable.isDataTable('#queries-' + user_id) ) {
            var table = $('#queries-' + user_id).DataTable();
            table.ajax.reload();
        }
        else {
            $('#queries-' + user_id).dataTable( {
                "ajax": {
                    "url": window.location.pathname + "user-tasks/" + user_id,
                    "dataSrc": ""
                },
                "columns": [
                    { "data": "enqueue_date" },
                    { "data": "result_status" },
                    { "data": "task_id" },

                ],
                "aoColumnDefs": [{
                    "aTargets": [2], // Column to target
                    "mRender": function ( data, type, full ) {
                        // 'full' is the row's data object, and 'data' is this column's data
                        // e.g. 'full[0]' is the comic id, and 'data' is the comic title
                        return '<a href="' + data  + '" target="_blank">' + data + '</a>';
                    }},
                    {
                    "aTargets": [0], // Column to target
                    "mRender": function ( data, type, full ) {
                        return new Date(data).toUTCString();
                    }}
                ],
                "order": [[ 0, "desc" ]],
            });
        }
    });

	$('#clustalw_submit').click(function() {
		{
			if (checktxt() && $("#MainClustalForm").valid()) {
				$('#program').val('clustalw');
				$('#MainClustalForm').submit();
			}
		}
	});

	$('#clustalo_submit').click(function() {
		{
			if (checktxt() && $("#MainClustalForm").valid()) {
				$('#program').val('clustalo');
				$('#MainClustalForm').submit();
			}
		}
	});

	$('.btn_reset').click(function() {
		{
			$('.sequenceType').attr('disabled', false).removeClass('disabled-radio');
			$('.enter-query-text').html('Enter sequence below in <a href="docs/fasta.html">FASTA</a> format:');
			var validator = $( "#MainClustalForm" ).validate();
			validator.resetForm();
            $('.sequenceType.protein').prop('checked', true);
            $('.sequenceType.protein').change();
            $('.pairwise.full').prop('checked', true);
            $('.pairwise.full').change();
		}
	});

});



//prevention of cache pages
$(window).unload(function () { });
