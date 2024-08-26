import plotly.express as px
import pandas as pd 
import plotly.graph_objects as go
import matplotlib.pyplot as plt

class PlotUtils: 
    """
    A utility class for generating various plots related to Solana transactions.
    
    Methods
    -------
    variables_type_to_colors(variables_type):
        Maps a type of variable to corresponding colors for plotting.
    variables_types_to_column_names(variables_type):
        Maps a type of variable to a list of column names in the DataFrame.
    simplify_types(df):
        Simplifies the DataFrame by consolidating category columns into an 'Other' category.
    plot_line_chart(df, variables_type, include_total=True, colors=None, title=None, fig_size=(12,6), simplify_types=False):
        Plots a stacked line chart using the provided DataFrame and variables type.
    plot_bar_chart(df, variables_type, colors=None, title=None, fig_size=(12,6), simplify_types=False):
        Plots a stacked bar chart using the provided DataFrame and variables type.
    bar_chart_dash(df, variables_type, include_total, title, simplify_types=False):
        Generates a Plotly bar chart suitable for use in Dash applications.
    empty_figure():
        Creates an empty figure with a black background for use as a placeholder.
    """
    
    def __init__(self):
        """
        Initializes the PlotUtils instance.
        """
        pass 

    @staticmethod 
    def variables_type_to_colors(variables_type):
        """
        Maps a type of variable to corresponding colors for plotting.

        Parameters:
        -----------
        variables_type : str
            The type of variable to map. Options include 'status', 'type', 'success_type', 'failed_type', and 'status_type'.

        Returns:
        --------
        dict
            A dictionary mapping variable types to colors.
        """
        match variables_type.lower(): 
            case 'status':
                keys = ['Status_Failed', 'Status_Success', 'Total'] 
                values = ['red', 'green', 'black']
            case 'type':
                keys = ['Type_CancelOrder', 'Type_ComputeBudget', 'Type_System', 
                        'Type_Transaction', 'Type_Unknown', 'Type_Vote', 'Type_Other'] 
                values = ['orange', 'blue', 'cyan', 'green', 'grey', 'red', 'blue']
            case 'success_type':
                keys = ['Success_CancelOrder', 'Success_ComputeBudget', 'Success_System', 
                        'Success_Transaction', 'Success_Unknown', 'Success_Vote', 'Success_Other']  
                values = ['yellow', 'blue', 'cyan', 'green', 'grey', 'red', 'blue']
            case 'failed_type':
                keys = ['Failed_CancelOrder', 'Failed_ComputeBudget', 'Failed_System', 
                        'Failed_Transaction', 'Failed_Unknown', 'Failed_Vote', 'Failed_Other']  
                values = ['beige', 'lightblue','teal', 'lightgreen', 'silver', 'red', 'lightblue']
            case 'status_type': 
                keys = ['Success_CancelOrder', 'Success_ComputeBudget', 'Success_System', 
                        'Success_Transaction', 'Success_Unknown', 'Success_Vote', 'Success_Other'] +\
                        ['Failed_CancelOrder', 'Failed_ComputeBudget', 'Failed_System', 
                        'Failed_Transaction', 'Failed_Unknown', 'Failed_Vote', 'Failed_Other']
                values = ['yellow', 'blue', 'cyan', 'green', 'grey', 'orange', 'blue'] +\
                         ['beige', 'lightblue','teal', 'lightgreen', 'silver', 'red', 'lightblue']
            case 'success_failed':
                keys = ['Success_CancelOrder', 'Success_ComputeBudget', 'Success_System', 
                        'Success_Transaction', 'Success_Unknown', 'Success_Vote', 'Success_Other', 
                        'Status_Failed']
                values = ['yellow', 'blue', 'cyan', 'green', 'grey', 'orange', 'blue', 'red']
            case _:
                raise ValueError('Variables type: one of "status", "type", "success_type", "failed_type", or "status_type".')

        return {k:v for k,v in zip(keys,values)}

    @staticmethod 
    def variables_types_to_column_names(variables_type):
        """
        Maps a type of variable to a list of column names in the DataFrame.

        Parameters:
        -----------
        variables_type : str
            The type of variable to map. Options include 'status', 'type', 'success_type', 'failed_type', and 'status_type'.

        Returns:
        --------
        list
            A list of column names corresponding to the variable type.
        """
        match variables_type.lower(): 
            case 'status':
                cols = ['Status_Failed', 'Status_Success'] 
            case 'type':
                cols = ['Type_CancelOrder', 'Type_ComputeBudget', 'Type_System', 
                        'Type_Transaction', 'Type_Unknown', 'Type_Vote', 'Type_Other'] 
            case 'success_type':
                cols = ['Success_CancelOrder', 'Success_ComputeBudget', 'Success_System', 
                        'Success_Unknown', 'Success_Vote', 'Success_Other', 'Success_Transaction']  
            case 'failed_type':
                cols = ['Failed_CancelOrder', 'Failed_ComputeBudget', 'Failed_System', 
                        'Failed_Unknown', 'Failed_Vote', 'Failed_Other', 'Failed_Transaction']  
            case 'status_type': 
                cols = ['Success_CancelOrder', 'Success_ComputeBudget', 'Success_System', 
                        'Success_Unknown', 'Success_Vote', 'Success_Other', 'Success_Transaction'] +\
                        ['Failed_CancelOrder', 'Failed_ComputeBudget', 'Failed_System', 
                        'Failed_Unknown', 'Failed_Vote', 'Failed_Other', 'Failed_Transaction']
            case 'success_failed': 
                cols = ['Success_CancelOrder', 'Success_ComputeBudget', 'Success_System', 
                        'Success_Unknown', 'Success_Vote', 'Success_Other', 'Success_Transaction', 
                        'Status_Failed']
            case _:
                raise ValueError('Variables type: one of "status", "type", "success_type", "failed_type", or "status_type".')
        return ['Min_Slot_Timestamp'] + cols

    @staticmethod
    def simplify_types(df): 
        """
        Simplifies the DataFrame by consolidating category columns into an 'Other' category.

        Parameters:
        -----------
        df : pd.DataFrame
            The DataFrame to be simplified.

        Returns:
        --------
        pd.DataFrame
            The simplified DataFrame.
        """
        categories_to_simplify = ['ComputeBudget', 'Unknown', 'CancelOrder', 'System'] 
        for prefix in ['Failed_', 'Success_', 'Type_']:
            if prefix + 'Other' not in df.columns:
                df[prefix + 'Other'] = 0
                for cat in categories_to_simplify:
                    if prefix + cat in df.columns:
                        df[prefix + 'Other'] += df[prefix + cat]
                        df = df.drop(prefix + cat, axis=1)
        return df         

    @staticmethod
    def plot_line_chart(df, variables_type, include_total=True, colors=None, title=None, fig_size=(12,6), simplify_types=False): 
        """
        Plots a stacked line chart using the provided DataFrame and variables type.

        Parameters:
        -----------
        df : pd.DataFrame
            The DataFrame containing the data to plot.
        variables_type : str
            The type of variable to plot. Options include 'status', 'type', 'success_type', 'failed_type', 'status_type', and 'success_failed'.
        include_total : bool, optional
            If True, includes a 'Total' line in the chart. Defaults to True.
        colors : dict, optional
            A dictionary mapping variable names to colors. If None, uses default colors.
        title : str, optional
            The title of the chart. If None, a default title is used.
        fig_size : tuple, optional
            The size of the figure. Defaults to (12,6).
        simplify_types : bool, optional
            If True, simplifies the DataFrame before plotting. Defaults to False.

        Returns:
        --------
        None
        """
        if variables_type.lower() == 'type_status':
            variables_type = 'status_type'

        if variables_type.lower() not in ['status', 'type', 'success_type', 'failed_type', 'status_type', 'success_failed']:
            raise ValueError('Variables type: one of "status", "type", "success_type", "failed_type", or "status_type".')

        if ('type' in variables_type.lower() or variables_type.lower() == 'success_failed') and simplify_types:
            df_plot = PlotUtils.simplify_types(df.copy(deep=True))
        else:
            df_plot = df.copy(deep=True)
        
        if colors is None:
            colors = PlotUtils.variables_type_to_colors(variables_type)

        if title is None:
            title = "Solana Transactions" 

        cols = PlotUtils.variables_types_to_column_names(variables_type)
        cols = [c for c in cols if c in df_plot.columns] # check
        cols = cols + ['Total'] if include_total else cols 
        df_plot = df_plot.loc[:, cols].set_index('Min_Slot_Timestamp', inplace=False)

        fig, ax = plt.subplots(figsize=fig_size)
        bottoms = pd.Series([0] * len(df_plot.index), index = df_plot.index) 
        legend_names = []
        for category in df_plot.columns.difference(['Total']):
            ax.fill_between(df_plot.index, bottoms, bottoms + df_plot[category], alpha=0.2, label=category, color=colors.get(category))
            bottoms += df_plot[category]
            legend_names.append(category.split('_')[1])

        if include_total:
            df_plot[['Total']].plot(ax=ax, color='black', linestyle='-', linewidth=1, label='Total')
            legend_names.append('Total')

        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        ax.set_title(title)
        ax.legend(legend_names)
        plt.show()
        return

    @staticmethod
    def plot_bar_chart(df, variables_type, colors=None, title=None, fig_size=(12,6), simplify_types=False): 
        """
        Plots a stacked bar chart using the provided DataFrame and variables type.

        Parameters:
        -----------
        df : pd.DataFrame
            The DataFrame containing the data to plot.
        variables_type : str
            The type of variable to plot. Options include 'status', 'type', 'success_type', 'failed_type', 'status_type', and 'success_failed'.
        colors : dict, optional
            A dictionary mapping variable names to colors. If None, uses default colors.
        title : str, optional
            The title of the chart. If None, a default title is used.
        fig_size : tuple, optional
            The size of the figure. Defaults to (12,6).
        simplify_types : bool, optional
            If True, simplifies the DataFrame before plotting. Defaults to False.

        Returns:
        --------
        None
        """
        if variables_type.lower() == 'type_status':
            variables_type = 'status_type'

        if variables_type.lower() not in ['status', 'type', 'success_type', 'failed_type', 'status_type', 'success_failed']:
            raise ValueError('Variables type: one of "status", "type", "success_type", "failed_type", or "status_type".')
        
        if colors is None:
            colors = PlotUtils.variables_type_to_colors(variables_type)

        if title is None:
            title = "Solana Transactions" 

        if ('type' in variables_type.lower() or variables_type.lower() == 'success_failed') and simplify_types:
            df_plot = PlotUtils.simplify_types(df.copy(deep=True))
        else:
            df_plot = df.copy(deep=True)

        cols = PlotUtils.variables_types_to_column_names(variables_type)
        cols = [c for c in cols if c in df_plot.columns] # check
        df_plot = df_plot.loc[:, cols].set_index('Min_Slot_Timestamp', inplace=False)

        ax = df_plot.plot(kind='bar', stacked=True, color=[colors.get(x) for x in df_plot.columns], alpha=0.5, figsize=fig_size)
        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        ax.set_title(title)
        ax.legend([c.split('_')[1] for c in df_plot.columns])
        plt.show()
        return

    @staticmethod
    def bar_chart_dash(df, variables_type, include_total, title, simplify_types=False):
        """
        Generates a Plotly bar chart suitable for use in Dash applications.

        Parameters:
        -----------
        df : pd.DataFrame
            The DataFrame containing the data to plot.
        variables_type : str
            The type of variable to plot. Options include 'status', 'type', 'success_type', 'failed_type', 'status_type', and 'success_failed'.
        include_total : bool
            If True, includes a 'Total' column in the chart.
        title : str
            The title of the chart.
        simplify_types : bool, optional
            If True, simplifies the DataFrame before plotting. Defaults to False.

        Returns:
        --------
        plotly.graph_objects.Figure
            A Plotly figure object for the bar chart.
        """
        if variables_type.lower() == 'type_status':
            variables_type = 'status_type'

        if variables_type.lower() not in ['status', 'type', 'success_type', 'failed_type', 'status_type', 'success_failed']:
            raise ValueError('Variables type: one of "status", "type", "success_type", "failed_type", or "status_type".')
        
        if ('type' in variables_type.lower() or variables_type.lower() == 'success_failed') and simplify_types:
            df_plot = PlotUtils.simplify_types(df.copy(deep=True))
        else:
            df_plot = df.copy(deep=True)

        x_col = 'Min_Slot_Timestamp'
        y_cols = PlotUtils.variables_types_to_column_names(variables_type)
        y_cols.remove('Min_Slot_Timestamp')
        y_cols = [c for c in y_cols if c in df_plot.columns]

        labels = {col:col.replace('_',": ") for col in y_cols}
        labels_rev = {col.replace('_',": "):col for col in y_cols}
        if include_total:
            hover_template_dict = {col: f'<b>%{{x}}</b><br>{col.replace("_",":")} %{{y}}<br>Total: %{{customdata}}<extra></extra><extra></extra>' for col in y_cols}
        else: 
            hover_template_dict = {col: f'<b>%{{x}}</b><br>{col.replace("_",":")} %{{y}}<extra></extra>' for col in y_cols}

        custom_colors = PlotUtils.variables_type_to_colors(variables_type)
        custom_colors = [custom_colors[c] for c in y_cols]

        fig = px.bar(
            df_plot, 
            x=x_col, 
            y=y_cols, 
            labels = labels, 
            color_discrete_sequence=custom_colors,
        )

        fig.update_traces(marker=dict(line=dict(width=0.5, color='black')))

        for trace in fig.data:
            if trace.name in labels: 
                trace.name = labels[trace.name]
                if include_total:
                    trace.customdata = df_plot.loc[df_plot[x_col] == trace.x, 'Total'].values
                trace.hovertemplate = hover_template_dict[labels_rev[trace.name]]

        fig.update_layout(
            paper_bgcolor='black',  
            plot_bgcolor='black',   
            title={
                    'text': title,
                    'font': {'color': 'white', 'size': 18},  
                    'x': 0.5,  
                    'xanchor': 'center',  
                    'y': 1.0  
                },
            xaxis=dict(
                title='Time',
                tickfont=dict(family='Arial', size=14, color='white'),  
                title_font=dict(family='Arial', size=18, color='white'),  
                tickvals=df[x_col],
                tickangle = -45, 
            ),
            yaxis=dict(
                title='Count',
                title_font=dict(family='Arial', size=18, color='white'), 
                tickfont=dict(family='Arial', size=14, color='white'),  
                
                range=[0, df["Total"].max() * 1.25],  
            ),
            margin=dict(l=40, r=0, t=40, b=40),  
            legend_title = None, 
            legend_title_font_color='white', 
            legend_font_color='white',  
        )
        
        return fig

    @staticmethod
    def empty_figure():
        """
        Creates an empty figure with a black background for use as a placeholder.

        Returns:
        --------
        plotly.graph_objects.Figure
            An empty Plotly figure with a black background.
        """
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor='black', 
            plot_bgcolor='black',  
            font=dict(color='black'),  
            xaxis=dict(
                color='black', 
                showgrid=False, 
                zeroline=False  
            ),
            yaxis=dict(
                color='black',  
                showgrid=False, 
                zeroline=False  
            )
        )
        return fig
