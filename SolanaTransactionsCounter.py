import pandas as pd 
from matplotlib import pyplot as plt 

class SolanaTransactionsCounter: 

    col_order = [
        'Min_Slot_Timestamp', 'Max_Slot_Number',
        'Type_CancelOrder', 'Type_ComputeBudget', 'Type_System', 
        'Type_Transaction', 'Type_Unknown', 'Type_Vote',
        'Success_CancelOrder', 'Success_ComputeBudget', 'Success_System', 
        'Success_Transaction', 'Success_Unknown', 'Success_Vote',
        'Failed_CancelOrder', 'Failed_ComputeBudget', 'Failed_System', 
        'Failed_Transaction', 'Failed_Unknown', 'Failed_Vote',
        'Status_Failed', 'Status_Success', 'Total'
    ]

    def __init__(self):
        pass 

    @staticmethod
    def __sort_columns(df):
        new_df = pd.DataFrame()
        for c in SolanaTransactionsCounter.col_order:
            if c in df.columns:
                new_df[c] = df[c]
            else:
                new_df[c] = 0
        return new_df


    @staticmethod
    def prepare_df(df):
        df['Slot_Timestamp'] = pd.to_datetime(df['Slot_Timestamp'], unit='s')
        grouped = df.groupby('Batch_Number').agg(
            Min_Slot_Timestamp=('Slot_Timestamp', 'min'),
            Max_Slot_Number=('Slot_Number', 'max')
        ).reset_index()
        df = df.reset_index().merge(grouped, on='Batch_Number')
        return df 

    @staticmethod
    def count_column_values(df, column_name): 
        return df.groupby(['Min_Slot_Timestamp', 'Max_Slot_Number', column_name]).size().unstack(-1, fill_value=0).fillna(0).reset_index()

    @staticmethod
    def merge_tables(df1, df2, on = ['Min_Slot_Timestamp', 'Max_Slot_Number'], merge_type='left'):
        df = df2.reset_index().merge(df1, on=on, how=merge_type)
        return df

    @staticmethod
    def add_prefix_to_column_names(df, prefix, column_names_to_skip=['index', 'Min_Slot_Timestamp', 'Max_Slot_Number'], prefixes_to_skip=[]):
        c_start_condition = [False for _ in df.columns]
        if len(prefixes_to_skip):
            if isinstance(prefixes_to_skip, str):
                prefix_to_skip = [prefixes_to_skip]
            for prefix_to_skip in prefixes_to_skip:
                c_start_condition = [cond or col_name.startswith(prefix_to_skip) if not cond else cond for cond,col_name in zip(c_start_condition, df.columns)]
        df.columns = [prefix + c if (not cond and c not in column_names_to_skip) else c for c,cond in zip(df.columns, c_start_condition)]
        return df 

    @staticmethod 
    def get_count_data_from_tx_df(df):
        df = SolanaTransactionsCounter.prepare_df(df)
        count_table = SolanaTransactionsCounter.count_column_values(df, 'TX_Status')
        count_table = SolanaTransactionsCounter.add_prefix_to_column_names(count_table, 'Status_')
        
        df_tmp = SolanaTransactionsCounter.count_column_values(df, 'TX_Type')
        count_table = SolanaTransactionsCounter.merge_tables(count_table, df_tmp).drop('index', axis=1)
        count_table = SolanaTransactionsCounter.add_prefix_to_column_names(count_table, 'Type_', prefixes_to_skip=['Status_'])

        df_tmp = SolanaTransactionsCounter.count_column_values(df.loc[df['TX_Status'] == 'Success'], 'TX_Type')
        count_table = SolanaTransactionsCounter.merge_tables(count_table, df_tmp)
        count_table = count_table.drop('index', axis=1)
        count_table = SolanaTransactionsCounter.add_prefix_to_column_names(count_table, 'Success_', prefixes_to_skip=['Status_', 'Type_'])

        df_tmp = SolanaTransactionsCounter.count_column_values(df.loc[df['TX_Status'] == 'Failed'], 'TX_Type')
        count_table = SolanaTransactionsCounter.merge_tables(count_table, df_tmp)
        count_table = count_table.drop('index', axis=1)
        count_table = SolanaTransactionsCounter.add_prefix_to_column_names(count_table, 'Failed_', prefixes_to_skip=['Status_', 'Type_', 'Success_'])

        count_table['Total'] = count_table['Status_Failed'] + count_table['Status_Success']
        return(SolanaTransactionsCounter.__sort_columns(count_table.fillna(0)))
