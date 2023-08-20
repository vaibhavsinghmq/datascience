#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 11:54:38 2023

@author: vaibhavsingh
"""


import streamlit as st
import preprocessor


def get_plot_user_engagement(data):
    # Generate a bar plot
    x = df['user'].value_counts()
    user_names = x.index
    msg_count = x.values
    
    plt.bar(user_names, msg_count)
    plt.xticks(rotation='vertical')
    plt.xlabel("User")
    plt.ylabel("Message Count")
    plt.title("Top Users by Message Count")
    plt.yticks(range(0, max(msg_count) + 1, 500))  # Set y-axis ticks in intervals of 100
    plt.show()
    
    