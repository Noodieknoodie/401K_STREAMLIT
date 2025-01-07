"🟰  Row Layout
Submitted by Lukas Masuch

Summary
A multi-element horizontal container that places elements in a row.

Functions
row
Insert a multi-element, horizontal container into your app.

This function inserts a container into your app that can hold a number of elements as defined in the provided spec. Elements can be added to the returned container by calling methods directly on the returned object.

Parameters:

Name	Type	Description	Default
spec	SpecType	Controls the number and width of cells to insert in the row. Can be one of: * An integer specifying the number of cells. All cells will have equal width in this case. * An iterable of numbers (int or float) that specifies the relative width of each cell. For instance, [0.7, 0.3] creates two cells where the first one occupies 70% of the available width, and the second one occupies 30%. Or, [1, 2, 3] creates three cells where the second one is twice as wide as the first one, and the third one is three times that width.	required
gap	Optional[str]	"small", "medium", or "large" The size of the gap between cells, can be "small", "medium", or "large". This parameter specifies the visual space between the elements within the row. Defaults to "small".	'small'
vertical_align	Literal['top', 'center', 'bottom']	The vertical alignment of the cells in the row. It can be either "top", "center", or "bottom", aligning the contents of each cell accordingly. Defaults to "top".	'top'
Returns:

Type	Description
GridDeltaGenerator	grid.GridDeltaGenerator: RowContainer A row container object. Elements can be added to this row by calling methods directly on the returned object.
Source code in src/streamlit_extras/row/__init__.py
Import:


from streamlit_extras.row import row 
Examples
example

