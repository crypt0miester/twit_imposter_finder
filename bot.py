from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
import time, os
from PIL import Image
import imagehash
from db import session, Me, Imposter
import sys
from sqlalchemy.sql import exists
import re

class TwitterImposterbot:
    def __init__(self, username, password, headless, test_mode, report_reason):
        """Constructor

        Arguments:
                username {string} -- registered twitter username
                password {string} -- password for the twitter account
                headless {boolean} -- use gui or not
                test_mode {boolean} -- prints the file into csv file and don't report
                report_reason {string} -- reason of reporting for Twitter Inc.
        """

        self.username = username
        self.password = password
        self.test_mode = test_mode
        self.headless = headless
        self.report_reason = report_reason
        
        # initializing chrome options
        chrome_options = Options()
        
        # doesn't work
        if self.headless:
            # runs the chrome driver without GUI
            chrome_options.add_argument('--headless')
            
        # adding the path to the chrome driver and
        # integrating chrome_options with the bot
        self.bot = webdriver.Chrome(
            executable_path=os.path.join(os.getcwd(), "chromedriver"),
            options=chrome_options,
        )

    def login(self):
        """
        method for signing in the user
        with the provided username and password.
        """

        bot = self.bot
        # fetches the login page
        bot.get("https://twitter.com/login")
        # adjust the sleep time according to your internet speed
        time.sleep(3)

        username = bot.find_element_by_xpath(
            '//*[@id="react-root"]/div/div/div[2]/main/div/div/div[2]/form/div/div[1]/label/div/div[2]/div/input'
        )
        password = bot.find_element_by_xpath(
            '//*[@id="react-root"]/div/div/div[2]/main/div/div/div[2]/form/div/div[2]/label/div/div[2]/div/input'
        )

        # sends the username to the username input
        username.send_keys(self.username)
        # sends the password to the password input
        password.send_keys(self.password)
        # executes RETURN key action
        password.send_keys(Keys.RETURN)

        time.sleep(2)
        
        # wrong username or password exit
        if "https://twitter.com/login/error?username_or_email" in bot.current_url:
            print('===== Error Raised =====') 
            print("exiting") 
            sys.exit("reason: invalid username or password") 
        
        # 2fa needed to continue
        if "https://twitter.com/account/login_verification?" in bot.current_url:   
            print('===== 2FA needed - please click here =====')  
            totp_code = input("2FA code: (123456) ")
            self.verify_totp(totp_code)
            

    def verify_totp(self, totp_code):
        """
        Some users have two factor authentication setup. this helps with that step.

        Arguments:
                totp {object} -- Time-based One-time Password (TOTP) 
        """
        bot = self.bot

        totp_path = bot.find_element_by_xpath('//*[@id="challenge_response"]')
        totp_path.send_keys(totp_code)
        
        totp_path.send_keys(Keys.RETURN)

        time.sleep(2)
        
        # wrong totp or expired
        # retry
        if "https://twitter.com/account/login_verification?" in bot.current_url:   
            print('===== 2FA wrong or expired - let us try again - please click here =====')  
            totp_code = input("2FA code: (123456) ")
            self.verify_totp(totp_code)
        
    def get_profile_name_image_and_bio(self):
        """
        function to store user image and bio to be compared to later. 
        Note: you may want to delete the db if you updated your profile image or profile name
        """
        print()  
        print('===== fetching your data =====')  
        
        bot = self.bot
        bot.get(f"https://twitter.com/{self.username}/photo") 
        time.sleep(2)
        
        # fetching profile image
        img = bot.find_element_by_xpath('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/img')
        src = img.get_attribute('src')
        # download the image
        urllib.request.urlretrieve(src, "user_photo.png")
        img_hash = str(imagehash.average_hash(Image.open('user_photo.png')))
        
        bot.get(f"https://twitter.com/{self.username}") 
        
        time.sleep(2)
        # fetching profile name
        profile_name = bot.find_element_by_xpath("/html/body/div/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[2]/div/div/div[1]") 
        print(f"your profile name: {profile_name.text}")
        
        # fetching profile bio
        profile_bio = bot.find_element_by_xpath("/html/body/div/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/div/div[1]/div/div[3]/div/div")
        # couldn't remove instances where \n (newline) exists
        # profile_bio = profile_bio.text.replace(r'\n', '')
        profile_bio = profile_bio.text
        print(f"your profile bio: {profile_bio}")
        
        # saving to db for future references
        me = Me(username=self.username, bio=profile_bio, image_hash=img_hash,
                profile_name=profile_name.text)
        session.add(me)
        session.commit()
        
        print()
        print('fetched your profile data and saved into db')
        time.sleep(2)
    
    def parse_style_bg_image(self, style_string):
        if 'background-image' in style_string:
            style_string = style_string.split(' url("')[1].replace('");', '')
            return style_string
        return None
    
    def fetch_imposters(self):
        """
        function that fetchs the list of imposters and save the values to the database.
        this almost 100 line of code took about 3 days and countless coffees and cigarettes, please tread carefully.
        
        """
        print()  
        print('===== searching for imposters =====')  
        profile_names = []
        profile_usernames = []
        profile_images_hash = []
        
        bot = self.bot
        bot.get("https://twitter.com/home")
        time.sleep(2)
        
        
        # search for similair usernames
        search_path = bot.find_element_by_xpath('/html/body/div/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[1]/div/div/div[2]/input')
        search_path.send_keys(self.username)
        search_path.send_keys(Keys.RETURN)
        
        # go to peoples page because that is where to find imposters
        time.sleep(2)
        people_path = bot.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[2]/nav/div/div[2]/div/div[3]/a/div/span')
        people_path.click()    
        time.sleep(2)
                
        # pick from only a portion of the screen instead of the whole screen
        parent_element = bot.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]')

        while 1:
            # executing javascript code
            # get current height, presumably it is at the beginning 
            current_height = bot.execute_script("return document.documentElement.scrollHeight")
            
            # using list comprehension
            # for adding all the tweets link to the list
            # this particular piece of code might
            # look very complicated but the only reason
            # I opted for list comprehension because is
            # lot faster than traditional loops 
            [
                # fetch the profile name that may be identical to the original user
                profile_names.append(elem.text)
                for elem in parent_element.find_elements_by_xpath(".//*[@class='css-901oao css-bfa6kz r-18jsvk2 r-1qd0xha r-a023e6 r-b88u0q r-ad9z0x r-bcqeeo r-3s2u2q r-qvutc0']")
            ]
            
            [
                # fetch the link of username
                # we will remove the https://twitter.com/ string later on from href
                profile_usernames.append(elem.get_attribute("href"))
                for elem in parent_element.find_elements_by_xpath('.//a[@class="css-4rbku5 css-18t94o4 css-1dbjc4n r-1loqt21 r-1wbh5a2 r-dnmrzs r-1ny4l3l"]') 
            ]
            
            [   
                # fetch profile_image that are similair to the original user
                # maybe there is a different method of doing this
                # but the script currently uses Imagehash by JohannesBuchner's average hashing method
                # which is able to recognize images easily and store it in low bytes in the db
                # Original Source - https://github.com/JohannesBuchner/imagehash
                
                profile_images_hash.append(imagehash.average_hash(Image.open(urllib.request.urlopen(self.parse_style_bg_image(elem.get_attribute('style'))))))
                # the commented version below shows the image url instead of the image_hash
                # profile_images_hash.append(self.parse_style_bg_image(elem.get_attribute('style')))
                for elem in parent_element.find_elements_by_xpath(".//div[@class ='css-1dbjc4n r-1niwhzg r-vvn4in r-u6sd8q r-4gszlv r-1p0dtai r-1pi2tsx r-1d2f490 r-u8s1d r-zchlnj r-ipm5af r-13qz1uu r-1wyyakw']") 
            ] 
            
            # scroll to the bottom of the page
            bot.execute_script("window.scrollTo(0, document.body.scrollHeight)")

            # sleep because loading takes time. 
            time.sleep(4)
            
            # take new height after scrolling
            new_height = bot.execute_script("return document.documentElement.scrollHeight")
            
            # at the end of the page it will not scroll again so if the new height
            # is similair to the current height then we break.
            if current_height == new_height:
                break
        
        # check to avoid duplicates
        def record_exists(session, username):
            return session.query(exists().where(Imposter.username == username)).scalar()
        
        if self.test_mode:
            with open('twitter-imposters.csv', 'w+') as f:
                f.write("profile_name,username,image_hash\n")
                for profile_name, profile_username, profile_image_hash in zip(profile_names, profile_usernames, profile_images_hash):
                    profile_name = profile_name.rstrip('\u3164')
                    f.write(f"{profile_name.strip()},{profile_username[20:]},{profile_image_hash}\n")
            print("done writing to file")
        else:        
            # bulk insert to db for future entry
            for profile_name, profile_username, profile_image_hash in zip(profile_names, profile_usernames, profile_images_hash):
                # testing to see what it fetches
                # print(f"{profile_name}, {profile_username}, {profile_image_hash}\n")
                
                # add to db for now
                # let's not put ourselves in the Imposter db
                if profile_username[20:].lower() != self.username.lower():
                    if not record_exists(session, profile_username[20:]):
                        session.add(Imposter(
                                username=profile_username[20:],
                                profile_name=profile_name.strip(),
                                image_hash=str(profile_image_hash)
                            ))
                        session.flush()
            session.commit()
        print("done fetching")
        
    def screen_imposters(self):
        """
        function that screens scammers by checking their profile name and image
        if they are equal to original user, they get reported and blocked.
        """        
        print()  
        print('===== screening imposters =====')  
        me = session.query(Me).first()

        query = session.query(Imposter).filter_by(reported=False, profile_name=me.profile_name).all()

        if query:
            # get individual imposters
            for imposter in query:
                print(f"found a possible match for {imposter.username} with the name {imposter.profile_name}")
                # if matches imposters use similar profile pictures to original user
                if imposter.image_hash == me.image_hash:
                    print("definitely an imposter")
                    try: 
                        print("reporting")
                        # let us reporting him
                        self.report_scammer(imposter.username)
                    except Exception as e:
                        # print what's actually wrong
                        print(e) 
                        # we try again next time the script is run
                        print("something is wrong with this lad")
                        print("perhaps a false positive?")
                        # cool off
                        time.sleep(5)
                # cool off
                time.sleep(2)
        else:
            print()  
            print('===== exiting =====')  
            print("no imposters found")
    
    def waiting_driver(self, driver, by_variable, attribute):
        """
        function that waites for some variables to be viewable
        """    
        try:
            WebDriverWait(driver, 20).until(lambda x: x.find_element(by=by_variable,  value=attribute))
        except (NoSuchElementException, TimeoutException):
            print(f'{by_variable} {attribute} not found')
        
    def report_scammer(self, username):
        """
        function that does the blocking and reporting
        """    
        
        bot = self.bot
        
        bot.get(f"https://twitter.com/{username}/photo")
        time.sleep(2)
        
        me = session.query(Me).first()
        
        # we need to make sure we got the write scammer sometimes shit happens.
        profile_img_xpath = bot.find_element_by_xpath('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/img')
        profile_img_src = profile_img_xpath.get_attribute('src')
        # open the image
        profile_img_opened = Image.open(urllib.request.urlopen(profile_img_src))
        img_hash = str(imagehash.average_hash(profile_img_opened))
        
        # screen for false positives
        if img_hash != me.image_hash:
            # exit function if image hash are not the same
            return 
        
        bot.get(f"https://twitter.com/{username}") 
        
        time.sleep(2)
        
        # refresh again since the bot seems to be logged out, sometimes.
        try:
            bot.find_element_by_css_selector(
                '.css-18t94o4[data-testid ="userActions"]'
            ).click()
        except:
            bot.refresh()
            time.sleep(2)
            bot.find_element_by_css_selector(
                '.css-18t94o4[data-testid ="userActions"]'
            ).click()
            
        time.sleep(1)
        
        report_xpath = bot.find_element_by_xpath('//*[@id="layers"]/div[2]/div/div/div/div[2]/div[3]/div/div/div/div[4]/div[2]/div/span')
        report_xpath.click()
        
        time.sleep(3)
        
        # waiting for iframe
        self.waiting_driver(bot, 'tag name', 'iframe')
        iframe = bot.find_element_by_tag_name('iframe')
        bot.switch_to.frame(iframe)
        time.sleep(2)
        
        bot.find_element_by_id('impersonation-start-btn').click()
        self.waiting_driver(bot, 'id', 'me-btn')
        bot.find_element_by_id('me-btn').click()
        
        time.sleep(2)
        
        
        textarea_path = bot.find_element_by_xpath('/html/body/div/div/form/textarea')
        
        # you can reason for reporting here to be a customed to you
        # and comment the self.report_reason
        # reason_for_reporting = "This person is impersonating me and scamming other people"
        reason_for_reporting = self.report_reason
        
        # sends the reason for reporting
        textarea_path.send_keys(reason_for_reporting)
        
        # submit report
        bot.find_element_by_class_name('submit-btn').click()
        
        # blocks the username
        self.waiting_driver(bot, 'id', 'block-btn')
        bot.find_element_by_id('block-btn').click()
        
        # we are done, cool off
        time.sleep(2)
        
        # cant find the X or Done button but the reporting has been done.
        # so we go fo the next one
        # bot.find_elements_by_css_selector('.css-18t94o4.css-1dbjc4n.r-urgr8i.r-42olwf.r-sdzlij.r-1phboty.r-rs99b7.r-1w2pmg.r-1vsu8ta.r-aj3cln.r-1ny4l3l.r-1fneopy.r-o7ynqc.r-6416eg.r-lrvibr')
        
        # let's update the db 
        imposter_reported = session.query(Imposter).filter_by(username=username).first()
        imposter_reported.reported = True
        session.commit()
        print(f"reported {username}")