/// <reference path="../../../templates/blast/main.html" />
/////////////////////
// DATA PROCESSING //
/////////////////////
//var dataset_list = [['Genome Assembly', 'Nucleotide', 'Agla_Btl03082013.genome_new_ids.fa', 'Anoplophora glabripennis'], ['Genome Assembly', 'Nucleotide', 'Aros01112013-genome_new_ids.fa', 'Athalia rosae'], ['Genome Assembly', 'Nucleotide', 'Ccap01172013-genome_new_ids.fa', 'Ceratitis capitata'], ['Genome Assembly', 'Nucleotide', 'Clec_Bbug02212013.genome_new_ids.fa', 'Cimex lectularius'], ['Genome Assembly', 'Nucleotide', 'diaci1.1_new_ids.fa', 'Diaphorina citri'], ['Genome Assembly', 'Nucleotide', 'Edan07162013.scaffolds_new_ids.fa', 'Ephemera danica'], ['Genome Assembly', 'Nucleotide', 'Eaff_11172013.genome_new_ids.fa', 'Eurytemora affinis'], ['Genome Assembly', 'Nucleotide', 'Focc_FINAL.scaffolds_new_ids.fa', 'Frankliniella occidentalis'], ['Genome Assembly', 'Nucleotide', 'Lful_Scha04012013-genome_new_ids.fa', 'Ladona fulva'], ['Genome Assembly', 'Nucleotide', 'Ldec.genome.10062013_new_ids.fa', 'Leptinotarsa decemlineata'], ['Genome Assembly', 'Nucleotide', 'Ofas.scaffolds_new_ids.fa', 'Oncopeltus fasciatus'], ['Genome Assembly', 'Nucleotide', 'Oabi11242013.genome_new_ids.fa', 'Orussus abietinus'], ['Genome Assembly', 'Nucleotide', 'Pven10162013.scaffolds_new_ids.fa', 'Pachypsylla venusta'], ['Genome Assembly', 'Nucleotide', 'Ptep01282013.genome_new_ids.fa', 'Parasteatoda tepidariorum'], ['Genome Assembly', 'Nucleotide', 'Tpre_FINAL.scaffolds_new_ids.fa', 'Trichogramma pretiosum'], ['Transcript', 'Nucleotide', 'AGLA_new_ids.fna', 'Anoplophora glabripennis'], ['Transcript', 'Nucleotide', 'AROS_new_ids.fna', 'Athalia rosae'], ['Transcript', 'Nucleotide', 'CCAP_new_ids.fna', 'Ceratitis capitata'], ['Transcript', 'Nucleotide', 'CLEC_new_ids.fna', 'Cimex lectularius'], ['Transcript', 'Nucleotide', 'maker_genes_diaci1.1_transcripts_NALmod_new_ids.fasta', 'Diaphorina citri'], ['Transcript', 'Nucleotide', 'EDAN_new_ids.fna', 'Ephemera danica'], ['Transcript', 'Nucleotide', 'EAFF_new_ids.fna', 'Eurytemora affinis'], ['Transcript', 'Nucleotide', 'FOCC_new_ids.fna', 'Frankliniella occidentalis'], ['Transcript', 'Nucleotide', 'LFUL_new_ids.fna', 'Ladona fulva'], ['Transcript', 'Nucleotide', 'LDEC_new_ids.fna', 'Leptinotarsa decemlineata'], ['Transcript', 'Nucleotide', 'OFAS_new_ids.fna', 'Oncopeltus fasciatus'], ['Transcript', 'Nucleotide', 'OABI_new_ids.fna', 'Orussus abietinus'], ['Transcript', 'Nucleotide', 'PVEN_new_ids.fna', 'Pachypsylla venusta'], ['Transcript', 'Nucleotide', 'PTEP_new_ids.fna', 'Parasteatoda tepidariorum'], ['Transcript', 'Nucleotide', 'TPRE_new_ids.fna', 'Trichogramma pretiosum'], ['Protein', 'Peptide', 'AGLA_new_ids.faa', 'Anoplophora glabripennis'], ['Protein', 'Peptide', 'AROS_new_ids.faa', 'Athalia rosae'], ['Protein', 'Peptide', 'CCAP_new_ids.faa', 'Ceratitis capitata'], ['Protein', 'Peptide', 'CLEC_new_ids.faa', 'Cimex lectularius'], ['Protein', 'Peptide', 'maker_genes_diaci1.1_proteins_NALmod_new_ids.fasta', 'Diaphorina citri'], ['Protein', 'Peptide', 'EDAN_new_ids.faa', 'Ephemera danica'], ['Protein', 'Peptide', 'EAFF_new_ids.faa', 'Eurytemora affinis'], ['Protein', 'Peptide', 'FOCC_new_ids.faa', 'Frankliniella occidentalis'], ['Protein', 'Peptide', 'LFUL_new_ids.faa', 'Ladona fulva'], ['Protein', 'Peptide', 'LDEC_new_ids.faa', 'Leptinotarsa decemlineata'], ['Protein', 'Peptide', 'OFAS_new_ids.faa', 'Oncopeltus fasciatus'], ['Protein', 'Peptide', 'OABI_new_ids.faa', 'Orussus abietinus'], ['Protein', 'Peptide', 'PVEN_new_ids.faa', 'Pachypsylla venusta'], ['Protein', 'Peptide', 'PTEP_new_ids.faa', 'Parasteatoda tepidariorum'], ['Protein', 'Peptide', 'TPRE_new_ids.faa', 'Trichogramma pretiosum']];
// Sort dataset_list by organism

