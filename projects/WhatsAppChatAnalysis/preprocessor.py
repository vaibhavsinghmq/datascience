#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 11:10:11 2023

@author: vaibhavsingh
"""

import re
import pandas as pd
import streamlit as st

def check_line(line):
    pattern = r'^\s*\[\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}:\d{2}\]' #pattern
    return re.match(pattern, line) is not None

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

    
            ## Part-2
        
        merged_lines = []
        current_line = ""
        
        # Process the content from content_without_u200e
        for line in content_without_u200e.split('\n'):
            line = line.strip()
        
            if check_line(line):
                if current_line:
                    merged_lines.append(current_line)
                current_line = line
            else:
                current_line += " " + line
        
        if current_line:
            merged_lines.append(current_line)
        
        # Store the merged lines
        merged_content = '\n'.join(merged_lines)
 
        
        ## Part 3
        # Extract data from the lines using regular expressions
        pattern1 = r'\[(.*?)\] (.*?): (.*?)\n'
        pattern2 = r'^(.*?) - (.*?): (.*)$'
        
        # Extract components from input1
        matches = re.findall(pattern1, merged_content)
        
        chat_timestamps, users, messages = [],[],[]
        
        if matches:
            st.text("In IF loop")
            chat_timestamps, users, messages = extract_data(matches)
            
            
        else:
            st.text("In else loop")
            matches = re.findall(pattern2, merged_content)
            st.text(pattern2)
            st.text(matches)
            if matches:
                chat_timestamps, users, messages = extract_data(matches)
            
        

        
        # Create a Pandas DataFrame
        columns = ['chat_timestamp', 'user', 'message']
        df = pd.DataFrame(list(zip(chat_timestamps, users, messages)), columns=columns)
        
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