def example():
    random_df = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

    row1 = row(2, vertical_align="center")
    row1.dataframe(random_df, use_container_width=True)
    row1.line_chart(random_df, use_container_width=True)

    row2 = row([2, 4, 1], vertical_align="bottom")

    row2.selectbox("Select Country", ["Germany", "Italy", "Japan", "USA"])
    row2.text_input("Your name")
    row2.button("Send", 
	
	
	----
	
	
	♠️  Metric Cards
Submitted by Chanin Nantasenamat

Summary
Restyle metrics as cards

Functions
style_metric_cards
Applies a custom style to st.metrics in the page

Parameters:

Name	Type	Description	Default
background_color	str	Background color. Defaults to "#FFF".	'#FFF'
border_size_px	int	Border size in pixels. Defaults to 1.	1
border_color	str	Border color. Defaults to "#CCC".	'#CCC'
border_radius_px	int	Border radius in pixels. Defaults to 5.	5
border_left_color	str	Borfer left color. Defaults to "#9AD8E1".	'#9AD8E1'
box_shadow	bool	Whether a box shadow is applied. Defaults to True.	True
Source code in src/streamlit_extras/metric_cards/__init__.py
Import:


from streamlit_extras.metric_cards import style_metric_cards 
Examples
example

def example():
    col1, col2, col3 = st.columns(3)

    col1.metric(label="Gain", value=5000, delta=1000)
    col2.metric(label="Loss", value=5000, delta=-1000)
    col3.metric(label="No Change", value=5000, delta=0)

    style_metric_cards()
	
	
	---
	
	💠  Grid Layout
Submitted by Lukas Masuch

Summary
A multi-element container that places elements on a specified grid layout.

Functions
grid
Insert a multi-element, grid container into your app.

This function inserts a container into your app that arranges multiple elements in a grid layout as defined by the provided spec. Elements can be added to the returned container by calling methods directly on the returned object.

Parameters:

Name	Type	Description	Default
*spec	int | Iterable[int]	One or many row specs controlling the number and width of cells in each row. Each spec can be one of: * An integer specifying the number of cells. In this case, all cells have equal width. * An iterable of numbers (int or float) specifying the relative width of each cell. E.g., [0.7, 0.3] creates two cells, the first one occupying 70% of the available width and the second one 30%. Or, [1, 2, 3] creates three cells where the second one is twice as wide as the first one, and the third one is three times that width. The function iterates over the provided specs in a round-robin order. Upon filling a row, it moves on to the next spec, or the first spec if there are no more specs.	()
gap	Optional[str]	The size of the gap between cells, specified as "small", "medium", or "large". This parameter defines the visual space between grid cells. Defaults to "small".	'small'
vertical_align	Literal['top', 'center', 'bottom']	The vertical alignment of the cells in the row. Defaults to "top".	'top'
Source code in src/streamlit_extras/grid/__init__.py
Import:


from streamlit_extras.grid import grid 
Examples
example

def example():
    random_df = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

    my_grid = grid(2, [2, 4, 1], 1, 4, vertical_align="bottom")

    # Row 1:
    my_grid.dataframe(random_df, use_container_width=True)
    my_grid.line_chart(random_df, use_container_width=True)
    # Row 2:
    my_grid.selectbox("Select Country", ["Germany", "Italy", "Japan", "USA"])
    my_grid.text_input("Your name")
    my_grid.button("Send", use_container_width=True)
    # Row 3:
    my_grid.text_area("Your message", height=40)
    # Row 4:
    my_grid.button("Example 1", use_container_width=True)
    my_grid.button("Example 2", use_container_width=True)
    my_grid.button("Example 3", use_container_width=True)
    my_grid.button("Example 4", use_container_width=True)
    # Row 5 (uses the spec from row 1):
    with my_grid.expander("Show Filters", expanded=True):
        st.slider("Filter by Age", 0, 100, 50)
        st.slider("Filter by Height", 0.0, 2.0, 1.0)
        st.slider("Filter by Weight", 0.0, 100.0, 50.0)
    my_grid.dataframe(random_df, use_container_width=True)
	
	---
	
	
	🎨  Styleable Container
Submitted by Lukas Masuch

Summary
A container that allows to style its child elements using CSS.

Functions
stylable_container
Insert a container into your app which you can style using CSS. This is useful to style specific elements in your app.

Parameters:

Name	Type	Description	Default
key	str	The key associated with this container. This needs to be unique since all styles will be applied to the container with this key.	required
css_styles	str | List[str]	The CSS styles to apply to the container elements. This can be a single CSS block or a list of CSS blocks.	required
Returns:

Name	Type	Description
DeltaGenerator	'DeltaGenerator'	A container object. Elements can be added to this container using either the 'with' notation or by calling methods directly on the returned object.
Source code in src/streamlit_extras/stylable_container/__init__.py
Import:


from streamlit_extras.stylable_container import stylable_container 
Examples
example

def example():
    with stylable_container(
        key="green_button",
        css_styles="""
            button {
                background-color: green;
                color: white;
                border-radius: 20px;
            }
            """,
    ):
        st.button("Green button")

    st.button("Normal button")

    with stylable_container(
        key="container_with_border",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px)
            }
            """,
    ):
        st.markdown("This is a container with a border.")
		
		
		
		---
		
		
		🖱️  Switch page function
Submitted by Zachary Blackwood

Summary
Function to switch page programmatically in a MPA

Functions
switch_page
Switch page programmatically in a multipage app

Parameters:

Name	Type	Description	Default
page_name	str	Target page name	required
Source code in src/streamlit_extras/switch_page_button/__init__.py
Import:


from streamlit_extras.switch_page_button import switch_page 
Examples
example

def example():
    want_to_contribute = st.button("I want to contribute!")
    if want_to_contribute:
        switch_page("Contribute")
		
		
		---
		
		
		🎚  Vertical Slider
Submitted by Carlos D. Serrano

Summary
Continuous Vertical Slider with color customizations

Docstring
Visit the PyPI page for more information.

Examples
example

def example():
    st.write("## Vertical Slider")
    vertical_slider(
        key="slider",
        default_value=25,
        step=1,
        min_value=0,
        max_value=100,
        track_color="gray",  # optional
        thumb_color="blue",  # optional
        slider_color="red",  # optional
    )
	
	
	---
	
	
	ple
⬇️  Bottom Container
Submitted by Lukas Masuch

Summary
A multi-element container that sticks to the bottom of the app.

Functions
bottom
Insert a multi-element container that sticks to the bottom of the app.

Note that this can only be in the main body of the app, and not in other parts e.g. st.sidebar

Source code in src/streamlit_extras/bottom_container/__init__.py
Import:


from streamlit_extras.bottom_container import bottom 
Examples
example

def example():
    st.write("This is the main container")

    with bottom():
        st.write("This is the bottom container")
        st.text_input("This is a text input in the bottom container")
		
		---
		
		
		
		  Dataframe explorer UI
Submitted by Streamlit Data Team!

Summary
Let your viewers explore dataframes themselves! Learn more about it on this blog post

Functions
dataframe_explorer
Adds a UI on top of a dataframe to let viewers filter columns

Parameters:

Name	Type	Description	Default
df	DataFrame	Original dataframe	required
case	bool	If True, text inputs will be case sensitive. Defaults to True.	True
Returns:

Type	Description
DataFrame	pd.DataFrame: Filtered dataframe
Source code in src/streamlit_extras/dataframe_explorer/__init__.py
Import:


from streamlit_extras.dataframe_explorer import dataframe_explorer 
Examples
example_one

def example_one():
    dataframe = generate_fake_dataframe(
        size=500, cols="dfc", col_names=("date", "income", "person"), seed=1
    )
    filtered_df = dataframe_explorer(dataframe, case=False)
    st.dataframe(filtered_df, use_container_width=True)
	
	---
	
	
	🔖  Tags
Submitted by Maggie Liu

Summary
Display tags like github issues!

Functions
tagger_component
Displays tags next to your text.

Parameters:

Name	Type	Description	Default
content	str	Content to be tagged	required
tags	list	A list of tags to be displayed next to the content	required
color_name	list[str] | str | None	A list or a string that indicates the color of tags. Choose from lightblue, orange, bluegreen, blue, violet, red, green, yellow	None
text_color_name	list[str] | str | None	A list or a string that indicates the text color of tags.	None
Source code in src/streamlit_extras/tags/__init__.py
Import:


from streamlit_extras.tags import tagger_component 
Examples
example

def example():
    tagger_component("Here is a feature request", ["p2", "🚩triaged", "backlog"])
    tagger_component(
        "Here are colored tags",
        ["turtle", "rabbit", "lion"],
        color_name=["blue", "orange", "lightblue"],
    )
    tagger_component(
        "Annotate the feature",
        ["hallucination"],
        color_name=["blue"],
    )
	
	---
	
	
	✔️  To-do items
Submitted by Arnaud Miribel

Summary
Simple Python function to create to-do items in Streamlit!

Functions
to_do
Create a to_do item

Parameters:

Name	Type	Description	Default
st_commands	_type_	List of (cmd, args) where cmd is a streamlit command and args are the arguments of the command	required
checkbox_id	str	Use as a key to the checkbox	required
Returns:

Name	Type	Description
None		Prints the to do list
Source code in src/streamlit_extras/stodo/__init__.py
Import:


from streamlit_extras.stodo import to_do 
You should add this to the top of your .py file 🛠

Examples
example

def example():
    to_do(
        [(st.write, "☕ Take my coffee")],
        "coffee",
    )
    to_do(
        [(st.write, "🥞 Have a nice breakfast")],
        "pancakes",
    )
    to_do(
        [(st.write, ":train: Go to work!")],
        "work",
    )
	
	---
	
	🔑  Keyup text input
Submitted by Zachary Blackwood

Summary
A text input that updates with every key press

Docstring
Visit the PyPI page for more information.

Examples
example

def example():
    st.write("## Notice how the output doesn't update until you hit enter")
    out = st.text_input("Normal text input")
    st.write(out)
    st.write("## Notice how the output updates with every key you press")
    out2 = st_keyup("Keyup input")
    st.write(out2)
example_with_debounce

def example_with_debounce():
    st.write("## Notice how the output doesn't update until 500ms has passed")
    out = st_keyup("Keyup with debounce", debounce=500)
    st.write(out)
	
	
	---
	
	🗳️  No-Default Selectbox
Submitted by Zachary Blackwood

Summary
Just like st.selectbox, but with no default value -- returns None if nothing is selected.

Meant to be a solution to https://github.com/streamlit/streamlit/issues/949

Functions
selectbox
A selectbox that returns None unless the user has explicitly selected one of the options. All arguments are passed to st.selectbox except for no_selection_label, which is used to specify the label of the option that represents no selection.

Parameters:

Name	Type	Description	Default
no_selection_label	str	The label to use for the no-selection option. Defaults to "---".	required
Source code in src/streamlit_extras/no_default_selectbox/__init__.py
Import:


from streamlit_extras.no_default_selectbox import selectbox 
Examples
example

def example():
    st.write(
        """
        This is an example of a selectbox that returns None unless the user has
        explicitly selected one of the options.

        The selectbox below has no default value, so it will return None until the
        user selects an option.
        """
    )
    result = selectbox("Select an option", ["A", "B", "C"])
    st.write("Result:", result)

    result = selectbox(
        "Select an option with different label",
        ["A", "B", "C"],
        no_selection_label="<None>",
    )
    st.write("Result:", result)
	
	
	---
	
	
	➡️  Toggle button
Submitted by Arnaud Miribel

Summary
Toggle button just like in Notion!

Functions
stoggle
Displays a toggle widget in Streamlit

Parameters:

Name	Type	Description	Default
summary	str	Summary of the toggle (always shown)	required
content	str	Content shown after toggling	required
Source code in src/streamlit_extras/stoggle/__init__.py
Import:


from streamlit_extras.stoggle import stoggle 
You should add this to the top of your .py file 🛠

Examples
example

def example():
    stoggle(
        "Click me!",
        """🥷 Surprise! Here's some additional content""",
    )
