from datetime import datetime
from models.roster import Roster
from models.img import TIFFS2PDF, MergePDFs

import csv
import os
import re
import shutil
import sys


def naturalSort(l):
    """
    sorts a list naturally
    ['im1', 'im11', 'im2'] -> ['im1', 'im2', 'im11']
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('page(\d+)', key)]
    return sorted(l, key=alphanum_key)


def groupFiles(filenames):
    """parses a directory and groups similar files together into a list of lists"""
    digest = []
    keys = None
    for item in filenames:
        item_keys = item.split('_')[:4]+[item.split('.')[-1]]
        if keys == None:  # first item in list
            keys = item_keys
            l = [item]
        elif item_keys == keys:  # file matches previous group
            l.append(item)
        else:
            l = naturalSort(l)
            digest.append(l)
            keys = item_keys
            l = [item]
    l = naturalSort(l)  # ensure pages are in order [1, 2,...11] not [1, 11, 2]
    digest.append(l)  # catch final group

    return digest

def archiveGroup(group):
    for img in group:
        shutil.move('queue/'+img, 'archive/'+img)

def errorGroup(group):
    for img in group:
        shutil.move('queue/'+img, 'errors/'+img)

def processQueue(dir):
    queue = [item for item in os.listdir(dir) if os.path.isfile(os.path.join(dir, item))]
    if len(queue) < 1:
        print("No images to process.")
        return
    # get file groups for processing
    file_groups = groupFiles(queue)

    for group in file_groups:
        group_path = [os.path.join(dir, item) for item in group]
        if group[0].endswith('tif'):  # group of tiffs
            # combine tiffs and save in processing folder
            # as first filename in group
            outname = group[0].split('.')[0] + '.pdf'
            try:
                TIFFS2PDF(group_path, 'processing/{}'.format(outname))
                archiveGroup(group)
            except Exception as e:
                print(e)
                errorgroup(group)
        elif group[0].endswith('pdf'):  # group of pdfs
            # combine pdfs and save in processing folder
            # as first filename in group
            outname = group[0].split('.')[0] + '.pdf'
            try:
                MergePDFs(group_path, 'processing/{}'.format(outname))
            except Exception as e:
                print(e)
                errorGroup(group)
        else:
            pass  # neither tif or pdf
            archiveGroup(group)

def processFiles(dir, roster):
    files = [os.path.abspath(item) for item in os.listdir(dir) if os.path.isfile(item)]
    for pdf in files:
        bn = os.path.basename(pdf)
        filename, ext = os.path.splitext(pdf)
        print("Processing {}".format(os.path.basename(pdf)))
        keys = filename.split('_')
        emplid = keys[1]
        doctype = keys[3]
        if len(emplid) != 8 or not emplid.isdigit:  # emplid consists of non-numeric
            print("  Skipping: Unable to parse emplid ({})".format(emplid))
            continue  # go to next pdf
        match = roster.search('emplid', emplid)
        if match == None:
            # applicant not in roster, keep in processing
            print("  Skipping: Emplid ({emplid}) not found in roster".format(emplid))
        else:
            statuses = [item['prog_status'] for item in match]
            if 'AP' in statuses:  # application pending
                fn = '{lname}, {fname} - {doctype} - {career}{ext}'.format(
                    lname=result['last_name'],
                    fname=result['first_name'],
                    doctype=doctype,
                    career=result['career'],
                    ext=ext)
                outfile = 'ready/{}'.format(fn)
            else:
                outfile = 'inactive/{}'.format(fn)
            shutil.mv(pdf, 'inactive/{}'.format(bn))


def main():
    print("SMTD Image Converter\nCopyright 2017, Crespbro Software, Inc. -- We put the pee in your pineapple.")
    print('='*120)

    # combine and move files from queue folder
    processQueue('queue')

    # initialize a roster
    roster = Roster('data/roster.txt')
    processFiles('processing', roster)


    #for image in processing:
    #    outfile = Roster.suggest(image)
    #    if outfile != image:
    #        shutil.move('processing/'+image, 'ready/'+image)


if __name__ == '__main__':
    main()
