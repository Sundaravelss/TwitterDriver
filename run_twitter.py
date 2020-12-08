from twitterCrawler.myClass import TwitterDriver

p=TwitterDriver()

p.get_browser(usr="svelselvaraj",pwd="sundaravel")

print('\n============Testing Twitter===================\n')

print(p.get_user_info(user_id="TheSandboxGame"))

print(p.get_comment_by_key("merde",1,2,csv_parser=False))