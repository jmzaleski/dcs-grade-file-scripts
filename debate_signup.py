
def debate_signup(debate_signup_file_name, empty_fn):

    from grade_file_reader_writer import GradeFileReaderWriter
    empty = GradeFileReaderWriter(empty_fn)
    empty.read_file()

    utorid_to_student_map = {}
    for s in empty.students:
        utorid_to_student_map[s.utorid] = s

    #print(len(sorted(utorid_to_student_map.keys())))

    bad_utorids = []
    unpaired_utorids = []
    cross_section_pairs = []
    pairs = [] # list of pairs
    utorid_map = {}

    with open(debate_signup_file_name, 'r') as csv_file:
        import csv
        csv_file_reader = csv.reader(csv_file, delimiter=',')
        for student_record in csv_file_reader:
            if len(student_record[0]) == 0:
                continue #print("reject line because first field is empty",student_record)
            try:
                #sample line from debate signup file
                #$0,$1    ,$2,            ,$3,     ,$4,            $5
                # 1,crypto,Nicolette Alli,allinico,David Ansermino,ansermin
                (topic, utorid1, utorid2) = (student_record[1].lower().strip(),student_record[3].lower().strip(),student_record[5].lower().strip())
                #print(topic, utorid1, utorid2)
            except:
                print("oops", student_record)

            if len(utorid1)==0:
                continue #skip line because no utorid
            try:
                if not utorid1 in utorid_to_student_map:
                    #print(utorid1,'not in classlist')
                    bad_utorids.append(utorid1)
                    #exit(1)
                    continue

                if not utorid2:
                    #print("oops: no pair in", student_record)
                    unpaired_utorids.append(utorid1)
                    continue

                if not utorid2 in utorid_to_student_map:
                    #print(utorid2,'not in classlist')
                    bad_utorids.append(utorid2)
                    #exit(1)
                    continue

                s1 = utorid_to_student_map[utorid1]
                section1 = s1.sec

                s2 = utorid_to_student_map[utorid2]
                section2 = s2.sec
                if section1 != section2:
                    #print("not from same section", utorid1, utorid2, section1, section2)
                    cross_section_pairs.append((utorid1,utorid2))

                if utorid1 in utorid_map:
                    print("oh no, utorid appears in multiple pairs!", utorid1)
                    exit(2)
                if utorid2 in utorid_map:
                    print("oh no, utorid appears in multiple pairs!", utorid2)
                    exit(2)
                utorid_map[utorid1] = utorid1
                utorid_map[utorid2] = utorid2
                pairs.append((utorid1,utorid2))

                print("%s,%s,%s,%s,%s" % (topic,utorid1,section1,utorid2,section2))
            except:
                print("oops", student_record, s1, section1 )
                exit(0)

    ix = 0
    for (u1,u2) in pairs:
        #print(ix,u1,u2)
        ix += 1

    for utorid in utorid_to_student_map.keys():
        if not utorid in utorid_map:
            print("missing from any pair:", utorid)

    if bad_utorids:
        print("bad utorids:", bad_utorids)
    if unpaired_utorids:
        print("solo students", unpaired_utorids)
    if cross_section_pairs:
        print("cross_section_pairs",cross_section_pairs)
        emails = ""
        for (u1,u2) in cross_section_pairs:
            #print(u1,u2)
            print(utorid_to_student_map[u1].email)
            print(utorid_to_student_map[u2].email)
            emails += utorid_to_student_map[u1].email + ","
            emails += utorid_to_student_map[u2].email + ","
        print(emails)


if __name__ == '__main__':
    from grade_file_reader_writer import GradeFileReaderWriter
    from debate_signup import debate_signup
    debate_signup("/Users/mzaleski/Downloads/CSC300H1F_2016_Debate_SignUp - matz- signup.csv", "CSC300H1F-empty")

