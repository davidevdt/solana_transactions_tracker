# Solana Transaction Tracker

## Overview

The Solana Transaction Tracker is a Python-based application designed to monitor and visualize transactions on the Solana blockchain. It provides real-time and historical insights into transaction statuses and types, summarizing data collected directly  from the Solana blockchain.

## Features

- **Real-Time Data:** The application fetches and displays the latest transaction data from the Solana blockchain.
- **Interactive Charts:** Visualize transaction statuses and types using interactive bar charts.
- **Historical Data:** Track and analyze past transaction data to observe trends over time.

## Components

- **SolanaChainExplorer:** A class responsible for interacting with the Solana blockchain, fetching transaction data, and saving it to a CSV file.
- **PlotUtils:** A utility class for generating various types of plots and charts based on the transaction data.
- **Dash Web Application:** A web interface built with Dash that displays the transaction data and charts.

## Configuration

1. **Explorer Settings:** The application uses an `explorer_settings.json` file to configure parameters for the `SolanaChainExplorer` class. Ensure this file is present and correctly configured to tailor the blockchain data exploration to your needs.

2. **Initial Data Fetching:** If the `./data/chain.csv` file does not exist, and the `n_batches_to_explore` parameter is set to a large number in the JSON config file, the application will start by exploring a large number of blocks. This process may take some time before all the data is fetched and displayed on the dashboard.

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/solana-transaction-tracker.git
    cd solana-transaction-tracker
    ```

2. **Set Up a Virtual Environment (Optional but Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the Application:**

    ```bash
    python main.py
    ```

2. **Access the Dashboard:** Open your web browser and navigate to `http://127.0.0.1:8050` to view the Solana Transaction Tracker dashboard.

## Requirements

- Python 3.x
- `dash`
- `pandas`
- `plotly`
- `requests`
- `threading` (standard library)
- `matplotlib` 

For a complete list of dependencies, refer to the `requirements.txt` file.
