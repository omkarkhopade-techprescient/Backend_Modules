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
