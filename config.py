import os
import pandas as pd


class BaseConfig:
    input_dir = r"./input"
    output_path = r"./output"
    completed_path = r"./completed"
    google_file_path = r"./Requirement/poppler-0.68.0/include/poppler/cpp/Final Names.xlsx"
    custom_file_path = r"Religion.xlsx"
    caste_file_path = './caste.xlsx'
    df3 = pd.DataFrame(data=None,
                       columns=["id", "page", "split", "polling station", "polling address", "voterid", "name",
                                "father", "address", "age", "gender", 'religion', 'key_identifier', 'source',
                                'caste', 'sub_caste'])
    poppler_path = r"./Requirement/poppler-0.68.0/bin"
