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


# Custom plot style
plt.style.use("dark_background")
sns.set_theme(style="darkgrid", context='talk', font_scale=0.9)

##  ______________________________________________________________________________________________________

## _________________________________________________________________________________________________________
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
        fcol.markdown(f"*First Message:* {first_msg}")
        lcol.markdown(f"*Last Message:* {last_msg}")
        st.caption("Note: Media messages may appear as '<Media omitted>'.")

        ##  ______________________________________________________________________________________________________

        ## _________________________________________________________________________________________________________
        st.write("")
        st.markdown("---")
        st.markdown("### 📆 Monthly Activity")
        timeline = helper.montly_timeline(selected_user, df)

        # Create plot with custom style
        plt.style.use('default')  # Use matplotlib's default style
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#FFFFFF')  # White background for figure
        ax.set_facecolor('#F5F5F5')  # Light grey background for plot area

        # Plot styling
        ax.plot(timeline['month_year'], timeline['message'],
                color='#2C8C99', linewidth=2.5, marker='o', markersize=8,
                markerfacecolor='#FF6B6B', markeredgewidth=1)

        # Add data labels
        for i, (month, count) in enumerate(zip(timeline['month_year'], timeline['message'])):
            vertical_offset = 5 if i % 2 == 0 else -5
            ax.text(month, count + vertical_offset, f'{count}',
                    ha='center', va='bottom' if i % 2 == 0 else 'top',
                    fontsize=9, color='#2C8C99')

        # Customize axes and labels
        ax.set_xlabel("Month-Year", fontsize=12, labelpad=15, color='#333333')
        ax.set_ylabel("Messages", fontsize=12, labelpad=15, color='#333333')
        ax.tick_params(axis='both', which='major', labelsize=10, colors='#333333')

        # Rotate and align x-axis labels
        plt.xticks(rotation='vertical', ha='right', fontsize=10)
        plt.yticks(fontsize=10)

        # Add grid and remove borders
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7, color='#AAAAAA')
        ax.spines[['top', 'right']].set_visible(False)
        ax.spines[['left', 'bottom']].set_color('#666666')

        # Add annotation for peak point
        max_point = timeline[timeline['message'] == timeline['message'].max()]
        ax.annotate(f'Peak: {max_point["message"].values[0]}',
                    xy=(max_point['month_year'], max_point['message']),
                    xytext=(max_point['month_year'], max_point['message'] + 20),
                    arrowprops=dict(arrowstyle='->', color='#FF6B6B'),
                    ha='center', color='#FF6B6B', fontsize=10)

        plt.tight_layout()
        st.pyplot(fig)

##  ______________________________________________________________________________________________________

## _________________________________________________________________________________________________________
        st.write("")
        st.markdown("--")
        st.markdown("### 🗓 Activity Pattern")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔥 Weekly Heatmap")
            heatmap = helper.activity_heatmap(selected_user, df)

            # Fixed heatmap with float handling
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.heatmap(
                heatmap,
                ax=ax,
                cmap="YlGn",
                annot=True,
                fmt=".0f",  # Changed from 'd' to handle floats
                linewidths=0.5,
                linecolor='#444444',
                cbar_kws={'label': 'Message Count'}
            )
            plt.xlabel('Hour Intervals (12h or 24h format)', fontsize=10, color='#333333')
            plt.ylabel('Days', fontsize=10, color='#333333')
            plt.xticks(rotation=45, fontsize=8, color='#555555')
            plt.yticks(rotation=0, fontsize=8, color='#555555')
            ax.set_facecolor('#F5F5F5')
            plt.title("Activity Distribution by Day & Hour", pad=20, fontsize=12, color='#2C8C99')
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            st.subheader("📅 Day/Month Activity")
            tab1, tab2 = st.tabs(["📆 Daily", "🗓 Monthly"])

            with tab1:
                daily = helper.busyday_graph(selected_user, df)

                # Fixed daily plot
                fig, ax = plt.subplots(figsize=(8, 4))
                bars = ax.bar(
                    daily.index,
                    daily.values,
                    color='#2C8C99',
                    edgecolor='#1A5F69',
                    linewidth=1.2
                )

                # Fixed value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.,
                        height + 0.5,
                        f'{height:.0f}',  # Changed to handle floats
                        ha='center',
                        va='bottom',
                        fontsize=8,
                        color='#333333'
                    )

                plt.xticks(rotation=45, ha='right', fontsize=9, color='#555555')
                plt.yticks(fontsize=9, color='#555555')
                plt.grid(axis='y', linestyle='--', alpha=0.4)
                ax.set_facecolor('#F5F5F5')
                ax.spines[['top', 'right']].set_visible(False)
                plt.title("Daily Message Distribution", pad=15, fontsize=11, color='#2C8C99')
                plt.tight_layout()
                st.pyplot(fig)

            with tab2:
                monthly = helper.monthbusy_graph(selected_user, df)

                # Fixed monthly plot
                fig, ax = plt.subplots(figsize=(8, 4))
                bars = ax.bar(
                    monthly.index,
                    monthly.values,
                    color='#FF6B6B',
                    edgecolor='#CC5959',
                    linewidth=1.2
                )

                # Fixed value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.,
                        height + 1.5,
                        f'{height:.0f}',  # Changed to handle floats
                        ha='center',
                        va='bottom',
                        fontsize=8,
                        color='#333333'
                    )

                plt.xticks(rotation=45, ha='right', fontsize=9, color='#555555')
                plt.yticks(fontsize=9, color='#555555')
                plt.grid(axis='y', linestyle='--', alpha=0.4)
                ax.set_facecolor('#F5F5F5')
                ax.spines[['top', 'right']].set_visible(False)
                plt.title("Monthly Message Distribution", pad=15, fontsize=11, color='#FF6B6B')
                plt.tight_layout()
                st.pyplot(fig)