Output (beta)


---
  Color ya Headers
Submitted by Johannes Rieke / Tyler Richards

Summary
This function makes headers much prettier in Streamlit. Note that this now accessible in native Streamlit in st.header with parameter divider!

Functions
colored_header
Shows a header with a colored underline and an optional description.

Parameters:

Name	Type	Description	Default
label	str	Header label. Defaults to "Nice title".	'Nice title'
description	str	Description shown under the header. Defaults to "Cool description".	'Cool description'
color_name	_SUPPORTED_COLORS	Color of the underline. Defaults to "red-70". Supported colors are "light-blue-70", "orange-70", "blue-green-70", "blue-70", "violet-70", "red-70", "green-70", "yellow-80".	'red-70'
Source code in src/streamlit_extras/colored_header/__init__.py
Import:


from streamlit_extras.colored_header import colored_header 
Examples
example

def example():
    colored_header(
        label="My New Pretty Colored Header",
        description="This is a description",
        color_name="violet-70",
    )
Output (beta)

--



	
	ple_two
🖼️  Chart container
Submitted by Arnaud Miribel

Summary
Embed your chart in a nice tabs container to let viewers explore and export its underlying data.

Functions
chart_container
Embed chart in a (chart, data, export, explore) tabs container to let the viewer explore and export its underlying data.

