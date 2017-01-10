# imgnow-helper
An app to help the mass-extraction of files from ImageNow.

This app will take raw documents exported from ImageNow as either tiffs or pdfs and convert/combine/rename files so that they can be used in an external system. In order to help with the renaming, a roster with applicant data should be placed in `data/roster.txt`. This will assist in filtering and renaming the ImageNow files.

## Requirements
**Images**: Using the Export feature from ImageNow Client (PC version only, not WebNow), export a set of documents using the default export settings. Place the exported images in the `queue/` folder.

**Roster**: Add a tab-delimited roster file containing applicant data to the project under `data/roster.txt`. This roster should contain have a header row with at least the following fields: `emplid`, `acad_career`, `first_name`, `last_name`, and `prog_status`.


## Installation
### Install Python 3
Verify Python 3+ is installed on your machine by running the following Terminal command:

    python3 --version

If Python 3 is not installed, download the latest release from [Python.org](https://www.python.org/downloads/mac-osx/).

### Clone/Download Project
Clone or download this project to create a local copy of the files on your machine. I would recommend creating a `projects` folder under your user directory:

    /Users/{your_account}/projects/imgnow-helper/

### Open Project in Terminal
Open a Terminal window and navigate to your project folder with the following command:

    cd ~/projects/imgnow-helper

### Make Virtual Environment
Create a virtual environment for the project with the following Terminal command:

    python3 -m venv env

### Activate Virtual Environment
Activate your virtual environment with:

    source env/bin/activate

Once active, your bash prompt will be prefixed with `(venv)`.

### Install Requirements
All required packages are listed in `requirements.txt`

    pip install -r requirements.txt
    
### Run Setup Script
Run the setup script to build the project folder structure. This will ensure all of the required folders exist for the app to run.

    python3 setup.py


## Usage & Program Workflow
Once the project is installed, add the latest `roster.txt` file to the data directory and add images to the queue folder. Run the following Terminal commands in sequence:

    cd ~/projects/imgnow-helper
    source env/bin/activate
    python3 imgnow-helper.py
    
The program will begin processing files.

First the queue folder is worked. Images will be grouped, converted, and combined with the output file being moved to the processing folder. Once all conversion has finished, the program will begin working through the processing folder by parsing the ImageNow keys contained in each filename and trying to match against the roster. If the program finds a match and that application is still under consideration, that file will be renamed with the applicant's name and moved to the ready folder.

All source files will be moved to the archive folder for safe keeping. Any files with conversion errors or filename errors will be moved to the errors folder. If a filename is valid but the program cannot find a match in the roster, the file will be left in the processing folder so that it will be processed again in a future run with an updated roster (useful since images are available same-day but application data refreshes nightly). Files that match an inactive application (prog_status is CN) will be moved to the inactive folder.

Once the program has finished, the ready folder will contain all successfully processed files. These can be removed and uploaded to the external application. All other files can be removed at will.
