from datetime import datetime
import re
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.parser import parse



def preprocess(data):
    cleaned_data = []

    for line in data:
        # Remove AM/PM variations with optional unicode/regular spaces before them (case-insensitive)
        line = re.sub(r'[\u202f\u00a0 ]?\bAM\b', '', line, flags=re.IGNORECASE)
        line = re.sub(r'[\u202f\u00a0 ]?\bPM\b', '', line, flags=re.IGNORECASE)

        # Remove leading/trailing junk characters
        line = line.strip(" '\n,")

        # Normalize weird spacing before hyphen (e.g., double space before dash)
        line = re.sub(r'\s{2,}-', ' -', line)     # e.g. "  -" → " -"
        line = re.sub(r'\s+-', ' -', line)        # e.g. "   -" or " -" → " -"

        cleaned_data.append(line)

    date_time_list = []
    message_list = []


    pattern = r'^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),\s*(\d{1,2}:\d{2})\s*-\s*(.+)'

    for line in cleaned_data:
        match = re.match(pattern, line)
        if match:
            date, time, message = match.groups()
            date_time_list.append(f"{date}, {time}")
            message_list.append(message)

    df = pd.DataFrame({'user_message': message_list, 'dates': date_time_list})
    # df['dates'] = pd.to_datetime(df['dates'], errors='coerce')
    df['dates'] = df['dates'].apply(parse)

    users = []
    messages = []

    for msg in df['user_message']:
        # Try splitting only at the first colon that separates user from message
        split_msg = re.split(r'^([^:]+?):\s', msg)
        if len(split_msg) == 3:
            users.append(split_msg[1])
            messages.append(split_msg[2])
        else:
            users.append('group_notification')
            messages.append(msg)

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['year'] = df['dates'].dt.year
    df['month'] = df['dates'].dt.month_name()
    df['month_num'] = df['dates'].dt.month
    df['day'] = df['dates'].dt.day
    df['days_name'] = df['dates'].dt.day_name()
    df['hour'] = df['dates'].dt.hour
    df['minute'] = df['dates'].dt.minute

    period = []
    for hour in df[['days_name', 'hour']]['hour']:
        if hour == 12:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))
    df['period'] = period

    return df

