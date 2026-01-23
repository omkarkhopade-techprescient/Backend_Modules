# Working with Logging Module
# Problem Statement:

# Research and study the logging module in Python. Understand its purpose, features, and usage.
# code.py contains Python program that performs a specific task,Implement logging statements at different points in the program to record important information, such as variable values, function calls, or error messagess.
# Configure the logging module to output the log messages to both the console and a log file for the program in code.py file.
# Experiment with different log levels (e.g., debug, info, warning, error) and formatting options.
# Test your program and observe the log messages generated. Analyze the log file and identify any potential issues or areas for improvement in your program.
# Write a short report summarizing your findings. Include the log messages generated, any insights gained from analyzing the logs, and recommendations for using the logging module effectively.

############################################################################################################################################################

# Logging Module in Python :

# The logging module is used to record events while a program is running.
# Instead of using print(), logging gives you:

# Different severity levels

# Output to console + file

# Timestamped messages

# Easy debugging and error tracking

# Log Levels (most used):

# DEBUG    → Detailed info for debugging
# INFO     → General program flow
# WARNING  → Something unexpected, but program continues
# ERROR    → Serious problem, program failed
# CRITICAL → Program cannot continue

import logging

# Create logger manually (better than basicConfig for reliability)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# File Handler
file_handler = logging.FileHandler("code2.log", mode="a")
file_handler.setLevel(logging.DEBUG)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers only once
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def divide_numbers(a, b):
    logging.debug(f"divide_numbers() called with a={a}, b={b}")
    try:
        logging.info(f"Performing division: {a} / {b}")
        result = a / b
        logging.debug(f"Division result: {result}")
        return result

    except ZeroDivisionError:
        logging.exception("Cannot divide by zero")
        raise

    except Exception:
        logging.exception("Unexpected error in divide_numbers()")
        raise


def perform_task(a, b):
    logging.info("Task started")
    try:
        logging.debug(f"Input values: a={a}, b={b}")
        result = divide_numbers(a, b)
        logging.info(f"Task completed successfully. Result = {result}")

    except Exception:
        logging.warning("Task failed due to an error")


# Example usage
perform_task(10, 5)
perform_task(10, 0)


logging.shutdown()


# Initially, the log file was created but remained empty because the logging handlers were not properly flushing the output or were being overridden. By explicitly configuring file and console handlers and calling logging.shutdown(), the logs were reliably written to the file. This demonstrated the importance of proper handler configuration when working with Python’s logging module.