Parameters:

Name	Type	Description	Default
data	DataFrame	Dataframe used in the dataframe tab.	required
tabs	Sequence	Tab labels. Defaults to ("Chart 📈", "Dataframe 📄", "Export 📁").	('Chart 📈', 'Dataframe 📄', 'Export 📁')
export_formats	Sequence	Export file formats. Defaults to ("CSV", "Parquet")	_SUPPORTED_EXPORT_KEYS
Source code in src/streamlit_extras/chart_container/__init__.py
Import:


from streamlit_extras.chart_container import chart_container 
Examples
example_one

def example_one():
    chart_data = _get_random_data()
    with chart_container(chart_data):
        st.write("Here's a cool chart")
        st.area_chart(chart_data)
Output (beta)
example_two

def example_two():
    chart_data = _get_random_data()
    with chart_container(chart_data):
        st.write(
            "I can use a subset of the data for my chart... "
            "but still give all the necessary context in "
            "`chart_container`!"
        )
        st.area_chart(chart_data[["a", "b"]])
		
		
		---
		
		
		
		⬇  Chart annotations
Submitted by Arnaud Miribel

Summary
Add annotations to specific timestamps in your time series in Altair!

Functions
get_annotations_chart
Creates an Altair Chart with annotation markers on the horizontal axis. Useful to highlight certain events on top of another time series Altair Chart. More here https://share.streamlit.io/streamlit/example-app-time-series-annotation/main

Parameters:

Name	Type	Description	Default
annotations	Iterable[Tuple]	Iterable of annotations defined by tuples with date and annotation.	required
y	float	Height at which the annotation marker should be. Defaults to 0.	0
min_date	str	Only annotations older than min_date will be displayed. Defaults to None.	None
max_date	str	Only annotations more recent than max_date will be displayed. Defaults to None.	None
marker	str	Marker to be used to indicate there is an annotation. Defaults to "⬇".	'⬇'
marker_size	float	Size of the marker (font size). Defaults to 20.	20
marker_offset_x	float	Horizontal offset. Defaults to 0.	0
market_offset_y	float	Vertical offset. Defaults to -10.	-10
marker_align	str	Text-align property of the marker ("left", "right", "center"). Defaults to "center".	'center'
Returns:

Type	Description
Chart	alt.Chart: Altair Chart with annotation markers on the horizontal axis
Source code in src/streamlit_extras/chart_annotations/__init__.py
Import:


from streamlit_extras.chart_annotations import get_annotations_chart 
Examples
example

