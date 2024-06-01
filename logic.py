import os.path
import cv2
import csv
import shutil
import pdf2image
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes
import pytesseract
import numpy as np
import re
import pandas as pd
from datetime import datetime

# global df2


pytesseract.pytesseract.tesseract_cmd = r"./Requirement/Tesseract-OCR/tesseract.exe"
df = pd.DataFrame(data=None,
                  columns=["id", "page", "split", "polling station", "polling address", "voterid", "name", "father",
                           "address", "age", "gender"])

global origfile
global splitname
global splitnum
global pollingstation
global pollingaddress


def pdfs_identification(input_dir):
    listoffiles = []
    extDict = (".jpeg", ".jpg", ".png")

    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith(".pdf".lower()):
                listoffiles.append(filename)
            elif filename.lower().endswith(tuple(extDict)):
                os.remove(os.path.join(root, filename))

    return listoffiles


def extract_polling_station_details(file):
    global pollingstation
    global pollingaddress

    img = cv2.imread(file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config='--psm 4').replace('\n\n', '\n')

    # print(type(text))

    linesoftext = text.split("\n")

    firstrow = next(i for i, value in enumerate(linesoftext) if "Male/Female".lower() in value.lower()) + 1
    secondrow = next(i for i, value in enumerate(linesoftext) if "Stations in this part".lower() in value.lower()) + 1

    pollingstation = linesoftext[firstrow]
    pollingaddress = linesoftext[secondrow]


def imgcrop(input_file, indicator):
    page = []

    filename, file_extension = os.path.splitext(os.path.basename(input_file))
    filepath = os.path.dirname(input_file) + "\\" + 'Splits' + "\\"
    if os.path.exists(filepath):
        pass
    else:
        os.mkdir(filepath)
    # print(filepath, filename, file_extension)
    # print(os.path.join(filepath+filename))
    if indicator == 1:
        reqcut = 120
    else:
        reqcut = 200
    im = Image.open(input_file)
    box1 = (0, reqcut, 570, 2180)
    a = im.crop(box1)
    a.save(os.path.join(filepath + filename) + "-" + str(0) + "-" + str(0) + file_extension)
    page.append(os.path.join(filepath + filename) + "-" + str(0) + "-" + str(0) + file_extension)
    box2 = (571, reqcut, 1070, 2180)
    b = im.crop(box2)
    b.save(os.path.join(filepath + filename) + "-" + str(1) + "-" + str(1) + file_extension)
    page.append(os.path.join(filepath + filename) + "-" + str(1) + "-" + str(1) + file_extension)
    box3 = (1070, reqcut, 1653, 2180)
    c = im.crop(box3)
    c.save(os.path.join(filepath + filename) + "-" + str(2) + "-" + str(2) + file_extension)
    page.append(os.path.join(filepath + filename) + "-" + str(2) + "-" + str(2) + file_extension)

    return page


