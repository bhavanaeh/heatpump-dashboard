Welcome to the **Heat Pump Efficiency Counter**, an interactive dashboard designed to demystify the process of selecting the best heating solutions, tailored specifically according to the local climate conditions in the United States.

**Why Heat Pumps?**

Heat pumps are a sustainable alternative to traditional heating systems, offering a more energy-efficient and environmentally friendly solution. During the heating season, heat pumps move heat from the cool outdoors into your warm house. During the cooling season, heat pumps move heat from your house into the outdoors. Because they transfer heat rather than generate heat, heat pumps can efficiently provide comfortable temperatures for your home!

**Goal of the Dashboard:**

Compared to traditional gas-powered furnaces, heat pumps' efficacy is heavily influenced by the local climate conditions. However, understanding the impact of weather on the performance of heat pumps can be challenging. This dashboard serves as a user-friendly tool aimed at simplifying this complexity! By integrating comprehensive weather data, this dashboard aims to offer personalized insights that should help in making informed decisions about heat pump installations.

**How to use the Heat Pump Efficacy Explorer Dashboard:**

1. <ins>Select Your Location</ins>: Use the city input field in the sidebar to type the name of your city. As you type, the dashboard will suggest city-state combinations based on the SimpleMaps data. Select your city from the autocomplete suggestions to ensure accurate weather data retrieval. You can also use the map to visualize the location of your selected city by moving the marker to the desired location on the map.

2. <ins>Date Range Selection</ins>: Below the city input, select the start and end dates for which you wish to analyze historical weather data. The default range is set from January 1, 2022, to January 1, 2024, but you can adjust it according to your needs within the bounds of available data (from January 1, 2020, to January 1, 2024).

3. <ins>Temperature Preferences</ins>:

    - **Temperature Units**: Choose your preferred temperature units (Fahrenheit or Celsius) using the radio buttons provided. The dashboard will automatically update data visualizations to reflect your choice.
    - **Temperature Threshold for Analysis**: Use the slider to set a specific temperature threshold that is of interest to you. This feature is crucial for visualizing how often temperatures fall above or below this threshold, providing insights into heat pump performance under varying temperature conditions.
    - **Adjusting Temperature Ranges**: Utilize the temperature range slider in the sidebar to filter the data table based on temperatures of interest. This functionality facilitates a detailed analysis of temperature distributions over your selected period, enabling a nuanced understanding of local climate patterns relevant to heat pump efficiency.

4. <ins>Plotting Options</ins>:

    - **Historical**: Navigate to the "Historical" tab to view a plot and table showing the historical weather data for your selected location and date range. The plot provides a visual representation of daily minimum temperatures, while the table summarizes the proportion of days falling within specified temperature ranges.You can also opt to display weekly or monthly rolling averages for a more comprehensive view.
    - **Forecast**: Navigate to the "Forecast" tab to view a plot and table showing the predicted future temperature trends based on the historical data. You can adjust the forecast trend to be either flat or linear and specify the number of years you want to forecast in the years to forecast tab in the sidebar. The forecast plot and table will update based on your inputs, providing a prediction of future weather patterns and their implications for heat pump performance in your selected location.

**How to run the code:**

The dashboard is built primarily using the Shiny library in Python. To run the code, the first step is to have Python 3.11 installed on your system. You can directly download and install Python from [python.org](https://www.python.org/).
Once you have Python installed, you can run the code by executing the following commands in your terminal:

 ```
        python3.11 -m pip install uv
        cd heatpump-dashboard
        uv venv
        source .venv/bin/activate
        uv pip install -r requirements.txt
        shiny run --reload --launch-browser ./app.py
```

 **Citations:**

- [SimpleMaps](https://simplemaps.com/data/us-cities) for the US city data used in this dashboard.
- [OpenMeteo](https://open-meteo.com/) for the weather data API used in this dashboard.
- [Prophet](https://facebook.github.io/prophet/) for the forecasting model used in this dashboard.
