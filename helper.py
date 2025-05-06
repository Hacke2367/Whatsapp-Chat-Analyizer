from wordcloud import WordCloud
from urlextract import URLExtract
extract = URLExtract()
import pandas as pd
import emoji
from collections import Counter
import seaborn as sns
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re


analyzer = SentimentIntensityAnalyzer()


def fetch_start(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]


    num_message = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())

    num_media_message = df[df['message'] == '<Media omitted>'].shape[0]

    links = []
    for messages in df['message']:
        links.extend(extract.find_urls(messages))

    real_df = df[df['user'] != 'group_notification']

    first_row = real_df.iloc[0]
    last_row = real_df.iloc[-1]

    first_message = f"{first_row['user']}: {first_row['message']}: {first_row['dates']}"
    last_message = f"{last_row['user']}: {last_row['message']}: {last_row['dates']}"

    return num_message, len(words), num_media_message, len(links), first_message, last_message


def most_busy_person(df):
    x = df['user'].value_counts().head()
    df = round(df['user'].value_counts() / df['user'].shape[0] * 100).reset_index().rename(
        columns={'user': 'members', 'count': 'percentage'})

    return x, df

def create_wordcloud(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp['message'] = temp['message'].astype(str)
    temp = temp[temp['message'] != '<Media omitted>']
    temp = temp[temp['message'].str.contains(r'[a-zA-Z]', na=False)]

    def remove_stop_words(message):
        y = []
        for words in message.lower().split():
            if words not in stop_words:
                y.append(words)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    # temp['message'] = temp['message'].astype(str)
    temp = temp[temp['message'] != '<Media omitted>']
    # temp = temp[temp['message'].str.contains(r'[a-zA-Z]', na=False)]

    words = []

    for messages in temp['message']:
        for word in messages.lower().split():
            if word not in stop_words:
                words.append(word)
    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df



def emoji_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emoji_list = []
    for message in df['message']:
        # Use emoji.distinct_emoji_list() for better handling
        emojis_in_msg = emoji.emoji_list(message)
        emoji_list.extend([e['emoji'] for e in emojis_in_msg])

    emoji_counter = Counter(emoji_list)
    emoji_df = pd.DataFrame(
        emoji_counter.most_common(),
        columns=['Emoji', 'Count']
    )

    # Ensure numeric type
    emoji_df['Count'] = pd.to_numeric(emoji_df['Count'])

    return emoji_df

def montly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month', 'month_num']).count()['message'].reset_index()
    timeline = timeline.sort_values(by=['year', 'month_num']).reset_index(drop=True)
    timeline['month_year'] = timeline['month'] + "-" + timeline['year'].astype(str)

    return timeline

def busyday_graph(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    busiest_day = df['days_name'].value_counts()

    return busiest_day

def monthbusy_graph(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    busiest_month = df['month'].value_counts()

    return busiest_month

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmaps = df.pivot_table(index='days_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmaps

def get_response_times_df(df):
    # Preprocessing for response analysis
    filtered_df = df[
        (df['user'] != 'group_notification') &
        (~df['message'].str.contains('@', na=False)) &
        (~df['message'].str.contains('<Media omitted>', na=False))
        ].sort_values('dates').reset_index(drop=True)

    # Calculate dynamic threshold
    filtered_df['time_gap'] = filtered_df['dates'].diff().dt.total_seconds().div(60).fillna(0)
    threshold = filtered_df['time_gap'].quantile(0.90)

    # Calculate response times
    response_data = []
    for i in range(len(filtered_df)):
        sender = filtered_df.loc[i, 'user']
        sender_time = filtered_df.loc[i, 'dates']
        responders = set()

        for j in range(i + 1, len(filtered_df)):
            responder = filtered_df.loc[j, 'user']
            responder_time = filtered_df.loc[j, 'dates']

            if (responder_time - sender_time).total_seconds() / 60 > threshold:
                break

            if responder != sender and responder not in responders:
                time_diff = (responder_time - sender_time).total_seconds() / 60
                response_data.append({
                    'sender': sender,
                    'responder': responder,
                    'response_time_min': round(time_diff, 2)
                })
                responders.add(responder)

    return pd.DataFrame(response_data)


def get_response_time_analysis(selected_user, response_df):
    # Group-level analysis
    group_avg = response_df.groupby('responder')['response_time_min'].mean().sort_values().reset_index()

    # Individual-level analysis
    if selected_user != 'Overall':
        individual_df = response_df[response_df['responder'] == selected_user]
        individual_avg = individual_df.groupby('sender')['response_time_min'].mean().sort_values().reset_index()
        return group_avg, individual_avg

    return group_avg, None


## sentiment analyize


def preprocess_for_sentiment(df):
    """Clean messages for sentiment analysis"""
    filtered_df = df[
        (df['user'] != 'group_notification') &
        (~df['message'].str.contains('<Media omitted>', na=False))
    ].copy()

    filtered_df['clean_msg'] = filtered_df['message'].apply(
        lambda x: re.sub(r'http\S+|@\w+', '', str(x)).strip()
    )
    return filtered_df[filtered_df['clean_msg'] != '']

def get_sentiment_scores(df):
    """Calculate sentiment scores for messages"""
    df['sentiment'] = df['clean_msg'].apply(
        lambda x: analyzer.polarity_scores(x)['compound']
    )
    df['sentiment_label'] = pd.cut(
        df['sentiment'],
        bins=[-1, -0.05, 0.05, 1],
        labels=['Negative', 'Neutral', 'Positive']
    )
    return df

def get_sentiment_metrics(df):
    """Get key sentiment metrics"""
    if df.empty:
        return None, None, None

    avg_score = df['sentiment'].mean()
    sentiment_counts = df['sentiment_label'].value_counts()
    return avg_score, sentiment_counts, df

def get_individual_sentiment(df, username):
    """Ek specific user ke liye sentiment analysis"""
    user_df = df[df['user'] == username]
    if user_df.empty:
        return None, None, None

    avg_score = user_df['sentiment'].mean()
    sentiment_counts = user_df['sentiment_label'].value_counts()
    return avg_score, sentiment_counts, user_df

def compare_with_group(individual_df, group_df):
    """User vs Group comparison"""
    comparison = {
        'user_avg': individual_df['sentiment'].mean(),
        'group_avg': group_df['sentiment'].mean(),
        'user_positive_pct': (individual_df['sentiment_label'] == 'Positive').mean() * 100,
        'group_positive_pct': (group_df['sentiment_label'] == 'Positive').mean() * 100
    }
    return comparison

def get_extreme_messages(df, user_filter=None):
    """Return most positive and negative messages with optional user filtering"""
    if user_filter:
        df = df[df['user'] == user_filter]
    if df.empty:
        return None, None
    return (
        df.loc[df['sentiment'].idxmax()]['message'],
        df.loc[df['sentiment'].idxmin()]['message']
    )













