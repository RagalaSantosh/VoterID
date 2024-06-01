import pandas as pd

caste_file_path = './caste.xlsx'


def caste_function(df3, caste_file):
    df = df3.copy(deep=True)
    caste_df = pd.read_excel(caste_file, sheet_name='Caste' )
    caste_df.columns = ["Sub_Caste", "caste"]
    new_df = pd.merge(df, caste_df, how='left', left_on='sub_caste', right_on='Sub_Caste')

    return new_df


def sub_caste_function(df3, caste_file):
    try:
        df = df3.copy(deep=True)
        df["name"].fillna("not available", inplace=True)
        # read caste file
        df_name = pd.ExcelFile(caste_file)

        for sheet in df_name.sheet_names:
            if sheet == "Caste":
                continue
            else:
                caste_df = pd.read_excel(caste_file, sheet_name=sheet)

                # looping through sheets
                if len(caste_df) > 0:
                    caste_list = list(caste_df["Names"])
                    temp = (map(lambda x: x.lower(), caste_list))
                    caste_list = list(temp)

                    rowcount = 0

                    # Checking father name
                    for name in df["father"]:

                        for i in range(len(caste_list)):
                            if name != "":
                                if caste_list[i].lower() in name.lower():
                                    df.at[rowcount, "sub_caste"] = sheet
                                    break
                        rowcount += 1

                    # Hindu and name
                    rowcount = 0

                    for name in df["name"]:
                        # print(name)
                        for i in range(len(caste_list)):
                            print("caste_list", caste_list[i])
                            print("name", name)
                            if not name or pd.isnull(name):
                                if caste_list[i].lower() in name.lower():
                                    df.at[rowcount, "sub_caste"] = sheet
                                    break
                            rowcount += 1
    except:
        print('Error while reading caste file.')
        exit(0)

    return df


df3 = pd.read_excel(r'./output/Materdata of Electroll rolls 1 to 100.xlsx', sheet_name="Extract")

df1 = sub_caste_function(df3, caste_file_path)

final_df = caste_function(df1, caste_file_path)
print(final_df.columns)
export_df = final_df[['id', 'page', 'split', 'polling station',
                      'polling address', 'voterid', 'name', 'father', 'address', 'age',
                      'gender', 'religion', 'key_identifier', 'source', 'caste', 'sub_caste']]

export_df.to_excel('Materdata of Electroll rolls 1 to 100.xlsx')
