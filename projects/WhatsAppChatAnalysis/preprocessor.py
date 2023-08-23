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





pattern2=r'\[(.*?)\] (.*?): (.*?)$'

## ANdroid code
def identify_and_convert_date(date_string):
    possible_formats = [
        "%m/%d/%y, %I:%M %p",
        "%d/%m/%Y, %I:%M %p"
    ]

    for format_str in possible_formats:
        try:
            parsed_date = datetime.strptime(re.split(r' - |: ', date_string)[0], format_str)
            formatted_date = parsed_date.strftime('%-m/%-d/%y, %-I:%M %p')
            return date_string.replace(re.split(r' - |: ', date_string)[0], formatted_date, 1)
        except ValueError:
            pass
    
    return date_string

def make_common_date_format(attr_keys,lines):
  common_date_lines=[]
  for date_string in lines:

      converted_date = identify_and_convert_date(date_string)
      common_date_lines.append(converted_date)
  st.text(f"==STAGE 1== {attr_keys}::=> Original lines {len(lines)}, common date lines {len(common_date_lines)}")
  return common_date_lines


def filter_line(line):
    return "joined using this group's invite link" not in line and "changed to" not in line and "Messages and calls are end-to-end encrypted." not in line

def is_valid_line(line):
    return '-' in line.split(" - ")[1] if "changed to" in line else True

def convert_to_24_hour_format(match):
    return datetime.strptime(match.group(), '%m/%d/%y, %I:%M %p').strftime('[%d/%m/%Y, %H:%M:%S]')

def remove_non_compliant_lines(attr_keys,lines):
    check_non_compliant_pattern = r'\[(.*?)\] (.*?): (.*?)$'

    non_compliant_lines = []

    for line in lines:
        if not re.match(check_non_compliant_pattern, line):
            non_compliant_lines.append(line)

    total_lines = len(lines)
    non_compliant_count = len(non_compliant_lines)
    percentage_of_non_compliant_lines = (non_compliant_count / total_lines) * 100
    st.text(f"==STAGE 3== {attr_keys}::=> Total lines: {total_lines}, Non-compliant lines: {non_compliant_count},Percentage of non-compliant lines: {percentage_of_non_compliant_lines:.2f}%")

    if percentage_of_non_compliant_lines < 10:
        st.text("Removing non-compliant lines due to high percentage.")
        lines = [line for line in lines if re.match(check_non_compliant_pattern, line)]
        st.text(f"Return Compliant lines: {len(lines)}")
        return lines
    else:
        for line in non_compliant_lines:
            print(line.strip())  # Print the non-compliant lines without leading/trailing whitespace

        st.text(f"==STAGE 3-ERROR== {attr_keys}::=> Return Empty Array as Non-Compliant lines >10%:===> {len(non_compliant_lines)}")
        return []


def process_lines(attr_keys,lines):
    filtered_lines = [line for line in lines if filter_line(line) and is_valid_line(line)]
    st.text(f"==STAGE 2A== {attr_keys}::=> Original lines {len(lines)}, filtered_lines {len(filtered_lines)}")

    pattern = r'\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}(?:\s*[APapMm]{2})'
    datetime_lines = [re.sub(pattern, convert_to_24_hour_format, line) for line in filtered_lines]
    st.text(f"==STAGE 2B== {attr_keys}::=> Original lines {len(lines)}, datetime_lines {len(datetime_lines)}")

    merged_lines = []
    current_line = ''

    for line in datetime_lines:
        if line.startswith('[') and current_line:
            merged_lines.append(current_line.strip())
            current_line = line.strip()
        else:
            current_line += ' ' + line.strip()

    if current_line:
        merged_lines.append(current_line.strip())

    st.text(f"==STAGE 2C== {attr_keys}::=> Original lines {len(lines)}, merged_lines {len(merged_lines)}")

    output_lines = []

    for line in merged_lines:
        index = line.find(']')
        if index != -1:
            hyphen_index = line.find('- ', index)
            if hyphen_index != -1:
                line = line[:hyphen_index] + line[hyphen_index+2:]
        output_lines.append(line)
    
    ##st.text(f"==STAGE 2D== {attr_keys}::=> Original lines {len(lines)}, merged_lines {len(output_lines)}")

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

        attr_keys={"name:":"1sqdwe.txt","Size":1234,"Mode":5678}


        lines = data.split("\n")
        ##st.text(lines)
        
        common_date_lines = make_common_date_format(attr_keys,lines)
        output_lines = process_lines(attr_keys,common_date_lines)
        output_lines = remove_non_compliant_lines(attr_keys,output_lines)

        ##st.text(f"pattern2::{pattern2}")
        ##st.text(f"output_lines::{output_lines}")
        ##st.text(f"output_lines::{len(output_lines)}, type:==>{type(output_lines)}")

        
        datetime_list = []
        user_list = []
        message_list = []
        
        for entry in output_lines:
            match = re.match(pattern2, entry)
            if match:
                datetime_list.append(match.group(1))
                user_list.append(match.group(2))
                message_list.append(match.group(3))
        
        # Create a Pandas DataFrame
        columns = ['chat_timestamp', 'user', 'message']
        df = pd.DataFrame(list(zip(datetime_list, user_list, message_list)), columns=columns)
        
        # Convert 'chat_timestamp' to datetime
        df['chat_timestamp'] = pd.to_datetime(df['chat_timestamp'], dayfirst=True)
        
        df['only_date'] = df['chat_timestamp'].dt.date
        df['year'] = df['chat_timestamp'].dt.year
        df['month_num'] = df['chat_timestamp'].dt.month
        df['month'] = df['chat_timestamp'].dt.month_name()
        df['day'] = df['chat_timestamp'].dt.day
        df['day_of_week'] = df['chat_timestamp'].dt.day_name()
        df['hour'] = df['chat_timestamp'].dt.hour
        df['minute'] = df['chat_timestamp'].dt.minute
    
        
    
   except Exception as e:
        st.error("An error occurred:")
        st.error(str(e))
        print("Something went wrong",e)
        df = pd.DataFrame({})
        
    
   return df
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
