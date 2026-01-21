# File Input/Output and Exception Handling
# Problem Statement:

# Write a Python program that reads a text file and counts the number of lines in the file. Display the total number of lines as the output.
# Create a Python script that prompts the user to enter their name and saves it to a text file. Handle any file-related exceptions that may occur during the process.
# Implement a Python program that reads a CSV file containing student records. Each line in the file represents a student's name and their corresponding scores in multiple subjects. Calculate the average score for each student and display the results.(Do not use any third party library)

# Solution:
# Program to count the number of lines in a text file

def count_lines(filename):
    try:
        with open(filename,"r") as file:
            lines = file.readlines()
            return len(lines)
    except FileNotFoundError:
        print("File not found. Please check the file name.")
        return None
    except Exception as e:
        print("An error occured" , e)
        return None    
     
result = count_lines("sample.txt")
print("Total number of lines : " , result)

# Program to prompt user for name and save it to a text file

def save_name_to_file():
    try:
        name = input("Enter your name : ")
        with open("username.txt" , "w") as file:
            file.write(name)
        print()





