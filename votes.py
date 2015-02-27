#Test Commit
#This script parses data from openparliament.ca and return a CSV file that shows how each MP's voting record in a parliament session
#Created by Stephen Fung
#January 2014

import json
import time
import pandas as pd
import urllib.request

class Bill:
    def __init__(self, bill_number, name_en, name_fr, sponsor, last_vote, last_vote_ballot, intro_date, legisinfo_id, status, description):
        #Bill Number
        self.bill_number = bill_number
        #Bill Names
        self.name_en = name_en
        self.name_fr = name_fr
        #Bill Sponsor
        self.sponsor = sponsor
        #Bill final vote url
        self.last_vote = last_vote
        #The ballot of the final vote (How each MP voted)
        self.last_vote_ballot = last_vote_ballot
        #Bill Introduction Date
        self.intro_date = intro_date
        #Bill legistative ID
        self.legisinfo_id = legisinfo_id
        #Final status of the Bill
        self.status = status
        #Description of the Bill
        self.description = description


#Input:
#session is the parliament session(Example: '41-1'). It is a string
#limit is the number of bills to output. It is an integer
#Output: List of Bill Objects

def get_bills_from_session(session, limit):

    url = 'http://api.openparliament.ca/bills/'
    data = {}
    data['session'] = session
    data['format'] = 'json'
    data['limit'] = limit
    counter = 0

    url_values = urllib.parse.urlencode(data)
    #print(url_values)
    full_url = url + '?' + url_values
    response = urllib.request.urlopen(full_url)
    json_object = json.loads(response.read().decode('utf8'))

    #Here we have a list of all the bills in a particular parliamentary session.
    bills_info_brief = json_object['objects']
    list_of_bills = []

    #Using the bill number with the API to turn each bill into a bill object
    for i in bills_info_brief:

        print(i['number'])

        url = 'http://api.openparliament.ca/bills/'
        data = {}
        data['format'] = 'json'

        url_values = urllib.parse.urlencode(data)
        full_url = url + session + '/' + i['number'] + '/' + '?' + url_values
        response = urllib.request.urlopen(full_url)
        bill_json = json.loads(response.read().decode('utf8'))
        counter = counter + 1

        #Some bills don't have any vote record
        if not bill_json['vote_urls']:
            bill = Bill(bill_json['number'], bill_json['short_title']['en'], bill_json['short_title']['fr'], bill_json['sponsor_politician_url'], '', '',bill_json['introduced'], bill_json['legisinfo_id'], bill_json['status']['en'], bill_json['name']['en'])
            #print(bill.name_en)
            #print(bill.last_vote)
            #print(counter)
        else:
            bill = Bill(bill_json['number'], bill_json['short_title']['en'], bill_json['short_title']['fr'], bill_json['sponsor_politician_url'], bill_json['vote_urls'][0], '', bill_json['introduced'], bill_json['legisinfo_id'], bill_json['status']['en'], bill_json['name']['en'])

            #print(bill.name_en)
            #print(bill.last_vote)
            #print(counter)

            #Using the API to find out how each MP voted
            url = 'http://api.openparliament.ca/votes/ballots/'
            parameters = {}
            parameters['vote'] = bill.last_vote
            parameters['format'] = 'json'
            parameters['limit'] = 400
            url_values = urllib.parse.urlencode(parameters)
            full_url = url + '?' + url_values

            response = urllib.request.urlopen(full_url)
            json_object = json.loads(response.read().decode('utf8'))

            ballot_info_brief = json_object['objects']

            ballot_dict = {}

            for i in ballot_info_brief:
                #print(i)
                politician_url = i['politician_url']
                politician_name = politician_url.split('/')[2]
                politician_name_with_space = politician_name.replace('-',' ')
                politician_name_final = politician_name_with_space.title()
                ballot_dict[politician_name_final] = i['ballot']


            bill.last_vote_ballot = ballot_dict
            print(bill.last_vote_ballot)

        #input('Press Enter to continue')

        list_of_bills.append(bill)
        time.sleep(5)

    return list_of_bills

#Input: list of bill objects
#Output: CSV file

def export_vote_results(list_of_bills):

    bill_numbers = []
    en_names = []
    sponsors = []
    votes = []
    status = []
    descriptions = []

    for i in list_of_bills:

        #Sponsor name can be null
        if not i.sponsor:
            sponsor_name_final = ' '
        else:
            #Reformat Spsonsor's names
            sponsor_url = i.sponsor
            sponsor_name = sponsor_url.split('/')[2]
            sponsor_name_with_space = sponsor_name.replace('-',' ')
            sponsor_name_final = sponsor_name_with_space.title()

        #Voting record can be empty for a bill
        if not i.last_vote_ballot:
            votes.append({})
        else:
            votes.append(i.last_vote_ballot)

        bill_numbers.append(i.bill_number)
        en_names.append(i.name_en)
        sponsors.append(sponsor_name_final)
        status.append(i.status)
        descriptions.append(i.description)

    data_frame = pd.DataFrame(votes, index=bill_numbers)

    data_frame.insert(0, 'Names (EN)', en_names)
    data_frame.insert(1, 'Description (EN)', descriptions)
    data_frame.insert(2, 'Bill Sponsor', sponsors)
    data_frame.insert(3, 'Status', status)

    data_frame.to_csv('J:/41-1.csv')

if __name__ == "__main__":

    lobs = get_bills_from_session('41-1', 1000)

    export_vote_results(lobs)
