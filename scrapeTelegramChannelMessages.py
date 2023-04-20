from telethon import TelegramClient, events, sync
import pandas as pd
import asyncio
import os
from dotenv import load_dotenv
load_dotenv() 
import datetime
from tqdm import tqdm 
import argparse
import time


# To run this code. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.

TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID") #add your own api_id, we load this from .env file
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH") #add your own api_hash, we load this from .env file

def validate_file(f): #function to check if file exists
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return f

async def callAPI(input_file_path, output_folder_path):
    """
    This function takes an input file, output folder path
    It reads the input file, extracts the chats and then uses the TelegramClient to scrape message.text and message.date from each chat.
    Appending the chat's URL, message text, and message datetime to different lists.
    Then it creates a dataframe from the lists and saves the dataframe to a CSV file in the specified output folder.
    
    :input_file_path: .txt file containing the list of chats to scrape, each line should represent one chat
    :output_folder_path: folder path where the output CSV file will be saved containing the scraped data
    """
    with open(input_file_path) as file:
        chats = file.readlines()
        chats = [chat.replace('\n','') for chat in chats if not chat.startswith("#")]
    chatHttps = []
    messageText = []
    messageDatetime = []
    for chat in tqdm(chats):
        print('scrapping chat:', chat)
        async with TelegramClient('SessionName', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
            chat_short=chat.split('/')[-1]
            async for message in client.iter_messages(chat):
                chatHttps.append(chat)
                messageText.append(message.text)
                messageDatetime.append(message.date)
    df = pd.DataFrame({'chat':chatHttps, 
                       'messageDatetime':messageDatetime, 
                       'messageText':messageText})
    df.to_csv(f'{output_folder_path}', index=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', help="Specify the input file", type=validate_file, required=True)
    parser.add_argument('-o', '--output_folder', help="Specify location of output folder", required=True)
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(callAPI(args.input_file, args.output_folder))
    loop.close()

if __name__ == '__main__':
    main()