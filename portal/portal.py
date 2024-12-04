import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin 
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def aicte():
    url = 'https://aicte-india.org/bulletins/annoucement'

    # Send a request to the website
    response = requests.get(url)

    # Parse the page content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all headlines, dates, and links
    headlines = soup.find_all(class_='views-field views-field-title')
    dates = soup.find_all(class_='views-field views-field-field-date')
    links = soup.find_all(class_='views-field views-field-field-file-name-url')

    # Data to be written to CSV
    data = []

    # Iterate over headlines, dates, and links, and create a row for each
    for headline, date, link in zip(headlines, dates, links):
        headline_text = headline.get_text(strip=True)
        date_text = date.get_text(strip=True)
        link_tag = link.find('a')
        link_url = link_tag['href'] if link_tag else 'No link available'
        row = {
            'heading': headline_text,
            'link': link_url,
            'time': date_text,
            'source': 'AICTE'
        }
        data.append(row)

    df = pd.DataFrame(data)
    return df

def mhtcet():
    url = 'https://cetcell.mahacet.org/notices/'

    # Send a request to the website
    response = requests.get(url)

    # Parse the page content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all headlines, dates, and links
    headlines = []
    table_html = soup.find('div', {'id': 'elementor-tab-content-1001'})
    df = pd.read_html(str(table_html.find('table')))
    df = df[0]
    rows = table_html.find_all('tr')
    rows = rows[1:]
    links = []
    for row in rows:
        if row.find('a'):
            links.append(str(row.find('a')['href']))
        else:
            links.append('No link available')    
    df = df.iloc[0:5,:]
    headings = []
    for i in range(0,5):
        headings.append(" ".join(["Department:",str(df['Course Name'][i]), "Subject:", str(df['Subject'][i])]))
    df['heading'] = headings
    df['link'] = links[0:5]
    df['time'] = df['Published Date']
    df['source'] = 'MahaCET'
    df = df.drop(columns=['Download', 'Sr.No', 'Course Name', 'Subject', 'Published Date'])
    df 
    return df

def iitd():
    base_url = 'https://home.iitd.ac.in/'
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    container = soup.find('div', class_='container pb-40 ar-container-pad')
    announcements = container.find_all('h3', class_='kk-bold mt-0 text-theme-colored2')

    data = []
    for announcement in announcements:
        link = announcement.find('a')
        text = link.text.strip()
        href = link['href']
        if not href.startswith('http'):
            href = base_url + href
        row = {'heading':text,'link':href, 'time':'Not available', 'source': 'IIT-DELHI'}
        data.append(row)

    return pd.DataFrame(data)

def hbcse():
    url = 'https://olympiads.hbcse.tifr.res.in/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    headlines = soup.find_all(class_='title')
    links = soup.find_all(class_='listing-item')

    data = []
    for headline, link in zip(headlines, links):
        headline_text = headline.get_text(strip=True)
        link_tag = link.find('a')
        link_url = link_tag['href'] if link_tag else 'No link available'
        data.append({'heading': headline_text, 'link': link_url, 'time': 'Not available', 'source': 'HBCSE Olympiads'})

    return pd.DataFrame(data)

def cbse():
    base_url = "https://www.cbse.gov.in/cbsenew/"
    url = urljoin(base_url, "cbse.html")
    response = requests.get(url)

    data = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        latest_updates_section = soup.find('ul', class_='list')

        if latest_updates_section:
            li_tags = latest_updates_section.find_all('li', class_='list-new')
            for li_tag in li_tags[:5]:
                title = li_tag.get_text().strip()
                time = title[-10:]
                a_tag = li_tag.find('a')
                link = urljoin(base_url, a_tag.get('href')) if a_tag else None
                data.append({'heading': title, 'link': link, 'time': time, 'source': 'CBSE'})

    return pd.DataFrame(data)

def fetch_and_print(url, class_name=None, notification_class=None, website_name=None, date_class=None):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
           
            if notification_class:
                Notification = soup.find('div', class_=notification_class)
                a_tags = Notification.find_all('a') if Notification else None
            elif class_name:
                a_tags = soup.find_all('a', class_=class_name)
            else:
                a_tags = None
           
            if a_tags:
                data = []
                for a_tag in a_tags[:7]:
                    href = urljoin(url, a_tag['href'])
                    text = a_tag.get_text(strip=True)
                    date_text = 'Not available'
                    if date_class:
                        date_tag = a_tag.find_previous_sibling('span', class_=date_class)
                        date_text = date_tag.get_text(strip=True) if date_tag else 'No date available'
                    else:
                        if website_name=='NIOS':
                            if 'dt.' in text:
                                date_text = text[24:35]
                            else:
                                date_text = 'Not available'
    
                        if website_name=='Education Ministry':
                            date_pattern = re.compile(r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\d{2}-[A-Za-z]+-\d{4}\b')
                            # Find the date in the text
                            match = date_pattern.search(text)
    
                            if match:
                                extracted_date = match.group()
                                date_text = extracted_date
                       
                    row = {'heading': text, 'link': href, 'time': date_text, 'source': website_name}
                    data.append(row)
                df = pd.DataFrame(data)
                return df
            else:
                print(f"{website_name}: No relevant tags found.\n")
                return pd.DataFrame()
        else:
            print(f"{website_name}: Failed to retrieve the webpage. Status code: {response.status_code}\n")
            return pd.DataFrame()
    except:
        return pd.DataFrame()

def multiple():
    websites = [
        {'url': 'https://www.education.gov.in/#main-content', 'class_name': 'pdfIcon', 'website_name': 'Education Ministry'},
        {'url': 'https://nios.ac.in/#pause', 'notification_class': 'scrollingtext', 'website_name': 'NIOS'},
        {'url': 'https://niepa.ac.in/', 'notification_class': 'popup-imp', 'website_name': 'NIEPA'},
        #{'url': 'https://jeemain.nta.nic.in/#1648447930282-deb48cc0-95ec', 'notification_class': 'gen-list', 'website_name': 'JEE Main NTA'},
        ]

    all_data = []
    for site in websites:
        df = fetch_and_print(**site)
        if not df.empty:
            all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)

def icai():
    url = "https://www.icai.org/category/notifications"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        data = []
        latest_updates_section = soup.find('ul', class_='list-group')
        if latest_updates_section:
            li_tags = latest_updates_section.find_all('li', class_='list-group-item')
            for i,li_tag in enumerate(li_tags[:10]):
                title = li_tag.get_text().strip()
                a_tag = li_tag.find('a')
                if a_tag:
                    link =  a_tag.get('href')
                else:
                    link = None
                time = title[-12:]
                time = time[1:-1]
                data.append({'heading': title, 'link': link, 'time': time, 'source': 'ICAI'})
            df = pd.DataFrame(data)
            return df
def buddy4study():
    url = 'https://www.buddy4study.com/'
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    data= []
    d = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div/ul/li[3]/div/div[1]/div')))
    #d = driver.find_element(By.XPATH, f'/html/body/div/div[2]/div/div/ul/li[3]/div/div[1]/div')
    for a in d.find_elements(By.TAG_NAME, 'a'):
        data.append({'heading': a.get_property('innerText').strip(),'link': a.get_attribute('href'),'time': 'Not available', 'source': 'buddy4study'}) 
    df = pd.DataFrame(data)
    return df
