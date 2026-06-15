"""Sample file with intentional bugs/style issues for demo review."""

import os


def divide(a, b):
    return a / b  # no zero-check


def calculate_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    return total / len(numbers)  # crashes on empty list


def load_config(path):
    f = open(path)
    data = f.read()
    return data  # file handle never closed


API_KEY = "sk-test-123456789"  # hardcoded secret


def run_command(user_input):
    os.system("echo " + user_input)  # command injection risk


class calculator:
    def __init__(self):
        self.history=[]
    def add(self,a,b):
        result=a+b
        self.history.append(result)
        return result
