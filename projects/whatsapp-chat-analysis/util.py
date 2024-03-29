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
    words = [word for message in df['message'] for word in message.split()]

    # fetch number of media messages
    num_media_messages = df['message'].str.contains(" omitted").sum()

    # fetch number of links shared
    links = [link for message in df['message'] for link in extract.find_urls(message)]

    return num_messages, len(words), num_media_messages, len(links)

def sentiment_helper(df):
    # Initialize the SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    
    # Calculate sentiment scores for each message
    df['sentiment_score'] = df['message'].apply(lambda x: sia.polarity_scores(x)['compound'])
    
    # Group data by month and calculate average sentiment score
    monthly_sentiment = df.groupby(['month_num'])['sentiment_score'].mean()
    
    return monthly_sentiment

def keyword_analysis(df):
    df_temp = df[~df['message'].str.contains('omitted', case=False)]

    # Set up WordCloud parameters
    wc = WordCloud(width=800, height=450, min_font_size=10, background_color='white')
    cloud = wc.generate(df_temp['message'].str.cat(sep=" "))

    return cloud

def network_analysis(df_plot):
    # Extract usernames from messages
    df_plot['user'] = df_plot['user'].str.split().str[0]
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Iterate through DataFrame to add edges (interactions) between users
    for _, row in df_plot.iterrows():
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
    monthly_counts = df.groupby(['year', 'month_num'])['message'].count()
    # Fill gaps with zero values and reindex
    monthly_counts = monthly_counts.reindex(pd.MultiIndex.from_product([df['year'].unique(), range(1, 13)], names=['year', 'month_num']), fill_value=0)
    return monthly_counts

def emoji_helper(df):
    emojis = [c for message in df['message'] for c in message if c in emoji.EMOJI_DATA]
    return pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis)))).rename(columns={0: 'emoji', 1: 'count'})
