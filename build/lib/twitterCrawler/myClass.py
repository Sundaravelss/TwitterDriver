import time
import pathlib 
import json
import click
import urllib.request
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from abc import ABC
import pandas as pd
import os
from .functions import *
from bs4 import BeautifulSoup as soup
import requests
import re


class Driver(ABC):

    def get_user_info(self,driver,url):
        pass
    
    def get_publications(self,user_id,nb_tweets,nb_comments,scroll,comments):
        pass
    
    def get_comment_by_publication(self,publication_id,n,scroll):
        pass
    
    def get_comment_by_key(self,key,n,scroll):
        pass
    
    def get_comment_by_keys(self,keys,n,scroll):
        pass
    
    def get_images(self,user_id,scroll,nb_images):
        pass

    def get_followers(self,user_id,scroll):
        pass

    def get_following(self,user_id,scroll):
        pass

class TwitterDriver(Driver):
    def __init__(self,driver=''):
        self.driver=driver
        """Constructeur de notre classe"""
        pass
    def get_browser(self,usr,pwd):
        options = webdriver.firefox.options.Options()
        home=os.path.expanduser("~")
        options.headless = True
        #self.driver = webdriver.Firefox(executable_path=r"C:\Users\sundar\Downloads\geckodriver.exe", options=options)
        self.driver = webdriver.Firefox(executable_path=home+r"/geckodriver",options=options)
        self.driver.set_window_position(0, 0) #NOTE: 0,0 might fail on some systems
        self.driver.maximize_window()
        self.driver.get("https://twitter.com/login")
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-1j3t67a r-1w50u8q']")))
        email = self.driver.find_element_by_name('session[username_or_email]')
        email.send_keys(usr)
        password = self.driver.find_element_by_name('session[password]')
        password.send_keys(pwd)
        password.send_keys(Keys.ENTER)
   
        
    def get_user_info(self,user_id):
        """function that takes the user id and return info about it"""
        self.driver.get("https://twitter.com/"+str(user_id))
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-901oao r-hkyrab r-1qd0xha r-1b6yd1w r-1vr29t4 r-ad9z0x r-bcqeeo r-qvutc0']")))
        #c=self.driver.find_element_by_xpath(".//div[@class='css-1dbjc4n r-1habvwh']").text
        name=self.driver.find_element_by_xpath(".//div[@class='css-901oao r-hkyrab r-1qd0xha r-1b6yd1w r-1vr29t4 r-ad9z0x r-bcqeeo r-qvutc0']").text
        nb_tweets=self.driver.find_element_by_xpath(".//div[@class='css-901oao css-bfa6kz r-1re7ezh r-1qd0xha r-n6v787 r-16dba41 r-1sf4r6n r-bcqeeo r-qvutc0']").text
        UserDescription=self.driver.find_element_by_xpath(".//div[@data-testid='UserDescription']").text
        date=self.driver.find_element_by_xpath(".//div[@data-testid='UserProfileHeader_Items']").text
        following=self.driver.find_element_by_xpath(f".//a[@href='/{user_id}/following']").text
        followers=self.driver.find_element_by_xpath(f".//a[@href='/{user_id}/followers']").text
        img=self.driver.find_elements_by_xpath(".//img[@class='css-9pa8cd']")[1].get_attribute("src")
        dic={
            "name":name,
            "nb_tweets":nb_tweets,
            "user_description":UserDescription,
            "date":date,
            "following":following,
            "followers":followers,
            "image":img
            }
        self.user_info=dic
        return(dic)

    def get_publication(self,user_id,nb_tweets,nb_comments,scroll,comments):
        
        self.driver.get("https://twitter.com/"+str(user_id))
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-18u37iz r-1wtj0ep r-156q2ks r-1mdbhws']")))
        result=[]
        urls=[]
        li=[]
        for i in range(scroll):
            time.sleep(4)
            #list of publication
            c=self.driver.find_elements_by_xpath(".//article[@class ='css-1dbjc4n r-1loqt21 r-18u37iz r-1ny4l3l r-o7ynqc r-6416eg']")
            links = self.driver.find_elements_by_xpath("//a[@href]")
            for link in links:
                if 'status' in link.get_attribute("href") and 'photo' not in link.get_attribute("href"):
                    li.append(link.get_attribute("href"))
            urls+=li

            try:
                self.driver.execute_script("arguments[0].scrollIntoView();",c[len(c)-1])
            except:
                pass
        urls=list(set(urls))[:nb_tweets]
        #print(urls)
        for e in urls:
            m=self.get_all_data_by_publication(e,nb_comments,scroll,comments)
            #print(m)
            result.append(m)    
        return(result)
    
    def get_post(self,driver):
        """function that takes the id of a twitter post and return data about that post"""
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH,".//a[@class='css-4rbku5 css-18t94o4 css-901oao css-16my406 r-1re7ezh r-1loqt21 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0']")))
        try:
            contenu1=self.driver.find_element_by_xpath(".//div[contains(@class ,'css-901oao r-hkyrab r-1k78y06 r-1blvdjr r-16dba41')]").text
        except:
            contenu1=self.driver.find_element_by_xpath(".//div[contains(@class ,'css-901oao r-hkyrab r-1qd0xha r-1blvdjr r-16dba41')]").text
        try:
            image=self.driver.find_element_by_xpath(".//img[@alt='Image']").get_attribute("src")
            image=self.driver.find_element_by_xpath(".//div/img[@class='css-9pa8cd']").get_attribute("src")
        except:
            image=""
        date=self.driver.find_element_by_xpath(".//a[@class='css-4rbku5 css-18t94o4 css-901oao css-16my406 r-1re7ezh r-1loqt21 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0']").text
        try:
            retweets=self.driver.find_element_by_xpath(".//a[contains(@href ,'/retweets')]").text
            #getting digits alone
            retweets=re.findall('\d+', retweets )[0]
            retweets=0 if retweets=='' else retweets
        except:
            retweets=0
        try:
            likes=self.driver.find_element_by_xpath(".//a[contains(@href ,'/likes')]").text
            likes=re.findall('\d+', likes )[0]
            likes=0 if likes=='' else likes
        except:
            likes=0
        i=0
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Show more replies')]"))).click()
        except:
            pass
        dic={
                "contenu":contenu1,
                "image":image,
                "date":date,
                "Retweets":retweets,
                "likes":likes,
            }
        return(dic)
    
    def get_all_data_by_publication(self,publication_id,n,scroll,comments):
        """function that takes the id of a twitter post and gets to the publication page and returns user,comment,date of the publication"""
        self.driver.get(str(publication_id))
        li=[]
        
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//article[@class ='css-1dbjc4n r-18u37iz r-1ny4l3l']")))
        post_data=self.get_post(driver=self.driver)
        result_dic={"post_data":post_data}
        if comments=="T":
            result=self.get_comment_by_publication(publication_id,n,scroll)
            result_dic["post_data"]["comments"]=result
        return(result_dic)
    
    def get_comment_by_publication(self,publication_id,n,scroll):
        self.driver.get(str(publication_id))
        li=[]
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//article[@class ='css-1dbjc4n r-18u37iz r-1ny4l3l']")))
        for i in range(scroll):
            time.sleep(1)
            try:
                self.driver.find_element_by_xpath(".//div[@class ='css-18t94o4 css-1dbjc4n r-1777fci r-1jayybb r-1ny4l3l r-o7ynqc r-6416eg r-13qz1uu']").click()
            except:
                pass
            try:
                self.driver.find_element_by_xpath(".//div[@class ='css-18t94o4 css-1dbjc4n r-1ny4l3l r-1j3t67a r-atwnbb r-o7ynqc r-6416eg']").click()  
            except:
                pass
            a=self.driver.find_elements_by_xpath(".//article[contains(@class ,'css-1dbjc4n r-1loqt21')]")
            for e in a:
                try:
                    user=e.find_element_by_xpath(".//a[contains(@class ,'css-4rbku5 css-18t94o4 css-1dbjc4n r-1loqt21')]").text
                except:
                    user=''
                try:
                    comment=e.find_element_by_xpath(".//div[@class ='css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0']").text
                except:
                    comment=''
                try:
                    date=e.find_element_by_xpath(".//a[contains(@class ,'r-1re7ezh r-1loqt21')]").get_attribute("title")
                except:
                    date=''
                try:
                    likes=e.find_element_by_xpath(".//div[contains(@data-testid ,'like')]").text
                    likes=0 if likes=='' else likes
                except:
                    likes=0
                try:
                    number_of_replies=e.find_element_by_xpath(".//div[contains(@data-testid ,'reply')]").text
                    number_of_replies=0 if number_of_replies=='' else number_of_replies
                except:
                    number_of_replies=0
                try:
                    comment_url=e.find_element_by_xpath(".//a[contains(@class ,'r-1re7ezh r-1loqt21 r-1q142lx r-1qd0xha r-a023e6 r-16dba41')]").get_attribute('href')
                except:
                    comment_url=""
                dic={"user":user,"comment":comment,"date":date,"likes":likes,"number_of_replies":number_of_replies,'comment_url':comment_url}
                li.append(dic)
            try:
                self.driver.execute_script("arguments[0].scrollIntoView();",a[len(a)-1])
            except:
                pass
        result=list({v['user']:v for v in li}.values())
        #getting replies from comment_url
        for index,comment in enumerate(result):
            if comment['number_of_replies']!=0:
                replies=self.get_reply(comment['comment_url'],comment['number_of_replies'])
                result[index]['replies']=replies
        return(result[:n])
    
    def get_reply(self,comment_url,number_of_replies):
        '''function to get reply to comments'''
        self.driver.get(str(comment_url))
        li=[]
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//article[contains(@class ,'css-1dbjc4n r-1loqt21')]")))
        #minimum 2 scrolls to atleast click show more replies
        scroll=(int(number_of_replies)//10)+2
        for i in range(scroll):
            time.sleep(1)
            #comment container box excluding first publication container for first view
            if i==0:
                a=self.driver.find_elements_by_xpath(".//article[contains(@class ,'css-1dbjc4n r-1loqt21')]")[1:]
            else:
                a=self.driver.find_elements_by_xpath(".//article[contains(@class ,'css-1dbjc4n r-1loqt21')]")
            for e in a:
                try:
                    user=e.find_element_by_xpath(".//a[contains(@class ,'css-4rbku5 css-18t94o4 css-1dbjc4n r-1loqt21')]").text
                except:
                    user=''
                try:
                    reply=e.find_element_by_xpath(".//div[@class ='css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0']").text
                except:
                    reply=''
                try:
                    date=e.find_element_by_xpath(".//a[contains(@class ,'r-1re7ezh r-1loqt21 r-1q142lx r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-3s2u2q r-qvutc0 css-4rbku5 css-18t94o4 css-901oao')]").get_attribute("title")
                except:
                    date=''
                try:
                    likes=e.find_element_by_xpath(".//div[contains(@data-testid ,'like')]").text
                    likes=0 if likes=='' else likes
                except:
                    likes=0
                try:
                    number_of_replies=e.find_element_by_xpath(".//div[contains(@data-testid ,'reply')]").text
                    number_of_replies=0 if number_of_replies=='' else number_of_replies
                except:
                    number_of_replies=0
                try:
                    reply_url=e.find_element_by_xpath(".//a[contains(@class ,'r-1re7ezh r-1loqt21 r-1q142lx r-1qd0xha r-a023e6 r-16dba41')]").get_attribute('href')
                except:
                    reply_url=""
                dic={"user":user,"reply":reply,"date":date,"likes":likes,"number_of_replies":number_of_replies,'reply_url':reply_url}
                li.append(dic)
            try:
                self.driver.execute_script("arguments[0].scrollIntoView();",a[len(a)-1])
            except:
                pass
            #show more replies
            try:
                self.driver.find_element_by_xpath(".//div[@class ='css-18t94o4 css-1dbjc4n r-1777fci r-1jayybb r-1ny4l3l r-o7ynqc r-6416eg r-13qz1uu']").click()
            except:
                pass
        return(li)

    def get_comment_by_key(self,key,n,scroll,csv_parser=False):
        self.driver.get("https://twitter.com/search?q="+str(key)+"&src=typed_query&f=live")
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//div[@class ='css-1dbjc4n r-14lw9ot']")))
        li=[]
        for i in range(scroll):
            time.sleep(2)
            #list of comments
            c=self.driver.find_elements_by_xpath(".//article[@class ='css-1dbjc4n r-1loqt21 r-18u37iz r-1ny4l3l r-o7ynqc r-6416eg']")
            #print(c)
            for e in c:
                try:
                    WebDriverWait(e, 8).until(EC.visibility_of_element_located((By.XPATH, ".//div[@class ='css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0']")))
                    #wait until finding text element
                    user=e.find_element_by_xpath(".//a[@class ='css-4rbku5 css-18t94o4 css-1dbjc4n r-1loqt21 r-1wbh5a2 r-dnmrzs r-1ny4l3l']").text
                    user=user.replace('\n',':')
                    #print(user)
                    comment=e.find_element_by_xpath(".//div[@class ='css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0']").text
                    comment=comment.replace('\n','')
                    date=e.find_element_by_xpath(".//a[@class ='r-1re7ezh r-1loqt21 r-1q142lx r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-3s2u2q r-qvutc0 css-4rbku5 css-18t94o4 css-901oao']").get_attribute("title")
                    dic={"user":user,"comment":comment,"date":date}
                    #print(dic)
                    li.append(dic)
                except:
                    continue
            try:
                self.driver.execute_script("arguments[0].scrollIntoView();",c[len(c)-1])
            except:
                pass
        
        result=list({v['user']:v for v in li}.values())
        
        if(csv_parser==True):
            df=pd.DataFrame(result)
            if(os.path.exists(f"./{key}.xlsx")):         # If an old dataset exists, we concatenate it with the new data.
                old_data = pd.read_excel(f"./{key}.xlsx")
                full_data = pd.concat([old_data, df], axis=0)				
                full_data.drop_duplicates(inplace=True)		
                full_data.reset_index(drop=True, inplace=True)
                full_data.to_excel(f"./{key}.xlsx", index=True,index_label='id')   
            else:
                df.to_excel(f"./{key}.xlsx",index=True,index_label='id')
        return(result[:n])
        
    def get_comment_by_keys(self,keys,n,scroll,csv_parser=False):
        result=[]
        for word in keys: 
            li=self.get_comment_by_key(str(word),n,scroll,csv_parser)
            dic={str(word):li}
            result.append(dic)
        return(result)
    def get_followers(self,user_id,scroll):
        self.driver.get("https://twitter.com/"+str(user_id)+"/followers")
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//div[@data-testid='UserCell']")))
        
        users=[]
        for i in range(scroll):
            time.sleep(1)
            c=self.driver.find_elements_by_xpath(".//div[@class ='css-18t94o4 css-1dbjc4n r-1ny4l3l r-1j3t67a r-1w50u8q r-o7ynqc r-6416eg']")
            for e in c:
                user=e.find_element_by_xpath(".//div[@class ='css-1dbjc4n r-18u37iz r-1wbh5a2']").text
                users.append(user)
            try:
                self.driver.execute_script("arguments[0].scrollIntoView();",c[len(c)-1])
            except:
                pass
            
        return(list(set(users)))
    def get_following(self,user_id,scroll):
        self.driver.get("https://twitter.com/"+str(user_id)+"/following")
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//div[@data-testid='UserCell']")))
        
        users=[]
        for i in range(scroll):
            time.sleep(2)
            #list of following
            c=self.driver.find_elements_by_xpath(".//div[@class ='css-18t94o4 css-1dbjc4n r-1ny4l3l r-1j3t67a r-1w50u8q r-o7ynqc r-6416eg']")
            for e in c:
                user=e.find_element_by_xpath(".//div[@class ='css-1dbjc4n r-18u37iz r-1wbh5a2']").text
                users.append(user)
            try:
                self.driver.execute_script("arguments[0].scrollIntoView();",c[len(c)-1])
            except:
                pass
            
        return(list(set(users)))
    def get_images(self,user_id,scroll,nb_images):
        self.driver.get("https://twitter.com/"+str(user_id))
        try:
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-18u37iz r-1wtj0ep r-156q2ks r-1mdbhws']")))
            urls=[]
            li=[]
            for i in range(scroll):
                time.sleep(2)
                #list of tweets
                c=self.driver.find_elements_by_xpath(".//article[@class ='css-1dbjc4n r-1loqt21 r-18u37iz r-1ny4l3l r-o7ynqc r-6416eg']")
                links = self.driver.find_elements_by_xpath("//a[@href]")
                for link in links:
                    if 'status' in link.get_attribute("href") and 'photo' in link.get_attribute("href") and user_id in link.get_attribute("href"):
                        li.append(link.get_attribute("href"))
                urls+=li
                self.driver.execute_script("arguments[0].scrollIntoView();",c[len(c)-1])
        
            urls=list(set(urls))
            #print(urls)
            #remove multiple urls for same status
            urls=[url for url in urls if 'photo/1' in url]
            img_urls=[]
            for url in urls:
                self.driver.get(url)
                try:
                    WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-9x6qib r-1ylenci r-1phboty r-rs99b7 r-156q2ks r-1ny4l3l r-1udh08x r-o7ynqc r-6416eg']")))
                    html=self.driver.find_element_by_xpath(".//div[@class ='css-1dbjc4n r-9x6qib r-1ylenci r-1phboty r-rs99b7 r-156q2ks r-1ny4l3l r-1udh08x r-o7ynqc r-6416eg']").get_attribute('innerHTML')
                except:
                    continue
                txt=soup(html,'html.parser')
                #get all img tags
                images=txt.findAll('img')
                for image in images:
                    src=image['src']
                    #to add large to the url to get hd images
                    if 'small' in src:
                        img_urls.append(src[:-5]+"large")
                    elif 'medium' in src:
                        img_urls.append(src[:-6]+"large")
                    elif 'large' in src:
                        img_urls.append(src)
                    else:
                        img_urls.append(src[:-7]+"large")
            #create image directory if not exists and img_urls list is not empty
            if not os.path.exists(f'./images/{user_id}') and img_urls:
                try:
                    os.mkdir(f'./images/{user_id}')
                except OSError:
                    print ("Creation of the directory failed")
            #download image
            for i,img_url in enumerate(img_urls):
                img_content=requests.get(img_url).content
                file=open(f'./images/{user_id}/image{i+1}.jpg','wb')
                file.write(img_content)
                
            print('Image Downloaded')
            return(img_urls[:nb_images])
        except:
            pass
        
    def get_profile_pic(self,user_id):
        try:
            self.driver.get("https://twitter.com/"+str(user_id)+"/photo")
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-sdzlij r-1p0dtai r-1mlwlqe r-1d2f490 r-dnmrzs r-1udh08x r-u8s1d r-zchlnj r-ipm5af r-417010']")))
            profile_pic_url=self.driver.find_element_by_xpath(".//div[@class ='css-1dbjc4n r-sdzlij r-1p0dtai r-1mlwlqe r-1d2f490 r-dnmrzs r-1udh08x r-u8s1d r-zchlnj r-ipm5af r-417010']/img").get_attribute("src")   
            #cover_pic
            self.driver.get("https://twitter.com/"+str(user_id)+"/header_photo")
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='css-1dbjc4n r-1p0dtai r-1mlwlqe r-1d2f490 r-ywje51 r-dnmrzs r-1udh08x r-u8s1d r-zchlnj r-ipm5af r-417010']")))
            cover_pic_url=self.driver.find_element_by_xpath(".//div[@class ='css-1dbjc4n r-1p0dtai r-1mlwlqe r-1d2f490 r-ywje51 r-dnmrzs r-1udh08x r-u8s1d r-zchlnj r-ipm5af r-417010']/img").get_attribute("src")   
            #download
            print(f"profile_pic_url={profile_pic_url} \ncover_pic_url={cover_pic_url}")
            if os.path.exists(f'./images/{user_id}'):
                img_content1=requests.get(profile_pic_url).content
                file1=open(f'./images/{user_id}/profile_pic.jpg','wb')
                file1.write(img_content1)
                img_content2=requests.get(cover_pic_url).content
                file2=open(f'./images/{user_id}/cover_pic.jpg','wb')
                file2.write(img_content2)
                print("\nimage downloaded")
        except:
            pass
        
            
            
        
    
            
       
