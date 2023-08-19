#import Librtaries and Dependencies
import numpy as np
import pandas as pd
import re  # Import the regular expressions module for text pattern matching

# Load the CSV file with messages and assign it to the variable df
df = pd.read_csv('messages.csv')

# Display the first few rows of the dataframe
df.head()

# Set an option to display the full contents of cells in the dataframe
pd.set_option('display.max_colwidth', None)

# Separate the transaction code from the message body into its own column
df['transaction_code'] = df['Message_body'].str.split().str[0]

# Extract the first appearance of the amount, remove 'Ksh' prefix, remove commas, and convert to float
df['transaction_amount'] = df['Message_body'].str.extract(r'\b(Ksh\S*)', expand=False).str.replace('Ksh', '').str.replace(',', '').astype(float)

# Define a function to classify each transaction type based on specific text in the message body
def check_message(df):
    if 'received' in df['Message_body']:
        return 'Money Received'
    elif 'for account ' in df['Message_body']:
        return 'Paybill Payment'
    elif 'sent to' in df['Message_body']:
        return 'Customer transfer'
    elif 'paid to' in df['Message_body']:
        return 'Merchant Payment'
    elif 'Withdraw' in df['Message_body']:
        return 'Withdrawal'
    elif 'Give' in df['Message_body'] and 'cash to' in df['Message_body']:
        return 'Deposit'
    elif 'airtime' in df['Message_body']:
        return 'Airtime Purchase'
    else:
        return 'Other'

# Apply the classification function to create a new 'Transaction Type' column
df['Transaction Type'] = df.apply(check_message, axis=1)

# Extract the date from the message body using a regular expression
df['date'] = df['Message_body'].str.extract(r"(\d{1,2}/\d{1,2}/\d{2})")

# Convert the 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%y')

# Extract year, month, and day from the date and create separate columns for them
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day

# Get the day of the week from the date and create a 'day_of_week' column
df['day_of_week'] = df['date'].dt.day_name()

# Extract the time from the message using a regular expression
df['time'] = df['Message_body'].apply(lambda x: re.search(r'\d{1,2}:\d{2} [AP]M', x).group())

# Convert the 'time' column to a 24-hour format
df['time'] = pd.to_datetime(df['time'], format='%I:%M %p').dt.strftime('%H:%M')

# Create a column to show whether the transaction was done in the morning, afternoon, evening, or night
df['time'] = pd.to_datetime(df['time'])
conditions = [
    (df['time'].dt.hour >= 5) & (df['time'].dt.hour < 12),
    (df['time'].dt.hour >= 12) & (df['time'].dt.hour < 17),
    (df['time'].dt.hour >= 17) & (df['time'].dt.hour < 20),
    (df['time'].dt.hour >= 20) | (df['time'].dt.hour < 5)
]
values = ['Morning', 'Afternoon', 'Evening', 'Night']
df['time_of_day'] = np.select(conditions, values)

# Extract the Mpesa balance from the message and store it in a new column
df['Mpesa_balance'] = pd.DataFrame(df['Message_body'].str.findall(r'(Ksh\S*)').tolist()).iloc[:, 1].reset_index(drop=True).str.replace('Ksh', '').str.replace(',', '')

# Remove the last decimal point and convert the 'Mpesa_balance' column to float
df['Mpesa_balance'] = df['Mpesa_balance'].str.rstrip('.').astype(float)

# Extract the transaction cost from the message and store it in a new column
df['Transaction_cost'] = pd.DataFrame(df['Message_body'].str.findall(r'(Ksh\S*)').tolist()).iloc[:, 2].reset_index(drop=True).str.replace('Ksh', '').str.replace(',', '')

# Remove excess characters after the amount, convert to float, and handle NaN entries
df['Transaction_cost'] = df['Transaction_cost'].str.rsplit('.', 1).str[0].astype(float).fillna(0)
