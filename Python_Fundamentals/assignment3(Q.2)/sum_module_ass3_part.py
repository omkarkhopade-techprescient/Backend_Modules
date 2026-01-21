# Write a Python program that imports a custom module. The module should contain a function that takes a list of numbers as input and returns the sum of all the numbers in the list. Use this function to calculate and display the sum of a given list of numbers.

def sum_of_list(num_list):
    total = 0
    for num in num_list:
        total += num
    return total
# Example usage
numbers = [10, 20, 30, 40, 50]
print("Sum of the list:", sum_of_list(numbers))