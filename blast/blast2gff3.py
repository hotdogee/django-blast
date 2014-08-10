import os
import sys
import subprocess
import csv
import re
from itertools import groupby
import sqlite3

__DEFINE_OVERLAP_BASE_FOR_QUERY = 5 # move this to form field

db_path = 'C:\\Users\\clee\\Desktop\\Works\\blast2gff3\\python\\blast2gff3\\blast2gff3\\blast2gff.db'

ID_num = 1
name_num = 1

#blast_out_col_name_str = 'qseqid sseqid evalue qlen slen length nident mismatch positive gapopen gaps qstart qend sstart send bitscore qcovs qframe sframe'
def blast2gff3(blast_program='blastn', csv_path='C:\\Users\\clee\\Desktop\\Works\\blast2gff3\\python\\6a991080e94a4174bbd2ac09ba840251\\6a991080e94a4174bbd2ac09ba840251.csv', blast_out_col_types = [str, str, float, int, int, int, int, int, int, int, int, int, int, int, int, float, int, int, int]):
    try:
        basedir = os.path.dirname(csv_path)
        csv_content = []
        with open(csv_path, 'r') as f:
            cr = csv.reader(f)
            for row in cr:
                row = list(convert(value) for convert, value in zip(blast_out_col_types, row))
                csv_content.append(row)
        content_groups = []
        for k, g in groupby(csv_content, lambda x: x[0]+x[1]):
            content_groups.append(list(g))      # Store group iterator as a list

        for hsps in content_groups:
        
            hsp_plus_strand = []
            hsp_minus_strand = []
            hsp_unknown_strand = []
            hsp_all_seq = []

            if check_is_genome(hsps) == 0 : continue

            for hsp in hsps: #Get HSPs data here
                # Get 'hsp' data and write out 'hsp' line
                gff_col1_sseqid = hsp[1] #sseqid
                gff_col2_source = blast_program
                gff_col3_type = ''
                gff_col7_strand = get_strand(hsp[13], hsp[14])
                if gff_col7_strand == '-': hsp[13], hsp[14] = hsp[14], hsp[13]
                gff_col4_start = hsp[13] #sstart
                gff_col5_end = hsp[14] #send
                gff_col6_score = hsp[2] #evalue
                gff_col8_phase = hsp[18]
                gff_col9_class_name = ''
                tmp_col10_qseqid = replace_blank_query_name(hsp[0]) + '_'
                tmp_col11_name = 'Query:' + replace_blank_query_name(hsp[0]) + '_'
                tmp_col12_target = blast_program + ':' + replace_blank_query_name(hsp[0])
                tmp_col15_strand = get_strand(hsp[11], hsp[12])
                if tmp_col15_strand == '-': hsp[11], hsp[12] = hsp[12], hsp[11]
                tmp_col13_query_start = hsp[11]
                tmp_col14_query_end = hsp[12]           

                tmp_hsp = [gff_col1_sseqid, gff_col2_source, gff_col3_type, gff_col4_start, gff_col5_end, gff_col6_score, gff_col7_strand, gff_col8_phase, gff_col9_class_name, tmp_col10_qseqid, tmp_col11_name, tmp_col12_target, tmp_col13_query_start, tmp_col14_query_end, tmp_col15_strand, 0, 0, 0]
                # Identify sequence strand and put it in a specified track
                if gff_col7_strand == '+':
                    hsp_plus_strand.append(tmp_hsp)
                elif gff_col7_strand == '-':
                    hsp_minus_strand.append(tmp_hsp)
                else:
                    hsp_unknown_strand.append(tmp_hsp)

            # Sort HSPs by queried sequence coordination
            hsp_plus_strand = sort_by_query_coordination(hsp_plus_strand)
            hsp_minus_strand = sort_by_query_coordination(hsp_minus_strand)
            hsp_unknown_strand = sort_by_query_coordination(hsp_unknown_strand)

            # Check overlapping at queried regions and add the flag
            hsp_plus_strand = check_query_overlap(hsp_plus_strand)
            hsp_minus_strand = check_query_overlap(hsp_minus_strand)
            hsp_unknown_strand = check_query_overlap(hsp_unknown_strand)

            # Sort HSPs by reference sequence coordination
            hsp_plus_strand = sort_by_ref_coordination(hsp_plus_strand)
            hsp_minus_strand = sort_by_ref_coordination(hsp_minus_strand)
            hsp_unknown_strand = sort_by_ref_coordination(hsp_unknown_strand)

            # Check overlapping at ref. regions and add the flag
            hsp_plus_strand = check_ref_overlap(hsp_plus_strand)
            hsp_minus_strand = check_ref_overlap(hsp_minus_strand)
            hsp_unknown_strand = check_ref_overlap(hsp_unknown_strand)

            # Merge arrays together
            hsp_all_seq.extend(make_gff(hsp_plus_strand))
            hsp_all_seq.extend(make_gff(hsp_minus_strand))
            hsp_all_seq.extend(make_gff(hsp_unknown_strand))

            output_gff(hsp_all_seq, basedir)

        return 1

    except:
        return 0

