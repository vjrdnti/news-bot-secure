import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from portal.portal import aicte, mhtcet, iitd, hbcse, cbse, multiple, icai, buddy4study
import tweepy
import yaml

url_di_list = {'portal':['AICTE', 'MHTCET', 'IITD', 'HBCSE', 'CBSE', 'MULTIPLE', 'ICAI','buddy4study' 'add value'], 'twitter': ['@fff', '@aaaa']}
csv_file_path = './main.csv'
creds = yaml.load(open('./social_keys.yml'), Loader=yaml.FullLoader) #twitter keys

def send_tweet(row): 
    consumer_key = creds['twitter']['consumer_key']
    consumer_secret = creds['twitter']['consumer_secret']
    access_token  = creds['twitter']['access_token']
    access_secret = creds['twitter']['access_secret']    
    bearer_token = creds['twitter']['bearer_token']
    
    client = tweepy.Client(
        bearer_token=bearer_token,consumer_key = consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_secret)
    
    source_to_handle = {
        'AICTE': '@AICTE_INDIA',
        'MHTCET': '@CETCELL',
        'IITD': '@iitdelhi',
        'HBCSE': '@HBCSE_TIFR',
        'CBSE': '@cbseindia29',
        'ICAI': '@theicai',
        'Education Ministry': '@EduMinOfIndia',
        'nios': '',
        'NIEPA': '@NIEPA_Official',
        'buddy4study': '@Buddy4Study'
    }
    
    #hashtags = "#Education #Announcements #Students #Learning #HigherEducation #EdTech #Teaching #School #College #University #STEM #Scholarships #Academics #OnlineLearning #DistanceEducation"

    msgl = []
    source = row["source"]
    twitter_handle = source_to_handle.get(source, '')
    
    if twitter_handle:
        msgl.append(f'The following announcements were made on {source} portal ({twitter_handle}):')
    else:
        msgl.append(f'The following announcements were made on {source} portal:')
    
    msgl.append(f'{row["heading"]}:')
    msgl.append(f'{row["link"]}')
    
    if row['time'] != 'Not available':
        msgl.append(f'date: {row["time"]}')
    
    msgl.append('- Vidyarthi Mitra')
    #msgl.append(hashtags)
    msg = '\n'.join(msgl)
    print(msg)
    response = client.create_tweet(text = msg)

def append_new_rows_to_csv(df):
    csv_file_path = './main.csv'
    try:
        csv_df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        df.to_csv(csv_file_path, index=False)
        return
    combined_df = pd.concat([csv_df, df])
    combined_df = combined_df.drop_duplicates()
    combined_df.to_csv(csv_file_path, index=False)
    
def check_csv(dfl):
    df = pd.read_csv('./main.csv')
    difference = pd.merge(df, dfl, how='outer', indicator=True).loc[lambda x : x['_merge']=='left_only']
    difference = difference.drop(columns=['_merge'])
    return difference    
    
def send_email(row):
    try:
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = "example@gmail.com"
        login = "example@gmail.com"
        password = "uavj $$$$ $$$$ ghia"
        recipient_email = "vm-interns@googlegroups.com"
        #recipient_email = "44tripathi55@gmail.com"
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = str(row['heading'])
        message = "".join(["time: ", str(row['time']) ," source: ", str(row['source']), " link: ", str(row['link'])])
        msg.attach(MIMEText(message, 'plain'))
        
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(login, password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        #print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")

def driver_fn(url_di_list):
    check_fn(url_di_list['portal'], 'portal')
    check_fn(url_di_list['twitter'], 'twitter')
    
def check_fn(list1, list_type):
    df_l = pd.read_csv('./main.csv')
    if list_type=='portal':
        for i in range(0,len(list1)):
            if i==0:
                try:
                    df = aicte()
                    append_new_rows_to_csv(df)
                    print('aicte done')
                except:
                    print('aicte failed')
            elif i==1:
                try:
                    df = mhtcet()
                    append_new_rows_to_csv(df)
                    print('mhtcet done')
                except:
                    print('mhtcet failed')
            elif i==2:
                try:
                    df = iitd()
                    append_new_rows_to_csv(df)
                    print("iitd done")
                except:
                    print('hbcse failed')
            elif i==3:
                try:
                    df = hbcse()
                    append_new_rows_to_csv(df)
                    print('hbcse done')
                except:
                    print('hbcse failed')
            elif i==4:
                try:
                    df = cbse()
                    append_new_rows_to_csv(df)
                    print("cbse done")
                except:
                    print('cbse failed')
            elif i==5:
                try:
                    df = multiple()
                    append_new_rows_to_csv(df)
                    print("multiple done")
                except:
                    print('multiple failed')
            elif i==6:
                try:
                    df = icai()
                    append_new_rows_to_csv(df)
                    print('icai done')
                except:
                    print('icai failed')
            elif i==7:
                try:
                    df = buddy4study()
                    append_new_rows_to_csv(df)
                    print('b4s done')
                except:
                    print('b4s failed')
            new_df = check_csv(df_l)
            for i in range(0,new_df.shape[0]):
                send_email(new_df.iloc[i,:])
                try:
                    send_tweet(new_df.iloc[i,:])
                except Exception as e:
                    print(f'tweet failed error:{e}')
                print(new_df.iloc[i,:])
    elif list_type=='twitter':
        print()
    #check_csv(df_l)
    
if __name__ == '__main__':
    driver_fn(url_di_list)