##  ______________________________________________________________________________________________________

## _________________________________________________________________________________________________________

        # Most Active Users
        st.write("")
        st.markdown("-")
        if selected_user == "Overall":
            st.markdown("### 👥 Top Contributors")
            top_users, user_df = helper.most_busy_person(df)

            col1, col2 = st.columns([2, 1])
            with col1:
                fig, ax = plt.subplots(figsize=(8, 4))
                bars = ax.bar(top_users.index, top_users.values,
                              color='#2C8C99', edgecolor='#1A5F69', linewidth=1.2)

                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., height + 3,
                            f'{height}', ha='center', va='bottom',
                            fontsize=9, color='#333333')

                plt.xticks(rotation=45, ha='right', fontsize=9)
                plt.grid(axis='y', linestyle='--', alpha=0.4)
                ax.set_facecolor('#F5F5F5')
                ax.spines[['top', 'right']].set_visible(False)
                plt.tight_layout()
                st.pyplot(fig)

            with col2:
                # Style dataframe without changing data
                st.dataframe(
                    user_df.style
                    .format({'count': '{:,.0f}'})
                    .highlight_max(color='#FF6B6B')
                    .set_properties(**{'color': 'black', 'background-color': '#F5F5F5'}),
                    height=300
                )

##  ______________________________________________________________________________________________________

## _________________________________________________________________________________________________________

        # Wordcloud + Common Words
        st.write("")
        st.markdown("--")
        st.markdown("### 💬 Word Usage")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("☁ Word Cloud")
            wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 6))

            # Enhanced word cloud styling
            ax.imshow(wc.recolor(colormap='viridis', random_state=42))  # ✅ Fixed closing parenthesis
            ax.axis("off")
            ax.set_facecolor('#F5F5F5')
            fig.patch.set_facecolor('#F5F5F5')

            plt.title(
                "Word Frequency Cloud\n(Size = Frequency)",
                fontsize=14,
                color='#2C8C99',
                pad=20,
                fontweight='bold'
            )
            st.pyplot(fig)

        with col2:
            st.subheader("🔠 Lexical Analysis")
            common = helper.most_common_words(selected_user, df)

            fig, ax = plt.subplots(figsize=(10, 6))

            # Enhanced bar plot
            bars = ax.barh(
                common[0],
                common[1],
                color='#2C8C99',
                edgecolor='#1A5F69',
                linewidth=1.5,
                height=0.8
            )

            # Add value labels for each bar
            for i, (word, count) in enumerate(zip(common[0], common[1])):
                ax.text(count + 1, i, str(count), va='center', fontsize=9, color='#333333')

            ax.set_facecolor('#F5F5F5')
            fig.patch.set_facecolor('#F5F5F5')
            ax.tick_params(colors='black')
            ax.spines[['top', 'right']].set_visible(False)
            ax.grid(axis='x', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)

 ##_______________________________________________________________________________

