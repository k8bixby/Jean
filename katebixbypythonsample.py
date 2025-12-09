# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 19:05:35 2023

@author: kate.bixby
"""

import pandas as pd
import glob
from datetime import date

pd.set_option('display.max_rows', None)

# change to current data dump
data_dump = 'DD06.30.2023'

today = date.today().strftime("%m.%d.%Y")

# date function
def make_date(column):
    column = pd.to_datetime(column).dt.date
    return column

def get_data(data_dump):
    # change to current axs data folder
    folder_name = 'some_folder_on_this_computer' + data_dump

    # initialize empty frame
    raw_data = pd.DataFrame()

    file_type = 'txt'
    csv_files = glob.glob(folder_name + '/*.' + file_type)

    # pile the files together into one big file
    for file in csv_files:
        dataframe = pd.read_csv(file, delimiter='|')
        raw_data = pd.concat([raw_data, dataframe])

    # reset the index (sometimes it gets wonky)
    clean_data = raw_data[raw_data['Event Id'].notnull()].reset_index(drop=True)

    # rename the columns
    renamed_data = clean_data.rename(columns={'A Event Id': 'a_event_id', 'Event Title': 'event', 'Venue Name': 'venue', 'Venue City': 'city', 'Venue Zip': 'zipcode', 'Event Datetime': 'event_date', 'Ticketing Event Code': 'ticketing_code', 'Offer Qualifier': 'offer_qual', 'Onsale Date': 'onsale_date', 'Seat Status': 'seat_status', 'Tickets': 'ticket_count', 'Amount': 'charge_volume', 'Currency': 'currency', 'Sale Date': 'sale_date'})

    # find where the offer qualifier is pref and put in new column
    renamed_data.loc[renamed_data['offer_qual'].str.contains('PREF'), 'pref_seating'] = 'Pref'

    # anything that's not pref is blue
    renamed_data['pref_seating'] = renamed_data['pref_seating'].fillna('Blue')

    # only keep data sold in USD
    us_data = renamed_data[renamed_data['currency'] == 'USD']
    
    # filter out anything weird and adjust as necessary
    filtered_data = us_data[~us_data['event'].str.contains('LA Kings')]

    # set all dates to timestamps with date only
    filtered_data['event_date'] = make_date(filtered_data['event_date'])
    filtered_data['onsale_date'] = make_date(filtered_data['onsale_date'])
    filtered_data['sale_date'] = make_date(filtered_data['sale_date'])
    
    return filtered_data

def get_missing_ids(data):
    
    # import the latest data dump ids
    latest_ids = pd.read_csv('some_folder_on_this_computer/Latest_data_dump_ids.csv')
    
    # set dates to timestamps with date only
    latest_ids['event_start_date'] = make_date(latest_ids['event_start_date'])
    latest_ids['event_end_date'] = make_date(latest_ids['event_end_date'])
    latest_ids['eos_start_date'] = make_date(latest_ids['eos_start_date'])
    latest_ids['eos_end_date'] = make_date(latest_ids['eos_end_date'])
    
    # merge axs data with database ids
    events = pd.merge(data, latest_ids, how='left', left_on=['event_date', 'venue'], right_on=['event_start_date', 'venue'])
    
    # separate into missing and matched
    unmatched_events = events[events['artist'].isnull()]
    matched_events = events[events['artist'].notnull()]
    
    # filter down the missing ids to only crucial info
    missing_ids = unmatched_events[['axs_event_id', 'event', 'venue', 'event_date']].drop_duplicates()
    
    return missing_ids, matched_events 
    
def run_mapping_update(data, data_dump, today):
    
    # pull in the mapping update
    mapping_update = pd.read_csv('some_folder_on_this_computer/mapping_updates.csv')
    
    # dedupe
    mapped_ids = mapping_update[['a_event_id', 'event_id']].drop_duplicates()
    
    # pull in missing ids
    missing_ids, matched_events = get_missing_ids(data)
    
    # merge the missing ids with mapped ids
    missing_ids = pd.merge(missing_ids, mapped_ids, how='left', on='a_event_id')
    
    # find the new matches
    rematched_ids = missing_ids[missing_ids['event_id'].notnull()]

    # find the still missing
    still_missing = missing_ids[missing_ids['event_id'].isnull()]
    
    # folder for missing ids
    missing_folder = 'some_folder_on_this_computer'
    
    # export missing for rematchings
    still_missing.to_csv(missing_folder + data_dump + ' unmapped_events ' + today + '.csv')
    
    return rematched_ids, matched_events

data = get_data(data_dump)

rematched_ids, matched_events = run_mapping_update(data, data_dump, today)
# i left out some stuff at the end here because it was too specific to be shared but hopefully this gives you an idea of my skills