def check_is_genome(arr_hsps_input):
    global db_path

    conn = sqlite3.connect(db_path).cursor()
    conn.execute("SELECT COUNT(*) FROM sseqid2dbname, dbname2dbtype WHERE sseqid2dbname.dbname=dbname2dbtype.dbname AND sseqid2dbname.sseqid='%s' AND dbname2dbtype.dbtype='Genome Assembly'"%arr_hsps_input[0][1])
    r = conn.fetchone()[0]
    conn.close()

    return 1 if r else 0

def get_dbname(arr_hsps_input):
    global db_path

    conn = sqlite3.connect(db_path).cursor()
    conn.execute("SELECT dbname FROM sseqid2dbname WHERE sseqid='%s'"%arr_hsps_input[0][0])
    r = conn.fetchone()
    conn.close()
    if r:
        return r[0]
    else:
        return 'NA'

def get_strand(start, end):
    return '+' if end - start >= 0 else '-'

def replace_blank_query_name(qn):
    if qn=='':
        qn = 'My%20Sequence'
    return qn

# Sort start (the #3 index) and end (the #4 index) positions by ascending
def sort_by_ref_coordination(arr_needsort):
    return sorted(arr_needsort, key = lambda x : (x[3], x[4]))

# Sort start (the #12 index) and end (the #13 index) positions by ascending
def sort_by_query_coordination(arr_needsort):
    return sorted(arr_needsort, key = lambda x : (x[12], x[13]))

def check_ref_overlap(arr_hsps_input):
    if len(arr_hsps_input) == 0: #Skip null array
        return arr_hsps_input

    arr_hsps_output = []
    pre_ref_end = 0
    pre_query_start_for_plus_strand = 0
    pre_query_end_for_plus_strand = 0
    pre_query_start_for_minus_strand = max(arr_hsps_input, key=lambda x:x[12])[12] + 1
    pre_query_end_for_minus_strand = max(arr_hsps_input, key=lambda x:x[13])[13] + 1

    for arr_hsp_input in arr_hsps_input:
        if arr_hsp_input[3] < pre_ref_end:
            arr_hsp_input[16] = 1
        pre_ref_end = arr_hsp_input[4]

        # Identify the query sequences if they are consecutive (i.e., In the case of the reference sequences are sorted by ascending, if the queried sequences are consecutive, they should also be ascending order in ref. strand '+' and descending order in  ref. strand '-', respectively.)
        if arr_hsp_input[6] == '+':
            if arr_hsp_input[12] < pre_query_start_for_plus_strand and arr_hsp_input[13] < pre_query_end_for_plus_strand:
                arr_hsp_input[17] = 1
            pre_query_start_for_plus_strand = arr_hsp_input[12]
            pre_query_end_for_plus_strand = arr_hsp_input[13]
        if arr_hsp_input[6] == '-':
            if arr_hsp_input[12] > pre_query_start_for_minus_strand and arr_hsp_input[13] > pre_query_end_for_minus_strand:
                arr_hsp_input[17] = 1
            pre_query_start_for_minus_strand = arr_hsp_input[12]
            pre_query_end_for_minus_strand = arr_hsp_input[13]

        arr_hsps_output.append(arr_hsp_input)

    return arr_hsps_output

def check_query_overlap(arr_hsps_input):
    define_overlap_base_for_query = __DEFINE_OVERLAP_BASE_FOR_QUERY
    arr_hsps_output = []
    pre_query_end = 0

    for arr_hsp_input in arr_hsps_input:
        if arr_hsp_input[12] < pre_query_end and pre_query_end - arr_hsp_input[12] > define_overlap_base_for_query:
            arr_hsp_input[15] = 1
        
        pre_query_end = arr_hsp_input[13]

        arr_hsps_output.append(arr_hsp_input)

    return arr_hsps_output

