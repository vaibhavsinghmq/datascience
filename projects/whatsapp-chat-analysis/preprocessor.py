#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 11:10:11 2023

@author: vaibhavsingh
"""

import re,os
import pandas as pd
import streamlit as st
from datetime import datetime


chat_pattern=r'\[(.*?)\] (.*?): (.*?)$'

## ANdroid code
def identify_and_convert_date(date_string):
    formats_to_try = [
      '%d/%m/%Y, %I:%M %p',
      '%d/%m/%y, %I:%M %p',
      '%m/%d/%y, %I:%M %p',
      '%m/%d/%Y, %I:%M%p',
      '%Y/%m/%d, %I:%M %p',
      '%Y/%m/%d, %H:%M',
      '%m/%d/%Y, %H:%M',
      '%d/%m/%Y, %H:%M',
      '%Y/%d/%m, %I:%M%p',
      '%Y/%d/%m, %H:%M'
    ]

    for date_format in formats_to_try:
        try:
            dt = datetime.strptime(date_string[:date_string.index('-')].strip(), date_format)
            rest_of_line = date_string[date_string.index('-')+1:].strip()
            formatted_date_time = dt.strftime('[%d/%m/%Y, %H:%M:%S]')
            formatted_line = f"{formatted_date_time} - {rest_of_line}"
            return formatted_line
        except ValueError:
            pass
    
    return date_string


def make_common_date_format(attr_keys,lines):
  common_date_lines=[]
  for date_string in lines:
      converted_date = identify_and_convert_date(date_string)
      common_date_lines.append(converted_date)
  
  return common_date_lines

def filter_line(line):
    return "joined using this group's invite link" not in line and "changed to" not in line and "Messages and calls are end-to-end encrypted." not in line

def is_valid_line(line):
    return '-' in line.split(" - ")[1] if "changed to" in line else True

def convert_to_24_hour_format(match):
    return datetime.strptime(match.group(), '%m/%d/%y, %I:%M %p').strftime('[%d/%m/%Y, %H:%M:%S]')

def remove_non_compliant_lines(attr_keys,lines):
    check_non_compliant_pattern = r'\[(\d{1,2}\/\d{1,2}\/\d{4}, \d{2}:\d{2}:\d{2})\] (.*?): (.*)$'

    non_compliant_lines = []

    for line in lines:
        if not re.match(check_non_compliant_pattern, line):
            non_compliant_lines.append(line)

    total_lines = len(lines)
    non_compliant_count = len(non_compliant_lines)
    percentage_of_non_compliant_lines = (non_compliant_count / total_lines) * 100
    
    if percentage_of_non_compliant_lines < 10:
        
        lines = [line for line in lines if re.match(check_non_compliant_pattern, line)]
        
        return lines
    else:
        for line in non_compliant_lines:
            print(line.strip())  # Print the non-compliant lines without leading/trailing whitespace
        return []


def process_lines(attr_keys,lines):
    filtered_lines = [line for line in lines if filter_line(line) and is_valid_line(line)]
    pattern = r'\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}(?:\s*[APapMm]{2})'
    datetime_lines = [re.sub(pattern, convert_to_24_hour_format, line) for line in filtered_lines]

    merged_lines = []
    current_line = ''

    for index, line in enumerate(datetime_lines):
        if line.startswith('[') and current_line:
            merged_lines.append(current_line.strip())
            current_line = line.strip()
        else:
            current_line += ' ' + line.strip()

    if current_line:
        merged_lines.append(current_line.strip())

    output_lines = []
    for line in merged_lines:
        index = line.find(']')
        if index != -1:
            hyphen_index = line.find('- ', index)
            if hyphen_index != -1:
                line = line[:hyphen_index] + line[hyphen_index+2:]
        output_lines.append(line)
  
    return output_lines



def has_special_characters(line):
    for char in line:
        if ord(char) < 32 or ord(char) > 127:
            return True
    return False


def extract_data(matches):
    # Create lists for each column
    chat_timestamps = [match[0] for match in matches]
    users = [match[1] for match in matches]
    messages = [match[2] for match in matches]
    
    return chat_timestamps, users, messages


## Take a text file as in input and return a dataframe
def preprocess(data):
   try:
    
        content_without_u200e = data.replace('\u200E', '')

        attr_keys={}

        lines = content_without_u200e.split("\n")
        
        common_date_lines = make_common_date_format(attr_keys,lines)
        output_lines = process_lines(attr_keys,common_date_lines)
        output_lines = remove_non_compliant_lines(attr_keys,output_lines)
        
        datetime_list = []
        user_list = []
        message_list = []
        
        for entry in output_lines:
            match = re.match(chat_pattern, entry)
            if match:
                datetime_list.append(match.group(1))
                user_list.append(match.group(2))
                message_list.append(match.group(3))

        # Create a Pandas DataFrame
        df = pd.DataFrame({
            'chat_timestamp': datetime_list,
            'user': user_list,
            'message': message_list
        })
        
        # Convert 'chat_timestamp' to datetime
        df['chat_timestamp'] = pd.to_datetime(df['chat_timestamp'], dayfirst=True)
        
        # Extract various datetime components using the 'assign' function
        df = df.assign(
            only_date=df['chat_timestamp'].dt.date,
            year=df['chat_timestamp'].dt.year,
            month_num=df['chat_timestamp'].dt.month,
            month=df['chat_timestamp'].dt.month_name(),
            day=df['chat_timestamp'].dt.day,
            day_of_week=df['chat_timestamp'].dt.day_name(),
            hour=df['chat_timestamp'].dt.hour,
            minute=df['chat_timestamp'].dt.minute
        )

    
   except Exception as e:
        st.error("An error occurred:")
        st.error(str(e))
        print("Something went wrong",e)
        df = pd.DataFrame({})
        
    
   return df