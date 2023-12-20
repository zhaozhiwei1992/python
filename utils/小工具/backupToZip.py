#! python3
# backupToZip.py
# Copies an entire folder and its contents into
# a zip file whose filename increments.

import zipfile, os, sys, logging

logging.basicConfig(level=logging.DEBUG)
def backupToZip(folder):
    # Backup the entire contents of "folder" into a zip file.

    folder = os.path.abspath(folder) # make sure folder is absolute

    # Figure out the filename this code should used based on 
    # what files already exist.
    number = 1
    while True:
        zipFilename = os.path.basename(folder) + '_' + str(number) + '.zip'
        if not os.path.exists(zipFilename):
            break
        number = number + 1

    # Create the zip file.
    # INFO:root:Creating tmp_4.zip...
    logging.info('Creating %s...' % (zipFilename))
    backupZip = zipfile.ZipFile(zipFilename, 'w')

    # Walk the entire folder tree and compress the files in each folder.

    # DEBUG:root:fordername: D:\tmp .
    # DEBUG:root:subfolders: ['pythontest'] .
    # DEBUG:root:filenames: ['capitalsquiz1.txt', 'capitalsquiz10.txt', 'capitalsquiz2.txt', 'capitalsquiz3.txt', 'capitalsquiz4.txt', 'capitalsquiz5.txt', 'capitalsquiz6.txt', 'capitalsquiz7.txt', 'capitalsquiz8.txt', 'capitalsquiz9.txt', 'capitalsquiz_answers1.txt', 'capitalsquiz_answers10.txt', 'capitalsquiz_answers2.txt', 'capitalsquiz_answers3.txt', 'capitalsquiz_answers4.txt', 'capitalsquiz_answers5.txt', 'capitalsquiz_answers6.txt', 'capitalsquiz_answers7.txt', 'capitalsquiz_answers8.txt', 'capitalsquiz_answers9.txt', 'gp-workbench.log'] .
    # INFO:root:Adding files in D:\tmp...

    # DEBUG:root:fordername: D:\tmp\pythontest .
    # DEBUG:root:subfolders: ['1'] .
    # DEBUG:root:filenames: [] .
    # INFO:root:Adding files in D:\tmp\pythontest...

    # DEBUG:root:fordername: D:\tmp\pythontest\1 .
    # DEBUG:root:subfolders: [] .
    # DEBUG:root:filenames: ['hello.txt'] .
    # INFO:root:Adding files in D:\tmp\pythontest\1...
    # INFO:root:Done.
    for foldername, subfolders, filenames in os.walk(folder):
        logging.debug('fordername: %s .' % (foldername))
        logging.debug("subfolders: %s ." % (subfolders))
        logging.debug("filenames: %s ." %(filenames))
        logging.info('Adding files in %s...' % (foldername))
        # Add the current folder to the ZIP file.
        backupZip.write(foldername)

        # Add all the files in this folder to the ZIP file.
        for filename in filenames:
            # don't backup the backup ZIP files
            if filename.startswith(os.path.basename(folder) + '_') and filename.endswith('.zip'):
                continue 
            backupZip.write(os.path.join(foldername, filename))
    backupZip.close()
    logging.info('Done.')

# logging.info(sys.argv)
if(len(sys.argv)) < 1:
  logging.info("请输入要压缩的目录")
else:
  # "C:\\delicious" 
  backupToZip(sys.argv[1])
