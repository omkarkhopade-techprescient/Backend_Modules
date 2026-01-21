# Python Installation and Setup

# Problem Statement:

# Install Python on your local machine.
# Set up your Python development environment with a code editor or integrated development environment (IDE) of your choice.
# Verify the installation by running a simple "Hello, World!" program.
# Create a Python script that prompts the user for their name and greets them with a personalized message.
# Execute the script and ensure it runs without errors.

# Solution:
print("Hello, World!")

name = input("What is your name? :  ")
print(f"Hello, {name}!")


############################################################################################################


# Python Basics and Control Flow

# Problem Statement:

# Write a Python program that calculates and displays the area of a rectangle. Prompt the user to enter the length and width of the rectangle, and calculate the area using appropriate variables and operators.
# Create a Python script that determines whether a given number is even or odd. Prompt the user to enter a number, use control flow (if statements), and display an appropriate message indicating whether the number is even or odd.
# Write a Python program that generates and prints a Fibonacci sequence. Prompt the user to enter the number of terms they want in the sequence and use loops to generate the sequence accordingly.

# Solution:

# Area of a Rectangle
length = float(input("Enter the length of the rectangle : "))
width = float(input("Enter the width of the rectangle :  "))
area = length * width 
print(f'area of rectangle is :',area)

# Even or Odd
num = int(input("Enter the Number : "))
if(num%2==0):
    print(num," is even number")
else:
    print(num," is odd number")

#Fibonacci Sequence 
nterms = int(input("How many terms? "))
n1, n2 = 0, 1
count = 0
if(nterms<=0):
    print("Enter a positive integer")
elif(nterms==1):
    print("Fibonacci sequence upto",nterms,":")
    print(n1)
else:
    print("Fibonacci sequence:")
    while(count<=nterms):
        print(n1)
        nth = n1 + n2
        n1 = n2
        n2 = nth
        count += 1
#####################################################################################################


# Functions, Modules, and Data Structures

# Problem Statement:

# Create a Python function that accepts a string as an argument and counts the number of vowels (a, e, i, o, u) in the string. Return the count as the output of the function.
# Write a Python program that imports a custom module. The module should contain a function that takes a list of numbers as input and returns the sum of all the numbers in the list. Use this function to calculate and display the sum of a given list of numbers.
# Implement a Python program that accepts a sentence as input and converts it into a list of words. Use the split() function and store the words in a list. Then, iterate over the list and display each word in uppercase.

# Solution:
# Function to count vowels in a string
def count_vowels(str):
    vowels = "aeiouAEIOU"
    count = 0
    for char in str:
        if char in vowels:
            count += 1
    return count

text = input("Enter the Characters : ")
print("Number of vowels : ", count_vowels(text))


# Program to convert a sentence into a list of words and display each word in uppercase

sentence = input("Enter a sentence : ")
words =sentence.split()
for i in words:
    print(i.upper())

##################################################################################################################

# Write a Python program that imports a custom module. The module should contain a function that takes a list of numbers as input and returns the sum of all the numbers in the list. Use this function to calculate and display the sum of a given list of numbers.

def sum_of_list(num_list):
    total = 0
    for num in num_list:
        total += num
    return total
# Example usage
numbers = [10, 20, 30, 40, 50]
print("Sum of the list:", sum_of_list(numbers))

##############    ##############################   #############################  ##############

# Write a Python program that imports a custom module. The module should contain a function that takes a list of numbers as input and returns the sum of all the numbers in the list. Use this function to calculate and display the sum of a given list of numbers.
from sum_module_ass3_part import sum_of_list
numbers = [10,20,30,40,50]
print("Sum of the list:", sum_of_list(numbers))

########################################################################################################

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





