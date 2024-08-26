import pandas as pd
from Slot import Slot
from SolanaTransactionsCounter import SolanaTransactionsCounter

class SolanaChain:
    """
    A class to represent a Solana blockchain, consisting of multiple slots.

    Attributes:
    -----------
    slots : list
        A list of Slot objects representing the blockchain.
    slot_numbers : list
        A list of slot numbers in the blockchain.
    latest_slot : Slot or None
        The latest slot added to the blockchain.
    df : pd.DataFrame or None
        A DataFrame representing aggregated transaction data across slots.
    batch_number : int
        The current batch number for slots added to the blockchain.
    """

    def __init__(self):
        """
        Initialize a SolanaChain object with an empty list of slots and other attributes.
        """
        self.slots = []
        self.slot_numbers = []
        self.latest_slot = None
        self.df = None
        self.batch_number = -1

    def set_latest_slot(self, slot_number, slot_data):
        """
        Set the latest slot in the blockchain.

        Parameters:
        -----------
        slot_number : int
            The slot number.
        slot_data : dict
            Raw data containing slot information.
        """
        self.latest_slot = Slot(slot_number, slot_data)

    def get_batch_number(self):
        """
        Get the current batch number.

        Returns:
        --------
        int
            The current batch number.
        """
        return self.batch_number

    def add_slot_to_chain_through_data(self, slot_number, slot_data, update_df=False):
        """
        Add a slot to the blockchain using raw slot data.

        Parameters:
        -----------
        slot_number : int
            The slot number to be added.
        slot_data : dict
            Raw data containing slot and transaction information.
        update_df : bool, optional
            If True, update the blockchain DataFrame (default is False).
        """
        if slot_number in self.slot_numbers:
            return

        self.slots.append(Slot(slot_number, slot_data))
        self.slot_numbers.append(slot_number)

        if update_df:
            self.update_df([self.slots[-1]])

    def add_slot_to_chain(self, slot, update_df=False, flush_slots=False):
        """
        Add a Slot object to the blockchain.

        Parameters:
        -----------
        slot : Slot
            The Slot object to be added.
        update_df : bool, optional
            If True, update the blockchain DataFrame (default is False).
        flush_slots : bool, optional
            If True, flush the list of slots after updating the DataFrame (default is False).
        """
        if slot.get_number() in self.slot_numbers:
            return

        self.slots.append(slot)
        self.slot_numbers.append(slot.get_number())

        if update_df:
            self.update_df([self.slots[-1]], flush_slots)

    def add_slots_to_chain(self, slot_list, flush_slots=False):
        """
        Add multiple Slot objects to the blockchain.

        Parameters:
        -----------
        slot_list : list
            A list of Slot objects to be added.
        flush_slots : bool, optional
            If True, flush the list of slots after updating the DataFrame (default is False).
        """
        self.batch_number += 1
        for slot in slot_list:
            slot.set_batch_number(self.batch_number)
            self.add_slot_to_chain(slot)
        self.update_df(slot_list, flush_slots)

    def to_string(self, with_transactions=False):
        """
        Convert the blockchain to a string representation.

        Parameters:
        -----------
        with_transactions : bool, optional
            If True, include transaction details in the string (default is False).

        Returns:
        --------
        str
            A string representation of the blockchain.
        """
        if not with_transactions:
            return f"{[s.to_string() + ' ' for s in self.slots]}"
        else:
            return f"{[s.to_string_with_transactions() for s in self.slots]}"

    def update_df(self, slots, flush_slots=False):
        """
        Update the blockchain DataFrame with data from the provided slots.

        Parameters:
        -----------
        slots : list
            A list of Slot objects to update the DataFrame with.
        flush_slots : bool, optional
            If True, flush the list of slots after updating the DataFrame (default is False).
        """
        slot_df = pd.concat([slot.to_df() for slot in slots])
        self.df = pd.concat([self.df] + [SolanaTransactionsCounter.get_count_data_from_tx_df(slot_df)]).fillna(0)
        self.df = self.df.sort_values(['Min_Slot_Timestamp'])

        if flush_slots:
            self.slots = []
            self.batch_number = 0

    def store_to_csv(self, filename):
        """
        Store the blockchain data to a CSV file.

        Parameters:
        -----------
        filename : str
            The name of the file to store the data.
        """
        if self.df is not None and self.df.shape[0] > 0:
            self.df.to_csv(filename, index=False)
        else:
            print("Empty blockchain dataset.")

    def load_from_csv(self, filename):
        """
        Load blockchain data from a CSV file.

        Parameters:
        -----------
        filename : str
            The name of the file to load the data from.
        """
        self.df = pd.read_csv(filename)
        self.df['Min_Slot_Timestamp'] = pd.to_datetime(self.df['Min_Slot_Timestamp'], format="%Y-%m-%d %H:%M:%S")
        self.latest_slot = Slot(slot_number=self.df['Max_Slot_Number'].max())
