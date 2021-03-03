# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import recomendation_system as rs
import mysql.connector as db


#####################################################################

mydb = db.connect(host='localhost',
                    user='root',
                    passwd='1234',
                    database='customers_data',
                    auth_plugin='mysql_native_password')

mycursor = mydb.cursor(buffered=True)

data = {}
# print(mycursor.execute('show databases'))
#####################################################################

# class ActionHelloWorld(Action):

#     def name(self) -> Text:
#         return "action_hello_world"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(text="Hello World!")

#         return []

class Asking_Restaurants(Action):

    def name(self) -> Text:
        return "ask_resto"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entites = tracker.latest_message['entities']
        query = 'select * from recommendation where Name = "{0}"'.format(entites[0]['value'])
        # print('query',query)
        mycursor.execute(query)
        db_data = mycursor.fetchall()
        # print('data  ',data)

        # print('data',data[1],type(data[1]))
        if len(db_data)!=0:
            respo = ' '.join(i for i in rs.recommend(db_data[0][1]))

        else:
            data['Name'] = entites[0]['value']
            rs_list = rs.restaurants_reco()
            respo = 'we are recommending for you top 5 rated Restaurants "\n"1, {0}"\n"2, {1}"\n"3, {2}"\n"4, {3}"\n"5, {4} '.format(rs_list[0],rs_list[1],rs_list[2],rs_list[3],rs_list[4])


        dispatcher.utter_message(text= respo)
        return []

class ItemSelection(Action):

    def name(self) -> Text:
        return "item_selection"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entites = tracker.latest_message['entities']
        # print('entites',entites)
        resto_name = entites[0]['value']
        respo = rs.cuisine_recommendation(resto_name)
        data['Restaurants'] = resto_name
        dispatcher.utter_message(text=respo)

        return []

class ItemSave(Action):

    def name(self) -> Text:
        return "item_save"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entites = tracker.latest_message['entities']
        print('entites',entites)
        try:
            resto_name = entites[0]['value']
            respo = rs.cuisine_recommendation(resto_name)
            print('respo',respo)
        except:
            data['Items'] = resto_name
        dispatcher.utter_message(text='Enter your location')

        return []

class OrderLocation(Action):

    def name(self) -> Text:
        return "order_location"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entites = tracker.latest_message['entities']
        print(entites)
        response = 'tell me the proper location'
        print('check',entites[0]['value'].lower())
        data['Items'] = entites[0]['value'].lower()
        # for place in entites:
            # response = 'are you in {0} ?'.format(place['value'])
        # if entites[0]['value'].lower() in ["madhapur","kphb","kukatpally housing board colony", "kukatpally", "panjagutta", "sr nagar", "hitech", "ameerpet"]:
        response =  'Enter the mobile to sent OTP'
        
        # else:
        #     response =  'Sorry, you are out of our service.'
        
        dispatcher.utter_message(text= response)
        return []

class OrderOtp(Action):

    def name(self) -> Text:
        return "sending_otp"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entites = tracker.latest_message['entities']
        # print('entites',entites)
        # response = 'tell me the proper location'
        # # for place in entites:
        #     # response = 'are you in {0} ?'.format(place['value'])
        # if entites['value'].lower() in ["madhapur","kphb","kukatpally housing board colony", "kukatpally", "panjagutta", "sr nagar", "hitech", "ameerpet"]:
        #     response =  'Enter the mobile to sent OTP'
        
        # else:
        #     response =  'Sorry, you are out of our service.'
        respo = None
        if len(entites[0]['value'])==10:
            respo = "Sent OTP to {0} number. '\n'enter otp and OKAY.".format(entites[0]['value'])
        else:
            respo = "Please enter proper mobile number."
        dispatcher.utter_message(text= respo)
        return []

class OrderOtp(Action):

    def name(self) -> Text:
        return "save_in_db"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entites = tracker.latest_message['entities']
        # print('database',data,tuple(data.keys()),tuple(data.values()))
        dispatcher.utter_message(text= 'Your order has been placed successfully. You will recive a call from delivery boy shortly. Thank you :)')
        return []