def make_gff(arr_hsps_input):
    if len(arr_hsps_input) == 0: #Skip null array
        return arr_hsps_input

    global ID_num
    global name_num

    arr_hsps_output = []
    is_query_seq_overlap = 0
    is_ref_seq_overlap = 0
    is_query_seq_non_consecutive = 0

    min_ref_start = arr_hsps_input[0][3]
    max_ref_end = 0

    #Pre-scan all flag for identification of class names (the 9th column), and get the maximum end position.
    for arr_hsp_input in arr_hsps_input:
        if arr_hsp_input[15] == 1:
            is_query_seq_overlap = 1
        if arr_hsp_input[16] == 1:
            is_ref_seq_overlap = 1
        if arr_hsp_input[17] == 1:
            is_query_seq_non_consecutive = 1

        if arr_hsp_input[4] > max_ref_end:
            max_ref_end = arr_hsp_input[4]
    
    # Congratulations! All HSPs here are perfect (i.e.,no overlapping and all consecutive) and can be linked together with a track
    if (is_query_seq_overlap or is_ref_seq_overlap or is_query_seq_non_consecutive) == 0: 
        sub_ID_num = 1 # The suffix number of match_part HSPs in a track

        # Generate the match record
        tmp_match = [arr_hsps_input[0][0], 
                     arr_hsps_input[0][1], 
                     'match', 
                     min_ref_start, 
                     max_ref_end, 
                     arr_hsps_input[0][5], 
                     arr_hsps_input[0][6], 
                     arr_hsps_input[0][7], 
                     'ID='+arr_hsps_input[0][9]+'%04d;Name='%ID_num+arr_hsps_input[0][10]+'0001;Target='+arr_hsps_input[0][11]+' '+str(arr_hsps_input[0][12])+' '+str(arr_hsps_input[0][13])+' '+arr_hsps_input[0][14]]

        # Put tmp_match into hsp_output
        arr_hsps_output.append(tmp_match)

        # Generate the match_part record
        for arr_hsp_input in arr_hsps_input:
            tmp_match_part = [arr_hsp_input[0], 
                                  arr_hsp_input[1], 
                                  'match_part', 
                                  arr_hsp_input[3], 
                                  arr_hsp_input[4], 
                                  arr_hsp_input[5], 
                                  arr_hsp_input[6], 
                                  arr_hsp_input[7], 
                                  'ID='+arr_hsp_input[9]+'%04d_%04d;Parent='%(ID_num, sub_ID_num)+arr_hsp_input[9]+'%04d;Target='%ID_num+arr_hsp_input[11]+' '+str(arr_hsp_input[12])+' '+str(arr_hsp_input[13])+' '+arr_hsp_input[14]]
        
            # Put tmp_match_part into hsp_output
            arr_hsps_output.append(tmp_match_part)

            sub_ID_num += 1

        ID_num += 1

    # Oops! Overlapping or non-consecutive sequences are occurred
    else:
        for arr_hsp_input in arr_hsps_input:
            # The HSP's ref. seq coordination is overlapping, it should be created a new track
            if arr_hsp_input[16] == 1:
                name_num += 1
                # Generate the match record
                tmp_match = [arr_hsp_input[0], 
                                  arr_hsp_input[1], 
                                  'match', 
                                  arr_hsp_input[3], 
                                  arr_hsp_input[4], 
                                  arr_hsp_input[5], 
                                  arr_hsp_input[6], 
                                  arr_hsp_input[7], 
                                  'ID='+arr_hsp_input[9]+'%04d;Name='%ID_num+arr_hsp_input[10]+'%04d;Target='%name_num+arr_hsp_input[11]+' '+str(arr_hsp_input[12])+' '+str(arr_hsp_input[13])+' '+arr_hsp_input[14]]

                # Put tmp_match into hsp_output
                arr_hsps_output.append(tmp_match)

                # Generate the match_part record
                tmp_match_part = [arr_hsp_input[0], 
                                       arr_hsp_input[1], 
                                       'match_part', 
                                       arr_hsp_input[3], 
                                       arr_hsp_input[4], 
                                       arr_hsp_input[5], 
                                       arr_hsp_input[6], 
                                       arr_hsp_input[7], 
                                       'ID='+arr_hsp_input[9]+'%04d_0001;Parent='%ID_num+arr_hsp_input[9]+'%04d;Target='%ID_num+arr_hsp_input[11]+' '+str(arr_hsp_input[12])+' '+str(arr_hsp_input[13])+' '+arr_hsp_input[14]]

                # Put tmp_match_part into hsp_output
                arr_hsps_output.append(tmp_match_part)

            # Use the same track here in the conditions of query sequences overlapping or non-consecutive
            else:
                # Generate the match record
                tmp_match = [arr_hsp_input[0], 
                                  arr_hsp_input[1], 
                                  'match', 
                                  arr_hsp_input[3], 
                                  arr_hsp_input[4], 
                                  arr_hsp_input[5], 
                                  arr_hsp_input[6], 
                                  arr_hsp_input[7], 
                                  'ID='+arr_hsp_input[9]+'%04d;Name='%ID_num+arr_hsp_input[10]+'0001;Target='+arr_hsp_input[11]+' '+str(arr_hsp_input[12])+' '+str(arr_hsp_input[13])+' '+arr_hsp_input[14]]

                # Put tmp_match into hsp_output
                arr_hsps_output.append(tmp_match)

                # Generate the match_part record
                tmp_match_part = [arr_hsp_input[0], 
                                       arr_hsp_input[1], 
                                       'match_part', 
                                       arr_hsp_input[3], 
                                       arr_hsp_input[4], 
                                       arr_hsp_input[5], 
                                       arr_hsp_input[6], 
                                       arr_hsp_input[7], 
                                       'ID='+arr_hsp_input[9]+'%04d_0001;Parent='%ID_num+arr_hsp_input[9]+'%04d;Target='%ID_num+arr_hsp_input[11]+' '+str(arr_hsp_input[12])+' '+str(arr_hsp_input[13])+' '+arr_hsp_input[14]]

                # Put tmp_match_part into hsp_output
                arr_hsps_output.append(tmp_match_part)

            ID_num += 1

    return arr_hsps_output

