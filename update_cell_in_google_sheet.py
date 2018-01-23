def update_sheet_data(query, column_name, datum, workbook_url):
    "use query to find a row, then update cell at column with datum"
    import gspread
    import re
    from oauth2client.service_account import ServiceAccountCredentials

    # see https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
    # see: https://github.com/burnash/gspread

    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']

    # follow the instructions in the blog above carefully to get this.
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/mzaleski/DCSFetchMarks-3cf40810a20f.json', scope)

    client = gspread.authorize(creds)
    # Find the workbook by name and open the first sheet
    try:
        work_book = client.open_by_url(workbook_url)
    except:
        print("failed to open google sheet at", workbook_url)
        return False

    # cheesy, but pretend the table is the first sheet in the workbook
    # hell, while at it assume first column is student #, name field as in clarke file
    # and there exists utorid column.
    
    work_sheet = work_book.sheet1
    utorid_dict = {}
    dest_column_number = -1
    
    try:
        col_names = work_sheet.row_values(1)
        print(col_names)
        if "utorid" in col_names:
            utorid_column_number = col_names.index("utorid") + 1
            utorid_column = work_sheet.col_values(utorid_column_number)
            first_column = work_sheet.col_values(1)
            for id,line in zip(utorid_column[2:],first_column[2:]):
                if len(id) > 0:
                    utorid_dict[id] = line
            print(utorid_dict)
        else:
            print("cannot find utorid column in first row of worksheet", col_names)
            return False
        
        if column_name in col_names:
            #watchit.. python array zero origin, worksheet column's one origin..
            dest_column_number = col_names.index(column_name) + 1 
        else:
            print("cannot find", column_name, "in first row of worksheet", col_names)
            return False
            
        print("found", column_name, "at dest_column_number", dest_column_number, "will update mark in that column")
    except:
        print("failed to find column_name", column_name, "in first row of sheet")
        return False

    from prompt_for_input_string_with_completions_curses import prompt_for_input_string_with_completions_curses

    while True:
        #prompt user for which student record to enter a mark for
        query_string = prompt_for_input_string_with_completions_curses(
            "student id (completion on utorid, EOF to finish): ",
            20,
            utorid_dict)
    
        print(query_string)
        if query_string == None:
            return None
        elif len(query_string) == 0:
            continue  # try query again..

        #find the line in the sheet corresponding to query_string
        try:
            query_re = re.compile(query_string)
            # find all the cells that match.. make sure only one before writing anything!
            cell_list = work_sheet.findall(query_re)
            if len(cell_list) == 1:
                cell = cell_list[0]
            else:
                print("multiple rows, skip somehow")
                continue

            row_number = cell.row
            column_number = cell.col
            print("row", row_number,"col",column_number)
        except:
            print(query, "not found (anyway, gspread.find throws)")
            return False

        # finally, write the data into the sheet
        try:
            print("about to write", datum, " to row", row_number,"col",dest_column_number)
            work_sheet.update_cell(row_number, dest_column_number, datum)
        except:
            print("failed to write", datum, " to row", row_number,"col",dest_column_number)
            return False
            
    return True

    # except:
    #     import traceback,sys
    #     print("failed to open sheet", workbook_url)
    #     traceback.print_exc(file=sys.stdout)
    #     exit(2)
        

def test():
    # example usage:
    update_sheet_data("ander510", "Jan11", 222, "https://docs.google.com/spreadsheets/d/19Gq_oL6WgelKszYJxhZf0YBuw1fgStt5wuoHuqbYWPs/edit#gid=1371474907")
    exit(0)        

    
if __name__ == '__main__':
    #test()
    def parse_positional_args():
        "parse the command line parameters of this program"
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("google_sheet_url", help="URL of google sheet. eg: https://docs.google.com/spreadsheets/stuff")
        parser.add_argument("query", help="string to search for to find row to modify")
        parser.add_argument("column_name", help="name of sheet column to add mark to")
        parser.add_argument("datum", help="value to write into cell identified above")
        args = parser.parse_args()
        return args

    args = parse_positional_args()

    update_sheet_data(query=args.query,
                          column_name=args.column_name,
                          datum=args.datum,
                          workbook_url=args.google_sheet_url)

