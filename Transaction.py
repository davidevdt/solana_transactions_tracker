class Transaction:
    """
    A class to represent a Solana blockchain transaction.

    Attributes:
    -----------
    slot_number : int or None
        The slot number of the transaction.
    signature : str or None
        The signature of the transaction.
    slot : int or None
        The slot in which the transaction was recorded.
    type : str or None
        The type of the transaction.
    status : str
        The status of the transaction.
    instruction_logs : list
        A list of logs related to the transaction's instructions.
    instruction_types : list
        A list of types corresponding to the transaction's instructions.
    program_ids : list
        A list of program IDs involved in the transaction.
    """

    def __init__(self, slot_number=None, tx_data=None):
        """
        Initialize a Transaction object.

        Parameters:
        -----------
        slot_number : int, optional
            The slot number of the transaction (default is None).
        tx_data : dict, optional
            The raw transaction data from which to initialize the object (default is None).
        """
        self.slot_number = slot_number

        if not tx_data:
            self.signature = None
            self.slot = None
            self.type = None
            self.status = "Unknown"
            self.instruction_logs = []
            self.instruction_types = []
            self.program_ids = []
        else:
            self.set_from_data(tx_data)

    def to_dict(self):
        """
        Convert the transaction to a dictionary.

        Returns:
        --------
        dict
            A dictionary representation of the transaction with keys 'TX_Signature', 'TX_Status', and 'TX_Type'.
        """
        return {
            'TX_Signature': self.signature,
            'TX_Status': self.status,
            'TX_Type': self.type
        }

    def to_string(self):
        """
        Convert the transaction to a string.

        Returns:
        --------
        str
            A string representation of the transaction.
        """
        return f'Signature: {self.signature} - Type: {self.type} - Status: {self.status}'

    def get_signature(self):
        """
        Get the transaction's signature.

        Returns:
        --------
        str or None
            The signature of the transaction.
        """
        return self.signature

    def get_type(self):
        """
        Get the transaction's type.

        Returns:
        --------
        str or None
            The type of the transaction.
        """
        return self.type

    def get_status(self):
        """
        Get the transaction's status.

        Returns:
        --------
        str
            The status of the transaction.
        """
        return self.status

    def set_from_data(self, tx_data):
        """
        Set the transaction attributes from raw transaction data.

        Parameters:
        -----------
        tx_data : dict
            The raw transaction data.
        """
        self._extract_transaction_data(tx_data)
        self._classify_transaction(relax_compute_budget_count=False)

    def _extract_transaction_data(self, data):
        """
        Extract and process the relevant data from the raw transaction data.

        Parameters:
        -----------
        data : dict
            The raw transaction data.
        """
        tx_data = {}
        self.signature = data['transaction']['signatures'][0]
        tx_status = "Unknown"
        tx_logs = []

        if data is not None and 'meta' in data and data['meta'] is not None:
            if 'err' in data['meta']:
                tx_status = "Success" if data['meta']['err'] is None else "Failed"

            if 'logMessages' in data['meta']:
                tx_logs = data['meta']['logMessages']

        self.status = tx_status
        self.instruction_logs = tx_logs

        instructions = data['transaction']['message']['instructions']
        instructions_types = []
        program_ids = []

        if instructions:
            for ins in instructions:
                if 'parsed' in ins.keys() and isinstance(ins['parsed'], dict) and 'type' in ins['parsed'].keys():
                    instructions_types.append(ins['parsed']['type'])
                else:
                    instructions_types.append(None)

                if 'programId' in ins.keys():
                    program_ids.append(ins['programId'])
                else:
                    program_ids.append(None)
        else:
            instructions_types = [None]
            program_ids = [None]

        self.instruction_types = instructions_types
        self.program_ids = program_ids

        if not isinstance(self.instruction_logs, list):
            self.instruction_logs = [self.instruction_logs]

        if not isinstance(self.instruction_types, list):
            self.instruction_logs = [self.instruction_types]

        if not isinstance(self.program_ids, list):
            self.program_ids = [self.program_ids]

    def _classify_transaction(self, relax_compute_budget_count=False):
        """
        Classify the transaction based on its program IDs and instruction logs.

        Parameters:
        -----------
        relax_compute_budget_count : bool, optional
            Whether to relax the condition for counting ComputeBudget instructions (default is False).
        """
        compute_budget_condition = (
            self.program_ids[0] == 'ComputeBudget111111111111111111111111111111'
            if not relax_compute_budget_count
            else all(p == 'ComputeBudget111111111111111111111111111111' for p in self.program_ids)
        )

        if self.program_ids[0] == 'FsJ3A3u2vn5cTVofAjvy6y5kwABJAqYWpe4975bi2epH':
            self.type = 'UpdatePrice'
        elif self.instruction_types[0] == 'transfer':
            self.type = 'Transaction'
        elif self.instruction_types[0] == 'create':
            self.type = 'Transaction'
        elif self.instruction_types[0] == 'mintTo':
            self.type = 'Transaction'
        elif self.instruction_types[0] == 'transferChecked':
            self.type = 'Transaction'
        elif self.instruction_types[0] == 'compactupdatevotestate':
            self.type = 'Vote'
        elif self.instruction_types[0] == 'BPFLoaderUpgradeab1e11111111111111111111111':
            self.type = 'BPF'
        elif self.instruction_types[0] == 'extendLookupTable':
            self.type = 'System'
        elif 'Program log: Instruction: FunctionVerify' in self.instruction_logs:
            self.type = 'System'
        elif 'Program log: Instruction: FleetStateHandler' in self.instruction_logs:
            self.type = 'System'
        elif compute_budget_condition:
            self.type = 'ComputeBudget'
        elif not compute_budget_condition:
            if 'Program log: Instruction: PreTransaction' in self.instruction_logs and 'Program log: Instruction: PostTransactionNoVault' in self.instruction_logs:
                self.type = 'Transaction'
            elif 'Program log: Instruction: ScanForSurveyDataUnits' in self.instruction_logs:
                self.type = 'Scan'
            elif 'Program log: Instruction: OracleHeartbeat' in self.instruction_logs or 'Program log: Oracle' in self.instruction_logs:
                self.type = 'Oracle'
            elif 'Program log: Instruction: RescindLoan' in self.instruction_logs:
                self.type = 'Transaction'
            elif 'Program log: Instruction: Transfer' in self.instruction_logs:
                self.type = 'Transaction'
            elif 'Program log: Instruction: ClosePositionRequest' in self.instruction_logs:
                self.type = 'Transaction'
            elif 'Program log: Instruction: Swap' in self.instruction_logs:
                self.type = 'Transaction'
            elif 'Program log: Instruction: Claim' in self.instruction_logs:
                self.type = 'Transaction'
            elif 'Program log: Instruction: Repay' in self.instruction_logs:
                self.type = 'Transaction'
            elif 'Program log: Instruction: Route' in self.instruction_logs:
                self.type = 'Transaction'
            elif 'Program log: Instruction: InitPool' in self.instruction_logs:
                self.type = 'Transaction'
            elif 'Program log: Instruction: AttachPoolToMargin' in self.instruction_logs:
                self.type = 'Transaction'
            elif 'Program log: Instruction: Borrow' in self.instruction_logs:
                self.type = 'Transaction'
            elif any(l.startswith('Program log: Returned loan of') for l in self.instruction_logs):
                self.type = 'Transaction'
            elif 'Program log: Create' in self.instruction_logs:
                self.type = 'Transaction'
            elif any(l.startswith('Program log: Instruction: Initialize') for l in self.instruction_logs):
                self.type = 'Transaction'
            elif 'Program log: Instruction: MintTo' in self.instruction_logs:
                self.type = 'Transaction'
            elif any(l.startswith('Program log: Instruction: PlacePerpOrder') for l in self.instruction_logs):
                self.type = 'Transaction'
            elif any(l.startswith('Program log: Instruction: LiquidatePerp') for l in self.instruction_logs):
                self.type = 'Transaction'
            elif 'Program log: Instruction: SharedAccountsRoute' in self.instruction_logs:
                self.type = 'Transaction'
            elif 'Program log: Instruction: LiquidUnstake' in self.instruction_logs:
                self.type = 'Transaction'
            elif any('Cancel' in l for l in self.instruction_logs):
                self.type = 'CancelOrder'
            else:
                self.type = 'Unknown'
        else:
            self.type = 'Unknown'