def example() -> None:
    data: pd.DataFrame = get_data()
    chart: alt.TopLevelMixin = get_chart(data=data)

    chart += get_annotations_chart(
        annotations=[
            ("Mar 01, 2008", "Pretty good day for GOOG"),
            ("Dec 01, 2007", "Something's going wrong for GOOG & AAPL"),
            ("Nov 01, 2008", "Market starts again thanks to..."),
            ("Dec 01, 2009", "Small crash for GOOG after..."),
        ],
    )

    st.altair_chart(chart, use_container_width=True)  # type: ignore
	
	
	
	===
	
	Summary
Streamlit Component, for a UI card

Docstring
Visit the PyPI page for more information.

Examples
example

def example():
    card(
        title="Hello World!",
        text="Some description",
        image="http://placekitten.com/300/250",
        url="https://www.google.com",
    )
	
	----
	
	
	👽  Add Vertical Space
Submitted by Tyler Richards

Summary
Add n lines of vertical space to your Streamlit app in one command

Functions
add_vertical_space
Add vertical space to your Streamlit app.

Parameters:

Name	Type	Description	Default
num_lines	int	Height of the vertical space (given in number of lines). Defaults to 1.	1
Source code in src/streamlit_extras/add_vertical_space/__init__.py
Import:


from streamlit_extras.add_vertical_space import add_vertical_space 
Examples
example

def example():
    add_n_lines = st.slider("Add n vertical lines below this", 1, 20, 5)
    add_vertical_space(add_n_lines)
    st.write("Here is text after the nth line!")
	
	
	
	====
	
	👸  Altex
Submitted by Arnaud Miribel

Summary
A simple wrapper on top of Altair to make Streamlit charts in an express API. If you're lazy and/or familiar with Altair, this is probably a good fit! Inspired by plost and plotly-express.

Functions
_chart
Create an Altair chart with a simple API. Supported charts include line, bar, point, area, histogram, sparkline, sparkbar, sparkarea.

Parameters:

Name	Type	Description	Default
mark_function	str	Altair mark function, example line/bar/point	required
data	DataFrame	Dataframe to use for the chart	required
x	Union[X, str]	Column for the x axis	required
y	Union[Y, str]	Column for the y axis	required
color	Optional[Union[Color, str]]	Color a specific group of your data. Defaults to None.	None
opacity	Optional[Union[value, float]]	Change opacity of marks. Defaults to None.	None
column	Optional[Union[Column, str]]	Groupby a specific column. Defaults to None.	None
rolling	Optional[int]	Rolling average window size. Defaults to None.	None
title	Optional[str]	Title of the chart. Defaults to None.	None
width	Optional[int]	Width of the chart. Defaults to None.	None
height	Optional[int]	Height of the chart. Defaults to None.	None
spark	bool	Whether or not to make spark chart, i.e. a chart without axes nor ticks nor legend. Defaults to False.	False
autoscale_y	bool	Whether or not to autoscale the y axis. Defaults to False.	False
Returns:

Type	Description
Chart	alt.Chart: Altair chart
Source code in src/streamlit_extras/altex/__init__.py
Import:


from streamlit_extras.altex import _chart 
scatter_chart
Source code in src/streamlit_extras/altex/__init__.py
Import:


from streamlit_extras.altex import scatter_chart 
Examples
example_line

@cache_data
def example_line():
    stocks = get_stocks_data()

    line_chart(
        data=stocks.query("symbol == 'GOOG'"),
        x="date",
        y="price",
        title="A beautiful simple line chart",
    )
example_multi_line

@cache_data
def example_multi_line():
    stocks = get_stocks_data()
    line_chart(
        data=stocks,
        x="date",
        y="price",
        color="symbol",
        title="A beautiful multi line chart",
    )
example_bar

@cache_data
def example_bar():
    stocks = get_stocks_data()
    bar_chart(
        data=stocks.query("symbol == 'GOOG'"),
        x="date",
        y="price",
        title="A beautiful bar chart",
    )
example_hist

@cache_data
def example_hist():
    stocks = get_stocks_data()
    hist_chart(
        data=stocks.assign(price=stocks.price.round(0)),
        x="price",
        title="A beautiful histogram",
    )
example_scatter

@cache_data
def example_scatter():
    weather = get_weather_data()
    scatter_chart(
        data=weather,
        x=alt.X("wind:Q", title="Custom X title"),
        y=alt.Y("temp_min:Q", title="Custom Y title"),
        title="A beautiful scatter chart",
    )
example_sparkline

