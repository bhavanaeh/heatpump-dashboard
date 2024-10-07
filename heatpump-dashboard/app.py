"""
Bhavana Sundar (bsundar3)
CS 498 - End to End Data Science
University of Illinois Urbana-Champaign

A majority of this code is referrenced from the Shiny library documentation and the openmeteo_requests library documentation. 
I have referenced the SimpleMaps and OpenMeteo websites for the data used in this dashboard, 
Prophet documentation for the forecasting model used in this dashboard, 
Plotnine documentation for the plotting functions used in this dashboard, and 
ipyleaflet documentation for the map widget used in this dashboard.
"""

from shiny import App, Inputs, Outputs, Session, render, ui, reactive
from shiny.types import NavSetArg
from ipyleaflet import GeoJSON, Map, Marker 
from shinywidgets import output_widget, render_widget 
import pandas as pd
import openmeteo_requests
from retry_requests import retry
import requests_cache
from plotnine import ggplot, aes, geom_point, theme, element_text, labs, scale_x_datetime, element_line, element_rect, geom_hline, geom_line, scale_color_manual
from mizani.breaks import date_breaks
from mizani.formatters import date_format
from prophet import Prophet
import matplotlib.pyplot as plt


cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

url = "https://archive-api.open-meteo.com/v1/archive"

cities_list = pd.read_csv("data/cities.csv")["city_state"].tolist()

def navControls():
    """A function to create the navigation controls present in the navbar for the dashboard. This function returns a list of UI elements that are used to create the navbar and is modified based off on the documentation provided by the Shiny library: https://shiny.posit.co/py/api/core/ui.nav_panel.html#shiny.ui.nav_panel"""

    return [
        ui.nav_panel("Historical",ui.output_plot("getHistPlot"),ui.tags.hr(),ui.output_data_frame("getHistTable")),
        ui.nav_panel("Forecast",ui.output_plot("getForecastPlot"),ui.tags.hr(),ui.output_data_frame("getForecastTable")),
        ui.nav_panel("About",ui.markdown("""                           
        Welcome to the **Heat Pump Efficiency Counter**, an interactive dashboard designed to demystify the process of selecting the best heating solutions, tailored specifically according to the local climate conditions in the United States.
        
        **Why Heat Pumps?** 
                                         
        Heat pumps are a sustainable alternative to traditional heating systems, offering a more energy-efficient and environmentally friendly solution. During the heating season, heat pumps move heat from the cool outdoors into your warm house. During the cooling season, heat pumps move heat from your house into the outdoors. Because they transfer heat rather than generate heat, heat pumps can efficiently provide comfortable temperatures for your home!
                                         
        **Goal of the Dashboard:**
                                         
        Compared to traditional gas-powered furnaces, heat pumps' efficacy is heavily influenced by the local climate conditions. However, understanding the impact of weather on the performance of heat pumps can be challenging. This dashboard serves as a user-friendly tool aimed at simplifying this complexity! By integrating comprehensive weather data, this dashboard aims to offer personalized insights that should help in making informed decisions about heat pump installations.[]

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
        
        ---
                                         
        Developed as a part of the coursework for [CS 498 : End to End Data Science](https://daviddalpiaz.github.io/cs498-sp24/syllabus.html) at the University of Illinois Urbana-Champaign by Bhavana Sundar (bsundar3)
                                         
"""
                                         )),
        ui.nav_spacer(),
    ]

app_ui = ui.page_sidebar(  
    
    ui.sidebar(
                
        ui.input_selectize("city", "City",choices=cities_list,selected='Urbana, Illinois'),
        ui.div(
            ui.output_text("loc_coords",),align="center",
        ),
        ui.input_date_range("dateRange", "Dates",start="2022-01-01",end="2024-01-01",min="2020-01-01",max="2024-01-01"),
        ui.input_numeric("yearsForecast", "Years to Forecast", min=1,max=5,value=1),
        ui.input_radio_buttons("getForecastPlot", "Forecast Trend", {"flat": "Flat", "linear": "Linear"}),
        ui.input_radio_buttons("units", "Units", {"F": "Fahrenheit", "C": "Celsius"}),
        ui.output_ui("plotTemperature"),
        ui.input_checkbox("weeklyAvg", "Weekly Rolling Average", False),
        ui.input_checkbox("monthlyAvg", "Monthly Rolling Average", False),
        ui.output_ui("tableTemperatureRange"),
        ui.tags.hr(),
        output_widget("map"),
        open="always", bg="#f8f8f8", width=350, margin="0 auto", display = "block",
    ),
    ui.div(
        ui.page_navbar(
            *navControls(),
            id="navbar_id",
            header=ui.div(
                {"style": "width:576; margin: 0 auto"},
            ui.tags.style(
                """
                h4 {
                    margin-top: 3em;
                }
                """
            ),
        ),
        ),
    ),
    title="Daily Heat Pump Efficiency Counter"
)

