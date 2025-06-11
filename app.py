import pandas as pd
import plotly.express as px



from faicons import icon_svg
from shinywidgets import render_plotly
from data import df, app_dir
from shiny import reactive
from shiny.express import input, render, ui

ui.include_css(app_dir / "styles.css")

with ui.sidebar(title="Filter controls", open="desktop"):
    mm_budget = (min(df['Budget(INR)']), max(df['Budget(INR)']))
    ui.input_slider("Budget", "Budget(INR)",min=mm_budget[0], max=mm_budget[1], value=mm_budget, pre=chr(0x20B9))
    ui.input_checkbox_group(
        "success",
        "success(Box Office-to-Budget Ratio > 3)",
        [True, False],
        selected=[True, False],
    )
    ui.input_action_button("reset", "Reset filter")

with ui.layout_column_wrap(fill=False):
    
    with ui.value_box(showcase=icon_svg("film")):
        "Number of movies"

        @render.text
        def count():
            return filtered_df().shape[0]

    with ui.value_box(showcase=icon_svg("indian-rupee-sign")):
        'Operating Profit'

        @render.text
        def count_op():
            return filtered_df()['Operating Profit'].mean()
        
with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Revenue by Genre")

        @render_plotly
        def Genre_stat():
            fig = px.pie(filtered_df(), values='Revenue(INR)', names='Genre')
            return fig

    with ui.card(full_screen=True):
        ui.card_header("bollywood movies data")

        @render.data_frame
        def summary_statistics():
            cols = [
                'Movie_Name', 'Release_Period', 'Whether_Remake', 'Whether_Franchise',
                'Genre', 'New_Actor', 'New_Director', 'New_Music_Director', 'Lead_Star',
                'Director', 'Music_Director', 'Number_of_Screens', 'Revenue(INR)',
                'Budget(INR)', 'Operating Profit', 'Box Office-to-Budget Ratio',
                'Per-Theater Average(PTA)', 'success'
            ]
            return render.DataGrid(filtered_df()[cols], filters=True)
    
with ui.layout_columns(col_widths=[8, 4]):


    with ui.card(full_screen=True):
        
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Revenue by Budget"

            with ui.popover(title="Add a color variable", placement="top"):
                icon_svg("gear")
                ui.input_radio_buttons(
                    "scatter_color", None,
                    ["Genre", "Release_Period", "Whether_Remake", "Whether_Franchise"],
                    inline=True
                )
        @render_plotly
        def scatterplot():
            color = input.scatter_color()
            return px.scatter(
                filtered_df(),
                x='Budget(INR)',
                y='Revenue(INR)',
                color=None if color == "none" else color,
                hover_data=['Movie_Name', 'Box Office-to-Budget Ratio'],
                marginal_x="histogram"
            )

    with ui.card(full_screen=True):
        ui.card_header("Lead Stars by number of films")

        @render.data_frame
        def count_ls():
            dls = filtered_df().groupby('Lead_Star')['Movie_Name'].count()
            dls = dls.reset_index(name='Number of Films')
            return render.DataGrid(dls, filters=True)

@reactive.calc
def filtered_df():
    filt_df = df.copy()

    filt_df['Operating Profit'] = filt_df['Revenue(INR)'] - filt_df['Budget(INR)']
    filt_df['Box Office-to-Budget Ratio'] = filt_df['Revenue(INR)'] / filt_df['Budget(INR)']
    filt_df['Per-Theater Average(PTA)'] = filt_df['Revenue(INR)'] / filt_df['Number_of_Screens']
    filt_df['success'] = filt_df['Box Office-to-Budget Ratio'] > 3
    
    filt_df = filt_df.loc[filt_df['Budget(INR)'] <= input.Budget()[1]]
    filt_df = filt_df.loc[filt_df['Budget(INR)'] >= input.Budget()[0]]
    input_values = input.success()
    bool_values = [False if x == 'on' else True for x in input_values]
    filt_df = filt_df[filt_df["success"].isin(bool_values)]
    return filt_df

@reactive.effect
@reactive.event(input.reset)
def _():
    mm_budget = (min(df['Budget(INR)']), max(df['Budget(INR)']))
    ui.update_slider("Budget", value=mm_budget)
    ui.update_checkbox_group("success", selected=[True, False])


