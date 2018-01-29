def get_sheet_data(sheet_name):
    "get the data for the named sheet as CSV"
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    # see https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html

    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']

    # follow the instructions in the blog above carefully to get this.
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/mzaleski/DCSFetchMarks-3cf40810a20f.json', scope)

    client = gspread.authorize(creds)
    # Find the workbook by name and open the first sheet
    try:
        sheet = client.open(sheet_name).sheet1
        csv_file_data = sheet.export(format='csv')
        return csv_file_data
    except:
        import traceback,sys
        print("failed to open sheet", sheet_name)
        traceback.print_exc(file=sys.stdout)

def get_sheet_data_from_url(sheet_url):
    "get the data for the sheet URL as CSV"
    #TODO: copy code name version? maybe just toss the name version
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    # see https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html

    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']

    # follow the instructions in the blog above carefully to get this.
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/mzaleski/DCSFetchMarks-3cf40810a20f.json', scope)

    client = gspread.authorize(creds)
    # Find the workbook by URL and open the first sheet
    try:
        work_book = client.open_by_url(sheet_url)
        sheet = work_book.sheet1
        csv_file_data = sheet.export(format='csv')
        return csv_file_data
    except:
        import traceback,sys
        print("failed to open sheet", sheet_url)
        traceback.print_exc(file=sys.stdout)
        
def write_grade_file_from_csv_metadata_and_marks(csv_file_data,ofn):
    """smack around the csv data from the google sheet so it's a jim
    clarke grades file. This depends on the first two lines being
    metadata that describes each column of the rest of the lines (csv student marks)
    See http://www.cdf.toronto.edu/~clarke/grade/fileformat.shtml
    """
    import os.path
    if os.path.isfile(ofn):
        modifiedTime = os.path.getmtime(ofn) 
        #from datetime import date
        #timestamp = date.fromtimestamp(modifiedTime).strftime("%b-%d-%Y_%H.%M.%S")
        import datetime
        timestamp = datetime.datetime.fromtimestamp(modifiedTime).strftime("%b-%d-%Y_%H.%M.%S")
        back_ofn = "%s-%s" % (ofn,timestamp)
        print("back up %s to %s" % (ofn, back_ofn))
        os.rename(ofn, back_ofn)
        #os.rename(ofn, ofn + "_" + timestamp + ".txt")

    # The first two lines of the ta mark entry google sheet
    # tell us all we need to know to build up a jim clarke format grade file header for the marks.
    # the first (top) line names the grade saved in the corresponding column
    # the second line gives the type, where /N is a mark out of N, " is a string
    #
    csv_file_as_list = csv_file_data.decode().splitlines()
    mark_names = csv_file_as_list[0].split(',') #first line
    mark_types = csv_file_as_list[1].split(',') #second line

    # note first line is magic and makes the grades file comma separated

    hdr = """*/,
* this header created from google sheet by prepend_header_write_grade_file function
* weird line above changes the separator char to , (comma). 
* "Jim Clarke" style grades file 
* See http://www.cdf.toronto.edu/~clarke/grade/fileformat.shtml
* CSC300 fall.. Sept to Dec 2017
"""    
    for (mark_name,mark_type) in zip(mark_names[1:],mark_types[1:]):
        if mark_type.startswith('"'):
            hdr += "%s \"\n" % (mark_name)   #double quote says a marks is a string (old school, eh?)
        else:
            hdr += "%s %s\n" % (mark_name,mark_type)

    # the rest of the lines of the ta mark sheet are CSV student grades described by above
    with open(ofn,'w') as new_file:
        print(hdr, file=new_file)
        for line in csv_file_as_list[2:]:
            print(line,file=new_file)

def test():
    import sys,os
    ofn = "p_tu_test"
    d = get_sheet_data("tutorial-participation")
    #print(d.decode())export
    write_grade_file_from_csv_metadata_and_marks(d,ofn)
    os.system("ls -l %s" % ofn)
    exit(0)        

    
if __name__ == '__main__':
    #test()
    def parse_positional_args():
        "parse the command line parameters of this program"
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("google_sheet_doc_name", help="name of google sheet. eg: tutorial-participation")
        parser.add_argument("output_grade_file_name", help="name of jim clarke grade file to write eg: p_tu")
        args = parser.parse_args()
        return args

    args = parse_positional_args()
    write_grade_file_from_csv_metadata_and_marks(
        get_sheet_data(args.google_sheet_doc_name),
        args.output_grade_file_name)

