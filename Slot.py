from Transaction import Transaction
import pandas as pd

class Slot:
    """
    A class to represent a blockchain slot, containing multiple transactions.

    Attributes:
    -----------
    number : int or None
        The slot number.
    batch_number : int or None
        The batch number to which this slot belongs.
    timestamp : int or None
        The timestamp of the slot.
    transactions : list
        A list of Transaction objects within the slot.
    """

    def __init__(self, slot_number=None, slot_data=None, batch_number=None):
        """
        Initialize a Slot object.

        Parameters:
        -----------
        slot_number : int, optional
            The slot number (default is None).
        slot_data : dict, optional
            Raw data containing slot and transaction information (default is None).
        batch_number : int, optional
            The batch number to which this slot belongs (default is None).
        """
        self.number = slot_number
        self.batch_number = batch_number

        if not slot_data:
            self.timestamp = None
            self.transactions = []
        else:
            self.set_from_data(slot_data)

    def set_batch_number(self, batch_number):
        """
        Set the batch number for the slot.

        Parameters:
        -----------
        batch_number : int
            The batch number to be set.
        """
        self.batch_number = batch_number

    def get_timestamp(self):
        """
        Get the timestamp of the slot.

        Returns:
        --------
        int or None
            The timestamp of the slot.
        """
        return self.timestamp

    def get_number(self):
        """
        Get the slot number.

        Returns:
        --------
        int or None
            The slot number.
        """
        return self.number

    def set_from_data(self, slot_data):
        """
        Set the slot's attributes from raw slot data.

        Parameters:
        -----------
        slot_data : dict
            Raw data containing slot and transaction information.
        """
        self.timestamp = slot_data['result']['blockTime']
        self.transactions = [Transaction(self.number, tx_data) for tx_data in slot_data['result']['transactions']]

    def to_string(self):
        """
        Convert the slot to a string representation.

        Returns:
        --------
        str
            A string representation of the slot.
        """
        return f"#{self.number} - Timestamp: {self.timestamp}"

    def to_string_with_transactions(self):
        """
        Convert the slot and its transactions to a string representation.

        Returns:
        --------
        str
            A string representation of the slot and its transactions.
        """
        transaction_str = ""
        for tx in self.transactions:
            transaction_str += '\t' + tx.to_string() + '\n'
        return f"#{self.number} - Timestamp: {self.timestamp}" + '\n' + transaction_str

    def to_dict(self):
        """
        Convert the slot and its transactions to a dictionary.

        Returns:
        --------
        dict
            A dictionary representation of the slot and its transactions, including slot number, timestamp, batch number, transaction signatures, status, and types.
        """
        slot_dict = {
            'Slot_Number': [],
            'Slot_Timestamp': [],
            'Batch_Number': [],
            'TX_Signature': [],
            'TX_Status': [],
            'TX_Type': []
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
        """
        Convert the slot and its transactions to a pandas DataFrame.

        Returns:
        --------
        pd.DataFrame
            A DataFrame representation of the slot and its transactions.
        """
        df = pd.DataFrame.from_dict(self.to_dict())
        return df
