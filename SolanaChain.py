import pandas as pd 
from Slot import Slot
from SolanaTransactionsCounter import SolanaTransactionsCounter

class SolanaChain: 

    def __init__(self): 

        self.slots = []
        self.slot_numbers = []
        self.latest_slot = None 
        self.df = None 
        self.batch_number = -1

    def set_latest_slot(self, slot_number, slot_data):
        self.latest_slot = Slot(slot_number, slot_data) 

    def get_batch_number():
        return self.batch_number

    def add_slot_to_chain_through_data(self, slot_number, slot_data, update_df=False): 
        if slot_number in self.slot_numbers:
            return 

        self.slots.append(Slot(slot_number, slot_data))
        self.slot_numbers.append(slot_number)
        
        if update_df:
            self.update_df([self.slots[-1]])

    def add_slot_to_chain(self, slot, update_df=False, flush_slots=False): 
        if slot.get_number() in self.slot_numbers:
            return 

        self.slots.append(slot)
        self.slot_numbers.append(slot.get_number())

        if update_df:
            self.update_df([self.slots[-1]], flush_slots)

    def add_slots_to_chain(self, slot_list, flush_slots=False): 
        self.batch_number += 1 
        for slot in slot_list: 
            slot.set_batch_number(self.batch_number)
            self.add_slot_to_chain(slot)
        self.update_df(slot_list, flush_slots)

    def to_string(self, with_transactions=False): 
        if not with_transactions:
            return f"{[s.to_string() + ' ' for s in self.slots]}"
        else: 
            return f"{[s.to_string_with_transactions() for s in self.slots]}"

    def update_df(self, slots, flush_slots=False): 
        slot_df = pd.concat([slot.to_df() for slot in slots])
        self.df = pd.concat([self.df] + [SolanaTransactionsCounter.get_count_data_from_tx_df(slot_df)]).fillna(0)
        self.df = self.df.sort_values(['Min_Slot_Timestamp'])

        if flush_slots:
            self.slots = []
            self.batch_number = 0 

    def store_to_csv(self, filename): 
        if self.df is not None and self.df.shape[0] > 0: 
            self.df.to_csv(filename, index=False)
        else:
            print("Empty blockchain dataset.")

    def load_from_csv(self, filename): 
        self.df = pd.read_csv(filename)
        self.df['Min_Slot_Timestamp'] = pd.to_datetime(self.df['Min_Slot_Timestamp'], format="%Y-%m-%d %H:%M:%S")
        self.latest_slot = Slot(slot_number = self.df['Max_Slot_Number'].max())


