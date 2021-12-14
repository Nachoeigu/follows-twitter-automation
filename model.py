import tweepy
import requests
import json
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from dotenv import load_dotenv
import os 


class TelegramBot():

    #We put the credentials for logining in Telegram
    def __init__(self):
        self.token = os.getenv('telegram_token')
        self.chat_id = os.getenv('telegram_chat_id')

    #This method get a text as input and send the message to the channel of Telegram    
    def send_message(text):
        url_request = "https://api.telegram.org/bot"+ self.token + "/sendMessage" + "?chat_id=" + self.chat_id + "&text=" + text
        results = requests.get(url_request)

class TwitterBot(TelegramBot):

    #We put the credentials and stablish the conection with the Twitter API and Google API
    def __init__(self):
        load_dotenv()

        #Conection with Twitter API
        auth = tweepy.OAuthHandler(os.getenv('twitter_consumer_key'), os.getenv('twitter_consumer_secret'))
        auth.set_access_token(os.getenv('twitter_access_token'), os.getenv('twitter_access_token_secret'))
        self.api = tweepy.API(auth,wait_on_rate_limit = True)

        # Conection with Google API
        gc = gspread.service_account(filename = 'credentials.json') 
        #Before executing the Bot, we should have the Google spreadsheets where we will store the data. One sheet per figure.
        self.sh = gc.open_by_key(os.getenv('spreadsheet_id')) 

    #We analyze if these figures started following someone new
    def analyzing_figures(self, usernames:list):
        for index in range(0, len(usernames)):
            #For each iteration, we place the google cursor in the respective sheet of each figure
            worksheet = self.sh.get_worksheet(index) #0 = first sheet, 1 = second sheet, etc...

            #We extract the stored users_ids who each figure follows 
            values_list = worksheet.col_values(1)
            description = values_list[1:]

            #We obtain the current users_ids who each figure follows and store them in the accounts variable
            pagination = tweepy.Cursor(self.api.get_friend_ids, screen_name = usernames[index]).items()
            accounts = []
            for item in pagination:
                accounts.append(str(item))

            #We create a variable which it will be empty unless we find that the figure started following someone new
            variable = []

            #We iterate between the current users_ids the figure follows with the past users_ids the figure followed in the last execution
            for account in accounts:
                if account in description:
                # If the account is in the Google Spreadsheet, nothing happens
                    print('Nothing new')
                else:
                    #If the account is not in the Google Spreadsheet, this means that the figure started following it
                    #First, we convert the user_id to the user_name for readibility purposes
                    new_account = self.api.get_user(user_id = account)
                    new_account = new_account.screen_name

                    #Then we execute the alert, sending the user_name to the Telegram Channel
                    telegram = TelegramBot()
                    telegram.send_message(f'This account {new_account} is a new follow for {usernames[index]}') 
                    print(f'There is a new account that {usernames[index]} follows')

                    #Finally, we add a value in the variable so the Bot knows that it has to send the new dataframe to the Google spreadsheet 
                    variable.append(1)

            #If the figure started following someone new, we upload the dataframe in the spreadsheet with the latest update
            if len(variable) > 0:
                try:
                    df = pd.DataFrame({'follows':accounts}) 
                except:
                    df = pd.DataFrame({'follows':accounts}, index= [0])

                set_with_dataframe(worksheet, df)
            else:
                continue




            





    


