# Written by Hugo Woesthuis (C0der)



import time 
import json
import logging
import cli

from selenium import webdriver
from seleniumrequests import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from browsermobproxy import Server


class Magister:
    def __init__(self, url, username=None, password=None, *, verbose=False):
        self.bearer = None
        # enable browser logging
        d = DesiredCapabilities.CHROME
        d['loggingPrefs'] = { 'browser':'ALL' }

        self.server = Server("BrowserMob\\bin\\browsermob-proxy")
        logging.info("Starting proxy server...")

        self.server.start()
        self.proxy = self.server.create_proxy()

        logging.info("Proxy Server has started!")
        logging.warning("NOTE: Connections will show as INSECURE!\n")
        
        options = webdriver.ChromeOptions()
        self.url = url
        options.add_argument("--proxy-server={0}".format(self.proxy.proxy))

        logging.info("Browser started\n")
        self.browser = Chrome(options = options, executable_path = "./chromedriver.exe", desired_capabilities=d)
        self.username = username
        self.password = password
        del password
        del username
        
    def destroy_creds(self):
        self.password = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        self.username = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        del self.password
        del self.username  
        
    def dispose(self):
        self.browser.quit()
        self.server.stop()
        self.destroy_creds()

    def login(self):
        browser = self.browser
        browser.get(self.url)
        time.sleep(5)

        self.proxy.new_har("LoginFlow")

        if self.username != None:
            logging.info("Attempting logon\n")
            
            try:
                
                un = browser.find_element_by_id("username")
            


                un.clear()
                un.send_keys(self.username)
                un.send_keys(Keys.ENTER)
                time.sleep(0.5)
                pd = browser.find_element_by_id("password")

                pd.clear()
                pd.send_keys(self.password)
            
                bt = browser.find_element_by_id("password_submit")
                bt.click()
            except exceptions.NoSuchElementException:
                logging.critical("Login Failed: Elements not found!\n")
                return False
        else:
            wait = WebDriverWait(browser, 30, poll_frequency=1)
            wait.until(EC.element_to_be_clickable((By.ID, 'password_submit')))
            wait.until(EC.visibility_of_element_located((By.ID, "menu-activiteiten")))


        time.sleep(5)

        # Test if we're actually logged in
        try:
            test = browser.find_element_by_id("menu-activiteiten")
            logging.info("Login OK!\n")
            
            del test
            self.destroy_creds()
            return True
        except exceptions.NoSuchElementException:
            logging.critical("Login Failed: Menu not found\n")
            return False
    
    def get_bearer(self):
        logging.info("Trying to get Authorization bearer from HAR...\n")
        try: 
            data = self.proxy.har
            for d in data['log']['entries']:
                if('response' in d):
                    l = d['response']['redirectURL'].find("access_token=")
                    if l != -1:
                        logging.info("Autorization bearer obtained!\n")
                        e = d['response']['redirectURL'].find("&token_type")
                        self.bearer = d['response']['redirectURL'][l+13:e]
                        return True
        except Exception as e:
            logging.debug(e)
            
        logging.error("Could not obtain Authorization bearer!\n")
        return False


    # Heheh MiTM JS 
    def inject_test(self):
        logging.info("Testing JS Injection...")
        self.browser.execute_script('console.log("INJECT OK!");')
        # print messages
        for entry in self.browser.get_log('browser'):
            if entry['level'] == 'INFO':
                if 'INJECT OK!' in entry['message']:
                    logging.info('Injection success!')
                    return True
        
        
    def GET(self, url):
        logging.info("Injecting JS for GET request\n")
        js = f"""
$.ajax({{ 
   type : "GET", 
   url : "{url}", 
   beforeSend: function(xhr){{xhr.setRequestHeader('Authorization', 'Bearer {self.bearer}');}},
   success : function(result) {{ 
       console.log("CALLBACK-GET: " + JSON.stringify(result));
   }}, 
   error : function(result) {{ 
       console.log("CALLBACKE-GET: " + JSON.stringify(result));
   }} 
 }}); """
        self.browser.execute_script(js)
        time.sleep(0.75)
        # print messages
        for entry in self.browser.get_log('browser'):
            if entry['level'] == 'INFO':
                e = entry['message'].find("CALLBACKE")
                i = entry['message'].find("CALLBACK")
                if(e != -1):
                    logging.critical(f"ERROR: {entry['message']}\n")
                    self.browser.execute_script("console.clear();")
                    return False
                elif(i != -1):
                    #logging.info(f"OK: {entry['message']}\n")
                    e = entry['message']
                    # Reformat voor die dingejes
                    s1 = 34
                    s2 = 34
                    try:
                        s1 = e.index('{')
                    except ValueError:
                        pass
                    try:
                        s2 = e.index('[')
                    except ValueError:
                        pass
                    
                    s = None
                    if s1 < s2:
                        s = s1 
                    else:
                        s = s2
                    self.browser.execute_script("console.clear();")
                    return e[s:len(e)-1].replace("\\\"", "\"")

                else:
                    logging.error("NO FEEDBACK GIVEN\n")
                    self.browser.execute_script("console.clear();")
                    return None
    
    # Inject a script!
    def POST(self, url, data):
        logging.info("Injecting JS for POST request\n")
        js = f"""
$.ajax({{ 
   type : "POST", 
   url : "{url}", 
   data: "{data}",
   beforeSend: function(xhr){{xhr.setRequestHeader('Authorization', 'Bearer {self.bearer}');}},
   success : function(result) {{ 
       console.log("CALLBACK-POST: " + JSON.stringify(result));
   }}, 
   error : function(result) {{ 
       console.log("CALLBACKE-POST: " + JSON.stringify(result));
   }} 
 }}); """
        self.browser.execute_script(js)
        time.sleep(0.2)
        # print messages
        for entry in self.browser.get_log('browser'):
            if entry['level'] == 'INFO':
                e = entry['message'].find("CALLBACKE")
                i = entry['message'].find("CALLBACK")
                if(e != -1):
                    logging.critical(f"ERROR: {entry['message']}\n")
                    return False
                elif(i != -1):
                    logging.info(f"OK: {entry['message']}\n")
                    return True
                else:
                    logging.error("WARNING: NO FEEDBACK GIVEN\n")
                    return False
        return False

    
 





