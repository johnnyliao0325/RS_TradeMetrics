**for RS-Insight Project**

# RS-Insight: A Relative Strength Analysis Toolkit

## Overview

RS-Insight is a specialized toolkit designed to analyze Relative Strength (RS) for stock trading. It provides several functionalities to calculate, evaluate, and visualize RS indicators, helping traders make better decisions. The project includes methods for initializing and updating RS indicators, calculating moving averages, and comparing stocks based on RS metrics. The tool is built using Python and leverages multiple libraries to manage data, perform calculations, and generate notifications.

## Features

### 1. **Daily Stock Data Updates**

- Step 1: **Download and Update Stock Data**  
  Downloads and updates daily stock information for all listed symbols. Updates include historical data, moving averages, and volume calculations.

### 2. **Technical Indicator Calculator**

- Step 2: **Calculate Technical Indicators**  
  Calculates various technical indicators for each stock, including Moving Averages, Relative Strength Index (RSI), MACD, and custom RS-based calculations.

### 3. **Daily RS Rate Calculation**

- Step 3: **Calculate RS Rates**  
  Calculates the RS rate for each stock based on moving averages of different periods. Supports RS and Exponential RS (ERS) metrics, with ranking and normalization.

### 4. **Historical RS Initialization**

- Step 4: **Initialize RS for Historical Data**  
  Initializes the RS rate for all historical data available. This feature is useful for preparing data for backtesting and initializing historical RS values for analysis.

### 5. **Maximum/Minimum RS Tracker**

- Step 5: **Track RS Max/Min Values**  
  Tracks if RS values are at their maximum or minimum during a specified window of time. Uses TA-Lib to perform efficient maximum and minimum calculations.

### 6. **Daily Stock Summary Generator**

- Step 6: **Generate Daily Summary Report**  
  Generates a daily summary report containing all stock information and calculated technical indicators. Produces a comprehensive `.xlsx` file summarizing the day's data.

## Directory Structure

```
- src/
    - __init__.py
    - daily_stock_summary.py  # Generates daily summaries of stock data
    - indicator_calculator.py # Calculates indicators such as SMA, MACD, etc.
    - line_notifier.py        # Handles notifications via Line API
    - rs_max_calculator.py    # Calculates if RS metrics are at max/min for specific windows
    - rs_rate_calculator.py   # Updates daily RS rates for all stocks
    - rs_rate_initialize.ipynb# Initializes historical RS rates for all stocks
    - stock_data_handler.py   # Manages downloading and updating stock data

- tests/
    - temp_data/              # Temporary files for testing purposes
    - test_stock_data_handler.py # Unit tests for StockDataHandler class
    - test.ipynb              # Miscellaneous testing notebook

- 全個股條件篩選/  # Directory for filtering specific stock conditions
- .gitignore
- main.py                    # Main script that coordinates all tasks and orchestrates the workflow
```

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/RS-Insight.git
   cd RS-Insight
   ```

2. Install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Set up your Line API token in the appropriate file (`line_notifier.py`) to receive notifications.

## Usage

### Running the Project

You can run the main program by executing:

```sh
python main.py
```

This script handles all the daily tasks, including updating stock data, calculating indicators, generating daily summaries, and updating RS rates.

### Configurations

- `main.py` can be customized by setting task conditions to determine which processes to run.
- Constants such as `data_dir`, `delay_days`, and `output_directory` are configured at the top of the `main.py` script for easy access.


## Acknowledgements

- **TA-Lib** for providing efficient calculation of various technical indicators.
- **Yahoo Finance API** for stock data.
- **Pandas** for data manipulation and analysis.
- **Line Notify** for notification services.

