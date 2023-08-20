#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 11:02:17 2023

@author: vaibhavsingh
"""

import streamlit as st
import preprocessor, util
import matplotlib.pyplot as plt
import networkx as nx


st.config.set_option("server.maxUploadSize", 1)


# Main Streamlit app code
def main():
    
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["txt"],accept_multiple_files=False)
    
        
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
        
        
        bytes_data = uploaded_file.getvalue()
        
        data = bytes_data.decode("utf-8")
        
        wa_users_data_df = preprocessor.preprocess(data) # create columns from chat file
        
        
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
                .custom-div {
                    padding: 10px;
                    border: 1px solid #ccc;
                    background-color: #fff;
                    text-align: center;
                    margin: 5px;
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
                    
                    col1.markdown('<div class="custom-div"><div>Total Messages</div><div>{}</div></div>'.format(num_messages), unsafe_allow_html=True)
                    col2.markdown('<div class="custom-div"><div>Total Words</div><div>{}</div></div>'.format(words), unsafe_allow_html=True)
                    col3.markdown('<div class="custom-div"><div>Media Shared</div><div>{}</div></div>'.format(num_media_messages), unsafe_allow_html=True)
                    col4.markdown('<div class="custom-div"><div>Links Shared</div><div>{}</div></div>'.format(num_links), unsafe_allow_html=True)
    
                # Create vertical space between containers
                st.markdown("<br><br>", unsafe_allow_html=True)
    
                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                
    
                    with col1:
                        # daily activity
                        fig, ax = plt.subplots()
                        util.hourly_activity(wa_users_data_df).plot(kind='bar')
                        plt.title('Message Frequency by Hour:')
                        ax.set_xlabel('Hours')
                        st.pyplot(fig)
                        
                    with col2:
                        # weekly activity
                        fig, ax = plt.subplots()
                        util.weekly_activity(wa_users_data_df).plot(kind='bar')
                        plt.title('Message Frequency by Day of the Week:')
                        plt.xticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
                        ax.set_xlabel('Day of week')
                        st.pyplot(fig)
                        
                    with col3:
                        # Create the bar plot
                        # Custom month labels
                        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
                        
                        fig, ax = plt.subplots()
                        monthly_counts =util.monthly_activity(wa_users_data_df)
                        monthly_counts.plot(kind='bar')
                        plt.title('Message Frequency by Month:')
                        plt.xlabel('Month')
                        plt.xticks(monthly_counts.index - 1, [month_labels[i - 1] for i in monthly_counts.index])  # Set custom month labels
                        st.pyplot(fig)
                        
                           
                        
                    with col4:
                        # emoji analysis
                        emoji_df = util.emoji_helper(wa_users_data_df)
                        st.dataframe(emoji_df, height=270)
    
                    st.markdown("<br>", unsafe_allow_html=True)
    
                    col1, col2= st.columns(2)
                    
                    with col1:
                        # daily activity
                        fig, ax = plt.subplots()
                        plt.title('Most common words')
                        plt.imshow(util.keyword_analysis(wa_users_data_df), interpolation='bilinear')
                        plt.axis('off')
                        st.pyplot(fig)
    
                    with col2:
                       
                        fig, ax = plt.subplots(figsize=(20, 16))
                        
                        # Call the sentiment_helper function and plot the data
                        util.sentiment_helper(wa_users_data_df).plot(marker='o', ax=ax)
                        
                        # Customize the plot
                        ax.set_title('Average Sentiment Scores Over Months', fontsize=20)
                        ax.set_xlabel('Month')
                        ax.set_ylabel('Average Sentiment Score', fontsize=15)
                        ax.set_ylim(-1, 1)  # Set y-axis limits for sentiment score
                        ax.grid()
                        
                        # Display the plot using st.pyplot()
                        st.pyplot(fig)
                        
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
                        
                        
                        # Get the first value (occurrence count)
                        first_occurrence = next(iter(in_degree_centrality.values()))
                        
                        
                        # Print the most influential users based on in-degree centrality
                        st.text("Top Influential Users based on In-Degree Centrality:")
                        for user, centrality in sorted(in_degree_centrality.items(), key=lambda x: x[1], reverse=True)[:6]:
                            st.text(f"{user}: {centrality:.4f}")
                        
                        # Print the most influential users based on out-degree centrality
                        out_sec = 0
                        st.text("\nTop Influential Users based on Out-Degree Centrality:")
                        for user, centrality in sorted(out_degree_centrality.items(), key=lambda x: x[1], reverse=True)[:6]:
                            if out_sec == 0:
                                out_sec = centrality
                            st.text(f"{user}: {centrality:.4f}")
                          
                            
                       
                        st.markdown(
                            "In this group of friends who like to talk to each other. Some friends talk more, and some talk less. These numbers show us which friends are really good at talking and who others like to talk to the most. "
                            "Top Influential Users based on In-Degree Centrality: These are the friends who get talked to a lot. "
                            "For example, the first number {} means that one friend got talked to by {}% of the other friends. "
                            "It's like saying approx {} out of every 10 friends like to talk to this friend a lot. "
                            "Top Influential Users based on Out-Degree Centrality: These are the friends who like to start conversations a lot. "
                            "For example, the first number {} means that this friend likes to start conversations with {}% of the other friends. "
                            "So, these numbers help us know which friends are really popular in the group and who likes to talk the most to others. "
                            "Just like in school, where some kids are really good at making friends and starting conversations."
                            "".format(
                                first_occurrence, (first_occurrence * 100), (int(first_occurrence * 10)),
                                out_sec, (out_sec * 100)
                            )
                        )
            else:
                st.text("Sorry! no data is available. Try another filter")
                        

if __name__ == "__main__":
    main()
