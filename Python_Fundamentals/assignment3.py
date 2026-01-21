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

