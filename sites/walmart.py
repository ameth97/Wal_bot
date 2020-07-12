from sites.walmart_encryption import walmart_encryption as w_e
from utils import  get_proxy, send_webhook, EventLogger
import urllib,requests,time,lxml.html,json,sys
import random
from colorama import Fore
import sys
from settings import get_settings

eventLogger = EventLogger()
class Walmart:
    def __init__(self,task_id,status_signal,image_signal,product,profile,proxy,monitor_delay,error_delay,max_price, flask=False, proxies=None,
    is_monitored=None, profile_name=None, monitor_group=None, run_task_group=None):
        self.task_id,self.status_signal,self.image_signal,self.product,self.profile,self.monitor_delay,self.error_delay,self.max_price,self.flask,\
             self.proxies, self.is_monitored, self.profile_name, self.monitor_group, self.run_task_group = (task_id,status_signal,image_signal,product,
                                    profile,float(monitor_delay),float(error_delay),max_price, flask, proxies, is_monitored, 
                                    profile_name, monitor_group, run_task_group)
        self.price = 0
        self.product_name = ""
        """
      Constructor of walmart class
      automatically load profiles and performs tasks when called
        """         
        self.session = requests.Session()
        if proxy != False:
            self.session.proxies.update(proxy) # add proxy to session
        if not self.flask: # I was trying to use flask to create api to upload directly csv this can be evolution
           self.status_signal.emit({"msg":"Starting","status":"normal"})
        else:
           time.sleep(random.random())
           eventLogger.normal(self.task_id, "Starting")
      
        # this are the requests send by walamart during the process of buying product it's just copy paste from console
        self.product_image, offer_id = self.monitor() #call the monitor product function if it's available the program continue
        self.atc(offer_id)  # add product to cart
        item_id, fulfillment_option, ship_method = self.check_cart_items() #load cart item
        self.submit_shipping_method(item_id, fulfillment_option, ship_method) # shipping method submit
        self.submit_shipping_address() # ssubmit shipping address
        card_data,PIE_key_id,PIE_phase = self.get_PIE() # get cart encryption details
        pi_hash = self.submit_payment(card_data,PIE_key_id,PIE_phase) # submit payment
        self.submit_billing(pi_hash) # submit billing infos
        self.submit_order() # put the order

    def monitor(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36"
        }
        image_found = False
        product_image = ""
        wait_restock = False
        while True:
            if not self.flask:
               self.status_signal.emit({"msg":"Loading Product Page","status":"normal"})
            else:
               eventLogger.normal(self.task_id, "Loading Product Page")
            try:
                r = self.session.get(self.product,headers=headers)
                if r.status_code == 200:
                    doc = lxml.html.fromstring(r.text)
                    self.product_name = doc.xpath('//h1[@itemprop="name"]/@content')[0]
                    if not image_found:
                        product_image = doc.xpath('//meta[@property="og:image"]/@content')[0]
                        if not self.flask:
                            self.image_signal.emit(product_image)
                        image_found = True
                    price = float(doc.xpath('//span[@itemprop="price"]/@content')[0])
                    self.price = price
                    if "add to cart" in r.text.lower():
                        if self.max_price !="":
                            if float(self.max_price) < price:
                                if not self.flask:
                                   self.status_signal.emit({"msg":"Waiting For Price Restock","status":"normal"})
                                else:
                                   eventLogger.alt(self.task_id, "Waiting For Price Restock")
                                if not self.is_monitored:
                                    eventLogger.alt(self.task_id, 'idle monitoring')
                                    sys.exit()
                                wait_restock = True
                                self.session.cookies.clear()
                                time.sleep(self.monitor_delay)
                                continue
                        offer_id = json.loads(doc.xpath('//script[@id="item"]/text()')[0])["item"]["product"]["buyBox"]["products"][0]["offerId"]
                        if(wait_restock):
                               self.run_task_group(self.profile_name, self.monitor_group)
                               exit()
                        return product_image, offer_id
                    if not self.flask:
                       self.status_signal.emit({"msg":"Waiting For Restock","status":"normal"})
                    else:
                        eventLogger.alt(self.task_id, "Waiting For Restock")
                    if not self.is_monitored:
                        eventLogger.alt(self.task_id, 'idle monitoring')
                        sys.exit()
                    wait_restock = True
                    self.session.cookies.clear()
                    time.sleep(self.monitor_delay)
                else:
                     if self.proxies:
                           self.session.proxies.update(get_proxy(self.proxies))
                     if not self.flask:
                        self.status_signal.emit({"msg":"Product Not Found","status":"normal"})
                     else:
                        eventLogger.error(self.task_id, "Product Not Found")
                     time.sleep(self.monitor_delay)
            except Exception as e:
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Loading Product Page (line {} {} {})".format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e),"status":"error"})
                else:
                   eventLogger.error(self.task_id, "Error Loading Product Page", e)
                time.sleep(self.error_delay)
    
    def atc(self,offer_id):
        headers={
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "content-type": "application/json",
            "origin": "https://www.walmart.com",
            "referer": self.product,
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36"
        }
        body = {"offerId":offer_id,"quantity":1}
        while True:
            if not self.flask:
               self.status_signal.emit({"msg":"Adding To Cart","status":"normal"})
            else:
               eventLogger.normal(self.task_id, "Adding To Cart")
            try:
                r = self.session.post("https://www.walmart.com/api/v3/cart/guest/:CID/items",json=body,headers=headers)
                if r.status_code == 201 and json.loads(r.text)["checkoutable"] == True:
                    if not self.flask:
                       self.status_signal.emit({"msg":"Added To Cart","status":"carted"})
                    else:
                       eventLogger.success(self.task_id, "Added To Cart")
                    return
                else:
                    if self.proxies:
                        self.session.proxies.update(get_proxy(self.proxies))
                    if not self.flask:
                       self.status_signal.emit({"msg":"Error Adding To Cart","status":"error"})
                    else:
                       eventLogger.error(self.task_id, "Error Adding To Cart")
                    time.sleep(self.error_delay) 
            except Exception as e:
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Adding To Cart (line {} {} {})".format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e),"status":"error"})
                else:
                   eventLogger.normal(self.task_id, "Error Adding To Cart (line {} {} {})")
                time.sleep(self.error_delay)

    def check_cart_items(self):
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "content-type": "application/json",
            "origin": "https://www.walmart.com",
            "referer": "https://www.walmart.com/checkout/",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36",
            "wm_vertical_id": "0"
        }
        profile = self.profile
        body = {"postalCode":profile["shipping_zipcode"],"city":profile["shipping_city"],"state":profile["shipping_state"],"isZipLocated":True,"crt:CRT":"","customerId:CID":"","customerType:type":"","affiliateInfo:com.wm.reflector":""}
        while True:
            if not self.flask:
               self.status_signal.emit({"msg":"Loading Cart Items","status":"normal"})
            else:
               eventLogger.normal(self.task_id, "Loading Cart Items")
            try:
                r = self.session.post("https://www.walmart.com/api/checkout/v3/contract?page=CHECKOUT_VIEW",json=body,headers=headers)
                if r.status_code == 201:
                    r = json.loads(r.text)["items"][0]
                    item_id = r["id"]
                    fulfillment_option = r["fulfillmentSelection"]["fulfillmentOption"]
                    ship_method = r["fulfillmentSelection"]["shipMethod"]
                    if not self.flask:
                       self.status_signal.emit({"msg":"Loaded Cart Items","status":"normal"})
                    else:
                       eventLogger.normal(self.task_id, "Loaded Cart Items")
                    return item_id, fulfillment_option, ship_method
                else:
                    if json.loads(r.text)["message"] == "Item is no longer in stock.":
                        if not self.flask:
                           self.status_signal.emit({"msg":"Waiting For Restock","status":"normal"})
                        else:
                           eventLogger.alt(self.task_id, "Waiting For Restock")
                        time.sleep(self.monitor_delay)
                    else:
                        if not self.flask:
                           self.status_signal.emit({"msg":"Error Loading Cart Items, Got Response: "+str(r.text),"status":"error"})
                        else:
                           eventLogger.error(self.task_id, "Error Loading Cart Items, Got Response: ")
                        time.sleep(self.error_delay) 
            except Exception as e:
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Loading Cart Items (line {} {} {})".format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e),"status":"error"})
                else:
                   eventLogger.normal(self.task_id, "Error Loading Cart Items (line {} {} {})")
                time.sleep(self.error_delay)

    def submit_shipping_method(self, item_id, fulfillment_option, ship_method):
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "content-type": "application/json",
            "origin": "https://www.walmart.com",
            "referer": "https://www.walmart.com/checkout/",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36",
            "wm_vertical_id": "0"
        }
        body = {"groups":[{"fulfillmentOption":fulfillment_option,"itemIds":[item_id],"shipMethod":ship_method}]}
        while True:
            if not self.flask:
               self.status_signal.emit({"msg":"Submitting Shipping Method","status":"normal"})
            else:
               eventLogger.normal(self.task_id, "Submitting Shipping Method")
            try:
                r = self.session.post("https://www.walmart.com/api/checkout/v3/contract/:PCID/fulfillment",json=body,headers=headers)
                if r.status_code == 200:
                    try:
                        r = json.loads(r.text)
                        if not self.flask:
                           self.status_signal.emit({"msg":"Submitted Shipping Method","status":"normal"})
                        else:
                           eventLogger.normal(self.task_id, "Submitted Shipping Method")
                        return
                    except:
                        pass
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Submitting Shipping Method","status":"error"})
                else:
                   eventLogger.error(self.task_id, "Error Submitting Shipping Method")
                time.sleep(self.error_delay)
            except Exception as e:
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Submitting Shipping Method (line {} {} {})".format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e),"status":"error"})
                else:
                   eventLogger.normal(self.task_id, "Error Submitting Shipping Method (line {} {} {})")
                time.sleep(self.error_delay)
    
    def submit_shipping_address(self):
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "content-type": "application/json",
            "inkiru_precedence": "false",
            "origin": "https://www.walmart.com",
            "referer": "https://www.walmart.com/checkout/",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36",
            "wm_vertical_id": "0"
        }
        profile = self.profile
        body = {
            "addressLineOne":profile["shipping_a1"],
            "city":profile["shipping_city"],
            "firstName":profile["shipping_fname"],
            "lastName":profile["shipping_lname"],
            "phone":profile["shipping_phone"],
            "email":profile["shipping_email"],
            "marketingEmailPref":False,
            "postalCode":profile["shipping_zipcode"],
            "state":profile["shipping_state"],
            "countryCode":"USA",
            "addressType":"RESIDENTIAL",
            "changedFields":[]
        }
        if profile["shipping_a2"] !="":
            body.update({"addressLineTwo":profile["shipping_a2"]})
        while True:
            if not self.flask:
               self.status_signal.emit({"msg":"Submitting Shipping Address","status":"normal"})
            else:
               eventLogger.normal(self.task_id, "Submitting Shipping Address")
            try:
                r = self.session.post("https://www.walmart.com/api/checkout/v3/contract/:PCID/shipping-address",json=body,headers=headers)
                if r.status_code == 200:
                    try:
                        r = json.loads(r.text)
                        if not self.flask:
                           self.status_signal.emit({"msg":"Submitted Shipping Address","status":"normal"})
                        else:
                           eventLogger.normal(self.task_id, "Submitted Shipping Address")
                        return
                    except:
                        pass
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Submitting Shipping Address","status":"error"})
                else:
                   eventLogger.error(self.task_id, "Error Submitting Shipping Address")
                time.sleep(self.error_delay)
            except Exception as e:
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Submitting Shipping Address (line {} {} {})".format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e),"status":"error"})
                else:
                   eventLogger.normal(self.task_id, "Error Submitting Shipping Address (line {} {} {})")
                time.sleep(self.error_delay)
    
    def get_PIE(self):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Connection": "keep-alive",
            "Host": "securedataweb.walmart.com",
            "Referer": "https://www.walmart.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36"
        }
        profile = self.profile
        while True:
            if not self.flask:
               self.status_signal.emit({"msg":"Getting Checkout Data","status":"normal"})
            else:
               eventLogger.normal(self.task_id, "Getting Checkout Data")
            try:
                r = self.session.get("https://securedataweb.walmart.com/pie/v1/wmcom_us_vtg_pie/getkey.js?bust="+str(int(time.time())),headers=headers)
                if r.status_code == 200:
                    PIE_L = int(r.text.split("PIE.L = ")[1].split(";")[0])
                    PIE_E = int(r.text.split("PIE.E = ")[1].split(";")[0])
                    PIE_K = str(r.text.split('PIE.K = "')[1].split('";')[0])
                    PIE_key_id = str(r.text.split('PIE.key_id = "')[1].split('";')[0])
                    PIE_phase = int(r.text.split('PIE.phase = ')[1].split(';')[0])
                    card_data = w_e.encrypt(profile["card_number"],profile["card_cvv"],PIE_L,PIE_E,PIE_K,PIE_key_id,PIE_phase)
                    if not self.flask:
                       self.status_signal.emit({"msg":"Got Checkout Data","status":"normal"})
                    else:
                       eventLogger.normal(self.task_id, "Got Checkout Data")
                    return card_data, PIE_key_id, PIE_phase
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Getting Checkout Data","status":"error"})
                else:
                   eventLogger.error(self.task_id, "Error Getting Checkout Data")
                time.sleep(self.error_delay)
            except Exception as e:
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Getting Checkout Data (line {} {} {})".format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e),"status":"error"})
                else:
                   eventLogger.normal(self.task_id, "Error Getting Checkout Data (line {} {} {})")
                time.sleep(self.error_delay)
    
    def submit_payment(self,card_data,PIE_key_id,PIE_phase):
        headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "content-type": "application/json",
            "authority":"www.walmart.com",
            "scheme":"https",
            "path":"/api/checkout-customer/:CID/credit-card",
            "accept":"application/json",
            "accept-language":"en-US,en;q=0.9,fr;q=0.8",
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "origin":"https://www.walmart.com",
            "sec-fetch-site":"same-origin",
            "sec-fetch-mode":"cors",
            "sec-fetch-dest":"empty",
            "referer":"https://www.walmart.com/checkout/",
            "accept-encoding":"gzip, deflate, br"
        
        }
        profile = self.profile
        body = {
            "encryptedPan": card_data[0],
            "encryptedCvv": card_data[1],
            "integrityCheck": card_data[2],
            "keyId": PIE_key_id,
            "phase": PIE_phase,
            "state": profile["billing_state"],
            "postalCode": profile["billing_zipcode"],
            "addressLineOne": profile["billing_a1"],
            "addressLineTwo": profile["billing_a2"],
            "city": profile["billing_city"],
            "firstName": profile["billing_fname"],
            "lastName": profile["billing_lname"],
            "expiryMonth": profile["card_month"],
            "expiryYear": profile["card_year"],
            "phone": profile["billing_phone"],
            "cardType": profile["card_type"].upper(),
            "isGuest":True
        }
        while True:
            if not self.flask:
               self.status_signal.emit({"msg":"Submitting Payment","status":"normal"})
            else:
               eventLogger.normal(self.task_id, "Submitting Payment")
            try:
                r = self.session.post("https://www.walmart.com/api/checkout-customer/:CID/credit-card",json=body,headers=headers)
                if r.status_code == 200:
                    pi_hash = json.loads(r.text)["piHash"]
                    if not self.flask:
                       self.status_signal.emit({"msg":"Submitted Payment","status":"normal"})
                    else:
                       eventLogger.normal(self.task_id, "Submitted Payment")
                    return pi_hash
                if self.proxies:
                        self.session.proxies.update(get_proxy(self.proxies))
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Submitting Payment","status":"error"})
                else:
                   eventLogger.error(self.task_id, "Error Submitting Payment")
                if self.check_browser():
                    return
                time.sleep(self.error_delay)
            except Exception as e:
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Submitting Payment (line {} {} {})".format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e),"status":"error"})
                else:
                   eventLogger.normal(self.task_id, "Error Submitting Payment (line {} {} {})")
                time.sleep(self.error_delay)

    def submit_billing(self,pi_hash):
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "content-type": "application/json",
            "inkiru_precedence": "false",
            "origin": "https://www.walmart.com",
            "referer": "https://www.walmart.com/checkout/",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36",
            "wm_vertical_id": "0"
        }
        profile = self.profile
        card_data,PIE_key_id,PIE_phase = self.get_PIE()
        body = {
            "payments":[{
                "paymentType":"CREDITCARD",
                "cardType": profile["card_type"].upper(),
                "firstName": profile["billing_fname"],
                "lastName": profile["billing_lname"],
                "addressLineOne": profile["billing_a1"],
                "addressLineTwo": profile["billing_a2"],
                "city": profile["billing_city"],
                "state": profile["billing_state"],
                "postalCode": profile["billing_zipcode"],
                "expiryMonth": profile["card_month"],
                "expiryYear": profile["card_year"],
                "email": profile["billing_email"],
                "phone": profile["billing_phone"],
                "encryptedPan": card_data[0],
                "encryptedCvv": card_data[1],
                "integrityCheck": card_data[2],
                "keyId": PIE_key_id,
                "phase": PIE_phase,
                "piHash": pi_hash
            }]
        }
        while True:
            if not self.flask:
               self.status_signal.emit({"msg":"Submitting Billing","status":"normal"})
            else:
               eventLogger.normal(self.task_id, "Submitting Billing")
            try:
                r = self.session.post("https://www.walmart.com/api/checkout/v3/contract/:PCID/payment",json=body,headers=headers)
                if r.status_code == 200:
                    try:
                        r  = json.loads(r.text)
                        if not self.flask:
                           self.status_signal.emit({"msg":"Submitted Billing","status":"normal"})
                        else:
                           eventLogger.normal(self.task_id, "Submitted Billing")
                        return
                    except:
                        pass
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Submitting Billing","status":"error"})
                else:
                   eventLogger.error(self.task_id, "Error Submitting Billing")
                if self.check_browser():
                    return
                time.sleep(self.error_delay)
            except Exception as e:
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Submitting Billing (line {} {} {})".format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e),"status":"error"})
                else:
                   eventLogger.normal(self.task_id, "Error Submitting Billing (line {} {} {})")
                time.sleep(self.error_delay)
    
    def submit_order(self):
        headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "content-type": "application/json",
            "authority":"www.walmart.com",
            "scheme":"https",
            "path":"/api/checkout/v3/contract/:PCID/order",
            "accept":"application/json",
            "accept-language":"en-US,en;q=0.9,fr;q=0.8",
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "origin":"https://www.walmart.com",
            "sec-fetch-site":"same-origin",
            "sec-fetch-mode":"cors",
            "sec-fetch-dest":"empty",
            "referer":"https://www.walmart.com/checkout/",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36",
            "wm_vertical_id": "0"
        }
        settings = get_settings()
        on_order, on_failed = settings['webhook_on_order'],settings['webhook_on_failed']
        while True:
            if not self.flask:
               self.status_signal.emit({"msg":"Submitting Order","status":"alt"})
            else:
               eventLogger.alt(self.task_id, "Submitting Order")
            try:
                r = self.session.put("https://www.walmart.com/api/checkout/v3/contract/:PCID/order",json={},headers=headers)
                try:
                    json.loads(r.text)["order"]
                    if not self.flask:
                       self.status_signal.emit({"msg":"Order Placed","status":"success"})
                    else:
                       eventLogger.success(self.task_id, "Order Placed")

                       try:
                          f = open("success.txt", 'at')
                          f.write("task {} succeeded!\n".format('self.task_id'))
                       except:
                          eventLogger.error(self.task_id, 'error logging success task')
                       finally:
                          f.close()
                    if (on_order):
                     send_webhook("OP","Walmart",self.profile["profile_name"],self.task_id,self.product_image,
                     self.price, self.profile["billing_email"], self.product_name)
                    return
                except:
                    if not self.flask:
                       self.status_signal.emit({"msg":"Payment Failed","status":"error"})
                    else:
                       eventLogger.error(self.task_id, "Payment Failed")

                    if self.check_browser():
                        return
                    if (on_failed):
                      send_webhook("PF","Walmart",self.profile["profile_name"],self.task_id,self.product_image,
                    self.price, self.profile["billing_email"], self.product_name)
                    return
            except Exception as e:
                if not self.flask:
                   self.status_signal.emit({"msg":"Error Submitting Order (line {} {} {})".format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e),"status":"error"})
                else:
                   eventLogger.error(self.task_id, str({"msg":"Error Submitting Order (line {} {} {})".format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e),"status":"error"}))
                time.sleep(self.error_delay)
    
    def check_browser(self):
      #   if settings.browser_on_failed:
      #       if not self.flask:
      #          self.status_signal.emit({"msg":"Browser Ready","status":"alt","url":"https://www.walmart.com/checkout/#/payment","cookies":[{"name":cookie.name,"value":cookie.value,"domain":cookie.domain} for cookie in self.session.cookies]})
      #       else:
      #           pass
      #       #    eventLogger.normal(self.task_id, "Browser Ready")
      #       # #send_webhook("B","Walmart",self.profile["profile_name"],self.task_id,self.product_image)
      #       return True
        return False