def output_gff(arr_hsps_input, out_path):
    try:
        save_file_name = os.path.splitext(get_dbname(arr_hsps_input))[0]+'.gff'
        fp = open(os.path.join(out_path, save_file_name), 'a')

        if os.path.getsize(os.path.join(out_path, save_file_name)) == 0:
            fp.write("##gff-version 3\n")

        jBrowse_ref_name = os.path.splitext(save_file_name)[0]
        m = re.findall('gnl\|(.+)\|(.+)', arr_hsps_input[0][0])
        if m : jBrowse_ref_name = m[0][1].split('_', 1)[1]

        m = re.findall('(diacit)\|(.*)', arr_hsps_input[0][0])
        if m : jBrowse_ref_name = m[0][1]

        for hsp in arr_hsps_input:
            tmp_str = jBrowse_ref_name+"\t"+hsp[1]+"\t"+hsp[2]+"\t"+str(hsp[3])+"\t"+str(hsp[4])+"\t"+str(hsp[5])+"\t"+hsp[6]+"\t"+str(hsp[7])+"\t"+hsp[8]+"\n"
            fp.write(tmp_str)
    
        fp.close()
        return 1

    except:
        return 0

#This function will generate an additional column of BLAST_DB which is queried by sseqid (the 2nd column in csv).
def output_csv(in_csv_path='C:\\Users\\clee\\Desktop\\Works\\blast2gff3\\python\\6a991080e94a4174bbd2ac09ba840251\\6a991080e94a4174bbd2ac09ba840251.csv', blast_out_col_types = [str, str, float, int, int, int, int, int, int, int, int, int, int, int, int, float, int, int, int]):
    ###########################################################################################################################################
    ## The hyperlinks for linking jBrowse should be formed as the format like: 
    ## http://gmod-dev.nal.usda.gov:8080/[ORGANISM]/jbrowse/?task_id=[TASK_ID]&dbname=[BLAST_DB]
    ## example: http://gmod-dev.nal.usda.gov:8080/cercap/jbrowse/?task_id=5a37a3e9994e4cac93a10621fe97e6f6&dbname=Ccap01172013-genome_new_ids
    ###########################################################################################################################################
    try:
        out_csv_path = os.path.splitext(in_csv_path)[0]+'_balst2gff.csv'

        with open(in_csv_path, 'r') as f:
            cr = csv.reader(f)
            csv_content = []
            sseqid_groups = []
            sseqid2dbname = dict()

            for row in cr:
                row = list(convert(value) for convert, value in zip(blast_out_col_types, row))
                csv_content.append(row)

        for k, g in groupby(csv_content, lambda x: x[1]):
            #sseqid_groups.append(list(g))      # Store group iterator as a list
            sseqid_groups.append(k)

        for sseqid in sseqid_groups:
            sseqid2dbname[sseqid] = str(get_dbname([[sseqid]]))

        with open(out_csv_path, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            for csv_row in csv_content:
                csv_row.append(sseqid2dbname[csv_row[1]])
                writer.writerow(csv_row)
        return 1

    except:
        return 0

## For testing function here!
print blast2gff3()
#print output_csv()


