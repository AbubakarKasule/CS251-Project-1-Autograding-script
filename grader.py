# Author: Abubakar Kasule
# Date: Sep 2021
# Description: Automatic grader for CS251 Project 1
"""
Requirments: 
1. All modules listed below & Python 3+
2. The desired java jdk to be in the same working directory in a folder name 'jdk'. 
3. Some submissions make use of responses.csv. It must be included in a folder called 'documents', in a folder called 'src', and in the working directory.
4. The folder containing all the submissions, 'assignment_1454331_export', must be in the working directory. This folder can be download from Gradescope
"""

from glob import glob 
import os
import bios
import subprocess


# Load submission_metadata.yml as a python dictionary
submissions = bios.read('assignment_1454331_export/submission_metadata.yml')[1]

# Answer response pairs sored in a 2D array // Ended up not using this
answer_response_pairs = [['Human', 'Computer'], ['Hello.', 'Hello how are you?'], ['Hey!', "What's sup?"], ['Howdy.', 'Howdy partner.'], ['How are you?', 'I am well how are you?'], ['How are you feeling?', 'I am a computer I do not have feelings...'], ['What time is it?', "It's miller time!"], ['Tell me a joke.', 'When life gives you melons you might be dyslexic.'], ['What kind of car do you drive?', 'KITT.'], ['What is your favorite type of pizza?', 'Sausage.'], ['What is your favorite food?', 'Chips.'], ['What is your favorite type of flower?', 'Tulip.'], ['What is your favorite type of tree?', 'Binary.'], ['Who is your favorite singer?', 'A Dell!'], ['What is your favorite type of music?', 'Disc-o!'], ['Why are you so good at PowerPoint?', 'Because I Excel at it!'], ['What is the best way to learn about computers?', 'Bit by bit!'], ['How many programmers does it take to change a light bulb?', "That's a hardware problem call IT!"], ['What is a hackers favorite sport?', 'Phishing!']]

# Test Input for program
test_input = "Hello.\nHey!\nHowdy.\nHow are you?\nHow are you feeling?\nWhat time is it?\nTell me a joke.\nWhat kind of car do you drive?\nWhat is your favorite type of pizza?\nWhat is your favorite food?\nWhat is your favorite type of flower?\nWhat is your favorite type of tree?\nWho is your favorite singer?\nWhat is your favorite type of music?\nWhy are you so good at PowerPoint?\nWhat is the best way to learn about computers?\nHow many programmers does it take to change a light bulb?\nWhat is a hackers favorite sport?\nsecond nonsense command\nWhat is a hackers favorite sport?\nEXIT"

# Expected output for program
expected_output = "Hello how are you?\nWhat's sup?\nHowdy partner.\nI am well how are you?\nI am a computer I do not have feelings...\nIt's miller time!\nWhen life gives you melons you might be dyslexic.\nKITT.\nSausage.\nChips.\nTulip.\nBinary.\nA Dell!\nDisc-o!\nBecause I Excel at it!\nBit by bit!\nThat's a hardware problem call IT!\nPhishing!\nI do not recognize that, please try again.\nPhishing!\n"
expected_output_as_list = list(expected_output.split("\n")[:-1]) # Get rid of pesky extra ""

# number of submissions
submissions_processed = 1

# Track files in need of manual grading
flagged_submisions = dict()

# print(submissions['submission_86175589'])

def grade_student(submission_id, grades_file):
    global submissions_processed
    # Write Student's name to file
    grades_file.write(str(submissions_processed) + ".\n\n\n" + "Student Name: " + submissions[submission_id][':submitters'][0][':name'] + "\n\n")

    # Find student's java file
    java_files = glob('assignment_1454331_export/' + submission_id + '/**/'+'*.java', recursive=True)

    # Track exceptions
    exceptions = 0

    # Because more than one java file might be found, run all of them
    for file in java_files:
        grades_file.write("\tFile: " + file + "\n")
        try:
            # Linked Compile and run via Java's "Launch Single-File Source-Code Programs" feature to avoid java package issues
            out = subprocess.run(['jdk\\bin\\java.exe', file], text=True, input=test_input, capture_output=True)

            # If program failed for some Reason
            if out.returncode != 0:
                # Write report into file with file name and out.stderr
                grades_file.write("\t\t" + "Program exited with exit code " + str(out.returncode) + "\n\t\tStderr: " + out.stderr + "\n")
            # else:
            try:
                # Compare student output with expected output        
                student_output = out.stdout.split("\n")

                # Get rid of pesky extra space
                if student_output[-1] == "":
                    student_output = student_output[:-1]

                # if submissions_processed == 10:
                #     print(student_output)

                # Some studens started their program with a greeting. Get rid of it
                if len(student_output) > len(expected_output_as_list):
                    student_output = list(student_output[1:])

                # Some students added a greeting after EACH prompt. get rid of it
                if student_output[0] == student_output[2] or student_output[1]==student_output[3]:
                    newList = [] # store cleaned list
                    start_cleaning_from = 0 # Sometimes it is the 2nd instead of the 1st
                    
                    # Check if it starts from 2nd
                    if student_output[1]==student_output[3]:
                        start_cleaning_from = 1

                    # Clean input
                    for j in range(start_cleaning_from, len(student_output), 2):
                        newList.append(student_output[j])
                    
                    student_output = newList
                

                # Variable to store total errors
                errors = 0

                # Check if One or more of the output's were incorrect, Find which ones and write the errors to the file
                for i in range(len(expected_output_as_list)):
                    if student_output[i] != expected_output_as_list[i]:
                        # Increment error counter
                        errors +=1

                        # Write error to file
                        grades_file.write("\t\t" + "Your output: " + student_output[i] + ", Expected output: " + expected_output_as_list[i] + "(-1)\n")

                # See if everything matches
                if errors == 0:
                    # write "All Correct!" to file
                    grades_file.write("\t\t" + "All Correct!" + "\n")
                else:
                    grades_file.write("\t\t" + "Total Points lost: (-" + str(errors) + ")\n")
            except Exception as e:
                grades_file.write("\t\t" + "(Student " + str(submissions_processed) + ") Program had a runtime error after  " + str(len(student_output)) + " inputs.  |  " + str(e) + "\n")
                
                # ADD THIS EXCEPTION TO THE TOTAL
                exceptions += 1

        except Exception as e:
            # major error such as compilation fail. Write to file
            grades_file.write("\t\t"+ "(Student " + str(submissions_processed)  + ") Program failed to compile" + str(e) + "\n")

            # ADD THIS EXCEPTION TO THE TOTAL
            exceptions += 1

        # Spacer between files
        grades_file.write("**************EOF**************\n")

    # If all files threww exceptions, flag submission
    if exceptions == len(java_files):
        flagged_submisions[submissions[submission_id][':submitters'][0][':name']] = submissions_processed

    # Spacer between student submissions
    grades_file.write("________________________________________________________________________________\n")
    
    print("Submission " + str(submissions_processed) + " graded")
    submissions_processed += 1

# Create file to write grades into
file = open("grades.txt", "w")

# Loop through submissions and grade them
for student in submissions.keys():

    grade_student(student, file) 

# grade_student('submission_87327230', file)

# Write flagged submissions in need of manual grading into file
file.write("\n\n\n________________________________________________________________________________\n")
file.write("______________________________Flagged submissions_______________________________\n")
file.write("________________________________________________________________________________\n\n\n")

num = 0

for key in flagged_submisions:
   file.write(key + ": ")
   file.write("Submission Number " + str(flagged_submisions[key]) + "\n\n")
   num += 1

file.write("Total flagged submissions: " + str(num))

# Close file
file.close()
