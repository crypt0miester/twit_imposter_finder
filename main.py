import bot as tib 
import db

credentials = {}

# couldn't get headless to work
headeless = ""
headeless_answer = ""

fetch_my_profile = "y"
test_mode_answer = "n"
print("======================")
print("twitter imposter finder")
print("======================")
print()
print("let us login")
print()
print("if you have 2FA enabled,")
print("you will be prompted for the 6 digit code")
print("upon request in this terminal. be ready.")
print()

credentials["username"] = input("username/email: ")
credentials['password'] = input("password: ")
report_reason = input("write down why are you reporting these scammer for Twitter: ")
fetch_my_profile = input("should we fetch your profile? (y/n) default y ")
test_mode_answer = input("testmode - prints data to csv file and won't report them: (y/n) default n ")
# couldn't get it to work headless
# headeless_answer = input("would you like to watch the bot perform? (y/n) default y ")

if headeless_answer == "y":
    headless = False
elif headeless_answer == "n":
    headless = True
else:
    headless = True

if test_mode_answer == "n":
    test_mode = False
elif test_mode_answer == "y":
    test_mode = True
else:
    test_mode = False

# initialize the bot with your credentials 
bot = tib.TwitterImposterbot(credentials['username'], credentials['password'], headeless, test_mode, report_reason) 
print()
print("alright logging in")
print()
bot.login() 
print()
print("logged in")

if fetch_my_profile == "y":
    bot.get_profile_name_image_and_bio()
elif fetch_my_profile == "n":
    pass
else:
    bot.get_profile_name_image_and_bio()
    
print()
bot.fetch_imposters()
if not test_mode:
    bot.screen_imposters()