def server(input, output, session):

    @output
    @render.ui()
    def plotTemperature():
        """A function to create a dynamic slider based on the selected temperature units."""
        units = input.units()
        if units == "C":
            return ui.input_slider("plotTemperature", "Plot Temperature", -25, 10, -15, step=1)
        else:
            return ui.input_slider("plotTemperature", "Plot Temperature", -15, 50, 5, step=1)
        
    
    @output
    @render.ui()
    def tableTemperatureRange():
        """A function to create a dynamic slider based on the selected temperature range."""
        units = input.units()
        if units == "C":
            return ui.input_slider("tableTemperature", "Table Temperatures", -30, 15, [-20, -10], step=1)
        else:  # Default to Fahrenheit
            return ui.input_slider("tableTemperature", "Table Temperatures", -25, 60, [0, 15], step=1)
        
    
    @reactive.Calc()
    def getCoords():
        """A function to retrieve the latitude and longitude coordinates of the selected city."""

        df = pd.read_csv("data/cities.csv")
        city_data = df[df['city_state'] == str(input.city())]
        lat = city_data['lat'].values[0]
        lng = city_data['lng'].values[0]
    
        params = {
	    "latitude": lat,
        "longitude": lng,
        "start_date": input.dateRange()[0],
        "end_date": input.dateRange()[1],
        "daily": "temperature_2m_min",
        "temperature_unit": "fahrenheit" if input.units() == "F" else "celsius",
        }

        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        lat = response.Latitude()
        lng = response.Longitude()
        ans = "{:.4f}°N, {:.4f}°E".format(lat, lng)
        return ans
    
    @render.data_frame()
    def getHistTable():
        """A function to retrieve the historical weather tabular data for the selected city and temperature range."""

        startTemp = input.tableTemperature()[0]
        endTemp = input.tableTemperature()[1]

        table = []

        df = pd.read_csv("data/cities.csv")
        city_data = df[df['city_state'] == str(input.city())]
        lat = city_data['lat'].values[0]
        lng = city_data['lng'].values[0]
    
        params = {
	    "latitude": lat,
        "longitude": lng,
        "start_date": input.dateRange()[0],
        "end_date": input.dateRange()[1],
        "daily": "temperature_2m_min",
        "temperature_unit": "fahrenheit" if input.units() == "F" else "celsius",
        }

        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        daily = response.Daily()
        daily_temperature_2m_min = daily.Variables(0).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds=daily.Interval()),
            inclusive = "left"
        )}
        
        daily_data["temperature_2m_min"] = daily_temperature_2m_min

        daily_dataframe = pd.DataFrame(data = daily_data)
        daily_dataframe['date'] = daily_dataframe['date'].dt.date

        for t in range(endTemp, startTemp-1, -1):
            days_below = daily_dataframe[daily_dataframe['temperature_2m_min'] < t].shape[0]
            proportin_below = days_below / daily_dataframe.shape[0]
            table.append({"Temp": t, "Days Below": days_below, "Proportion Below": round(proportin_below,3)})

        table_df = pd.DataFrame(table)

        return render.DataGrid(table_df,width="100%",height='fit-content')


    @render.plot()
    def getHistPlot():
        """A function to retrieve the historical weather plot for the selected city for a specific date range and threshold temperature. Also calculates weekly and monthly rolling averages if selected."""

        df = pd.read_csv("data/cities.csv")
        city_data = df[df['city_state'] == str(input.city())]
        lat = city_data['lat'].values[0]
        lng = city_data['lng'].values[0]
    
        params = {
	    "latitude": lat,
        "longitude": lng,
        "start_date": input.dateRange()[0],
        "end_date": input.dateRange()[1],
        "daily": "temperature_2m_min",
        "temperature_unit": "fahrenheit" if input.units() == "F" else "celsius",
        }

        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        daily = response.Daily()
        daily_temperature_2m_min = daily.Variables(0).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds=daily.Interval()),
            inclusive = "left"
        )}
        
        daily_data["temperature_2m_min"] = daily_temperature_2m_min

        daily_dataframe = pd.DataFrame(data = daily_data)
        daily_dataframe['date'] = daily_dataframe['date'].dt.date

        threshold = input.plotTemperature()
        daily_dataframe['temp_category'] = ['below' if x < threshold else 'above' for x in daily_dataframe['temperature_2m_min']]

        
        p = (
            ggplot(daily_dataframe, aes(x='date', y='temperature_2m_min', color='temp_category'))
            + geom_point(alpha=0.9)
            + labs(title='', x='', y='Daily Minimum Temperature °'+input.units())
            +scale_x_datetime(
            breaks=date_breaks('3 months'),  
            labels=date_format('%Y-%m'))
            +scale_color_manual(values={'below': '#D3D3D3', 'above': 'black'})
            + theme(
            panel_background=element_rect(fill='white', colour='white'),
            panel_border=element_rect(colour='#9E9E9E', fill=None, size=1),
            plot_background=element_rect(color='white', size=2),
            panel_grid_major=element_line(color='lightgrey', size=0.5),
            legend_position="none"
            )
            +geom_hline(yintercept=input.plotTemperature(), color="#A9A9A9", size=0.5)

        )

        if input.weeklyAvg():
            daily_dataframe['weekly_avg'] = daily_dataframe['temperature_2m_min'].rolling(window=7).mean()
            p += geom_line(aes(y='weekly_avg',group=1),color="#FF8C00",size=0.9)

        if input.monthlyAvg():
            daily_dataframe['monthly_avg'] = daily_dataframe['temperature_2m_min'].rolling(window=30).mean()
            p += geom_line(aes(y='monthly_avg',group=1),color="#1C90FF",size=0.9)

        return p
    
    @render.plot()
    def getForecastPlot():
        """A function to retrieve the forecasted weather plot for the selected city for a specific date range and threshold temperature. Also calculates weekly and monthly rolling averages if selected."""

        df = pd.read_csv("data/cities.csv")
        city_data = df[df['city_state'] == str(input.city())]
        lat = city_data['lat'].values[0]
        lng = city_data['lng'].values[0]
    
        params = {
	    "latitude": lat,
        "longitude": lng,
        "start_date": input.dateRange()[0],
        "end_date": input.dateRange()[1],
        "daily": "temperature_2m_min",
        "temperature_unit": "fahrenheit" if input.units() == "F" else "celsius",
        }

        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        daily = response.Daily()
        daily_temperature_2m_min = daily.Variables(0).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds=daily.Interval()),
            inclusive = "left"
        )}
        
        daily_data["temperature_2m_min"] = daily_temperature_2m_min

        daily_dataframe = pd.DataFrame(data = daily_data)
        daily_dataframe['date'] = daily_dataframe['date'].dt.date

        prophet_df = daily_dataframe.rename(columns={'date': 'ds', 'temperature_2m_min': 'y'})
        model = Prophet(growth='linear' if input.getForecastPlot() == 'linear' else 'flat')
        model.fit(prophet_df)
        forecast_model = model.make_future_dataframe(periods=365*int(input.yearsForecast()))
        forecast = model.predict(forecast_model).tail(365*int(input.yearsForecast()))
        p = model.plot(forecast, xlabel='', ylabel='Daily Minimum Temperature °'+input.units())
        plt.axhline(y=input.plotTemperature(), color='#A9A9A9')

        return p

    @render.data_frame()
    def getForecastTable():
        """A function to retrieve the forecasted weather tabular data for the selected city and temperature range."""

        startTemp = input.tableTemperature()[0]
        endTemp = input.tableTemperature()[1]

        table = []

        df = pd.read_csv("data/cities.csv")
        city_data = df[df['city_state'] == str(input.city())]
        lat = city_data['lat'].values[0]
        lng = city_data['lng'].values[0]
    
        params = {
	    "latitude": lat,
        "longitude": lng,
        "start_date": input.dateRange()[0],
        "end_date": input.dateRange()[1],
        "daily": "temperature_2m_min",
        "temperature_unit": "fahrenheit" if input.units() == "F" else "celsius",
        }

        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        daily = response.Daily()
        daily_temperature_2m_min = daily.Variables(0).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds=daily.Interval()),
            inclusive = "left"
        )}
        
        daily_data["temperature_2m_min"] = daily_temperature_2m_min

        daily_dataframe = pd.DataFrame(data = daily_data)
        daily_dataframe['date'] = daily_dataframe['date'].dt.date

        prophet_df = daily_dataframe.rename(columns={'date': 'ds', 'temperature_2m_min': 'y'})
        model = Prophet(growth='linear' if input.getForecastPlot() == 'linear' else 'flat',interval_width=0.95)
        model.fit(prophet_df)
        forecast_model = model.make_future_dataframe(periods=365*int(input.yearsForecast()))
        forecast = model.predict(forecast_model).tail(365*int(input.yearsForecast()))
        
        for t in range(endTemp, startTemp-1, -1):
            days_below = forecast[forecast['yhat_lower'] < t].shape[0]
            total_days = forecast.shape[0]
            proportion_below = days_below / total_days            
            table.append({"Temp": t, "Days Below": days_below, "Proportion Below": round(proportion_below,3)})

        table_df = pd.DataFrame(table)

        return render.DataGrid(table_df,width="100%",height='fit-content')

    
    @render.text()
    def loc_coords():
        '''A function to display the latitude and longitude coordinates of the selected city.'''

        return getCoords()
    
    @render_widget()
    def map():
        '''A function to display the map with the marker at the selected city's location. This function uses the ipyleaflet library and is based of the documentation provided at: https://shiny.posit.co/py/components/outputs/map-ipyleaflet/'''

        ans = getCoords()
        l1,l2 = ans.split(", ")
        lat = l1[:-2]
        lng = l2[:-2]
        map = Map(center=(lat, lng), zoom=12, layout={'height': '200px'}) 
        point = Marker(location=(lat, lng), draggable=True)  
        map.add_layer(point)
        return map

app = App(app_ui, server)