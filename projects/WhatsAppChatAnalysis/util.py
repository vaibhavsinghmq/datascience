#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 12:46:36 2023

@author: vaibhavsingh
"""

from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import networkx as nx
import streamlit as st
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer



extract = URLExtract()


def get_selected_dataframe(selected_year, selected_user, df):
    if selected_year != 'Overall':
        df = df[df['year'] == selected_year]    

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df

def fetch_stats(df):
        

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'].str.contains(" omitted")].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links)


def sentiment_helper(df):
    # Initialize the SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    
    df_plot = df.copy()
    
    # Calculate sentiment scores for each message
    df_plot['sentiment_score'] = df_plot['message'].apply(lambda x: sia.polarity_scores(x)['compound'])
    
    # Group data by month and calculate average sentiment score
    monthly_sentiment = df_plot.groupby(['month_num'])['sentiment_score'].mean()
    
    # Empty the DataFrame by dropping all rows
    df_plot = df_plot.drop(df_plot.index)
    
    
    return monthly_sentiment


def keyword_analysis(df):
    
    df_temp =df.copy()
    df_temp = df_temp[~df_temp['message'].str.contains('omitted', case=False)]

    # Set up WordCloud parameters
    wc = WordCloud(
        width=1000, height=800, min_font_size=10, background_color='white'
    )
    
    cloud = wc.generate(df_temp['message'].str.cat(sep=" "))

    # Empty the DataFrame by dropping all rows
    df_temp = df_temp.drop(df_temp.index)

    return cloud


def network_analysis(df_plot):
    # Extract usernames from messages
    df_plot['user'] = df_plot['user'].str.split().str[0]
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Iterate through DataFrame to add edges (interactions) between users
    for index, row in df_plot.iterrows():
        sender = row['user']
        message = row['message']
        mentions = [word for word in message.split() if word.startswith('@')]
    
        if mentions:
            for mention in mentions:
                mentioned_user = mention[1:]  # Remove '@' symbol
                G.add_edge(sender, mentioned_user)
    
    return G


def hourly_activity(df):
    return df.groupby(['hour'])['message'].count()

def weekly_activity(df):
    return df.groupby(['day_of_week'])['message'].count()

def monthly_activity(df):
    monthly_counts = df.groupby(['month_num'])['message'].count()
    # Fill gaps with zero values and reindex
    monthly_counts = monthly_counts.reindex(range(1, 13), fill_value=0)
    return monthly_counts

def emoji_helper(df):
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    return pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis)))).rename(
        columns={0: 'emoji', 1: 'count'})
