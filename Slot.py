from Transaction import Transaction
import pandas as pd 

class Slot: 

    def __init__(self, slot_number=None, slot_data=None, batch_number=None):
        self.number = slot_number
        self.batch_number = batch_number 

        if not slot_data: 
            self.timestamp = None 
            self.transactions = []
        else: 
            self.set_from_data(slot_data)

    def set_batch_number(self, batch_number): 
        self.batch_number = batch_number

    def get_timestamp(self):
        return self.timestamp

    def get_number(self):
        return self.number

    def set_from_data(self, slot_data): 
        self.timestamp = slot_data['result']['blockTime']
        self.transactions = [Transaction(self.number, tx_data) for tx_data in slot_data['result']['transactions']]

    def to_string(self):
        return f"#{self.number} - Timestamp: {self.timestamp}"

    def to_string_with_transactions(self): 
        transaction_str = ""
        for tx in self.transactions: 
            transaction_str += '\t' + tx.to_string() + '\n'
        return f"#{self.number} - Timestamp: {self.timestamp}" + '\n' + transaction_str

    def to_dict(self):

        slot_dict = {
            'Slot_Number' : [], 
            'Slot_Timestamp' : [],
            'Batch_Number' : [],  
            'TX_Signature' : [], 
            'TX_Status' : [], 
            'TX_Type' : []
        }

        for tx in self.transactions:
            slot_dict['Slot_Number'].append(int(self.number)) 
            slot_dict['Slot_Timestamp'].append(int(self.timestamp))
            slot_dict['Batch_Number'].append(self.batch_number)
            slot_dict['TX_Signature'].append(tx.get_signature())
            slot_dict['TX_Status'].append(tx.get_status())
            slot_dict['TX_Type'].append(tx.get_type())

        return slot_dict

    def to_df(self): 
        df = pd.DataFrame.from_dict(self.to_dict())
        return df 
