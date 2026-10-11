"""Convert BLAST+ tabular hits to GFF3 match / match_part features for JBrowse.

Contiguous HSPs with the same query, subject and strands, whose neighbours
overlap by no more than OVERLAP_CUTOFF bases, are grouped under one match.
"""
from itertools import groupby

GFF_COL_NAMES = 'seqid source type start end score strand phase attributes'.split()
HSP_DICT_COL_NAMES = 'qseqid sseqid evalue bitscore pident qlen qstart qend sstart send qstrand sstrand'.split()
OVERLAP_CUTOFF = 5

def hsp_dict_list(hsp_list, col_names):
    """Rows of typed BLAST tabular values -> dicts with strand information.

    Always let qend > qstart, if not swap both query and subject cords, than set strand.
    """
    cid = dict([(v, i) for i, v in enumerate(col_names)])
    return [dict(zip(HSP_DICT_COL_NAMES, [row[cid['qseqid']], row[cid['sseqid']], row[cid['evalue']], row[cid['bitscore']], row[cid['pident']], row[cid['qlen']], row[cid['qstart']], row[cid['qend']], row[cid['sstart']], row[cid['send']], '-' if row[cid['qend']] - row[cid['qstart']] < 0 else '+', '-' if row[cid['send']] - row[cid['sstart']] < 0 else '+'])) for row in hsp_list]


def gff_seqid(sseqid, seqid_prefix=''):
    """The reference sequence name JBrowse knows for a BLAST subject id."""
    # strip the database's sequence ID prefix (#9)
    if seqid_prefix and sseqid.startswith(seqid_prefix):
        sseqid = sseqid[len(seqid_prefix):]
    # seqid parsing currently customized for i5k
    original_seqid_tokens = sseqid.split('|')
    if len(original_seqid_tokens) < 2 or sseqid[:3] == 'gi|':
        return sseqid
    elif sseqid[:3] == 'gnl':
        return original_seqid_tokens[-1].split('_', 1)[-1]
    else:
        return original_seqid_tokens[1]


def gff3_lines(db_hsp_dict_list, blast_program, seqid_prefix=''):
    """Yield GFF3 lines (without the version pragma) for the HSPs of one database."""
    match_id = 1
    match_part_id = 1
    # sort before groupby using key = qseqid + sseqid + qstrand + sstrand
    sorted_db_hsp_dict_list = sorted(db_hsp_dict_list, key=lambda x: x['qseqid'] + x['sseqid'] + x['qstrand'] + x['sstrand'])
    # group hsps with the same key = qseqid + sseqid + qstrand + sstrand, sort groups asc on sstart or send according to sstrand
    for key_db_hsp_dict_list in [sorted(hsps, key=lambda h: (h['sstart'], h['send']) if h['sstrand'] == '+' else (h['send'], h['sstart'])) for _, hsps in groupby(sorted_db_hsp_dict_list, key=lambda x: x['qseqid'] + x['sseqid'] + x['qstrand'] + x['sstrand'])]:
        seqid = gff_seqid(key_db_hsp_dict_list[0]['sseqid'], seqid_prefix)
        gff_item = {'seqid': seqid, 'source': blast_program}
        # cut if overlap length > overlap_cutoff
        spos, qpos, matches, matches_list = 0, 0, [], []
        for hsp in key_db_hsp_dict_list:
            cut = False
            if hsp['sstrand'] == '+':
                if hsp['qstrand'] == '+':
                    if (spos - hsp['sstart'] > OVERLAP_CUTOFF or qpos - hsp['qstart'] > OVERLAP_CUTOFF):
                        cut = True
                    spos, qpos = (hsp['send'], hsp['qend'])
                else:
                    if (spos - hsp['sstart'] > OVERLAP_CUTOFF or qpos - (hsp['qlen'] - hsp['qstart']) > OVERLAP_CUTOFF):
                        cut = True
                    spos, qpos = (hsp['send'], hsp['qlen'] - hsp['qend'])
            else:
                if hsp['qstrand'] == '+':
                    if (spos - hsp['send'] > OVERLAP_CUTOFF or qpos - (hsp['qlen'] - hsp['qend']) > OVERLAP_CUTOFF):
                        cut = True
                    spos, qpos = (hsp['sstart'], hsp['qlen'] - hsp['qstart'])
                else:
                    if (spos - hsp['send'] > OVERLAP_CUTOFF or qpos - hsp['qend'] > OVERLAP_CUTOFF):
                        cut = True
                    spos, qpos = (hsp['sstart'], hsp['qstart'])
            if cut:
                matches_list.append(matches)
                matches = []
            matches.append(hsp)
        matches_list.append(matches)
        for matches in matches_list:
            gff_item['type'] = 'match'
            gff_item['start'] = str(matches[0]['sstart'] if matches[0]['sstrand'] == '+' else matches[0]['send'])
            gff_item['end'] = str(matches[-1]['send'] if matches[0]['sstrand'] == '+' else matches[-1]['sstart'])
            gff_item['score'] = '.'
            gff_item['strand'] = matches[0]['sstrand']
            gff_item['phase'] = '0' # for type CDS, this is not the frame
            gff_item['attributes'] = 'ID=match%05d;Name=%s;Target=%s %d %d %s' % (match_id, matches[0]['qseqid'], matches[0]['qseqid'], min(matches[0]['qstart'], matches[0]['qend'], matches[-1]['qstart'], matches[-1]['qend']), max(matches[0]['qstart'], matches[0]['qend'], matches[-1]['qstart'], matches[-1]['qend']), matches[0]['qstrand'])
            if len(matches) == 1:
                gff_item['score'] = str(matches[0]['evalue'])
            yield '\t'.join([gff_item[c] for c in GFF_COL_NAMES]) + '\n'
            gff_item['type'] = 'match_part'
            for match_part in matches:
                gff_item['start'] = str(match_part['sstart'] if match_part['sstrand'] == '+' else match_part['send'])
                gff_item['end'] = str(match_part['send'] if match_part['sstrand'] == '+' else match_part['sstart'])
                gff_item['score'] = str(match_part['evalue'])
                # Bitscore is kept as it was for existing consumers; the e-value
                # (also in the score column) and percent identity were added for #12.
                gff_item['attributes'] = 'ID=match_part%05d;Parent=match%05d;Target=%s %d %d %s;Bitscore=%g;evalue=%g;pident=%g' % (match_part_id, match_id, match_part['qseqid'], min(match_part['qstart'], match_part['qend']), max(match_part['qstart'], match_part['qend']), match_part['qstrand'], match_part['bitscore'], match_part['evalue'], match_part['pident'])
                yield '\t'.join([gff_item[c] for c in GFF_COL_NAMES]) + '\n'
                match_part_id += 1
            match_id += 1


def write_gff3(fgff, db_hsp_dict_list, blast_program, seqid_prefix=''):
    fgff.write('##gff-version 3\n')
    for line in gff3_lines(db_hsp_dict_list, blast_program, seqid_prefix):
        fgff.write(line)