## _________________________________________________________________________________________________________


        # Emoji Section
        st.write("")
        st.markdown("--")
        st.markdown("### 😄 Emoji Insights")
        emoji_df = helper.emoji_analysis(selected_user, df)

        if not emoji_df.empty:
            emoji_df.columns = ['Emoji', 'Count']
            emoji_df['Count'] = pd.to_numeric(emoji_df['Count'])

            # Calculate percentages
            total_emojis = emoji_df['Count'].sum()
            emoji_df['Percentage'] = (emoji_df['Count'] / total_emojis * 100).round(1)

            col1, col2 = st.columns([5, 4])
            with col1:
                # Enhanced dataframe display
                st.markdown("**Top Emojis Analysis**")
                styled_df = emoji_df.head(10).style \
                    .bar(subset=['Count'], color='#2C8C99') \
                    .format({'Count': '{:,}', 'Percentage': '{:.1f}%'}) \
                    .highlight_max(subset=['Count'], color='#FF6B6B') \
                    .set_properties(**{'color': 'black','background-color': '#F5F5F5'})

                st.dataframe(styled_df, height=380)

            with col2:
                # Enhanced pie chart
                fig, ax = plt.subplots(figsize=(8, 5))
                plt.rcParams['font.family'] = 'Segoe UI Emoji'

                # Use top 5 with percentage
                top_emojis = emoji_df.head(5)
                colors = ['#2C8C99', '#FF6B6B', '#1A5F69', '#CC5959', '#AAAAAA']

                # Create donut pie chart
                wedges, texts, autotexts = ax.pie(
                    top_emojis['Count'],
                    labels=top_emojis['Emoji'],
                    colors=colors,
                    autopct='%1.1f%%',
                    startangle=90,
                    wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'},
                    textprops={'fontsize': 14}
                )

                # Add center circle
                centre_circle = plt.Circle((0, 0), 0.70, fc='white')
                ax.add_artist(centre_circle)

                # Add legend
                ax.legend(wedges,
                          [f"{e} ({c})" for e, c in zip(top_emojis['Emoji'], top_emojis['Count'])],
                          title="Emoji Legend",
                          loc="center left",
                          bbox_to_anchor=(1, 0, 0.5, 1),
                          fontsize=9)

                # Equal aspect ratio
                ax.axis('equal')
                plt.title("Top 5 Emoji Distribution", color='#2C8C99', fontsize=12, pad=20)
                plt.setp(autotexts, size=10, color='white', weight='bold')
                st.pyplot(fig)
        else:
            st.info("🎭 No emojis detected in this conversation")

##_______________________________________________________________________________

