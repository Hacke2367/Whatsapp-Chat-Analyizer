from datetime import datetime
import re
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.parser import parse




def preprocess(data):
    cleaned_data = []

    for line in data:
        # Remove all AM/PM variations (including Unicode space variants)
        for variant in ['\u202fAM', '\u202fPM', ' AM', ' PM', ' AM', ' PM']:
            line = line.replace(variant, '')

        # Clean up leading/trailing junk
        line = line.strip(" '\n,")

        # Fix spacing before hyphen
        line = line.replace("  -", " -")

        cleaned_data.append(line)

    pattern_12h = r'^(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}) - (.+)'
    pattern_24h = r'^(\d{1,2}/\d{1,2}/\d{2}), ((?:[01]\d|2[0-3]):[0-5]\d) - (.+)'

    date_time_list = []
    message_list = []

    for line in cleaned_data:
        match = re.match(pattern_24h, line) or re.match(pattern_12h, line)
        if match:
            date, time, message = match.groups()
            date_time_list.append(f"{date}, {time}")
            message_list.append(message)

    df = pd.DataFrame({'user_message': message_list, 'dates': date_time_list})
    df['dates'] = df['dates'].apply(parse)

    users = []
    message = []

    for msg in df['user_message']:
        entry = re.split('([\w\W]+?):\s', msg)
        if entry[1:]:
            users.append(entry[1])
            message.append(entry[2])
        else:
            users.append('group_notification')
            message.append(entry[0])
    df['user'] = users
    df['message'] = message
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


