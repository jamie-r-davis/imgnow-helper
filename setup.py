import os


def buildProjectFolders():
    """Safely builds project folder structure"""
    folders = ['errors',
               'inactive',
               'processing',
               'ready',
               'data',
               'queue']
               
    for folder in folders:
        try:
            os.mkdir(folder)
            print("Created '{}/'".format(folder))
        except FileExistsError as e:
            print(e)


def main():
    buildProjectFolders()
    

if __name__ == '__main__':
    main()
