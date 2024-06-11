import os
import time
import glob
import shutil
i = 1
while True:
    lst_file_csv = []
    lst_folder_zip = []
    file_csv_path = os.getcwd() +'/File_Result_*'
    for file_csv in glob.glob(file_csv_path):
        file_csv_name = os.path.basename(file_csv)
        lst_file_csv.append(file_csv_name)

    folder_zip_path = os.getcwd() +'/Result-*'
    for folder_zip in glob.glob(folder_zip_path):
        folder_zip_name = os.path.basename(folder_zip)
        lst_folder_zip.append(folder_zip_name)

    if len(lst_file_csv) > 0:
        try:
            for file_csv in lst_file_csv:
                os.remove(file_csv)
                print(file_csv,' has been deleted')
        except:
            print("Can not delete file")
    else:
        print('No Result CSV File')

    if len(lst_folder_zip) > 0:
        try:
            for folder_zip in lst_folder_zip:
                if '.zip' in folder_zip:
                    os.remove(folder_zip)
                    print(folder_zip,' has been deleted')
                else:
                    shutil.rmtree(folder_zip)
        except:
            print("Can not delete file")
    else:
        print('No Result Folder and Zip File')

    print('Loops : ',i)
    i += 1
    time.sleep(72 * 60 * 60)