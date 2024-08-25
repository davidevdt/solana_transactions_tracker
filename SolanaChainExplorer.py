import requests
from Slot import Slot
from SolanaChain import SolanaChain
from Transaction import Transaction
from datetime import datetime, timedelta
from time import sleep 
import pandas as pd 
import json 

class SolanaChainExplorer: 

    SLEEP_TIME = 1.5 
    
    def __init__(self, n_batches_to_explore=5, jump=1000, seconds_per_batch=1, rpc_url=None): 
        self.chain = SolanaChain()

        if rpc_url is None: 
            rpc_url = "https://api.mainnet-beta.solana.com"

        self.rpc_url = rpc_url 
        self.n_batches_to_explore = n_batches_to_explore
        self.jump = jump 
        self.seconds_per_batch = seconds_per_batch

        self.find_latest_slot_number(True)    

    def import_settings_from_json(self, json_file): 
        with open(json_file, 'r') as jf: 
            settings = json.load(jf)
        self.n_batches_to_explore = settings['n_batches_to_explore']
        self.jump = settings['jumps']
        self.seconds_per_batch = settings['seconds_per_batch']

        print(f"Loaded settings::N_BATCHES={self.n_batches_to_explore}::JUMP={self.jump}::SECONDS_PER_BATCH={self.seconds_per_batch}")    

    def get_latest_slot_number(self):
        return self.chain.latest_slot.get_number()

    def find_latest_slot_number(self, update_chain=True):  
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSlot"
        }
        response = requests.post(self.rpc_url, json=payload)
        result = response.json()
        if update_chain:
            self.chain.set_latest_slot(result['result'], self.get_slot_data(result['result']))
        return result['result']

    def get_slot_data(self, slot_number):
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBlock",
            "params": [
                slot_number,
                {
                    "encoding": "jsonParsed",
                    "transactionDetails": "full",
                    "rewards": False, 
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        response = requests.post(self.rpc_url, json=payload, headers=headers)
        if response.status_code == 200 and 'result' in response.json():
            return response.json()
        else: 
            None 

    def is_timestamp_within_time_range(self, ref_timestamp, timestamp_to_check):

        if abs(ref_timestamp - timestamp_to_check) <= self.seconds_per_batch:
            return True
        return False 

    def get_slot_within_time_range(self, ref_slot, shift=1):
        ref_slot_number = ref_slot.get_number()
        ref_timestamp = ref_slot.get_timestamp() 

        slot_number_to_test = ref_slot_number + shift 

        slot_data_to_test = self.get_slot_data(slot_number_to_test)

        if slot_data_to_test: 
            timestamp_to_test = slot_data_to_test['result']['blockTime']
            
            if self.is_timestamp_within_time_range(ref_timestamp, timestamp_to_test):
                return Slot(slot_number_to_test, slot_data_to_test) 
            else: 
                return Slot(-1, None)
        return None

    def find_slots_within_time_range(self, ref_slot, find_subsequent = True): 
        found_slots = [ref_slot]
        new_slot = ref_slot

        if find_subsequent:
            shift = 1 
        else:
            shift = -1 

        while True: 
            sleep(self.SLEEP_TIME)
            new_slot = self.get_slot_within_time_range(ref_slot, shift)

            if not new_slot:
                return shift 
            
            if new_slot.get_number() == -1: 
                break 
            
            found_slots.append(new_slot)

            if find_subsequent:
                shift += 1
            else: 
                shift -= 1 

            if ref_slot.get_number() + shift > self.chain.latest_slot.get_number():
                break 

        return found_slots 

    def explore_chain(
        self, 
        starting_slot_number, 
        flush_slots_at_each_update=False,
        explore_chain_forward=True, 
        print_progress=True
    ):
        slot_number = starting_slot_number
        step_counter = 0 

        while True: 
            if step_counter == self.n_batches_to_explore or slot_number >= self.get_latest_slot_number():
                break 
            
            if print_progress:
                print(f"Fetching slot # {slot_number} ({step_counter+1} of {self.n_batches_to_explore})")

            shift = 0
            while True: 
                found_slots = []

                if explore_chain_forward:
                    new_slot_number = slot_number + shift 
                    if new_slot_number >= slot_number + self.jump or new_slot_number > self.get_latest_slot_number(): 
                        break 
                else: 
                    new_slot_number = slot_number - shift
                    if new_slot_number <= slot_number - self.jump or new_slot_number < 1: 
                        break 
                new_slot_data = self.get_slot_data(new_slot_number)

                if new_slot_data:
                    if self.seconds_per_batch != 0: 
                        found_slots = self.find_slots_within_time_range(
                            Slot(new_slot_number, new_slot_data), 
                            explore_chain_forward
                        )

                        if isinstance(found_slots, int): 
                            if print_progress:
                                print(f"Slots not found. Searching new batch...")
                            shift += found_slots
                        else: 
                            if print_progress:
                                print(f"Found slot(s)::{found_slots}")
                            break 
                    else: 
                        found_slots = [Slot(new_slot_number, new_slot_data)]
                        if print_progress:
                            print(f"Found slot::{found_slots}")
                        break 
                else: 
                    shift += (1 if explore_chain_forward else -1)
                    if print_progress:
                        print(f"Not found")
                    sleep(self.SLEEP_TIME)

            if len(found_slots): 
                self.chain.add_slots_to_chain(found_slots, flush_slots_at_each_update)

            if explore_chain_forward:
                slot_number += self.jump 
            else: 
                slot_number -= self.jump 
            step_counter += 1
            sleep(self.SLEEP_TIME)

            if print_progress:
                print(f"Added slot(s): # {[s.to_string() + ' ' for s in found_slots]}.")
        
        if print_progress:
            print("All data retrieved.")

    def update_slots(self, flush_slots_at_each_update=True, print_progress=True, n_updates = -1):

        step_counter = -2 if n_updates <= -1 else 0 

        if self.chain.df is None or self.chain.df.shape[0] == 0: 
            raise RuntimeError("Please load a df into the Solana Chain. Please use the .load_df() method.")

        last_visited_slot_number = int(self.chain.df['Max_Slot_Number'].max())

        if last_visited_slot_number >= self.get_latest_slot_number() or \
            last_visited_slot_number + self.jump > self.get_latest_slot_number():
            print("Chain up to date.")
            return None 

        slot_number = last_visited_slot_number

        while (slot_number + self.jump) <= self.get_latest_slot_number() and (step_counter < n_updates):
            slot_number = slot_number + self.jump 

            if print_progress:
                print(f"Fetching slot # {slot_number} (latest slot number: {self.chain.latest_slot.get_number()})")

            shift = 0
            while True: 
                found_slots = []

                new_slot_number = slot_number + shift 
                if new_slot_number >= slot_number + self.jump or new_slot_number > self.get_latest_slot_number(): 
                    break 
                
                new_slot_data = self.get_slot_data(new_slot_number)
                if new_slot_data:
                    if self.seconds_per_batch != 0: 
                        found_slots = self.find_slots_within_time_range(
                            Slot(new_slot_number, new_slot_data), 
                            True
                        )

                        if isinstance(found_slots, int): 
                            if print_progress:
                                print(f"Slots not found. Searching new batch...")
                            shift += found_slots
                        else: 
                            if print_progress:
                                print(f"Found slot(s)::{found_slots}")
                            break 
                    else: 
                        found_slots = [Slot(new_slot_number, new_slot_data)]
                        if print_progress:
                            print(f"Found slot::{found_slots}")
                        break 
                else: 
                    shift += 1
                    if print_progress:
                        print(f"Not found")

            if len(found_slots): 
                self.chain.add_slots_to_chain(found_slots, flush_slots_at_each_update)

            step_counter += 1 if n_updates > -1 else 0 
            sleep(self.SLEEP_TIME)

            if print_progress:
                print(f"Added slot(s): # {[s.to_string() + ' ' for s in found_slots]}.")
            
        if print_progress:
            print("All data retrieved.")

    def update_chain(self, print_progress, csv_file=None): 
        self.find_latest_slot_number(True)
        sleep(self.SLEEP_TIME)

        self.update_slots(print_progress)
        
        if csv_file:
            self.store_chain_to_csv(csv_file)

    def store_chain_to_csv(self, filename):
        self.chain.store_to_csv(filename)

    def load_chain_from_csv(self, filename): 
        self.chain.load_from_csv(filename)

    def get_df(self):
        return self.chain.df






    

        



            

            

            
            








