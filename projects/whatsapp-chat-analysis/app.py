#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 11:02:17 2023

@author: vaibhavsingh
"""

import streamlit as st
import preprocessor, util
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
from matplotlib.ticker import MultipleLocator



st.config.set_option("server.maxUploadSize", 10)


# Main Streamlit app code
def main():
    
    uploaded_file = st.sidebar.file_uploader("Choose a TXT file", accept_multiple_files=False)
    
        
    # Custom CSS for the header
    header_style = """
    <style>
        .fancy-header {
            background-color: #3498db;
            color: white;
            font-size: 36px;
            font-family: 'Arial', sans-serif;
            padding: 20px;
            text-align: center;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
    """
    
    # Display the custom CSS using st.markdown
    st.markdown(header_style, unsafe_allow_html=True)
    
    # Display the fancy header
    st.markdown('<div class="fancy-header">WhatsApp chat analysis</div>', unsafe_allow_html=True)
    
    
    if uploaded_file is not None:
        
       ## st.text(f"File Name: {uploaded_file.name}")
        ##st.text(f"File Size: {uploaded_file.size}")
        ##st.text(f"File Type: {uploaded_file.type}")
        
        
        bytes_data = uploaded_file.getvalue()
        
        data = bytes_data.decode("utf-8")
        
        wa_users_data_df = preprocessor.preprocess(data) # create columns from chat file
        ##st.text(wa_users_data_df)
        
        # Create a dropdown for year
        year_option = wa_users_data_df['year'].unique().tolist()
        year_option.sort()
        year_option.insert(0,"Overall")
        
        ## Create a dropdown for users
        user_option = wa_users_data_df['user'].unique().tolist()
        user_option.sort()
        user_option.insert(0,"Overall")

        selected_year = st.sidebar.selectbox("Select an year:", year_option) #selected year
        selected_user = st.sidebar.selectbox("Show analysis of ",user_option)  # Selected user
        
        if st.sidebar.button("Show Analysis"):
            
            custom_styles = """
            <style>
                .appview-container .block-container{
                    max-width: 100%;    
                }
                .g1{
                    background-color: #383edd;
                    border-color: #383edd;
                }
                .g2{
                    background-color: #3498f7;
                    border-color: #3498f7;
                }
                .g3{
                    background-color: #f6b243;
                    border-color: #f6b243;
                }
                .g4{
                    background-color: #e65353;
                    border-color: #e65353;
                }
                .custom-div {
                    padding: 10px;
                    border: 1px solid #ccc;
                    text-align: center;
                    margin: 5px;
                    text-color: #fff;
                }
                .custom-container {
                    display: flex;
                    justify-content: space-between;
                    margin: -5px; /* Compensate for margin added to divs */
                }
            </style>
            """
            
            # Display the custom styles using st.markdown
            st.markdown(custom_styles, unsafe_allow_html=True)
            

            # Select the dataframe
            wa_users_data_df = util.get_selected_dataframe(selected_year,selected_user,wa_users_data_df)
            
            
            # Check if the DataFrame is empty
            if not wa_users_data_df.empty:
                
                
                # Stats Area
                num_messages, words, num_media_messages, num_links = util.fetch_stats(wa_users_data_df)
    
                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                    
                    col1.markdown('<div class="custom-div g1"><div>Total Messages</div><div>{}</div></div>'.format(num_messages), unsafe_allow_html=True)
                    col2.markdown('<div class="custom-div g2"><div>Total Words</div><div>{}</div></div>'.format(words), unsafe_allow_html=True)
                    col3.markdown('<div class="custom-div g3"><div>Media Shared</div><div>{}</div></div>'.format(num_media_messages), unsafe_allow_html=True)
                    col4.markdown('<div class="custom-div g4"><div>Links Shared</div><div>{}</div></div>'.format(num_links), unsafe_allow_html=True)
    
                # Create vertical space between containers
                st.markdown("<br><br>", unsafe_allow_html=True)
    
                with st.container():
                    col1, col2 = st.columns(2)
                
    
                    with col1:
                        
                      
                        # Create a Pandas Series (replace this with your actual data)
                        hourly_counts = util.hourly_activity(wa_users_data_df)
                        
                        # Set the Seaborn style and context for a dark background
                        sns.set(style='darkgrid', context='notebook')
                        
                        # Create the Seaborn plot with a dark background using the Pandas Series
                        fig, ax = plt.subplots(figsize=(10, 6))
#                        sns.barplot(x=hourly_counts.index, y=hourly_counts.values, color='#42923b')  # Replace 'orange' with your desired color
                        sns.lineplot(x=hourly_counts.index, y=hourly_counts.values, color='#42923b')
                        
                        # Set the title and labels
                        plt.title('Message Frequency by Hour:')
                        ax.set_xlabel('Hours')
                        ax.set_ylabel('Message Count')
                        
                        # Display the plot using Streamlit
                        st.pyplot(fig)
                      
                        
                    with col2:
                        
                        # Create a Pandas Series (replace this with your actual data)
                        weekly_counts = util.weekly_activity(wa_users_data_df)
                        
                        # Define the order of days of the week
                        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        
                        # Set the Seaborn style and context for a dark background
                        sns.set(style='darkgrid', context='notebook')
                        
                        # Create the Seaborn plot with a dark background using the grouped data
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax = sns.barplot(x=weekly_counts.index, y=weekly_counts.values, order=day_order, color='#e892f3')
                        
                        # Set the title and labels
                        plt.title('Message Frequency by Day of the Week')
                        ax.set_xlabel('Day of the Week')
                        ax.set_ylabel('Message Count')
                        
                        # Annotate bars with values just above the bars
                        for i in ax.containers:
                            ax.bar_label(i,)



                        
                        # Display the plot using Streamlit
                        st.pyplot(fig)
                      
                
                with st.container():
                    col3, col4 = st.columns(2)
                    
                    
                    with col3:
    
                        # Assuming 'monthly_counts' is your data and 'month_labels' is defined
                        monthly_counts_by_year = util.monthly_activity(wa_users_data_df)
                        monthly_counts_by_year = monthly_counts_by_year.reset_index()
                        monthly_counts_by_year.columns = ["year", "month_num", "count"]


                        # Convert columns to proper types
                        monthly_counts_by_year["year"] = monthly_counts_by_year["year"].astype(str)
                        monthly_counts_by_year["month_num"] = monthly_counts_by_year["month_num"].astype(int)
                        monthly_counts_by_year["count"] = monthly_counts_by_year["count"].astype(int)
                        
                        #st.text(monthly_counts_by_year["year"])
                        ##st.text(monthly_counts_by_year["month_num"])
                        #st.text(monthly_counts_by_year["count"])
                        
                        test_df1 = pd.DataFrame({'year': monthly_counts_by_year["year"],
                                                   'month': monthly_counts_by_year["month_num"],
                                                   'count': monthly_counts_by_year["count"]})
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        # Set Y-axis ticks at intervals of 100
                        max_value = test_df1['count'].max()
                        y_ticks = range(0, max_value + 1, 100)
                        ax.yaxis.set_ticks(y_ticks)
                       
                        #set seaborn plotting aesthetics
                        sns.set(style='white')
                        
                        #create grouped bar chart
                        sns.barplot(x='month', y='count', hue='year', data=test_df1) 
                        st.pyplot(fig)           
             
    
                    with col4:
                        
                        # daily activity
                        fig, ax = plt.subplots()
                        plt.title('Most common words')
                        plt.imshow(util.keyword_analysis(wa_users_data_df), interpolation='bilinear')
                        plt.axis('off')
                        st.pyplot(fig)
                        
                        
                    st.markdown("<br>", unsafe_allow_html=True)
    
                    col1, col2= st.columns(2)
                    
                    with col1:
                        
                        col31, col41 = st.columns(2)
                            
                        # emoji analysis
                        emoji_df = util.emoji_helper(wa_users_data_df)
    
                        with col31:
                            # Extract top 5 emojis and 'Other'
                            top_5_emojis = emoji_df.head(5)
                            other_emojis_count = emoji_df['count'].iloc[5:].sum()
                            other_row = pd.DataFrame({'emoji': ['Other'], 'count': [other_emojis_count]})
                            
                            # Combine top 5 and 'Other' into a new DataFrame for pie chart
                            emoji_pie_df = pd.concat([top_5_emojis, other_row])
                            
                            # Reset the index of the DataFrame
                            emoji_pie_df.reset_index(drop=True, inplace=True)
                            
                            # Create a pie chart using Plotly
                            fig = px.pie(emoji_pie_df, values='count', names='emoji', title='Top 5 Emoji Distribution', width=300)
                            
                            # Display the pie chart using Streamlit
                            st.plotly_chart(fig)
                            
                        with col41:
                            
                            # Display the emoji DataFrame with colors
                            st.dataframe(emoji_df, height=500)
    
                    with col2:
                       
                        fig, ax = plt.subplots(figsize=(8, 6))
                        
                        # Call the sentiment_helper function and plot the data
                        sentiment_data = util.sentiment_helper(wa_users_data_df)
                        
                        # Create an interactive sentiment score plot using Plotly
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=sentiment_data.index, y=sentiment_data.values, mode='lines+markers'))
                        
                        # Customize the plot
                        fig.update_layout(
                            title='Average Sentiment Scores Over Months',
                            xaxis_title='Month',
                            yaxis_title='Average Sentiment Score',
                            yaxis_range=[-1, 1]  # Set y-axis limits for sentiment score
                        )
                        
                        # Display the interactive plot using Streamlit
                        st.plotly_chart(fig)
                        
                    if selected_user == 'Overall':
                        
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        
                        # Create a figure and axes
                        fig, ax = plt.subplots(figsize=(20, 16))
                        
                        df_plot = wa_users_data_df.copy()
                        G = util.network_analysis(df_plot)
                        
                        # Create the network graph plot
                        pos = nx.spring_layout(G)
                        nx.draw_networkx_nodes(G, pos, node_size=500)
                        nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.5)
                        nx.draw_networkx_labels(G, pos, font_size=10, font_color='black')
                        plt.title('Network Graph of User Interactions')
                        plt.axis('off')  # Turn off axis
                        st.pyplot(fig)  # Display the network graph plot
                        
                        # Calculate centrality measures to identify influential users
                        in_degree_centrality = nx.in_degree_centrality(G)
                        out_degree_centrality = nx.out_degree_centrality(G)
                        
                        
                        
                            
                            
                        # Create DataFrames for in-degree and out-degree centrality
                        in_degree_df = pd.DataFrame(sorted(in_degree_centrality.items(), key=lambda x: x[1], reverse=True)[:6], columns=['User', 'In-Degree Centrality'])
                        out_degree_df = pd.DataFrame(sorted(out_degree_centrality.items(), key=lambda x: x[1], reverse=True)[:6], columns=['User', 'Out-Degree Centrality'])
                        
                        #st.text("==BEGIN==")
                        first_occurrence = first_centrality = in_degree_df.iloc[0]['In-Degree Centrality']
                        out_sec = out_degree_df.iloc[0]['Out-Degree Centrality']
                        
                        
                        # Display side-by-side tables
                        st.write("**Top Influential Users based on In-Degree Centrality:**")
                        st.table(in_degree_df)
                        
                        st.write("**Top Influential Users based on Out-Degree Centrality:**")
                        st.table(out_degree_df)
                            
                            
                            
                        ##st.text(f"first_occurrence:::=>{first_occurrence}")
                        ##st.text(f"Out_sec:::=>{out_sec}")
                          
                            
                       
                        st.markdown(
                            "In this group of friends who like to talk to each other. Some friends talk more, and some talk less. These numbers show us which friends are really good at talking and who others like to talk to the most."
                            "\n\nTop Influential Users based on In-Degree Centrality:"
                            "\n- These are the friends who get talked to a lot."
                            "\n- For example, the first number {} means that one friend got talked to by {}% of the other friends."
                            "\n- It's like saying approx {} out of every 10 friends like to talk to this friend a lot."
                            "\n\nTop Influential Users based on Out-Degree Centrality:"
                            "\n- These are the friends who like to start conversations a lot."
                            "\n- For example, the first number {} means that this friend likes to start conversations with {}% of the other friends."
                            "\n- So, these numbers help us know which friends are really popular in the group and who likes to talk the most to others."
                            "\n- Just like in school, where some kids are really good at making friends and starting conversations."
                            "".format(
                                first_occurrence, (first_occurrence * 100), (int(first_occurrence * 10)),
                                out_sec, (out_sec * 100)
                            )
                        )

            else:
                st.text("Sorry! no data is available. Try another filter")
                        

if __name__ == "__main__":
    main()
