import os
import logic
import pandas as pd
from datetime import datetime
import shutil
import warnings
from config import BaseConfig
warnings.filterwarnings("ignore", category=FutureWarning)

global df3

# Variable assignment

df3 = BaseConfig.df3
input_dir = BaseConfig.input_dir
output_path = BaseConfig.output_path
completed_path = BaseConfig.completed_path
google_file_path = BaseConfig.google_file_path
custom_file_path = BaseConfig.custom_file_path
caste_file_path = BaseConfig.caste_file_path
poppler_path = BaseConfig.poppler_path


# Execution starts from here.

list_of_pdfs = logic.pdfs_identification(input_dir)
print("Number of input pdfs", len(list_of_pdfs))

if len(list_of_pdfs) >= 1:
    for pdf_name in list_of_pdfs:
        print(f"File Running-- {pdf_name}")
        print(f"Number of files left {len(list_of_pdfs)-1}")
        df3 = pd.concat([df3, logic.pageSplit(input_dir, pdf_name, poppler_path)], axis=0)


# Name and Father we are updating to not found since they are primary keys in religion identification.
df3["father"].fillna("not found", inplace=True)
df3["name"].fillna("not found", inplace=True)
df3.reset_index(inplace=True, drop=True)


# We are running the religion two times. One is google source and the other is custom.
# first run
print("Current Process -- Religion mapping from Google Source")
try:
    hindu, christian, muslim = logic.excel_read(google_file_path)
    df3 = logic.religion_update(df3, hindu, christian, muslim, "google")
except:
    print("first function call has a problem")


# second run
print("Current Process -- Religion mapping from Custom Source")
try:
    hindu, christian, muslim = [], [], []
    hindu, christian, muslim = logic.excel_read(custom_file_path)
    df3 = logic.religion_update(df3, hindu, christian, muslim, "custom")
except Exception as e:
    print(f"second function call has a problem {e}")


# Identification of caste and sub caste.
print("Current Process -- Caste & Subcaste mapping")
try:
    df1 = logic.sub_caste_function(df3, caste_file_path)

    final_df = logic.caste_function(df1, caste_file_path)
    export_df = final_df[['id', 'page', 'split', 'polling station',
                          'polling address', 'voterid', 'name', 'father', 'address', 'age',
                          'gender', 'religion', 'key_identifier', 'source', 'Caste', 'sub_caste']]
except:
    print('issue while identifying caste and sub caste')


# Export the extracted output to an excel file.
print("Current Process -- Exporting extracted data to Excel")
try:
    now = datetime.now()
    finaloutput = output_path + "//" + "output" + now.strftime("%d_%m_%Y_%H_%M_%S") + ".xlsx"
    export_df.to_excel(finaloutput)
except:
    print('error while exporting the extracted data.')

# Movement of files.
print("Current Process -- Completed file movement")
try:
    logic.move_completed_files(input_dir, completed_path)
    print("Process is Completed")
except:

    print('Error while moving the input files to completed folder.')


