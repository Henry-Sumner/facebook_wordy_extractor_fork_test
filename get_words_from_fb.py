import pandas as pd
import json
import os
import datetime

#I'm adding this comment right here to test doing a pull request

# Get current directory and add inbox folder
directory = os.getcwd()
inbox = directory + r"\messages\inbox"

# Initialize dataframe to store messages
df = pd.DataFrame()

for folder in os.listdir(inbox):
    name = folder.split("_")[0]
    files = []
    # Get files that are .json
    for x in os.listdir(inbox + "/" + folder):
        if ".json" in x:
            files.append(x)

    # Open files, convert to dataframe, and append to df
    for file in files:
        with open(inbox + "/" + folder + "/" + file, "r") as f:
            data = json.load(f)
        participants = str([x["name"] for x in data["participants"]])
        participant_count = len([x["name"] for x in data["participants"]])
        df1 = pd.io.json.json_normalize(data["messages"])
        df1["participants"] = participants
        df1["participants_count"] = participant_count
        df1["chat_name"] = name
        df = df.append(df1)

sender = (
    df[["sender_name", "content"]]
    .groupby("sender_name")
    .count()
    .sort_values("content", ascending=False)
    .reset_index()
)

# Get the modal sender (you)
you = sender.iloc[0]["sender_name"]

# Get dataframe with just your messages
df_you = df[df["sender_name"] == you]
df_you["date"] = pd.to_datetime(df_you["timestamp_ms"], unit="ms")

word = []
date = []
origin = []

# Extract each word from each of your messages
for row in df_you.itertuples():
    content = (
        str(row.content)
        .replace(",", "")
        .replace(".", "")
        .replace("*", "")
        .replace("?", "")
        .replace("!", "")
    )
    words = content.split(" ")
    length = len(words)

    word.extend([word.lower() for word in words])
    date.extend([str(row.date)] * length)
    origin.extend([str(row[0])] * length)

word_df = pd.DataFrame({"word": word, "date": date, "origin": origin})

word_df["type"] = "message"

comment = directory + "\comments"

files = []

# Get files that are .json
for x in os.listdir(comment):
    if ".json" in x:
        files.append(x)

df = pd.DataFrame()

comment_list = []
date_list = []

# Open files, convert to dataframe, and append to df
for file in files:
    with open(comment + "/" + file, "r") as f:
        data = json.load(f)

    for comment in data["comments"]:
        # The "data" attribute contains the actual comment
        # sometimes it's a pseudo comment without content which is why I'm testing for it
        if "data" in comment:
            comment_date = comment["data"][0]["comment"]["timestamp"]
            comment_comment = comment["data"][0]["comment"]["comment"]

            date_list.append(comment_date)
            comment_list.append(comment_comment)

comments = pd.DataFrame({"comment": comment_list, "date": date_list})

comments["date"] = pd.to_datetime(comments["date"], unit="s")

word = []
date = []
origin = []

for row in comments.itertuples():
    content = (
        str(row.comment)
        .replace(",", "")
        .replace(".", "")
        .replace("*", "")
        .replace("?", "")
        .replace("!", "")
    )
    words = content.split(" ")
    length = len(words)

    word.extend([word.lower() for word in words])
    date.extend([str(row.date)] * length)
    origin.extend([str(row[0])] * length)


word_df2 = pd.DataFrame({"word": word, "date": date, "origin": origin})

word_df2["type"] = "Comment"

# Append comments and messages together
word_df = word_df.append(word_df2)

# Split out date and time for easier analysis
word_df["date"] = pd.to_datetime(word_df["date"])
word_df["time"] = word_df["date"].dt.time
word_df["date"] = word_df["date"].dt.date

# Get rid of rows that are blank and reset index
word_df = word_df[word_df["word"] != ""].reset_index()

word_df.to_csv("word.csv")
