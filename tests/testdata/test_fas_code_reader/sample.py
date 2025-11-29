import os
import sys
import json
import pandas as pd
import requests  # Popular external library 

def helper():
    rows = [1,2,3,4,5]
    columns = [1,2,3,4,5]
    other = [1,2,3,4,5]

    for r in rows:
        for c in columns:
            for j in other:
                print(r,c,j)

class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        print("Woof")

count = 0

while count < 10:
    while count < 5:
        count += 1
    count +=2

