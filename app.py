import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import preprocessor, helper

# Set dark background and layout
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="📊",
    layout="wide"
)

# Set consistent dark mode visuals
plt.style.use("dark_background")
sns.set_theme(style="darkgrid", context='talk', font_scale=0.9)

def apply_dark_theme(ax):
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

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

# Main Section
if uploaded_file and 'analyze_btn' in locals():
    if df.empty:
        st.error("❌ Invalid or empty chat file.")
    else:
        st.markdown("## 📈 Chat Summary")

        num_messages, words, media, links, first_msg, last_msg = helper.fetch_start(selected_user, df)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("💬 Total Messages", num_messages or 0)
        with col2:
            st.metric("📝 Total Words", words or 0)
        with col3:
            st.metric("📷 Media Shared", media or 0)
        with col4:
            st.metric("🔗 Links Shared", links or 0)

        st.write("")
        st.markdown("---")
        st.markdown("### 🕐 First & Last Message")
        fcol, lcol = st.columns(2)
        fcol.markdown(f"**First Message:** `{first_msg}`")
        lcol.markdown(f"**Last Message:** `{last_msg}`")
        st.caption("Note: Media messages may appear as '<Media omitted>'.")

        # Monthly Activity Plot (Enhanced)
        st.write("")
        st.markdown("---")
        st.markdown("### 📆 Monthly Activity")
        timeline = helper.montly_timeline(selected_user, df)

        # Create figure with custom size
        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor('#0E1117')
        ax.set_facecolor('#0E1117')

        # Plot styling
        ax.plot(
            timeline['month_year'],
            timeline['message'],
            color='#00FFC6',  # Neon Cyan
            marker='D',  # Diamond markers
            markersize=8,  # Visible size
            linestyle='--',  # Dashed line
            linewidth=2,  # Thicker line
            alpha=0.8  # Slight transparency
        )

        # Axis labels with improved styling
        ax.set_xlabel("Month-Year",
                      fontsize=12,
                      labelpad=15,
                      color='white',
                      fontweight='bold')

        ax.set_ylabel("Messages",
                      fontsize=12,
                      labelpad=15,
                      color='white',
                      fontweight='bold')

        # Ticks customization
        plt.xticks(
            rotation=45,  # 45-degree rotation
            ha='right',  # Align rotated labels properly
            fontsize=10,
            color='white'
        )
        plt.yticks(
            fontsize=10,
            color='white'
        )

        # Add grid and annotation
        ax.grid(color='#404040', linestyle=':')  # Subtle grid lines

        # Highlight peak month
        max_point = timeline.loc[timeline['message'].idxmax()]
        ax.annotate(
            f"Peak: {max_point['message']} msgs",
            xy=(max_point['month_year'], max_point['message']),
            xytext=(10, 30),
            textcoords='offset points',
            arrowprops=dict(arrowstyle="->", color='white'),
            fontsize=10,
            color='white',
            backgroundcolor='#2A2A2A'
        )

        # Apply dark theme compatibility
        apply_dark_theme(ax)  # Ensure this sets facecolor properly

        # Tight layout and display
        plt.tight_layout()
        st.pyplot(fig)

        # Activity Patterns
        st.write("")
        st.markdown("---")
        st.markdown("### 🗓️ Activity Pattern")
        st.markdown("**This heatmap shows which and when your message frequency is most")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔥 Weekly Heatmap")
            heatmap = helper.activity_heatmap(selected_user, df)

            fig, ax = plt.subplots()

            # Heatmap with annotations and styling
            sns.heatmap(
                heatmap,
                ax=ax,
                cmap="viridis",  # Better color scheme for dark themes
                linewidths=0.5,
                annot=True,  # Show values in cells
                annot_kws={
                    'color': 'white',  # Annotation text color
                    'fontsize': 10  # Annotation font size
                },
                cbar_kws={
                    'label': 'Message Frequency',
                    'orientation': 'vertical',
                    'shrink': 0.6,
                    'pad': 0.02,
                    'aspect': 30
                }
            )

            # Customize color bar text
            cbar = ax.collections[0].colorbar
            cbar.set_label('Message Frequency', color='white')
            cbar.ax.yaxis.set_tick_params(color='white')
            plt.setp(cbar.ax.get_yticklabels(), color='white')

            # Axis labels and styling
            ax.set_xlabel('Time Window (e.g. 1pm-2pm)', color='white', fontsize=12)
            ax.set_ylabel('Day', color='white', fontsize=12)
            ax.tick_params(axis='both', colors='white', labelsize=10)

            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            st.subheader("📅 Day/Month Activity")
            st.markdown("** his bar graph will illustrate which day or month the message was highest.")
            tab1, tab2 = st.tabs(["📆 Daily", "🗓️ Monthly"])
            with tab1:
                daily = helper.busyday_graph(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(daily.index, daily.values, color='#25CED1',edgecolor='white')
                apply_dark_theme(ax)
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            with tab2:
                monthly = helper.monthbusy_graph(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(monthly.index, monthly.values, color='#FF8A5B',edgecolor='white')
                apply_dark_theme(ax)
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)


        # Most Active Users
        st.write("")
        st.markdown("---")
        if selected_user == "Overall":
            st.markdown("### 👥 Top Contributors")
            st.markdown("** Top Contributors")
            top_users, user_df = helper.most_busy_person(df)

            col1, col2 = st.columns([2, 1])

            with col1:
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.bar(
                    top_users.index,
                    top_users.values,
                    color='#25CED1',  # Modern Teal
                    edgecolor='white',
                    linewidth=1
                )
                ax.set_xlabel("Users", fontsize=12, color='white')
                ax.set_ylabel("Messages", fontsize=12, color='white')
                plt.xticks(rotation=45, ha='right', fontsize=10, color='white')
                plt.yticks(fontsize=10, color='white')
                apply_dark_theme(ax)
                plt.tight_layout()
                st.pyplot(fig)

            with col2:
                # Light design enhancement without error
                styled_df = (
                    user_df.style
                    .format({'Message Count': '{:,}'})
                    .set_properties(**{
                        'background-color': '#f9f9f9',
                        'color': '#333',
                        'border-color': '#ccc',
                        'font-size': '14px',
                        'text-align': 'left',
                    })
                    .set_table_styles([
                        {'selector': 'th',
                         'props': [('font-size', '15px'), ('background-color', '#eee'), ('color', '#000')]},
                        {'selector': 'td', 'props': [('padding', '6px')]},
                    ])
                )

                st.dataframe(styled_df, height=400)

        # Word Usage
        st.write("")
        st.markdown("---")
        st.markdown("### 💬 Word Usage")
        st.markdown("** most usage words.")
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
            apply_dark_theme(ax)
            plt.tight_layout()
            st.pyplot(fig)

        # Emoji Analysis
        st.write("")
        st.markdown("---")
        st.markdown("### 😄 Emoji Analysis")
        emoji_df = helper.emoji_analysis(selected_user, df)

        if not emoji_df.empty:
            emoji_df.columns = ['Emoji', 'Count']
            emoji_df['Count'] = pd.to_numeric(emoji_df['Count'])

            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df.head(10))

            with col2:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.set_facecolor('#0E1117')

                # Critical Fixes for Emoji Rendering
                plt.rcParams['font.family'] = 'Segoe UI Emoji'  # Windows
                plt.rcParams['font.sans-serif'] = ['Apple Color Emoji']  # MacOS
                plt.rcParams['axes.unicode_minus'] = False  # Special chars

                # Custom styling
                explode = [0.1] + [0] * (len(emoji_df.head(5)) - 1)  # Highlight first slice
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD']

                wedges, texts, autotexts = ax.pie(
                    emoji_df['Count'].head(5),
                    labels=emoji_df['Emoji'].head(5),
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=colors,
                    explode=explode,
                    textprops={'color': 'white', 'fontsize': 14},  # Force white text
                    wedgeprops={'edgecolor': 'black', 'linewidth': 1}  # Add borders
                )

                # Improve label visibility
                for text in texts:
                    text.set_color('white')
                    text.set_size(16)
                    text.set_weight('bold')

                ax.axis('equal')
                st.pyplot(fig)
        else:
            st.info("No emojis found in this chat.")

        # Response Time Analysis
        st.write("")
        st.markdown("---")
        st.markdown("### ⏱️ Response Time Analysis")
        response_df = helper.get_response_times_df(df)
        group_avg, _ = helper.get_response_time_analysis(selected_user, response_df)

        if not group_avg.empty:
            threshold = response_df['response_time_min'].quantile(0.90)
            top5 = group_avg.head(5)
            col1, col2 = st.columns(2)
            with col1:
                fastest_user = top5.iloc[0]['responder']
                fastest_time = top5.iloc[0]['response_time_min']
                st.metric("🚀 Fastest Responder", fastest_user, f"Avg: {fastest_time:.1f} mins")
                st.markdown(f"**📊 Threshold Info:** `{threshold:.1f} minutes` (90th percentile)")
            with col2:
                st.subheader("🏆 Top 5 Fastest Responders")
                fig, ax = plt.subplots()
                ax.bar(top5['responder'], top5['response_time_min'], color='#FF6B6B')
                ax.set_xlabel("Member")
                ax.set_ylabel("Avg Response Time (mins)")
                apply_dark_theme(ax)
                plt.xticks(rotation=35)
                plt.tight_layout()
                st.pyplot(fig)
            st.markdown("#### 📋 Full Response Time Stats")
            st.dataframe(group_avg.rename(columns={
                'responder': 'Member',
                'response_time_min': 'Avg Response (mins)'
            }))
        else:
            st.info("Not enough data to calculate response times")

        # Sentiment Analysis
        st.write("")
        st.markdown("---")
        st.markdown("### 😃 Sentiment Insights")
        st.caption("Sentiment score ranges from -1 (Negative) to +1 (Positive)")
        sentiment_df = helper.preprocess_for_sentiment(df)

        if not sentiment_df.empty:
            sentiment_df = helper.get_sentiment_scores(sentiment_df)
            avg_score, counts, _ = helper.get_sentiment_metrics(sentiment_df)

            if selected_user != "Overall":
                user_avg, _, user_df = helper.get_individual_sentiment(sentiment_df, selected_user)
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
                            y=['You', 'Group'], palette=['skyblue', 'lightgray'], ax=ax)
                ax.set_xlim(-1, 1)
                apply_dark_theme(ax)
                ax.set_title("You vs Group Average")
                st.pyplot(fig)

                example_positive, example_negative = helper.get_extreme_messages(user_df)
            else:
                st.markdown("#### Group-Level Analysis")
                col1, col2 = st.columns(2)
                col1.metric("Average Sentiment", f"{avg_score:.2f}")
                col2.metric("Dominant Sentiment", counts.idxmax())

                fig, ax = plt.subplots(1, 2, figsize=(16, 5))
                plt.yticks(rotation= 40)
                sns.countplot(data=sentiment_df, x='sentiment_label',
                              order=['Negative', 'Neutral', 'Positive'], ax=ax[0])
                ax[0].set_title("Sentiment Distribution")
                apply_dark_theme(ax[0])

                top_users = sentiment_df.groupby('user')['sentiment'].mean().sort_values(ascending=False).head(5)
                sns.barplot(x=top_users.values, y=top_users.index, ax=ax[1], palette='viridis')
                ax[1].set_title("Top 5 Positive Contributors")
                apply_dark_theme(ax[1])
                st.pyplot(fig)

                example_positive, example_negative = helper.get_extreme_messages(sentiment_df)

            with st.expander("Deep Dive Analysis"):
                tab1, tab2 = st.tabs(["📈 Trends", "💬 Examples"])
                with tab1:
                    sentiment_df['month'] = sentiment_df['dates'].dt.strftime('%Y-%m')
                    monthly = sentiment_df.groupby('month')['sentiment'].mean().reset_index()
                    fig, ax = plt.subplots()
                    sns.lineplot(data=monthly, x='month', y='sentiment', marker='o', ax=ax)
                    apply_dark_theme(ax)
                    plt.xticks(rotation=45)
                    ax.set_title("Monthly Sentiment Trend")
                    st.pyplot(fig)

                with tab2:
                    cols = st.columns(2)
                    cols[0].write("**😊 Positive Message Example**")
                    cols[0].code(example_positive)
                    cols[1].write("**😞 Negative Message Example**")
                    cols[1].code(example_negative)
        else:
            st.info("Not enough messages for sentiment analysis")




