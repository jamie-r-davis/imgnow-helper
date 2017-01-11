from datetime import datetime
from models.roster import Roster
from models.img import TIFFS2PDF, MergePDFs

import csv
import os
import re
import shutil
import sys
import textwrap


def projectCheck():
    """Ensures project folder integrity"""
    folders = ['data', 'queue', 'processing',
            'inactive', 'ready', 'errors', 'archive']
    for folder in folders:
        if not os.path.exists(folder):
            print("Project folder structure is not valid.")
            print("Run 'setup.py' to rebuild folders.")
            exit()


def preflightCheck():
    """Scans queue & processing dirs and print usage if empty"""
    USAGE = """
            To use this app, place pdfs and tiffs exported from ImageNow
            into the 'queue' folder and run this script.

            The app will convert and combine images that belong to the same
            doctype for the same person. Converted images will be renamed
            based off of the roster placed in the 'data' folder. The final
            pdfs will be found in the 'ready' folder. Images that failed to
            convert will be moved to 'errors'. All original files will be
            copied to 'archive'. As an additional feature, if an applicant
            no longer has an active program, those images will be moved to
            'inactive' so that they are not uploaded to the external system.
            """
    queue = os.listdir('queue')
    processing = os.listdir('processing')
    if len(queue) == 0 and len(processing) == 0:
        print(textwrap.dedent(USAGE))
        exit()


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
    """Moves a file group from queue/ to archive/"""
    for img in group:
        shutil.move('queue/'+img, 'archive/'+img)


def errorGroup(group):
    """Moves a file group from queue/ to errors/"""
    for img in group:
        shutil.move('queue/'+img, 'errors/'+img)


def processQueue(dir):
    """
    Processes the queue directory by grouping like files together and then converting/combining each group.
    All successfully processed files are moved to processing/.
    Errors are moved to errors/.
    Once a group has been processed, all original files are moved to archive/.
    """
    mask = lambda x: x[-4:] in ['.tif', '.pdf']  # filter to tiff and pdf only
    queue = [item for item in os.listdir(dir) if mask(item)]
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
                archiveGroup(group)
            except Exception as e:
                print(e)
                errorGroup(group)
        else:
            pass  # neither tif or pdf
            archiveGroup(group)


def processFiles(dir, roster):
    """
    Processes the processing/ directory by trying to parse an emplid out of each file name,
    performing a lookup against the roster, and renaming the file.
    Successfully processed files are moved to ready/ if they match an active application;
    files matched with an inactive application are moved to inactive.
    Errors are moved to errors/.
    Failed lookups are kept in processing/ for a future pass against a revised roster.
    """
    mask = lambda x: x.endswith('.pdf')
    files = [os.path.join(dir, item) for item in os.listdir(dir) if mask(item)]
    for pdf in files:
        bn = os.path.basename(pdf)
        filename, ext = os.path.splitext(bn)
        print("Processing {}".format(os.path.basename(pdf)))
        keys = filename.split('_')
        emplid = keys[1]
        doctype = keys[3]
        if len(emplid) != 8 or not emplid.isdigit:  # emplid consists of non-numeric
            print("  Skipping: Unable to parse emplid ({})".format(emplid))
            shutil.move(pdf, 'errors/{}'.format(bn))  # move to errors folder
            continue  # go to next pdf
        match = roster.search('emplid', emplid)
        if match == None:
            # applicant not in roster, keep in processing
            print("  Skipping: Emplid ({emplid}) not found in roster".format(emplid))
        else:
            statuses = [item['prog_status'] for item in match]
            if 'AP' in statuses:  # application pending
                fn = '{lname}, {fname} - {doctype} - {career}{ext}'.format(
                    lname=match[0]['last_name'],
                    fname=match[0]['first_name'],
                    doctype=doctype,
                    career=match[0]['acad_career'],
                    ext=ext)
                outfile = 'ready/{}'.format(fn)
                print('  Active: renaming to {}'.format(fn))
            else:
                outfile = 'inactive/{}'.format(bn)
                print('  Inactive: moving to inactive folder')
            shutil.move(pdf, outfile)


def main():
    print("SMTD Image Converter\nCopyright 2017, Crespbro Software, Inc. -- We put the pee in your pineapple.")
    print('='*80)

    projectCheck()
    preflightCheck()

    # combine and move files from queue folder
    processQueue('queue')
    print('\n'*3 + '='*80 + '\n'*3)
    # initialize a roster
    roster = Roster('data/roster.txt')
    processFiles('processing', roster)


if __name__ == '__main__':
    main()