## ______________________________________________________________________________


        st.write("")
        st.markdown("---")
        st.markdown("### ⏱ Response Time Analysis")

        # Get response time data (original logic untouched)
        response_df = helper.get_response_times_df(df)
        group_avg, _ = helper.get_response_time_analysis(selected_user, response_df)

        if not group_avg.empty:
            # Same threshold calculation
            threshold = response_df['response_time_min'].quantile(0.90)

            # Top 5 Fastest Responders (original logic)
            top5 = group_avg.head(5)

            # Create columns for metrics
            col1, col2 = st.columns(2)

            with col1:
                # Enhanced metric display
                fastest_user = top5.iloc[0]['responder']
                fastest_time = top5.iloc[0]['response_time_min']

                st.markdown(f"""
                <div style='background-color:#F9F9F9;padding:20px;border-radius:10px;border-left: 5px solid #2C8C99'>
                    <p style='color:#000000;margin:0 0 10px 0;font-size:16px'>🏆 Fastest Reply Award goes to</p>
                    <h3 style='color:#000000;margin:0;font-size:24px'>🚀 {fastest_user}</h3>
                    <p style='color:#333333;font-size:16px'>Avg: {fastest_time:.1f} mins</p>
                </div>
                """, unsafe_allow_html=True)

                # Threshold explanation with styling
                st.markdown(f"""
                <div style='margin-top:20px;padding:15px;background-color:#F9F9F9;border-radius:8px'>
                    📊 <b style='color:#000000'>Session Threshold:</b> <span style='color:#000000'>{threshold:.1f} minutes</span><br>
                    <small style='color:#444444'>Calculated as 90th percentile of message gaps</small>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Enhanced bar chart
                st.subheader("🏆 Top 5 Responders")
                fig, ax = plt.subplots(figsize=(8, 4))
                bars = ax.bar(top5['responder'], top5['response_time_min'],
                              color='#2C8C99', edgecolor='#1A5F69', linewidth=1.2)

                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., height,
                            f'{height:.1f} mins', ha='center', va='bottom',
                            fontsize=9, color='#333333')

                # Chart styling
                plt.xticks(rotation=35, ha='right', fontsize=9)
                plt.grid(axis='y', linestyle='--', alpha=0.4)
                ax.set_facecolor('#F5F5F5')
                ax.spines[['top', 'right']].set_visible(False)
                plt.ylabel("Avg Response (mins)", fontsize=10)
                plt.tight_layout()
                st.pyplot(fig)

            # Enhanced data table
            st.markdown("#### 📋 Response Time Statistics")
            styled_df = group_avg.rename(columns={
                'responder': 'Member',
                'response_time_min': 'Avg Response (mins)'
            }).style \
                .bar(subset=['Avg Response (mins)'], color='#FF6B6B', vmin=0) \
                .format({'Avg Response (mins)': '{:.1f}'}) \
                .highlight_min(subset=['Avg Response (mins)'], color='#2C8C99') \
                .set_properties(**{'color':'black','background-color': '#F5F5F5'})

            st.dataframe(styled_df, height=300)

        else:
            st.info("📭 Insufficient data for response time analysis")




        # Sentiment Analysis Section
        st.markdown("---")
        st.markdown("### 😃 Sentiment Insights")
        st.caption("Sentiment score ranges from -1 (Negative) to +1 (Positive)")

        # Get sentiment data (original logic)
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

                # Enhanced metrics
                color = '#1A5F69' if user_avg > comparison['group_avg'] else '#CC5959'
                direction = '↑ Above' if user_avg > comparison['group_avg'] else '↓ Below'

                col1.markdown(f"""
                <div style='background-color:#F9F9F9;padding:15px;'margin-bottom:30px';border-radius:8px;border-left:4px solid #2C8C99'>
                    <h4 style='color:#000000;margin:0'>📊 Avg Score</h4>
                    <p style='font-size:24px;margin:5px 0;color:#000000'>{user_avg:.2f}</p>
                    <small style='color:{color}'>{direction} Group</small>
                </div>
                """, unsafe_allow_html=True)

                col2.markdown(f"""
                <div style='background-color:#F9F9F9;padding:15px;'margin-bottom:30px';border-radius:8px'>
                    <h4 style='color:#000000;margin:0'>😊 Positive %</h4>
                    <p style='font-size:24px;margin:5px 0;color:#000000'>{comparison['user_positive_pct']:.1f}%</p>
                    <small style='color:#000000'>Group: {comparison['group_positive_pct']:.1f}%</small>
                </div>
                """, unsafe_allow_html=True)

                col3.markdown(f"""
                <div style='background-color:#F9F9F9;padding:15px;'margin-bottom:30px';border-radius:8px'>
                    <h4 style='color:#000000;margin:0'>💬 Messages</h4>
                    <p style='font-size:24px;margin:5px 0;color:#000000'>{len(user_df):,}</p>
                </div>
                """, unsafe_allow_html=True)

                # Enhanced comparison chart
                fig, ax = plt.subplots(figsize=(8, 3))
                sns.barplot(
                    x=[user_avg, comparison['group_avg']],
                    y=['You', 'Group'],
                    palette=['#2C8C99', '#F5F5F5'],
                    edgecolor=['#1A5F69', '#CCCCCC'],
                    linewidth=2
                )
                ax.set_xlim(-1, 1)
                ax.set_facecolor('#FFFFFF')
                ax.spines[['top', 'right', 'bottom']].set_visible(False)
                plt.title("Individual vs Group Sentiment Comparison",
                          fontsize=12, color='#2C8C99', pad=15)
                plt.xlabel("Sentiment Score", fontsize=10, color='#333333')
                plt.xticks(fontsize=9)
                st.pyplot(fig)

            # ================================
            # Group Analysis
            # ================================
            else:
                st.markdown("#### Group-Level Analysis")
                col1, col2 = st.columns(2)

                col1.markdown(f"""
                <div style='background-color:#F9F9F9;padding:20px;'margin-bottom:30px';border-radius:10px'>
                    <h4 style='color:#2C8C99;margin:0'>📈 Average Sentiment</h4>
                    <p style='color:#000000;font-size:32px;margin:10px 0'>{avg_score:.2f}</p>
                </div>
                """, unsafe_allow_html=True)

                col2.markdown(f"""
                <div style='background-color:#F9F9F9;padding:20px;'margin-bottom:30px';border-radius:10px'>
                    <h4 style='color:#2C8C99;margin:0'>🎭 Dominant Sentiment</h4>
                    <p style='color:#000000;font-size:32px;margin:10px 0'>{counts.idxmax()}</p>
                </div>
                """, unsafe_allow_html=True)

                # Enhanced group charts
                fig, ax = plt.subplots(1, 2, figsize=(14, 5))

                # Sentiment Distribution
                sns.countplot(
                    data=sentiment_df,
                    x='sentiment_label',
                    order=['Negative', 'Neutral', 'Positive'],
                    palette=['#FF6B6B', '#CCCCCC', '#2C8C99'],
                    ax=ax[0]
                )
                ax[0].set_title("Sentiment Distribution", fontsize=12, color='#333333')
                ax[0].set_facecolor('#F5F5F5')
                ax[0].spines[['top', 'right']].set_visible(False)

                # Top Contributors
                top_users = sentiment_df.groupby('user')['sentiment'].mean().sort_values(ascending=False).head(5)
                sns.barplot(
                    x=top_users.values,
                    y=top_users.index,
                    ax=ax[1],
                    palette='Blues_d',
                    edgecolor='#1A5F69',
                    linewidth=1
                )
                ax[1].set_title("Top 5 Positive Contributors", fontsize=12, color='#333333')
                ax[1].set_facecolor('#F5F5F5')
                ax[1].spines[['top', 'right']].set_visible(False)

                # Add value labels
                for p in ax[1].patches:
                    width = p.get_width()
                    ax[1].text(width + 0.05, p.get_y() + p.get_height() / 2,
                               f'{width:.2f}',
                               ha='left', va='center', fontsize=9)

                plt.tight_layout()
                st.pyplot(fig)

            # ================================
            # Common Deep Dive
            # ================================
            example_positive, example_negative = helper.get_extreme_messages(sentiment_df)

            with st.expander("🔍 Deep Dive Analysis", expanded=False):
                tab1, tab2 = st.tabs(["📈 Trends", "💬 Examples"])

                with tab1:
                    # Enhanced trend plot
                    sentiment_df['month'] = sentiment_df['dates'].dt.strftime('%b-%Y')
                    monthly = sentiment_df.groupby('month')['sentiment'].mean().reset_index()

                    fig, ax = plt.subplots(figsize=(10, 4))
                    sns.lineplot(
                        data=monthly,
                        x='month',
                        y='sentiment',
                        color='#2C8C99',
                        marker='o',
                        markersize=8,
                        linewidth=2
                    )
                    plt.xticks(rotation='vertical', ha='right', fontsize=9)
                    plt.yticks(fontsize=9)
                    plt.grid(axis='y', linestyle='--', alpha=0.3)
                    ax.set_facecolor('#F5F5F5')
                    ax.spines[['top', 'right']].set_visible(False)
                    plt.title("Monthly Sentiment Trend", fontsize=12, color='#333333', pad=15)
                    st.pyplot(fig)

                with tab2:
                    cols = st.columns(2)
                    with cols[0]:
                        st.markdown(f"""
                        <div style='background:#E8F5E9;padding:15px;border-radius:8px'>
                            <h4 style='color:#1B5E20;margin:0'>😊 Positive Example</h4>
                            <p style='color:#2E7D32;margin:10px 0'>{example_positive}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with cols[1]:
                        st.markdown(f"""
                        <div style='background:#FFEBEE;padding:15px;border-radius:8px'>
                            <h4 style='color:#B71C1C;margin:0'>😞 Negative Example</h4>
                            <p style='color:#C62828;margin:10px 0'>{example_negative}</p>
                        </div>
                        """, unsafe_allow_html=True)

        else:
            st.info("📭 Insufficient messages for sentiment analysis")