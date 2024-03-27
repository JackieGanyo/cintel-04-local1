import plotly.express as px
from shiny.express import input, ui
from shinywidgets import render_plotly, render_widget
import palmerpenguins # This package provides the Palmer Penguins dataset
import pandas as pd
import seaborn as sns
from shiny import App, reactive, render, req
import ipyleaflet as ipyl


# Palmer Penguins Dataset
# Column names for the penguins data set include:
# - species: Penguin species (Chinstrap, Adelie, or Gentoo)
# - island:  island name (Dream, Torgersen, or Biscoe)
# - bill_length_mm:  length of the bill in millimeters
# - bill_depth_mm:  depth of the bill in millimeters
# - flipper_length_mm:  length of the flipper in millimeters
# - body_mass_g:  body mass in grams
# - sex:  MALE or FEMALE

# Load the dataset into a pandas Dataframe
#Use the built-in function to load the Palmer Penguins dataset
penguins_df = palmerpenguins.load_penguins()

# Name your page
ui.page_opts(title="Palmer Penguins JGanyo", fillable=False)

# Creates user sidebar user interactive 
#and level 2 heading 'Sidebar'
with ui.sidebar(open= "open"): 
    ui.h2 ("Sidebar")

    # Creates a dropdown input to choose a column 
    ui.input_selectize(
        "selected_attribute",
        "Select Penguin Attribute",
        ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
    )


    #Create numeric input for the number of Plotly histogram bins 
    ui.input_numeric("plotly_bin_count", "Number of Bins", 25) 
   
    #Create Slider input for the number of Seaborn bins
    ui.input_slider("seaborn_bin_count", "Seaborn Bin Count", 1, 50, 5) 

    #Create a checkbox group input
    ui.input_checkbox_group(
        "selected_species_list", 
        "Species", 
        ["Adelie", "Gentoo", "Chinstrap" ], 
        selected=["Adelie", "Gentoo", "Chinstrap"], 
        inline=True,)
    
    ui.input_checkbox_group(  
        "penguin_islands",
        "Islands",
        ["Torgersen", "Biscoe", "Dream"],
        selected=["Dream"],
        inline=True,
    )
    
# Add a hyperlink to GitHub Repo
    ui.a("Ganyo GitHub",
         href="https://github.com/JackieGanyo/cintel-02-data", 
         target="_blank")
    
    #Set horizontal rule
    ui.hr() 

with ui.layout_columns():
    with ui.card(full_screen=True):
        "Penguins Table"
        @render.data_frame
        def render_penguins_table():
            return render.DataTable(filtered_data())

    with ui.card(full_screen=True):  # Full screen option
            "Penguins Data Grid"
            @render.data_frame
            def render_penguins_grid():
                return filtered_data()

#Set horizontal rule
ui.hr()

#Create histograms and scatterplots using Plotly and Seaborn

with ui.layout_columns():
    
    #Plotly Histogram Card
    with ui.card(full_screen=True):
        "Plotly By Island Histogram"
        
         # Define custom colors for each category
        custom_colors = {'Dream': 'skyblue', 'Biscoe': 'salmon', 'Torgersen': 'lightgreen'}

        # Create a function to render the Plotly histogram
        @render_plotly
        def render_plotly_histogram():
            return px.histogram(filtered_data(), 
                                x="species", 
                                color="island",
                                color_discrete_map=custom_colors)
    #Seaborn Histogram Card
    with ui.card(full_screen=True):
         "Seaborn Histogram"
         #Create custom colors by species
         
         
         @render.plot(alt="A Seaborn Histogram with penguin species by island")
         def plot():
                    sns.set_style("whitegrid") # Set Seaborn style to white
            
                    ax = sns.histplot(
                            filtered_data(), 
                            x="island",
                            y="species",
                            multiple="stack"
                                                )
                    ax.set_title("Seaborn Palmer Penguins by Island")
                    ax.set_xlabel("Island")
                    ax.set_ylabel("Species", rotation=90)
                    return ax
             
    #Plotly Scatterplot Card
    with ui.card(full_screen=True):
        "Plotly Scatterplot: Species"        
        @render_plotly
        def ploty_scatterplot():
            
            return px.scatter(
                filtered_data(),
                x="body_mass_g",
                y="year",
                color="species",
                #facet_row="species", 
                facet_col="sex",
                labels={"body_mass_g": "Mass (g)", "year": "Year"})

#Create interactive map of penguins by location

penguin_islands = {
    "Biscoe": (-65.7474, -65.9164),
    "Dream": (-64.7333, -64.2333),
    "Torgersen": (-64.7667, -64.0833),
}
ui.input_select('center', "Centers", choices=list(penguin_islands.keys()))

@render_widget
def map():
    return ipyl.Map(zoom=6)

@reactive.effect
def _():
    map.widget.center = penguin_islands[input.center()]
 
# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

# Add a reactive calculation to filter the data
# By decorating the function with @reactive, we can use the function to filter the data
# The function will be called whenever an input functions used to generate that output changes.
# Any output that depends on the reactive function (e.g., filtered_data()) will be updated when the data changes.

@reactive.calc
def filtered_data():
    return penguins_df[(penguins_df["species"].isin(input.selected_species_list())) &
        (penguins_df["island"].isin(input.penguin_islands()))]
