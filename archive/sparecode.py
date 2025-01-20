    # # Print and create txt file (BASIC TEXT)[REDACTED] #
    # lst = []
    # for name in file_names:
    #     name = name.split("_")[1]
    #     lst.append(name)
    # def create_pretty_table():
    #     x = PrettyTable()
    #     x.field_names = lst
    #     return x
    # file_name = "comparison_tables\WEEK_" + str(wk_num) + "_TABLE.txt"
    # f = open(file_name,"w")
    # f.write("*-----------------------------------------------------------*\n")
    # f.write("            TEACHING WEEK " + str(wk_num) + " -> " + DATES[wk_num] + "\n")
    # f.write("*-----------------------------------------------------------*\n\n")
    # for i in range(len(WEEK)):
    #     x = create_pretty_table()
    #     transposed_data = list(map(list, zip(*WEEK[i])))
    #     if len(errorList) != 0:
    #         transposed_data = [row[:-len(errorList)] for row in transposed_data]
    #     x.add_rows(transposed_data)
    #     fieldname = 'Period'
    #     x._field_names.insert(0, fieldname) 
    #     x._align[fieldname] = 'c' 
    #     x._valign[fieldname] = 't' 
    #     for n, _ in enumerate(x._rows): 
    #         x._rows[n].insert(0, PERIODS[n]) 
    #     f.write(DAYS[i]+"\n")
    #     f.write(x.get_string() + '\n\n')
    # f.close()
    # print("\n\n !!! SUCCESS !!! \n\n")
    # print("Txt file created... -> WEEK_" + str(wk_num) + "_TABLE.txt\n")
    # return file_name











### REFERENCES ###
# Course No 1
# Title 2
# AU 3
# CourseType 4
# S/U Grade option 5
# GERType 6
# IndexNumber 7
# Status 8
# Choice 9
# ClassType 10
# Group 11
# Day 12
# Time 13
# Venue 14
# Remark 15
# Exam 16



    ### REFERENCE CODE ###
    # Create an event #
    #event = Event()
    # Assign timestampe and UID #
    #timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    #random_id = str(uuid.uuid4())
    #uid = f'{timestamp}-{random_id}'
    #event.add('uid', uid)
    #event.add('dtstamp', datetime.now())
    #event.add('summary', 'Event 1')
    #event.add('location', 'Event 1')
    #event.add('description', 'Event 1')
    #event.add('dtstart', datetime(2023, 8, 15, 10, 0, 0))
    #event.add('dtend', datetime(2023, 8, 15, 12, 0, 0))
    #event.add('categories', ['Work'])
    #cal.add_component(event)

    ### REFERENCES ###
    # Course No 1
    # Title 2
    # AU 3
    # CourseType 4
    # S/U Grade option 5
    # GERType 6
    # IndexNumber 7
    # Status 8
    # Choice 9
    # ClassType 10
    # Group 11
    # Day 12
    # Time 13
    # Venue 14
    # Wk 15
    # Exam 16

    # Summary -> Course Code + Course Name
    # Location -> Location
    # Description -> Class Type, Group, Remarks, Exam, AUs
    # DTSTART -> Date + StartTime
    # DTEND -> Date + EndTime
    # Category -> Course Code