@cache_data
def example_sparkline():
    stocks = get_stocks_data()
    sparkline_chart(
        data=stocks.query("symbol == 'GOOG'"),
        x="date",
        y="price",
        title="A beautiful sparkline chart",
        rolling=7,
        height=150,
    )
example_minisparklines

@cache_data
def example_minisparklines():
    stocks = get_stocks_data()

    left, middle, right = st.columns(3)
    with left:
        data = stocks.query("symbol == 'GOOG'")
        st.metric("GOOG", int(data["price"].mean()))
        sparkline_chart(
            data=data,
            x="date",
            y="price:Q",
            height=80,
            autoscale_y=True,
        )
    with middle:
        data = stocks.query("symbol == 'MSFT'")
        st.metric("MSFT", int(data["price"].mean()))
        sparkline_chart(
            data=data,
            x="date",
            y="price:Q",
            height=80,
            autoscale_y=True,
        )
    with right:
        data = stocks.query("symbol == 'AAPL'")
        st.metric("AAPL", int(data["price"].mean()))
        sparkline_chart(
            data=data,
            x="date",
            y="price:Q",
            height=80,
            autoscale_y=True,
        )
example_sparkbar

@cache_data
def example_sparkbar():
    stocks = get_stocks_data()
    sparkbar_chart(
        data=stocks.query("symbol == 'GOOG'"),
        x="date",
        y="price",
        title="A beautiful sparkbar chart",
        height=150,
    )
example_sparkarea

@cache_data
def example_sparkarea():
    random_data = get_random_data()
    df = pd.melt(
        random_data,
        id_vars="index",
        value_vars=list("abcdefg"),
    )

    sparkarea_chart(
        data=df,
        x="index",
        y="value",
        color=alt.Color("variable", legend=None),
        title="A beautiful (also probably useless) sparkarea chart",
        opacity=alt.value(0.6),
        height=200,
    )
example_hist_time

@cache_data
def example_hist_time():
    weather = get_weather_data()
    hist_chart(
        data=weather,
        x="week(date):T",
        y="day(date):T",
        color=alt.Color(
            "median(temp_max):Q",
            legend=None,
        ),
        title="A beautiful time hist chart",
    )
example_bar_sorted

@cache_data
def example_bar_sorted():
    weather = get_weather_data()
    bar_chart(
        data=weather.sort_values(by="temp_max", ascending=False).head(25),
        x=alt.X("date", sort="-y"),
        y=alt.Y("temp_max:Q"),
        title="A beautiful sorted-by-value bar chart",
    )
example_bar_normalized

@cache_data
def example_bar_normalized():
    barley = get_barley_data()
    bar_chart(
        data=barley,
        x=alt.X("variety:N", title="Variety"),
        y=alt.Y("sum(yield):Q", stack="normalize"),
        color="site:N",
        title="A beautiful normalized stacked bar chart",
    )
example_bar_grouped

@cache_data
def example_bar_grouped():
    barley = get_barley_data()
    bar_chart(
        data=barley,
        x="year:O",
        y="sum(yield):Q",
        color="year:N",
        column="site:N",
        title="A beautiful grouped bar charts",
        width=90,
        use_container_width=False,
    )
example_bar_horizontal

@cache_data
def example_bar_horizontal():
    weather = get_weather_data()
    bar_chart(
        data=weather.head(15),
        x="temp_max:Q",
        y=alt.Y("date:O", title="Temperature"),
        title="A beautiful horizontal bar chart",
    )
example_bar_log

@cache_data
def example_bar_log():
    weather = get_weather_data()
    bar_chart(
        data=weather,
        x=alt.X("temp_max:Q", title="Temperature"),
        y=alt.Y(
            "count()",
            title="Count of records",
            scale=alt.Scale(type="symlog"),
        ),
        title="A beautiful histogram... with log scale",
    )
example_scatter_opacity

@cache_data
def example_scatter_opacity():
    weather = get_weather_data()
    scatter_chart(
        data=weather,
        x=alt.X("wind:Q", title="Custom X title"),
        y=alt.Y("temp_min:Q", title="Custom Y title"),
        title="A beautiful scatter chart with custom opacity",
        opacity=0.2,
    )
example_bar_normalized_custom

@cache_data
def example_bar_normalized_custom():
    barley = get_barley_data()
    bar_chart(
        data=barley,
        x=alt.X("variety", title="Variety"),
        y="sum(yield)",
        color=alt.Color("site", scale=alt.Scale(scheme="lighttealblue"), legend=None),
        title="A beautiful stacked bar chart (without legend, custom colors)",
    )