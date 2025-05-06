import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import preprocessor, helper

# Set dark theme-compatible background and layout
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom plot style
plt.style.use("dark_background")
sns.set_theme(style="darkgrid")

# Sidebar
with st.sidebar:
    st.title("📊 WhatsApp Chat Analyzer")
    uploaded_file = st.file_uploader("📁 Upload a WhatsApp TXT File", type=["txt"])

    if uploaded_file:
        data = uploaded_file.getvalue().decode("utf-8").splitlines()
        df = preprocessor.preprocess(data)

        if not df.empty:
            users = ['Overall'] + sorted([
                u for u in df['user'].unique()
                if u != 'group_notification'
            ])
            selected_user = st.selectbox("👤 Select User", users)
            analyze_btn = st.button("🔍 Analyze")

# Main Analysis Section
if uploaded_file and 'analyze_btn' in locals():
    if df.empty:
        st.error("❌ Invalid or empty chat file.")
    else:
        st.markdown("## 📈 Chat Summary")

        # Basic stats
        num_messages, words, media, links, first_msg, last_msg = helper.fetch_start(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💬 Total Messages", num_messages)
        col2.metric("📝 Total Words", words)
        col3.metric("📷 Media Shared", media)
        col4.metric("🔗 Links Shared", links)

        st.markdown("---")
        st.markdown("### 🕐 First & Last Message")

        fcol, lcol = st.columns(2)
        with fcol:
            st.markdown(f"**First Message:** `{first_msg}`")
        with lcol:
            st.markdown(f"**Last Message:** `{last_msg}`")
        st.caption("Note: Media messages may appear as '<Media omitted>'.")

        # Monthly Timeline
        st.markdown("---")
        st.markdown("### 📆 Monthly Activity")
        timeline = helper.montly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['month_year'], timeline['message'], color='cyan')
        ax.set_xlabel("Month-Year")
        ax.set_ylabel("Messages")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        # Activity Maps
        st.markdown("### 🗓️ Activity Pattern")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔥 Weekly Heatmap")
            heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots()
            sns.heatmap(heatmap, ax=ax, cmap="YlGnBu", linewidths=0.5)
            plt.xlabel('period(ex -1pm to 2pm)')
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            st.subheader("📅 Day/Month Activity")
            tab1, tab2 = st.tabs(["📆 Daily", "🗓️ Monthly"])

            with tab1:
                daily = helper.busyday_graph(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(daily.index, daily.values, color='skyblue')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)

            with tab2:
                monthly = helper.monthbusy_graph(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(monthly.index, monthly.values, color='orange')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)

        # Most Active Users
        if selected_user == "Overall":
            st.markdown("### 👥 Top Contributors")
            top_users, user_df = helper.most_busy_person(df)

            col1, col2 = st.columns([2, 1])
            with col1:
                fig, ax = plt.subplots()
                ax.bar(top_users.index, top_users.values, color='salmon')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)

            with col2:
                st.dataframe(user_df)

        # Wordcloud + Common Words
        st.markdown("### 💬 Word Usage")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("☁️ Word Cloud")
            wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(wc)
            ax.axis("off")
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            st.subheader("🔠 Most Common Words")
            common = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(common[0], common[1], color='limegreen')
            plt.tight_layout()
            st.pyplot(fig)

        # Emoji Section
        st.markdown("### 😄 Emoji Analysis")
        emoji_df = helper.emoji_analysis(selected_user, df)

        if not emoji_df.empty:
            emoji_df.columns = ['Emoji', 'Count']
            emoji_df['Count'] = pd.to_numeric(emoji_df['Count'])

            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(emoji_df.head(10))

            with col2:
                fig, ax = plt.subplots()
                plt.rcParams['font.family'] = 'Segoe UI Emoji'
                ax.pie(
                    emoji_df['Count'].head(5),
                    labels=emoji_df['Emoji'].head(5),
                    autopct='%1.1f%%',
                    startangle=90
                )
                ax.axis('equal')
                st.pyplot(fig)
        else:
            st.info("No emojis found in this chat.")

        # =====================================
        # RESPONSE TIME ANALYSIS SECTION
        # =====================================
        st.markdown("---")
        st.markdown("### ⏱️ Response Time Analysis")

        # Get response time data
        response_df = helper.get_response_times_df(df)
        group_avg, _ = helper.get_response_time_analysis(selected_user, response_df)

        if not group_avg.empty:
            # Calculate threshold for explanation
            threshold = response_df['response_time_min'].quantile(0.90)  # Same threshold calculation

            # Top 5 Fastest Responders
            top5 = group_avg.head(5)

            # Create columns for metrics
            col1, col2 = st.columns(2)

            with col1:
                # Fastest Responder Metric
                fastest_user = top5.iloc[0]['responder']
                fastest_time = top5.iloc[0]['response_time_min']
                st.metric(f"🚀 Fastest Responder",
                          f"{fastest_user}",
                          f"Avg: {fastest_time:.1f} mins")

                # Threshold Explanation
                st.markdown(f"""
                **📊 Threshold Info:**  
                Conversations are split if gap exceeds (EX- no chat > Threshold then it was new session) 
                `{threshold:.1f} minutes` (90th percentile of message gaps)
                """)

            with col2:
                # Top 5 Bar Chart
                st.subheader("🏆 Top 5 Fastest Responders")
                fig, ax = plt.subplots()
                ax.bar(top5['responder'], top5['response_time_min'], color='#FF6B6B')
                ax.set_xlabel("Member")
                ax.set_ylabel("Avg Response Time (mins)")
                plt.xticks(rotation=35)
                plt.tight_layout()
                st.pyplot(fig)

            # Full Data Table
            st.markdown("#### 📋 Full Response Time Stats")
            st.dataframe(group_avg.rename(columns={
                'responder': 'Member',
                'response_time_min': 'Avg Response (mins)'
            }))

        else:
            st.info("Not enough data to calculate response times")

        # Sentiment Analysis Section
        st.markdown("---")
        st.markdown("### 😃 Sentiment Insights")
        st.caption("Sentiment score ranges from -1 (Negative) to +1 (Positive)")

        # Get sentiment data
        sentiment_df = helper.preprocess_for_sentiment(df)

        if not sentiment_df.empty:
            sentiment_df = helper.get_sentiment_scores(sentiment_df)
            avg_score, counts, _ = helper.get_sentiment_metrics(sentiment_df)

            # ================================
            # Individual User Analysis
            # ================================
            if selected_user != "Overall":
                user_avg, user_counts, user_df = helper.get_individual_sentiment(sentiment_df, selected_user)
                comparison = helper.compare_with_group(user_df, sentiment_df)

                st.markdown(f"#### {selected_user}'s Sentiment Breakdown")
                col1, col2, col3 = st.columns(3)
                col1.metric("Avg Score", f"{user_avg:.2f}",
                            f"{'↑ Above' if user_avg > comparison['group_avg'] else '↓ Below'} Group Avg")
                col2.metric("Positive %", f"{comparison['user_positive_pct']:.1f}%",
                            f"Group: {comparison['group_positive_pct']:.1f}%")
                col3.metric("Total Messages", len(user_df))

                fig, ax = plt.subplots()
                sns.barplot(x=[user_avg, comparison['group_avg']],
                            y=['You', 'Group'],
                            palette=['skyblue', 'lightgray'])
                ax.set_title("You vs Group Average")
                ax.set_xlim(-1, 1)
                st.pyplot(fig)

                example_positive, example_negative = helper.get_extreme_messages(user_df)

            # ================================
            # Group Analysis
            # ================================
            else:
                st.markdown("#### Group-Level Analysis")
                col1, col2 = st.columns(2)
                col1.metric("Average Sentiment", f"{avg_score:.2f}")
                col2.metric("Dominant Sentiment", counts.idxmax())

                fig, ax = plt.subplots(1, 2, figsize=(15, 5))
                sns.countplot(data=sentiment_df, x='sentiment_label',
                              order=['Negative', 'Neutral', 'Positive'], ax=ax[0])
                ax[0].set_title("Sentiment Distribution")

                top_users = sentiment_df.groupby('user')['sentiment'].mean().sort_values(ascending=False).head(5)
                sns.barplot(x=top_users.values, y=top_users.index, ax=ax[1], palette='viridis')
                ax[1].set_title("Top 5 Positive Contributors")
                st.pyplot(fig)

                example_positive, example_negative = helper.get_extreme_messages(sentiment_df)

            # ================================
            # Common Deep Dive
            # ================================
            with st.expander("Deep Dive Analysis"):
                tab1, tab2 = st.tabs(["📈 Trends", "💬 Examples"])

                with tab1:
                    sentiment_df['month'] = sentiment_df['dates'].dt.strftime('%Y-%m')
                    monthly = sentiment_df.groupby('month')['sentiment'].mean().reset_index()
                    fig, ax = plt.subplots()
                    sns.lineplot(data=monthly, x='month', y='sentiment', marker='o')
                    plt.xticks(rotation=45)
                    plt.title("Monthly Sentiment Trend")
                    st.pyplot(fig)

                with tab2:
                    cols = st.columns(2)
                    with cols[0]:
                        st.write("**😊 Positive Message Example**")
                        st.code(example_positive)
                    with cols[1]:
                        st.write("**😞 Negative Message Example**")
                        st.code(example_negative)

        else:
            st.info("Not enough messages for sentiment analysis")