def pageSplit(input_dir, filename, poppler_path):
    global origfile
    global splitname
    global splitnum

    origfile = filename
    totalimages = []
    pagelist = []

    input_page_path = os.path.join(input_dir, 'pages')
    if os.path.exists(input_page_path):
        pass
    else:
        os.mkdir(input_page_path)
    print("Current Process -- PDF to Image Split")
    images = convert_from_path(os.path.join(input_dir,filename), fmt="jpeg", jpegopt={'quality': 100}, poppler_path=poppler_path)
    for image in images:
        totalimages.append(image)

    for image in range(len(totalimages)):
        totalimages[image].save(input_page_path + '\\' + 'page' + str(image) + '.jpg', 'JPEG')
        pagelist.append(input_page_path + '\\' + 'page' + str(image) + '.jpg')

    extract_polling_station_details(pagelist[0])
    # pagelist=pagelist[32:]

    totalsplitimages = []
    for pslit in range(len(pagelist)):
        splitname = os.path.basename(pagelist[pslit])
        img = cv2.imread(pagelist[pslit], cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
        inittext = pytesseract.image_to_string(img, config='--psm 6').replace('\n\n', '\n')
        maintext = inittext.split("\n")

        if "Section No and Name".lower() in maintext[1].lower():
            totalsplitimages.extend(imgcrop(pagelist[pslit], 1))
        elif "List of Additions".lower() in maintext[1].lower():
            totalsplitimages.extend(imgcrop(pagelist[pslit], 2))

    # print(totalsplitimages)
    # print(len(totalsplitimages))
    # totalsplitimages = totalsplitimages[0:1]
    table = []
    df2 = pd.DataFrame(data=None,
                       columns=["id", "page", "split", "polling station", "polling address", "voterid", "name",
                                "father",
                                "address", "age", "gender", 'religion', 'key_identifier', 'source'])

    print("Current Process -- Data Extraction from Images")

    for im in range(len(totalsplitimages)):
        splitnum = os.path.basename(totalsplitimages[im])
        img = cv2.imread(totalsplitimages[im], cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
        text = pytesseract.image_to_string(img, config='--psm 11').replace('\n\n', '\n')
        lines_text = text.split("\n")
        table.append(lines_text)
        table = [i for i in table if i]
        # print("initial table", table)
        # print(len(table))

        df2 = pd.concat([df2, dataextraction(table)], axis=0)
        table = []
    # print(len(df2))
    return df2


def dataextraction(inputlist):
    # reqlist = inputlist

    global origfile
    global splitname
    global splitnum
    global pollingstation
    global pollingaddress

    # print("data extraction input", inputlist)
    df = pd.DataFrame(data=None,
                      columns=["id", "page", "split", "polling station", "polling address", "voterid", "name", "father",
                               "address", "age", "gender"])

    for i in range(len(inputlist)):
        reqlist = inputlist[i]
        # print(reqlist)
        temp2 = []
        splitlist = []
        # print("reqlist", reqlist)
        for j in range(len(reqlist)):
            if reqlist[j].lower() == "male".lower() or reqlist[j].lower() == "female".lower():
                reqlist.insert(j - 1, reqlist[j - 1] + reqlist[j])
                reqlist.pop(j)

        for j in reqlist:
            # if j.lower()=="male".lower() or j.lower()

            # print(j)
            if ("gender".lower() in j.lower() and "male".lower() in j.lower()):

                temp2.append(j)
                splitlist.append(temp2)
                temp2 = []
            else:
                temp2.append(j)

        temp = []

        # print("splitlist", splitlist)
        # print("splitlist", len(splitlist))
        if len(splitlist) < 10:
            splitlist = []
            templist = reqlist
            start = 0
            final_list = []
            # print("templist", templist)
            templist_2 = reqlist
            for z in range(len(templist)):
                if "Name" in templist[z] and "Father" not in templist[z] \
                        and "Husband" not in templist[z] and "Mother" not in templist[z] and "Wife" not in templist[z] \
                        and "Other" not in templist[z] and "Legal" not in templist[z]:
                    if z < 4:
                        continue
                        # split_list = templist[:z]
                    else:
                        check_string = templist[z-1]
                        check_string = check_string.replace("_", "")
                        check_string = check_string.replace("[", "")
                        check_string = check_string.replace("]", "")
                        check_string = check_string.replace(" ", "")
                        # print("check_string", check_string)
                        if len(check_string)>=6:

                            final_list = templist[start:z - 1]
                            templist_2 = templist[z - 1:]

                        else:
                            final_list = templist[start:z - 2]
                            templist_2 = templist[z - 2:]

                        # templist_2 = templist[z - 1:]
                    # print("split_list", final_list)
                    splitlist.append(final_list)
                    if len(check_string) >= 6:
                        start = z - 1
                    else:
                        start = z-2
            splitlist.append(templist_2)
            # print("new_splitlist", splitlist)
            # print("new_splitlist", len(splitlist))
        for split in range(len(splitlist)):
            rowcount = len(df) + 1

            templist = splitlist[split]

            if 'Available'.lower() in (name.lower() for name in templist):
                templist.remove('Available')
            if 'Photo is' in templist:
                templist.remove('Photo is')
            if 'Photo Is' in templist:
                templist.remove('Photo Is')
            templist = [x for x in templist if len(x) > 3]

            # print("templist", templist)
            temp = []
            presentcolumn = ""
            for z in range(len(templist)):

                # print(z, templist[z])

                # if len(templist[z]) > 9 and ("Name" not in templist[z] and "House" not in templist[z]\
                #      and "Age" not in templist[z] and "Gender" not in templist[z] and "Father" not in templist[z]\
                #                              and "Husband" not in templist[z] and "Mother" not in templist[z]):
                #         df.at[rowcount, "id"]= templist[z]
                if len(templist[z]) > 9 and ("Name" not in templist[z] and "House" not in templist[z] \
                                             and "Age" not in templist[z] and "Gender" not in templist[
                                                 z] and "Father" not in templist[z] \
                                             and "Husband" not in templist[z] and "Mother" not in templist[
                                                 z] and "Wife" not in templist[z] \
                                             and "Other" not in templist[z]):
                    if presentcolumn == "":
                        df.at[rowcount, "voterid"] = templist[z][-10:]
                        df.at[rowcount, "id"] = origfile
                        df.at[rowcount, "page"] = splitname.replace(".jpg", "")
                        df.at[rowcount, "split"] = splitnum.replace("jpg", "")
                        df.at[rowcount, "polling station"] = pollingstation
                        df.at[rowcount, "polling address"] = pollingaddress
                        presentcolumn = "voterid"

                if "Name" in templist[z][0:5]:
                    df.at[rowcount, "name"] = templist[z]
                    if presentcolumn == "":
                        df.at[rowcount, "id"] = origfile
                        df.at[rowcount, "page"] = splitname.replace(".jpg", "")
                        df.at[rowcount, "split"] = splitnum.replace("jpg", "")
                        df.at[rowcount, "polling station"] = pollingstation
                        df.at[rowcount, "polling address"] = pollingaddress
                    presentcolumn = "name"
                if ("Father" in templist[z] or "Husband" in templist[z] or "Mother" in templist[z] or "Wife" in
                        templist[z] \
                        or "Other" in templist[z]):
                    df.at[rowcount, "father"] = templist[z]
                    if presentcolumn == "":
                        df.at[rowcount, "id"] = origfile
                        df.at[rowcount, "page"] = splitname.replace(".jpg", "")
                        df.at[rowcount, "split"] = splitnum.replace("jpg", "")
                        df.at[rowcount, "polling station"] = pollingstation
                        df.at[rowcount, "polling address"] = pollingaddress
                    presentcolumn = "father"
                elif "House" in templist[z]:
                    df.at[rowcount, "address"] = templist[z]
                    presentcolumn = "address"
                elif "Age".lower() in templist[z].lower() or "Gender".lower() in templist[z].lower():
                    # templist[z].split("Gender")
                    if len(templist[z].split("Gender")) > 1:
                        df.at[rowcount, "age"] = templist[z].split("Gender")[0]
                        df.at[rowcount, "gender"] = templist[z].split("Gender")[1]

                elif "female".lower() in templist[z].lower():
                    df.at[rowcount, "age"] = 'FEMALE'

                elif "male".lower() in templist[z].lower() and "female".lower() not in templist[z].lower():
                    df.at[rowcount, "age"] = 'MALE'

                elif z > 1 and ("Name" not in templist[z] and "House" not in templist[z] \
                                and "Age" not in templist[z] and "Gender" not in templist[z]):
                    # if presentcolumn:
                    df.at[rowcount, presentcolumn] = df.at[rowcount, presentcolumn] + " " + templist[z]
                #     if df.iat[rowcount,5] == "":
                #         df.at[rowcount, "address"] = df.iat(rowcount, 4)+ templist[z]
                #     elif df.iloc(rowcount, "address") == "":
                #         df.at[rowcount, "father"] = df.iloc(rowcount, "father")+ templist[z]
                #     elif df.iloc(rowcount, "father") == "":
                #         df.at[rowcount, "name"] = df.iloc(rowcount, "name")+ templist[z]
    df1 = df

    # print("lenght", len(df1))
    try:
        df1 = df1.replace('Available|Photo is', " ", regex=True)
        # df1["father"] = df1["father"].str.replace('Available|Photo is', " ", regex = True)
        df1["address"] = df1["address"].str.replace("House Number", "")
        df1["address"] = df1["address"].str.replace("FEMALE", "")
        df1["address"] = df1["address"].str.replace("MALE", "")
        df1["address"] = df1["address"].str.replace(': |: -|: =|=', '', regex=True)
        df1["address"] = df1["address"].apply(lambda x: x[1:] if str(x).startswith("-") else x)
        df1["address"] = df1["address"].apply(lambda x: x[1:] if str(x).startswith(" -") else x)
        # df1['address'] = df1['address'].str.replace('\W', '', regex = True)
        df1['gender'] = df1['gender'].str.replace('\W', '', regex=True)
        df1['age'] = df1['age'].str.replace('\D+', '', regex=True)
        df1['name'] = df1['name'].str.replace('[^\w\s]', '', regex=True)
        df1["name"] = df1["name"].str[4:]
        df1["name"] = df1["name"].apply(lambda x: x[1:] if str(x).startswith(" ") else x)
        df1["name"] = df1["name"].apply(lambda x: x[1:] if str(x).startswith(" ") else x)
        df1["voterid"] = df["voterid"].str.replace('[#,|,_,—,-,@,&]', "")
    except:
        pass
    # print("printing df1 head in extraction")
    # print(len(df1))

    return df1


def excel_read(filepath):
    try:
        hindu = pd.read_excel(filepath, sheet_name=0)
        hindu = list(hindu["Names"])
        a = (map(lambda x: x.lower(), hindu))
        hindu = list(a)
    except:
        print("Hindu file is not read properly")
    try:
        christian = pd.read_excel(filepath, sheet_name=1)
        christian = list(christian["Names"])
        b = (map(lambda x: x.lower(), christian))
        christian = list(b)
    except:
        print("Christian file is not read properly")
    try:
        muslim = pd.read_excel(filepath, sheet_name=2)
        muslim = list(muslim["Names"])
        c = (map(lambda x: x.lower(), muslim))
        muslim = list(c)
    except:
        print("Muslim file is not read properly")
    return hindu, christian, muslim


def caste_function(df3, caste_file):
    df = df3.copy(deep=True)
    caste_df = pd.read_excel(caste_file, sheet_name='Caste', )
    new_df = pd.merge(df, caste_df, how='left', left_on='sub_caste', right_on='Sub_Caste')

    return new_df


def religion_update(df2, hindu, christian, muslim, source):
    df = df2.copy(deep=True)
    rowcount = 0
    # df["father"].fillna("not found", inplace=True)
    for name in df["father"]:
        # print(name)
        for i in range(len(hindu)):
            if hindu[i].lower() in name.lower():
                df.at[rowcount, "religion"] = "hindu"
                df.at[rowcount, "key_identifier"] = str(hindu[i])
                df.at[rowcount, "source"] = source
                break
        rowcount += 1

    # Hindu and name
    rowcount = 0
    # df["name"].fillna("not found", inplace=True)
    for name in df["name"]:
        # print(name)
        for i in range(len(hindu)):
            if hindu[i].lower() in name.lower():
                df.at[rowcount, "religion"] = "hindu"
                df.at[rowcount, "key_identifier"] = str(hindu[i])
                df.at[rowcount, "source"] = source
                break
        rowcount += 1

    # christian and father
    rowcount = 0
    for name in df["father"]:
        # print(name)
        for i in range(len(christian)):
            if christian[i].lower() in name.lower():
                df.at[rowcount, "religion"] = "christian"
                df.at[rowcount, "key_identifier"] = str(christian[i])
                df.at[rowcount, "source"] = source
                break
        rowcount += 1

    # christian and name
    rowcount = 0
    # df["name"].fillna("not found", inplace=True)
    for name in df["name"]:
        # print(name)
        for i in range(len(christian)):
            if christian[i].lower() in name.lower():
                df.at[rowcount, "religion"] = "christian"
                df.at[rowcount, "key_identifier"] = str(christian[i])
                df.at[rowcount, "source"] = source
                break
        rowcount += 1

    # muslim and father
    rowcount = 0
    # df["father"].fillna("not found", inplace=True)
    for name in df["father"]:
        # print(name)
        for i in range(len(muslim)):
            if muslim[i].lower() in name.lower():
                df.at[rowcount, "religion"] = "muslim"
                df.at[rowcount, "key_identifier"] = str(muslim[i])
                df.at[rowcount, "source"] = source
                break
        rowcount += 1

    # muslim and name
    rowcount = 0
    # df["name"].fillna("not found", inplace=True)
    for name in df["name"]:
        # print(name)
        for i in range(len(muslim)):
            if muslim[i].lower() in name.lower():
                df.at[rowcount, "religion"] = "muslim"
                df.at[rowcount, "key_identifier"] = str(muslim[i])
                df.at[rowcount, "source"] = source
                break
        rowcount += 1

    return df


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
                            # print("caste_list", caste_list[i])
                            # print("name", name)
                            if not name or pd.isnull(name):
                                if caste_list[i].lower() in name.lower():
                                    df.at[rowcount, "sub_caste"] = sheet
                                    break
                            rowcount += 1
    except:
        print('Error while reading caste file.')
        exit(0)

    return df


def move_completed_files(input_path, completed_path):
    listoffiles = []
    extDict = (".jpeg", ".jpg", ".png")

    shutil.rmtree(r'./input/pages')

    for root, dirs, files in os.walk(input_path):
        for filename in files:
            if filename.lower().endswith(".pdf"):
                # print(filename)
                listoffiles.append(filename)

            if len(listoffiles) >= 1:
                for i in range(len(listoffiles)):
                    try:
                        shutil.move(input_path + "//" + listoffiles[i],
                                    completed_path + "//" + os.path.basename(listoffiles[i]))
                    except:
                        try:
                            shutil.rmtree(input_path + "//" + listoffiles[i])
                        except:
                            if os.path.isfile(input_path + "//" + listoffiles[i]):
                                os.remove(input_path + "//" + listoffiles[i])