from myClass import *

@click.command()
@click.option('--url', default='', help='url of the user')
@click.option('--n', default=1, help='number of posts')
@click.option('--s', default=False, help='Download data')
@click.option('--usr', default="", help="your Twitter login")
@click.option('--pwd', default="", help='password')

def main(url,n,s,usr,pwd):
    
    p = TwitterDriver()
    p.get_browser(usr,pwd)
    #p.get_user_info(url)
    #p.get_publications(url,n)
    
    dic=p.user_info
    print(dic)
    dic1={"posts":p.posts}
    dic.update(dic1)
    save_data(dic,dic["name"],r"C:\Users\Hamza\Desktop\Twitter_Crawler\Twitter_Crawler\datalll\.")


        
if __name__=='__main__':
    main()