var dataset_dict = {};
var organism_list = [];
var alphabet_list = [];
var dataset_list_count = dataset_list.length;
for (var i = 0; i < dataset_list_count; i++) {
    var entry = dataset_list[i];
	var data_type = entry[0];
	var alphabet = entry[1];
	var file_name = entry[2];
	var organism_name = entry[3];
	var description = entry[4];
    if (!(organism_name in dataset_dict)) {
		dataset_dict[organism_name] = {};
		organism_list.push(organism_name);
		//console.log(organism_name);
	}
	if (!(alphabet in dataset_dict[organism_name])) {
		dataset_dict[organism_name][alphabet] = [];
	}
	if ($.inArray(alphabet, alphabet_list) < 0) {
		alphabet_list.push(alphabet);
	}
	dataset_dict[organism_name][alphabet].push([file_name, data_type, description]); // add info
}
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
	///////////////////////////////
	// HTML STRUCTURE GENERATION //
	///////////////////////////////
	
	//Reset all element if reload of previous page when back button is pressed
	if($('#click_submit_hidden').val() == 'true') {
		$('#click_submit_hidden').val('false');
        $('#query-textarea').val('');
		$(".query-file").replaceWith('<input type="file" name="query-file" class="query-file">');
        $('.all-organism-checkbox').prop("checked", false).attr("checked", false);
        $('.all-organism-checkbox').change();
        $('.program').attr('disabled', false).removeClass('disabled-radio');
		chooseProgram();
	}
	
	var organism_list_count = organism_list.length;
	var alphabet_list_count = alphabet_list.length;
	for (var i = 0; i < organism_list_count; i++) {
		var organism_id = organism_list[i].toLowerCase().replace(' ', '-');
		// organism-checkbox
		var $organism_checkbox = $('<input>', {
			'organism': organism_id,
			'type': 'checkbox',
			'class': 'organism-checkbox ' + organism_id,
            'name': 'organism-checkbox[]',
		});
		var $organism_div = $('<div/>', {
			'organism': organism_id,
			'class': 'organism-div italic',
		}).append($organism_checkbox).append(organism_list[i]);
		$('<label/>').append($organism_div).appendTo('#box-organism');
		var $organism_datasets_div = $('<div/>', {
			'class': organism_id + ' datasets-div',
			'style': 'display: none',
		}).appendTo('#box-datasets');
		$('<div class="dataset-title">' + organism_list[i] + '</div>').appendTo($organism_datasets_div);
		var dataset_i = 1;
		for (var j = 0; j < alphabet_list_count; j++) {
			if (alphabet_list[j] in dataset_dict[organism_list[i]]) {
				var alphabet_class = alphabet_list[j].toLowerCase();
				var alphabet_fieldset_id = organism_id + '-' + alphabet_class + '-fieldset'
				var $alphabet_fieldset = $('<fieldset class="' + alphabet_class + '"><legend>' + alphabet_list[j] + '</legend></fieldset>').appendTo($organism_datasets_div);
				var entry_count = dataset_dict[organism_list[i]][alphabet_list[j]].length;
				for (var k = 0; k < entry_count; k++) {
					var file_name = dataset_dict[organism_list[i]][alphabet_list[j]][k][0];
					var data_type = dataset_dict[organism_list[i]][alphabet_list[j]][k][1];
					var description = dataset_dict[organism_list[i]][alphabet_list[j]][k][2];
					var data_type_class = data_type.toLowerCase().replace(' ', '-');
					// dataset checkbox
					var $organism_datasets_checkbox = $('<input>', {
						'type': 'checkbox',
						'name': 'db-name',
						'value': file_name,
						'organism': organism_id,
						'dataset-type': data_type_class,
						'class': 'dataset-checkbox ' + organism_id + ' ' + data_type_class + ' ' + alphabet_class,
					});
					var $organism_datasets_checkbox_div = $('<div/>').append($organism_datasets_checkbox).append(data_type + ' - ' + description);
					var $organism_datasets_label = $('<label/>').append($organism_datasets_checkbox_div);
					$alphabet_fieldset.append($organism_datasets_label);
					//dataset_i++;
				}
			}
		}
	}
	////////////////////
	// EVENT HANDLING //
	////////////////////
	var default_data_type = 'genome-assembly';
	$('.organism-div').hoverIntent(function() {
		// show and hide right panel
		$('.datasets-div').hide();
		$('.' + $(this).attr('organism') + '.datasets-div').show();
		// background toggle
		$('.organism-div').removeClass('organism-active-background'); 
		$(this).addClass('organism-active-background');
		//console.log('.' + $(this).attr('organism') + '.datasets-div');
	});
	$('.organism-checkbox').change(function(e) {
		if ($(this).is(':checked')) {
			$('.dataset-checkbox.' + $(this).attr('organism') + '.' + default_data_type).prop('checked', true).change();
			//console.log('.datasets-checkbox.' + $(this).attr('organism') + '.' + default_data_type);
		} else {
			// uncheck all dataset checkboxes of the organism
			$('.dataset-checkbox.' + $(this).attr('organism')).prop('checked', false).change();
		}
	});
	$('.dataset-checkbox').change(function() {
		if ($(this).is(':checked')) {
			// check organism checkbox
			$('.organism-checkbox.' + $(this).attr('organism')).prop('checked', true);
			default_data_type = $(this).attr('dataset-type');
		} else {
			//console.log($('.dataset-checkbox.' + $(this).attr('organism')).is(':checked'));
			// if none of the dataset checkboxes are checked
			if (!$('.dataset-checkbox.' + $(this).attr('organism')).is(':checked')) {
				// uncheck the organism checkbox
				$('.organism-checkbox.' + $(this).attr('organism')).prop('checked', false);
			}
		}
		setDatabaseType();
	});
	$('.all-organism-checkbox').change(function() {
		if ($(this).is(':checked')) {
			$('.all-dataset-checkbox.' + default_data_type).prop('checked', true);
			// check all dataset checkboxes with the dataset type
			$('.dataset-checkbox.' + default_data_type).prop('checked', true).change();
		} else {
			// uncheck all dataset checkboxes of the organism
			$('.all-dataset-checkbox').prop('checked', false).change();
		}
	});
	$('.all-dataset-checkbox').change(function() {
		if ($(this).is(':checked')) {
			// check organism checkbox
			$('.all-organism-checkbox').prop('checked', true);
			// check all dataset checkboxes with the dataset type
			$('.dataset-checkbox.' + $(this).attr('dataset-type')).prop('checked', true).change();
		} else {
			// uncheck all dataset checkboxes with the dataset type
			$('.dataset-checkbox.' + $(this).attr('dataset-type')).prop('checked', false).change();
			// if none of the dataset checkboxes are checked
			if (!$('.all-dataset-checkbox').is(':checked')) {
				// uncheck the organism checkbox
				$('.all-organism-checkbox').prop('checked', false);
			}
		}
	});
	
	var db_type = '';
	function setDatabaseType() {
		if (db_type == '') {
			// check what has been checked
			if ($('.nucleotide').is(':checked')) {
				db_type = 'nucleotide';
				$('.peptide').attr('disabled', 'disabled').addClass('disabled-fieldset');
			} else if ($('.peptide').is(':checked')) {
				db_type = 'peptide';
				$('.nucleotide').attr('disabled', 'disabled').addClass('disabled-fieldset');
			}
		} else {
			if (!$('.dataset-checkbox').is(':checked')) {
				db_type = '';
				$('.peptide').attr('disabled', false).removeClass('disabled-fieldset');
				$('.nucleotide').attr('disabled', false).removeClass('disabled-fieldset');
			}
		}
		chooseProgram();
	}
	
	var query_type = '';
	function setQueryType(qtype) {
		query_type = qtype;
		if (qtype == '') {
			$('.enter-query-text').html('Enter sequence below in <a href="docs/fasta.html">FASTA</a> format:');
		} else if (qtype == 'invalid') {
			$('.enter-query-text').html('Your sequence is invalid:');
		} else if (qtype == 'nucleotide') {
			$('.enter-query-text').html('Your sequence is detected as nucleotide:');
		} else if (qtype == 'peptide') {
			$('.enter-query-text').html('Your sequence is detected as peptide:');
		}
		chooseProgram();
	}
	
	var program_selected = 'blastn';
	var chooseProgram = _.debounce(function () {
		$('.program').attr('disabled', false).removeClass('disabled-radio');
		if (db_type == 'nucleotide') {
			$('.blastp').attr('disabled', 'disabled').addClass('disabled-radio');
			$('.blastx').attr('disabled', 'disabled').addClass('disabled-radio');
		} else if (db_type == 'peptide') {
			$('.blastn').attr('disabled', 'disabled').addClass('disabled-radio');
			$('.tblastn').attr('disabled', 'disabled').addClass('disabled-radio');
			$('.tblastx').attr('disabled', 'disabled').addClass('disabled-radio');
		}
		if (query_type == 'nucleotide') {
			$('.blastp').attr('disabled', 'disabled').addClass('disabled-radio');
			$('.tblastn').attr('disabled', 'disabled').addClass('disabled-radio');
		} else if (query_type == 'peptide') {
			$('.blastn').attr('disabled', 'disabled').addClass('disabled-radio');
			$('.blastx').attr('disabled', 'disabled').addClass('disabled-radio');
			$('.tblastx').attr('disabled', 'disabled').addClass('disabled-radio');
		}
		query_type = '';
		// select first non disabled option
		$('input.program:not([disabled])').first().prop('checked', true);
		program_selected = $('input.program:not([disabled])').first().val();
		$('.' + program_selected).mouseover();
        add_blast_options(program_selected.toUpperCase());
	}, 90);
	
	
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
	
	var parseTextarea = _.debounce(function () {
		// parse only the first 100 chars for speed
		//console.log($('#query-textarea').val());
	    var lines = $('#query-textarea').val().substring(0, 1000).match(/[^\r\n]+/g);
		if (lines == null) {
			setQueryType('');
			return;
		}
		var line_count = lines.length;
		var seq_count = 0;
		var alphabets = {};
		// http://www.ncbi.nlm.nih.gov/BLAST/blastcgihelp.shtml
		var normal_nucleic_codes = 'ATCGN';
		var valid_amino_codes = 'ABCDEFGHIKLMNPQRSTUVWXYZ*';
		var amino_only_codes = 'EFILPQZX*';
		for (var i = 0; i < line_count; i++) {
			//console.log(i + ' ' + lines[i]);
			var line = $.trim(lines[i]).toUpperCase();
			if (line[0] == '>') {
				seq_count++;
			} else {
				// check_alphabet(line);
				for (var j = 0; j < line.length; j++) {
					if (!(line[j] in alphabets)) {
						alphabets[line[j]] = 1;
					} else {
						alphabets[line[j]]++;
					}
				}
			}
		}
		//console.log(alphabets);
	    var valid_amino_count = sum(filter_key(alphabets, function (key) {
			return valid_amino_codes.indexOf(key) != -1;
		}));
	    var amino_only_count = sum(filter_key(alphabets, function (key) {
			return amino_only_codes.indexOf(key) != -1;
		}));
	    var normal_nucleic_count = sum(filter_key(alphabets, function (key) {
			return normal_nucleic_codes.indexOf(key) != -1;
		}));
		var total_count = sum(alphabets);
		// Too many degenerate codes within an input nucleotide query will cause blast.cgi to 
		// reject the input. For protein queries, too many nucleotide-like code (A,C,G,T,N) may also 
		// cause similar rejection.
		if (total_count == 0) {
			setQueryType('');
	    } else if ((normal_nucleic_count / total_count) > 0.6 && amino_only_count == 0) {
			setQueryType('nucleotide');
	    } else if (valid_amino_count == total_count) {
			setQueryType('peptide');
		} else {
			setQueryType('invalid');
		}
		//console.log(query_type, normal_nucleic_count, total_count);
	}, 150);
	$('#query-textarea').keyup(parseTextarea);
	
	 // blast program descriptions for labels and their radio buttons
	$('.blastn').mouseover(function() {
		$('#blastProgramDescription').text('blastn - Nucleotide vs. Nucleotide');
	});
	$('.tblastn').mouseover(function() {
		$('#blastProgramDescription').text('tblastn - Peptide vs. Translated Nucleotide');
	});
	$('.tblastx').mouseover(function() {
		$('#blastProgramDescription').text('tblastx - Translated Nucleotide vs. Translated Nucleotide');
	});
	$('.blastp').mouseover(function() {
		$('#blastProgramDescription').text('blastp - Peptide vs. Peptide');
	});
	$('.blastx').mouseover(function() {
		$('#blastProgramDescription').text('blastx - Translated Nucleotide vs. Peptide');
	});
	$('#fieldset-program').mouseleave(function() {
		$('.' + $('input.program:checked').val()).mouseover();
	});
	
	// example sequences for testing
	var ex_nucleotide = ">AI134428 GH11893.5prime GH Drosophila melanogaster head pOT2 Drosophila melanogaster cDNA clone GH11893 5prime similar to M21017: D.melanogaster 18S, 5.8S 2S and 28S rRNA genes, complete, and 18S rRNA gene, 5' end, clone pDm238., mRNA sequence\n\
TTATATGCTTGTCTCAAAGATTAAGCCATGCATGTCTAAGTACACACGAATTAAAAGTGAAACCGCAAAAGGCTCATTATATCAGTTATGGTTCCTTAGATCGTTAACAGTTACTTGGATAACTGTGGTAATTCTAGAGCTAATACATGCAATTAAAACATGAACCTTATGGGACATGTGCTTTTATTAGGCTAAAACCAAGCGATCGCAAGATCGTTATATTGGTTGAACTCTAGATAACATGCAGATCGTATGGTCTTGTACCGACGACAGATCTTTCAAATGTCTGCCCTATCAACTTTTGATGGTAGTATCTAGGACTACCATGGTTGCAACGGGTAACGGGGAATCAGGGTTCGATTCCGGAGAGGGAGCCTGAGAAACGGCTACCACATCTAAGGAAGGCAGCAGGCGCGTAAATTACCCACTCCCAGCTCGGGGAGGTAGTGACGAAAAATAACAATACAGGACTCATATCCGAGGCCCTGTAATTGGAATGAGTACACTAAAAAAAAAAAAAATAGAAAAAAAGAAAAATTAAAAATTTAAAAAAAATAAAAAA\n\
>TCALIF_07877-PA transcript Name:'Similar to Actin, muscle (Manduca sexta)' offset:143 AED:0.01 eAED:0.01 QI:143|1|0.5|1|1|1|2|0|376\n\
TCGACCTCCGAGGTCGACTATAAAAGACCTCGGCGCTTTAGTTCGGTGTCACAGATTGTTTCCAGCATCTGCATACGGAGCACCGCTCTCGTTGATCCCATCTTTTTCTCCATTCCCAAACCTCCGAAAACTCTACCTTCAACATGTGTGACGAGGATGTTGCCGCTTTGGTCGTTGACAACGGCTCCGGTATGTGCAAGGCCGGATTCGCCGGTGACGATGCTCCCCGTGCAGTGTTCCCCTCCATTGTCGGCCGCCCCAGACATCAGGGTGTGATGGTCGGTATGGGACAAAAGGACGCCTATGTGGGTGATGAGGCCCAATCCAAGCGTGGTATCTTGACCCTCAAGTACCCCGTGGAGCACGGGATCATCACCAACTGGGACGATATGGAGAAAATCTGGCATCACACCTTCTACAACGAGCTCCGTGTGGCCCCCGAGGAGCAGCCCGTCCTCTTGACTGAGGCCCCCTTGAACCCCAAGGCCAACCGAGAGAAGATGACTCAAATCATGTTCGAGACCTTCAACATGCCCGCCATGTACGTGGCCATCCAAGCCGTGCTCTCCCTGTACGCCTCCGGTCGTACCACCGGTATCGTCATGGACTCCGGCGACGGTGTGTCCCACACCGTGCCCATCTATGAAGGTTACGCCCTGCCCCACGCCATCCTCCGTCTGGACTTGGCTGGCCGTGAGCTCACCAACTACTTGATGAAGATCCTCACCGAGCGCGGTTACTCGTTCACCACCACCGCCGAGCGCGAGATCGTGCGCGACATCAAGGAGAAGCTCTGCTACGTGGCCCTGGACTTTGAGCAGGAAATGGCCACGGCCGCCGCCTCCACCTCCCTGGAGAAGTCCTACGAGCTTCCCGACGGCCAAGTCATCACCATTGGCAACGAGCGCTTCCGCGCCCCTGAGGCCCTCTTCCAACCTTCCTTCTTGGGTATGGAATCCTGCGGCATCCACGAGACCACCTACAACTCCATCATGAAGTGCGACGTGGACATCCGTAAGGACTTGTACGCCAACACCGTCATGTCCGGCGGCACCACCATGTACCCCGGTATCGCCGATCGTATGCAGAAGGAGATCACCGCCTTGGCTCCCTCCACCATTAAGATCAAGATCATCGCTCCCCCTGAGAGGAAATACTCCGTCTGGATCGGAGGCTCCATCTTGGCTTCCCTGTCCACCTTCCAACAGATGTGGATCTCCAAGCAGGAGTACGACGAGTGCGGTCCCTCCATTGTCCATCGCAAGTGCTTCTAA\n";
	var ex_peptide = ">M.tuberculosis H37Rv|Rv2565|Rv2565\n\
MTTARRRPKRRGTDARTALRNVPILADIDDEQLERLATTVERRHVPANQWLFHAGEPADSIYIVDSGRFVAVAPEGHVFAEMASGDSIGDLGVIAGAARSAGVRALRDGVVWRIAAETFTDMLEATPLLQSAMLRAMARMLRQSRPAKTARRPRVIGVVSNGDTAAAPMVDAIATSLDSHGRTAVIAPPVETTSAVQEYDELVEAFSETLDRAERSNDWVLVVADRGAGDLWRHYVSAQSDRLVVLVDQRYPPDAVDSLATQRPVHLITCLAEPDPSWWDRLAPVSHHPANSDGFGALARRIAGRSLGLVMAGGGARGLAHFGVYQELTEAGVVIDRFGGTSSGAIASAAFALGMDAGDAIAAAREFIAGSDPLGDYTIPISALTRGGRVDRLVQGFFGNTLIEHLPRGFFSVSADMITGDQIIHRRGSVSGAVRASISIPGLIPPVHNGEQLLVDGGLLNNLPANVMCADTDGEVICVDLRRTFVPSKGFGLLPPIVTPPGLLRRLLTGTDNALPPLQETLLRAFDLAASTANLRELPRVAAIIEPDVSKIGVLNFKQIDAALEAGRMAARAALQAQPDLVR\n\
>TCALIF_07877-PA protein Name:'Similar to Actin, muscle (Manduca sexta)' AED:0.01 eAED:0.01 QI:143|1|0.5|1|1|1|2|0|376\n\
MCDEDVAALVVDNGSGMCKAGFAGDDAPRAVFPSIVGRPRHQGVMVGMGQKDAYVGDEAQSKRGILTLKYPVEHGIITNWDDMEKIWHHTFYNELRVAPEEQPVLLTEAPLNPKANREKMTQIMFETFNMPAMYVAIQAVLSLYASGRTTGIVMDSGDGVSHTVPIYEGYALPHAILRLDLAGRELTNYLMKILTERGYSFTTTAEREIVRDIKEKLCYVALDFEQEMATAAASTSLEKSYELPDGQVITIGNERFRAPEALFQPSFLGMESCGIHETTYNSIMKCDVDIRKDLYANTVMSGGTTMYPGIADRMQKEITALAPSTIKIKIIAPPERKYSVWIGGSILASLSTFQQMWISKQEYDECGPSIVHRKCF\n";
   	$('.load-nucleotide').click(function() {
		$('#query-textarea').val(ex_nucleotide);
		$('#query-textarea').keyup();
	});
   	$('.load-peptide').click(function() {
		$('#query-textarea').val(ex_peptide);
		$('#query-textarea').keyup();
	});
	
	// load file into textarea
	$('.query-file').change(function(evt) {
		if (window.File && window.FileReader) {
			var f = evt.target.files[0]; 
			console.log(f.type);
			if (f && (f.type.match('text.*') || f.type == '')) {
				var r = new FileReader();
				r.onload = function(e) { 
					var contents = e.target.result;
					$('#query-textarea').val(contents);
					$('#query-textarea').keyup();  
				}
				r.readAsText(f);
			}
		}
    });

    function add_blast_options(blast_program) {
        var html_content='';
        
        $('#fieldset-options-blast legend:first').html(blast_program+' Options');   //Show the option title
        $('#fieldset-options-blast label.error').remove();
		$('.parms').hide().addClass('unselected_parms');
		$('.' + blast_program.toLowerCase() + '-parms').show();
		$('.' + blast_program.toLowerCase() + '-parms').removeClass('unselected_parms');
        
		$('.chk_low_complexity').change();
		$('.chk_soft_masking').change();
                
        }
        
        // Validate MainBlastForm form on keyup and submit
        $("#MainBlastForm").validate({
            rules: {
                'query-sequence': {
                    //'textarea_valid':'', 
                    required: true
                },
                'organism-checkbox[]': {
                    required: true
                },
                'db-name': {
                    required: true
                },
                evalue: {
                    required: true,
                    number: true
                },
                word_size: {
                    required: true,
                    number: true
                },
                reward: {
                    required: true,
                    number: true
                },
                penalty: {
                    required: true,
                    number: true
                },
                gapopen: {
                    required: true,
                    number: true
                },
                gapextend: {
                    required: true,
                    number: true
                },
                threshold: {
                    required: true,
                    number: true
                }
            },
            messages: {
                'query-sequence': {
                    required: "No sequence found!"
                },
                'organism-checkbox[]': {
                    required: "Please choose at least one organism"
                },
                'db-name': {
                    required: "Please choose the type of databases"
                },
                evalue: {
                    required: "Please provide an E-value",
                    number: "Please enter a valid number"
                },
                word_size: {
                    required: "Please provide word size value",
                    number: "Please enter a valid number"
                },
                reward: {
                    required: "Please provide match score value",
                    number: "Please enter a valid number"
                },
                penalty: {
                    required: "Please provide mismatch score value",
                    number: "Please enter a valid number"
                },
                gapopen: {
                    required: "Please provide a value for gap opening penalty",
                    number: "Please enter a valid number"
                },
                gapextend: {
                    required: "Please provide a value for gap extension penalty",
                    number: "Please enter a valid number"
                },
                threshold: {
                    required: "Please provide a threshold",
                    number: "Please enter a valid number"
                }
            },
            errorPlacement: function (error, element){
                switch (element.attr('name').toString()) {
                    case 'query-sequence':
                        error.insertAfter('#legend-sequence');
                        break;
                    case 'organism-checkbox[]':
                        error.insertAfter('#legend-Organisms');
                        break;
                    case 'db-name':
                        error.insertAfter('.dataset-title');
                        break;
                    default:
                        error.insertAfter(element);
                }
        }
    });
    
    $('input.program:radio').click(function() {
        add_blast_options($('input.program:checked').val().toUpperCase());
	});
    
    $('.btn_reset').click(function() {
        $('#query-textarea').val('');
        $('.all-organism-checkbox').prop("checked", false).attr("checked", false);
        $('.all-organism-checkbox').change();
        $('.program').attr('disabled', false).removeClass('disabled-radio');
        add_blast_options('BLASTN');
        //$(".query-file").replaceWith('<input type="file" name="query-file" class="query-file">');
        
        $('label.error').remove();
        $('#MainBlastForm')[0].reset();
    });
    
	$('.chk_low_complexity').change(function() {
		if ($('#'+$('input.program:checked').val()+'_chk_low_complexity').is(':checked')) {
			$('#low_complexity_hidden').val('yes');
		}else {
			$('#low_complexity_hidden').val('no');
		}
    });
    
	$('.chk_soft_masking').change(function() {
		if ($('#'+$('input.program:checked').val()+'_chk_soft_masking').is(':checked')) {
			$('#soft_masking_hidden').val('true');
		}else {
			$('#soft_masking_hidden').val('false');
		}
	});
	
    add_blast_options('BLASTN'); //show initially
        
});

function On_Submit(){
    if($("#MainBlastForm").valid()) {
		$('.unselected_parms').remove();
		$('#click_submit_hidden').val('true');	//Use for a back button is pressed. See line 52. 
        $('#MainBlastForm').submit();
    }
}

//prevention of cache pages
$(window).unload(function () { });