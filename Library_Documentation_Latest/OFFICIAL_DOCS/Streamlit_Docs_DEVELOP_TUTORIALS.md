******** Streamlit Official Documentation 2024: TUTORIALS ********

------------------------------------------------------------------------------------------------
CHAPTER 1: elements.md
------------------------------------------------------------------------------------------------

################################################
Section 1.1 - charts\annotate-altair-chart.md
################################################


---
title: Annotate an Altair chart
slug: /develop/tutorials/elements/annotate-an-altair-chart
---

# Annotate an Altair chart

Altair allows you to annotate your charts with text, images, and emojis. You can do this by overlaying two charts to create a [layered chart](#layered-charts).

## Applied concepts

- Use layered charts in Altair to create annotations.

## Prerequisites

- This tutorial requires the following Python libraries:

  ```txt
  streamlit
  altair>=4.0.0
  vega_datasets
  ```

- This tutorial assumes you have a clean working directory called `your-repository`.
- You should have a basic understanding of the Vega-Altair charting library.

## Summary

In this example, you will create a time-series chart to track the evolution of stock prices. The chart will have two layers: a data layer and an
annotation layer. Each layer is an `altair.Chart` object. You will combine the two charts with the `+` opterator to create a layered chart.

Within the data layer, you'll add a multi-line tooltip to show information about datapoints. To learn more about multi-line tooltips, see this [example]() in Vega-Altair's documentation. You'll add another tooltip to the annotation layer.

Here's a look at what you'll build:

<Collapse title="Complete code" expanded={false}>

```python
import streamlit as st
import altair as alt
import pandas as pd
from vega_datasets import data


@st.cache_data
def get_data():
    source = data.stocks()
    source = source[source.date.gt("2004-01-01")]
    return source


stock_data = get_data()

hover = alt.selection_single(
    fields=["date"],
    nearest=True,
    on="mouseover",
    empty="none",
)

lines = (
    alt.Chart(stock_data, title="Evolution of stock prices")
    .mark_line()
    .encode(
        x="date",
        y="price",
        color="symbol",
    )
)

points = lines.transform_filter(hover).mark_circle(size=65)

tooltips = (
    alt.Chart(stock_data)
    .mark_rule()
    .encode(
        x="yearmonthdate(date)",
        y="price",
        opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
        tooltip=[
            alt.Tooltip("date", title="Date"),
            alt.Tooltip("price", title="Price (USD)"),
        ],
    )
    .add_selection(hover)
)

data_layer = lines + points + tooltips

ANNOTATIONS = [
    ("Sep 01, 2007", 450, "🙂", "Something's going well for GOOG & AAPL."),
    ("Nov 01, 2008", 220, "🙂", "The market is recovering."),
    ("Dec 01, 2007", 750, "😱", "Something's going wrong for GOOG & AAPL."),
    ("Dec 01, 2009", 680, "😱", "A hiccup for GOOG."),
]
annotations_df = pd.DataFrame(
    ANNOTATIONS, columns=["date", "price", "marker", "description"]
)
annotations_df.date = pd.to_datetime(annotations_df.date)

annotation_layer = (
    alt.Chart(annotations_df)
    .mark_text(size=20, dx=-10, dy=0, align="left")
    .encode(x="date:T", y=alt.Y("price:Q"), text="marker", tooltip="description")
)

combined_chart = data_layer + annotation_layer
st.altair_chart(combined_chart, use_container_width=True)
```

</Collapse>

<Cloud name="doc-annotate-altair" height="450px" />

## Build the example

### Initialize your app

1. In `your_repository`, create a file named `app.py`.
1. In a terminal, change directories to `your_repository` and start your app.

   ```bash
   streamlit run app.py
   ```

   Your app will be blank since you still need to add code.

1. In `app.py`, write the following:

   ```python
    import streamlit as st
    import altair as alt
    import pandas as pd
    from vega_datasets import data
   ```

   You'll be using these libraries as follows:

   - You'll download a dataset using [`vega_datasets`]().
   - You'll maniputate the data using `pandas`.
   - You'll define a chart using `altair`.

1. Save your `app.py` file and view your running app.
1. Click "**Always rerun**" or hit your "**A**" key in your running app.

   Your running preview will automatically update as you save changes to `app.py`. Your preview will still be blank. Return to your code.

### Build the data layer

You'll build an interactive time-series chart of the stock prices with a multi-line tooltip. The x-axis represents the date, and the y-axis represents the stock price.

1. Import data from `vega_datasets`.

   ```python
   @st.cache_data
   def get_data():
       source = data.stocks()
       source = source[source.date.gt("2004-01-01")]
       return source

   stock_data = get_data()
   ```

   The `@st.cache_data` decorator turns `get_data()` into a cahced function. Streamlit will only download the data once since the data will be saved in a cache. For more information about caching, see [Caching overview].

1. Define a mouseover selection event in Altair.

   ```python
   hover = alt.selection_single(
       fields=["date"],
       nearest=True,
       on="mouseover",
       empty="none",
   )
   ```

   This defines a mouseover selection for points. `fields=["date"]` allows Altair to identify other points with the same date. You will use this to create a vertical line highlight when a user hovers over a point.

1. Define a basic line chart to graph the five series in your data set.

   ```python
   lines = (
       alt.Chart(stock_data, title="Evolution of stock prices")
       .mark_line()
       .encode(
           x="date",
           y="price",
           color="symbol",
       )
   )
   ```

1. Draw points on the lines and highlight them based on the mouseover selection.

   ```python
   points = lines.transform_filter(hover).mark_circle(size=65)
   ```

   Since the mouseover selection includes `fields=["date"]`, Altair will draw circles on each series at the same date.

1. Draw a vertical rule at the location of the mouseover selection.

   ```python
   tooltips = (
       alt.Chart(stock_data)
       .mark_rule()
       .encode(
           x="yearmonthdate(date)",
           y="price",
           opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
           tooltip=[
               alt.Tooltip("date", title="Date"),
               alt.Tooltip("price", title="Price (USD)"),
           ],
       )
       .add_selection(hover)
   )
   ```

   The `opacity` parameter ensures each vertical line is only visible when it's part of a mouseover selection. Each `alt.Tooltip` adds a line to your multi-line tooltip.

1. Combine the lines, points, and tooltips into a single chart.

   ```python
   data_layer = lines + points + tooltips
   ```

1. Optional: Test out your code by rendering your data layer.

   ```python
   st.altair_chart(data_layer, use_container_width=True)
   ```

   Save your file and examine the chart in your app. Use your mouse to hover over points. Observe the circle marks, vertical line, and tooltip as you hover over a point. Delete the line or keep it at the end of your app to be updated as you continue.

### Build the annotation layer

Now that you have the first chart that shows the data, you can annotate it with text and an emoji. In this section, you'll add some emojis and tooltips to mark specifc points of interest.

1. Create a list of annotations.

   ```python
   ANNOTATIONS = [
       ("Sep 01, 2007", 450, "🙂", "Something's going well for GOOG & AAPL."),
       ("Nov 01, 2008", 220, "🙂", "The market is recovering."),
       ("Dec 01, 2007", 750, "😱", "Something's going wrong for GOOG & AAPL."),
       ("Dec 01, 2009", 680, "😱", "A hiccup for GOOG."),
   ]
   annotations_df = pd.DataFrame(
       ANNOTATIONS, columns=["date", "price", "marker", "description"]
   )
   annotations_df.date = pd.to_datetime(annotations_df.date)
   ```

   The first two columns ("date" and "price") determine where Altair will place the marker. The third column ("marker") determines what icon Altair will place. The last column ("description") will fill in the associated tooltip.

1. Create a scatter plot with the x-axis representing the date and the y-axis representing the height ("price") of each annotation.

   ```python
   annotation_layer = (
       alt.Chart(annotations_df)
       .mark_text(size=20, dx=-10, dy=0, align="left")
       .encode(x="date:T", y=alt.Y("price:Q"), text="marker", tooltip="description")
   )
   ```

   The `dx=-10, dy=0` inside of `.mark_text()` offsets the icons so they are centered at the coordinate in your annotations dataframe. The four columns are passed to the chart through the `.encode()` method. If you want to use the same marker for all points, you can remove `text="marker"` from the `.encode()` method and add the marker to `.mark_text()`. For example, `.mark_text(text="🥳")` would make all the icons be "🥳". For more information about `.mark_text()`, see Altair's [documentation]().

### Combine the chart layers

1. Define the combined chart.

   ```python
   combined_chart = data_layer + annotation_layer
   ```

1. Display the chart in Streamlit.

   ```python
   st.altair_chart(combined_chart, use_container_width=True)
   ```

## Next steps

Play around with your new app.

- If you want to use custom images instead of text or emojis to annotation your chart, you can replace the line containing `.mark_text()` with `.mark_image()`. For some URL string stored in a variable `IMAGE_URL`, you could do something like this:

  ```python
  .mark_image(
      width=12,
      height=12,
      url=IMAGE_URL,
  )
  ```

- If you want to enable panning and zooming for your chart, add `.interactive()` when you define your combined chart:

  ```python
  combined_chart = (data_layer + annotation_layer).interactive()
  ```


################################################
Section 1.2 - dataframes\row-selections (old).md
################################################


---
title: Get dataframe row-selections from users (streamlit<1.35.0)
slug: /develop/tutorials/elements/dataframe-row-selections-old
---

# Get dataframe row-selections from users (`streamlit<1.35.0`)

Before dataframe selections were introduced in Streamlit version 1.35.0, [`st.dataframe`](/api-reference/data/st.dataframe) and [`st.data_editor`] did not natively support passing user-selected rows to the Python backend. If you would like to work with row (or column)selections for dataframes, we recommend upgrading to `streamlit>=1.35.0`. For a newer tutorial, see [Get dataframe row-selections from users].

However, if you need a workaround for an older version of Streamlit, you can effectively get row selections by adding an extra [Checkbox column]) to your dataframe using `st.data_editor`. Use this extra column to collect a user's selection(s).

## Example

In the following example, we define a function which accepts a dataframe and returns the rows selected by a user. Within the function, the dataframe is copied to prevent mutating it. We insert a temporary "Select" column into the copied dataframe before passing the copied data into `st.data_editor`. We have disabled editing for all other columns, but you can make them editable if desired. After filtering the dataframe and dropping the temporary column, our function returns the selected rows.

```python
import streamlit as st
import numpy as np
import pandas as pd

df = pd.DataFrame(
    {
        "Animal": ["Lion", "Elephant", "Giraffe", "Monkey", "Zebra"],
        "Habitat": ["Savanna", "Forest", "Savanna", "Forest", "Savanna"],
        "Lifespan (years)": [15, 60, 25, 20, 25],
        "Average weight (kg)": [190, 5000, 800, 10, 350],
    }
)

def dataframe_with_selections(df):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)


selection = dataframe_with_selections(df)
st.write("Your selection:")
st.write(selection)
```


################################################
Section 1.3 - dataframes\row_selections.md
################################################


---
title: Get dataframe row-selections from users
slug: /develop/tutorials/elements/dataframe-row-selections
---

# Get dataframe row-selections from users

Streamlit offers two commands for rendering beautiful, interactive dataframes in your app. If you need users to edit data, add rows, or delete rows, use `st.data_editor`. If you don't want users to change the data in your dataframe, use `st.dataframe`. Users can sort and search through data rendered with `st.dataframe`. Additionally, you can activate selections to work with users' row and column selections.

This tutorial uses row selections, which were introduced in Streamlit version 1.35.0. For an older workaround using `st.data_editor`, see [Get dataframe row-selections (`streamlit<1.35.0`)].

## Applied concepts

- Use dataframe row selections to filter a dataframe.

## Prerequisites

- The following must be installed in your Python environment:

  ```text
  streamlit>=1.35.0
  ```

- You should have a clean working directory called `your-repository`.
- You should have a basic understanding of caching and `st.dataframe`.

## Summary

In this example, you'll build an app that displays a table of members and their activity for an imaginary organization. Within the table, a user can select one or more rows to create a filtered view. Your app will show a combined chart that compares the selected employees.

Here's a look at what you'll build:

<Collapse title="Complete code" expanded={false}>

    ```python
    import numpy as np
    import pandas as pd
    import streamlit as st

    from faker import Faker

    @st.cache_data
    def get_profile_dataset(number_of_items: int = 20, seed: int = 0) -> pd.DataFrame:
        new_data = []

        fake = Faker()
        np.random.seed(seed)
        Faker.seed(seed)

        for i in range(number_of_items):
            profile = fake.profile()
            new_data.append(
                {
                    "name": profile["name"],
                    "daily_activity": np.random.rand(25),
                    "activity": np.random.randint(2, 90, size=12),
                }
            )

        profile_df = pd.DataFrame(new_data)
        return profile_df


    column_configuration = {
        "name": st.column_config.TextColumn(
            "Name", help="The name of the user", max_chars=100, width="medium"
        ),
        "activity": st.column_config.LineChartColumn(
            "Activity (1 year)",
            help="The user's activity over the last 1 year",
            width="large",
            y_min=0,
            y_max=100,
        ),
        "daily_activity": st.column_config.BarChartColumn(
            "Activity (daily)",
            help="The user's activity in the last 25 days",
            width="medium",
            y_min=0,
            y_max=1,
        ),
    }

    select, compare = st.tabs(["Select members", "Compare selected"])

    with select:
        st.header("All members")

        df = get_profile_dataset()

        event = st.dataframe(
            df,
            column_config=column_configuration,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row",
        )

        st.header("Selected members")
        people = event.selection.rows
        filtered_df = df.iloc[people]
        st.dataframe(
            filtered_df,
            column_config=column_configuration,
            use_container_width=True,
        )

    with compare:
        activity_df = {}
        for person in people:
            activity_df[df.iloc[person]["name"]] = df.iloc[person]["activity"]
        activity_df = pd.DataFrame(activity_df)

        daily_activity_df = {}
        for person in people:
            daily_activity_df[df.iloc[person]["name"]] = df.iloc[person]["daily_activity"]
        daily_activity_df = pd.DataFrame(daily_activity_df)

        if len(people) > 0:
            st.header("Daily activity comparison")
            st.bar_chart(daily_activity_df)
            st.header("Yearly activity comparison")
            st.line_chart(activity_df)
        else:
            st.markdown("No members selected.")
    ```

</Collapse>

<Cloud name="doc-tutorial-dataframe-row-selections" height="600px" />

## Build the example

### Initialize your app

1. In `your_repository`, create a file named `app.py`.
1. In a terminal, change directories to `your_repository` and start your app.

   ```bash
   streamlit run app.py
   ```

   Your app will be blank since you still need to add code.

1. In `app.py`, write the following:

   ```python
   import numpy as np
   import pandas as pd
   import streamlit as st

   from faker import Faker
   ```

   You'll be using these libraries as follows:

   - You'll generate random member names with `faker`.
   - You'll generate random activity data with `numpy`.
   - You'll manipulate the data with `pandas`.

1. Save your `app.py` file and view your running app.
1. Click "**Always rerun**" or hit your "**A**" key in your running app.

   Your running preview will automatically update as you save changes to `app.py`. Your preview will still be blank. Return to your code.

### Build a function to create random member data

To begin with, you'll define a function to randomly generate some member data. It's okay to skip this section if you just want to copy the function.

<Collapse title="Complete function to randomly generate member data" expanded={false}>

    ```python
    @st.cache_data
    def get_profile_dataset(number_of_items: int = 20, seed: int = 0) -> pd.DataFrame:
        new_data = []

        fake = Faker()
        np.random.seed(seed)
        Faker.seed(seed)

        for i in range(number_of_items):
            profile = fake.profile()
            new_data.append(
                {
                    "name": profile["name"],
                    "daily_activity": np.random.rand(25),
                    "activity": np.random.randint(2, 90, size=12),
                }
            )

        profile_df = pd.DataFrame(new_data)
        return profile_df
    ```

</Collapse>

1. Use an `@st.cache_data` decorator and start your function definition.

   ```python
   @st.cache_data
   def get_profile_dataset(number_of_items: int = 20, seed: int = 0) -> pd.DataFrame:
   ```

   The `@st.cache_data` decorator turns `get_profile_dataset()` into a cached function. Streamlit saves the output of a cached function to reuse when the cached function is called again with the same inputs. This keeps your app performant when rerunning as part of Streamlit's execution model. For more information, see [Caching].

   The `get_profile_dataset` function has two parameters to configure the size of the data set and the seed for random generation. This example will use the default values (20 members in the set with a seed of 0). The function will return a `pandas.DataFrame`.

1. Initialize an empty list to store data.

   ```python
       new_data = []
   ```

1. Initialize the random generators.

   ```python
       fake = Faker()
       random.seed(seed)
       Faker.seed(seed)
   ```

1. Iterate through a range to generate new member data as a dictionary and append it to your list.

   ```python
       for i in range(number_of_items):
           profile = fake.profile()
           new_data.append(
               {
                   "name": profile["name"],
                   "daily_activity": np.random.rand(25),
                   "activity": np.random.randint(2, 90, size=12),
               }
           )
   ```

   For `daily_activity`, you're generating an array of length 25. These values are floats in the interval `[0,1)`. For `activity`, you're generating an array of length 12. These values are integers in the interval `[2,90)`.

1. Convert your list of dictionaries to a single `pandas.DataFrame` and return it.

   ```python
       profile_df = pd.DataFrame(new_data)
       return profile_df
   ```

1. Optional: Test out your function by calling it and displaying the data.

   ```python
   st.dataframe(get_profile_dataset())
   ```

   Save your `app.py` file to see the preview. Delete this line before you continue.

### Display your data with multi-row selections enabled

1. Define your column configuration to format your data.

   ```python
   column_configuration = {
       "name": st.column_config.TextColumn(
           "Name", help="The name of the user", max_chars=100, width="medium"
       ),
       "activity": st.column_config.LineChartColumn(
           "Activity (1 year)",
           help="The user's activity over the last 1 year",
           width="large",
           y_min=0,
           y_max=100,
       ),
       "daily_activity": st.column_config.BarChartColumn(
           "Activity (daily)",
           help="The user's activity in the last 25 days",
           width="medium",
           y_min=0,
           y_max=1,
       ),
   }
   ```

   For each column of your dataframe, this defines nicely formatted column name, tooltip, and column width. You'll use a line chart to show yearly activity, and a bar chart to show daily activity.

1. Insert a header to identify the data you will display.

   ```python
   st.header("All members")
   ```

1. Store your data in a convenient variable.

   ```python
   df = get_profile_dataset()
   ```

1. Display your dataframe with selections activated.

   ```python
   event = st.dataframe(
       df,
       column_config=column_configuration,
       use_container_width=True,
       hide_index=True,
       on_select="rerun",
       selection_mode="multi-row",
   )
   ```

   By setting `on_selection="rerun"`, you've activated selections for the dataframe. `selection_mode="multi_row"` specifies the type of selections allowed (multiple rows, no columns). `event` stores the selection data from the user. Selections can be accessed from the `event.selection` attribute.

### Display the selected data

1. Insert a header to identify the subset of data you will display.

   ```python
   st.header("Selected members")
   ```

1. Get the list of selected rows and filter your dataframe.

   ```python
   people = event.selection.rows
   filtered_df = df.iloc[people]
   ```

   Row selections are returned by positional index. You should use pandas methods `.iloc[]` or `.iat[]` to retrieve rows.

1. Display the selected rows in a new dataframe.

   ```python
       st.dataframe(
           filtered_df,
           column_config=column_configuration,
           use_container_width=True,
       )
   ```

   For consistency, reuse the existing column configuration.

1. Optional: Save your file and test it out. Try selecting some rows in your app, and then return to your code.

### Combine activity data for the selected rows

1. Create an empty dictionary to store (yearly) activity data.

   ```python
   activity_df = {}
   ```

1. Iterate through selected rows and save each member's activity in the dictionary indexed by their name.

   ```python
   for person in people:
       activity_df[df.iloc[person]["name"]] = df.iloc[person]["activity"]
   ```

1. Convert the activity dictionary into a `pandas.DataFrame`.

   ```python
   activity_df = pd.DataFrame(activity_df)
   ```

1. Repeat the previous three steps similarly for daily activity.

   ```python
   daily_activity_df = {}
   for person in people:
       daily_activity_df[df.iloc[person]["name"]] = df.iloc[person]["daily_activity"]
   daily_activity_df = pd.DataFrame(daily_activity_df)
   ```

1. Optional: Test out your combined data by displaying it.

   ```python
   st.dataframe(activity_df)
   st.dataframe(daily_activity_df)
   ```

   Save your `app.py` file to see the preview. Delete these two lines before you continue.

### Use charts to visualize the activity comparison

1. Start a conditional block to check if anyone is currently selected.

   ```python
   if len(people) > 0:
   ```

   Since no members are selected when the app loads, this check will prevent empty charts from being displayed.

1. Add a header to identify your first chart.

   ```python
       st.header("Daily activity comparison")
   ```

1. Show the daily activity comparison in a bar chart.

   ```python
       st.bar_chart(daily_activity_df)
   ```

1. Similarly, for yearly activity, add a header and line chart.

   ```python
       st.header("Yearly activity comparison")
       st.line_chart(activity_df)
   ```

1. Complete the conditional block with a default message to show when no members are selected.

   ```python
   else:
       st.markdown("No members selected.")
   ```

### Make it pretty

You should have a functioning app at this point. Now you can beautify it. In this section, you'll separate the selection UI from the comparison by using `st.tabs`.

1. Immediately after the column configuration definition, insert two tabs.

   ```python
   select, compare = st.tabs(["Select members", "Compare selected"])
   ```

1. Indent the code following the line in the previous step and group it into the two new tabs.

   ```python
   with select: # Add select tab #############################################
       st.header("All members")

       df = get_profile_dataset()

       event = st.dataframe(
           df,
           column_config=column_configuration,
           use_container_width=True,
           hide_index=True,
           on_select="rerun",
           selection_mode="multi-row",
       )

       st.header("Selected members")
       people = event.selection.rows
       filtered_df = df.iloc[people]
       st.dataframe(
           filtered_df,
           column_config=column_configuration,
           use_container_width=True,
       )

   with compare: # Add compare tab ###########################################
       activity_df = {}
       for person in people:
           activity_df[df.iloc[person]["name"]] = df.iloc[person]["activity"]
       activity_df = pd.DataFrame(activity_df)

       daily_activity_df = {}
       for person in people:
           daily_activity_df[df.iloc[person]["name"]] = df.iloc[person]["daily_activity"]
       daily_activity_df = pd.DataFrame(daily_activity_df)

       if len(people) > 0:
           st.header("Daily activity comparison")
           st.bar_chart(daily_activity_df)
           st.header("Yearly activity comparison")
           st.line_chart(activity_df)
       else:
           st.markdown("No members selected.")
   ```

1. Save your file and try out your completed example.




------------------------------------------------------------------------------------------------
CHAPTER 2: execution-flow.md
------------------------------------------------------------------------------------------------

################################################
Section 2.1 - fragments\create-a-multiple-container-fragment.md
################################################


---
title: Create a fragment across multiple containers
slug: /develop/tutorials/execution-flow/create-a-multiple-container-fragment
---

# Create a fragment across multiple containers

Streamlit lets you turn functions into [fragments], which can rerun independently from the full script. If your fragment doesn't write to outside containers, Streamlit will clear and redraw all the fragment elements with each fragment rerun. However, if your fragment _does_ write elements to outside containers, Streamlit will not clear those elements during a fragment rerun. Instead, those elements accumulate with each fragment rerun until the next full-script rerun. If you want a fragment to update multiple containers in your app, use [`st.empty()`] containers to prevent accumulating elements.

## Applied concepts

- Use fragments to run two independent processes separately.
- Distribute a fragment across multiple containers.

## Prerequisites

- The following must be installed in your Python environment:

  ```text
  streamlit>=1.37.0
  ```

- You should have a clean working directory called `your-repository`.
- You should have a basic understanding of fragments and `st.empty()`.

## Summary

In this toy example, you'll build an app with six containers. Three containers will have orange cats. The other three containers will have black cats. You'll have three buttons in the sidebar: "**Herd the black cats**," "**Herd the orange cats**," and "**Herd all the cats**." Since herding cats is slow, you'll use fragments to help Streamlit run the associated processes efficiently. You'll create two fragments, one for the black cats and one for the orange cats. Since the buttons will be in the sidebar and the fragments will update containers in the main body, you'll use a trick with `st.empty()` to ensure you don't end up with too many cats in your app (if it's even possible to have too many cats). 😻

Here's a look at what you'll build:

<Collapse title="Complete code" expanded={false}>

```python
import streamlit as st
import time

st.title("Cats!")

row1 = st.columns(3)
row2 = st.columns(3)

grid = [col.container(height=200) for col in row1 + row2]
safe_grid = [card.empty() for card in grid]


def black_cats():
    time.sleep(1)
    st.title("🐈‍⬛ 🐈‍⬛")
    st.markdown("🐾 🐾 🐾 🐾")


def orange_cats():
    time.sleep(1)
    st.title("🐈 🐈")
    st.markdown("🐾 🐾 🐾 🐾")


@st.fragment
def herd_black_cats(card_a, card_b, card_c):
    st.button("Herd the black cats")
    container_a = card_a.container()
    container_b = card_b.container()
    container_c = card_c.container()
    with container_a:
        black_cats()
    with container_b:
        black_cats()
    with container_c:
        black_cats()


@st.fragment
def herd_orange_cats(card_a, card_b, card_c):
    st.button("Herd the orange cats")
    container_a = card_a.container()
    container_b = card_b.container()
    container_c = card_c.container()
    with container_a:
        orange_cats()
    with container_b:
        orange_cats()
    with container_c:
        orange_cats()


with st.sidebar:
    herd_black_cats(grid[0].empty(), grid[2].empty(), grid[4].empty())
    herd_orange_cats(grid[1].empty(), grid[3].empty(), grid[5].empty())
    st.button("Herd all the cats")
```

</Collapse>

<Cloud name="doc-tutorial-fragment-multiple-container" height="650px" />

## Build the example

### Initialize your app

1. In `your_repository`, create a file named `app.py`.
1. In a terminal, change directories to `your_repository` and start your app.

   ```bash
   streamlit run app.py
   ```

   Your app will be blank since you still need to add code.

1. In `app.py`, write the following:

   ```python
   import streamlit as st
   import time
   ```

   You'll use `time.sleep()` to slow things down and see the fragments working.

1. Save your `app.py` file and view your running app.
1. Click "**Always rerun**" or hit your "**A**" key in your running app.

   Your running preview will automatically update as you save changes to `app.py`. Your preview will still be blank. Return to your code.

### Frame out your app's containers

1. Add a title to your app and two rows of three containers.

   ```python
   st.title("Cats!")

   row1 = st.columns(3)
   row2 = st.columns(3)

   grid = [col.container(height=200) for col in row1 + row2]
   ```

   Save your file to see your updated preview.

1. Define a helper function to draw two black cats.

   ```python
   def black_cats():
       time.sleep(1)
       st.title("🐈‍⬛ 🐈‍⬛")
       st.markdown("🐾 🐾 🐾 🐾")
   ```

   This function represents "herding two cats" and uses `time.sleep()` to simulate a slower process. You will use this to draw two cats in one of your grid cards later on.

1. Define another helper function to draw two orange cats.

   ```python
   def orange_cats():
       time.sleep(1)
       st.title("🐈 🐈")
       st.markdown("🐾 🐾 🐾 🐾")
   ```

1. Optional: Test out your functions by calling each one within a grid card.

   ```python
   with grid[0]:
       black_cats()
   with grid[1]:
       orange_cats()
   ```

   Save your `app.py` file to see the preview. Delete these four lines when finished.

### Define your fragments

Since each fragment will span across the sidebar and three additional containers, you'll use the sidebar to hold the main body of the fragment and pass the three containers as function arguments.

1. Use an [`@st.fragment`] decorator and start your black-cat fragment definition.

   ```python
   @st.fragment
   def herd_black_cats(card_a, card_b, card_c):
   ```

1. Add a button for rerunning this fragment.

   ```python
       st.button("Herd the black cats")
   ```

1. Write to each container using your helper function.

   ```python
       with card_a:
           black_cats()
       with card_b:
           black_cats()
       with card_c:
           black_cats()
   ```

   **This code above will not behave as desired, but you'll explore and correct this in the following steps.**

1. Test out your code. Call your fragment function in the sidebar.

   ```python
   with st.sidebar:
       herd_black_cats(grid[0], grid[2], grid[4])
   ```

   Save your file and try using the button in the sidebar. More and more cats are appear in the cards with each fragment rerun! This is the expected behavior when fragments write to outside containers. To fix this, you will pass `st.empty()` containers to your fragment function.

   ![Example Streamlit app showing accumulating elements when a fragment writes to outside containers](/images/tutorials/fragment-multiple-containers-tutorial-app-duplicates.jpg)

1. Delete the lines of code from the previous two steps.

1. To prepare for using `st.empty()` containers, correct your cat-herding function as follows. After the button, define containers to place in the `st.empty()` cards you'll pass to your fragment.

   ```python
       container_a = card_a.container()
       container_b = card_b.container()
       container_c = card_c.container()
       with container_a:
           black_cats()
       with container_b:
           black_cats()
       with container_c:
           black_cats()
   ```

   In this new version, `card_a`, `card_b`, and `card_c` will be `st.empty()` containers. You create `container_a`, `container_b`, and `container_c` to allow Streamlit to draw multiple elements on each grid card.

1. Similarly define your orange-cat fragment function.

   ```python
   @st.fragment
   def herd_orange_cats(card_a, card_b, card_c):
       st.button("Herd the orange cats")
       container_a = card_a.container()
       container_b = card_b.container()
       container_c = card_c.container()
       with container_a:
           orange_cats()
       with container_b:
           orange_cats()
       with container_c:
           orange_cats()
   ```

### Put the functions together together to create an app

1. Call both of your fragments in the sidebar.

   ```python
   with st.sidebar:
       herd_black_cats(grid[0].empty(), grid[2].empty(), grid[4].empty())
       herd_orange_cats(grid[1].empty(), grid[3].empty(), grid[5].empty())
   ```

   By creating `st.empty()` containers in each card and passing them to your fragments, you prevent elements from accumulating in the cards with each fragment rerun. If you create the `st.empty()` containers earlier in your app, full-script reruns will clear the orange-cat cards while (first) rendering the black-cat cards.

1. Include a button outside of your fragments. When clicked, the button will trigger a full-script rerun since you're calling its widget function outside of any fragment.

   ```python
       st.button("Herd all the cats")
   ```

1. Save your file and try out the app! When you click "**Herd the black cats**" or "**Herd the orange cats**," Streamlit will only redraw the three related cards. When you click "**Herd all the cats**," Streamlit redraws all six cards.


################################################
Section 2.2 - fragments\start-and-stop-fragment-auto-reruns.md
################################################


---
title: Start and stop a streaming fragment
slug: /develop/tutorials/execution-flow/start-and-stop-fragment-auto-reruns
---

# Start and stop a streaming fragment

Streamlit lets you turn functions into [fragments], which can rerun independently from the full script. Additionally, you can tell Streamlit to rerun a fragment at a set time interval. This is great for streaming data or monitoring processes. You may want the user to start and stop this live streaming. To do this, programmatically set the `run_every` parameter for your fragment.

## Applied concepts

- Use a fragment to stream live data.
- Start and stop a fragment from automatically rerunning.

## Prerequisites

- The following must be installed in your Python environment:

  ```text
  streamlit>=1.37.0
  ```

- You should have a clean working directory called `your-repository`.
- You should have a basic understanding of fragments.

## Summary

In this example, you'll build an app that streams two data series in a line chart. Your app will gather recent data on the first load of a session and statically display the line chart. Two buttons in the sidebar will allow users to start and stop data streaming to update the chart in real time. You'll use a fragment to manage the frequency and scope of the live updates.

Here's a look at what you'll build:

<Collapse title="Complete code" expanded={false}>

```python
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def get_recent_data(last_timestamp):
    """Generate and return data from last timestamp to now, at most 60 seconds."""
    now = datetime.now()
    if now - last_timestamp > timedelta(seconds=60):
        last_timestamp = now - timedelta(seconds=60)
    sample_time = timedelta(seconds=0.5)  # time between data points
    next_timestamp = last_timestamp + sample_time
    timestamps = np.arange(next_timestamp, now, sample_time)
    sample_values = np.random.randn(len(timestamps), 2)

    data = pd.DataFrame(sample_values, index=timestamps, columns=["A", "B"])
    return data


if "data" not in st.session_state:
    st.session_state.data = get_recent_data(datetime.now() - timedelta(seconds=60))

if "stream" not in st.session_state:
    st.session_state.stream = False


def toggle_streaming():
    st.session_state.stream = not st.session_state.stream


st.title("Data feed")
st.sidebar.slider(
    "Check for updates every: (seconds)", 0.5, 5.0, value=1.0, key="run_every"
)
st.sidebar.button(
    "Start streaming", disabled=st.session_state.stream, on_click=toggle_streaming
)
st.sidebar.button(
    "Stop streaming", disabled=not st.session_state.stream, on_click=toggle_streaming
)

if st.session_state.stream is True:
    run_every = st.session_state.run_every
else:
    run_every = None


@st.fragment(run_every=run_every)
def show_latest_data():
    last_timestamp = st.session_state.data.index[-1]
    st.session_state.data = pd.concat(
        [st.session_state.data, get_recent_data(last_timestamp)]
    )
    st.session_state.data = st.session_state.data[-100:]
    st.line_chart(st.session_state.data)


show_latest_data()
```

</Collapse>

<Cloud name="doc-tutorial-fragment-streaming" height="550px" />

## Build the example

### Initialize your app

1. In `your_repository`, create a file named `app.py`.
1. In a terminal, change directories to `your_repository` and start your app.

   ```bash
   streamlit run app.py
   ```

   Your app will be blank since you still need to add code.

1. In `app.py`, write the following:

   ```python
    import streamlit as st
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
   ```

   You'll be using these libraries as follows:

   - You'll work with two data series in a `pandas.DataFrame`.
   - You'll generate random data with `numpy`.
   - The data will have `datetime.datetime` index values.

1. Save your `app.py` file and view your running app.
1. Click "**Always rerun**" or hit your "**A**" key in your running app.

   Your running preview will automatically update as you save changes to `app.py`. Your preview will still be blank. Return to your code.

### Build a function to generate random, recent data

To begin with, you'll define a function to randomly generate some data for two time series, which you'll call "A" and "B." It's okay to skip this section if you just want to copy the function.

<Collapse title="Complete function to randomly generate sales data" expanded={false}>

```python
def get_recent_data(last_timestamp):
    """Generate and return data from last timestamp to now, at most 60 seconds."""
    now = datetime.now()
    if now - last_timestamp > timedelta(seconds=60):
        last_timestamp = now - timedelta(seconds=60)
    sample_time = timedelta(seconds=0.5)  # time between data points
    next_timestamp = last_timestamp + sample_time
    timestamps = np.arange(next_timestamp, now, sample_time)
    sample_values = np.random.randn(len(timestamps), 2)

    data = pd.DataFrame(sample_values, index=timestamps, columns=["A", "B"])
    return data
```

</Collapse>

1. Start your function definition.

   ```python
   def get_recent_data(last_timestamp):
       """Generate and return data from last timestamp to now, at most 60 seconds."""
   ```

   You'll pass the timestamp of your most recent datapoint to your data-generating function. Your function will use this to only return new data.

1. Get the current time and adjust the last timestamp if it is over 60 seconds ago.

   ```python
       now = datetime.now()
       if now - last_timestamp > timedelta(seconds=60):
           last_timestamp = now - timedelta(seconds=60)
   ```

   By updating the last timestamp, you'll ensure the function never returns more than 60 seconds of data.

1. Declare a new variable, `sample_time`, to define the time between datapoints. Calculate the timestamp of the first, new datapoint.

   ```python
       sample_time = timedelta(seconds=0.5)  # time between data points
       next_timestamp = last_timestamp + sample_time
   ```

1. Create a `datetime.datetime` index and generate two data series of the same length.

   ```python
       timestamps = np.arange(next_timestamp, now, sample_time)
       sample_values = np.random.randn(len(timestamps), 2)
   ```

1. Combine the data series with the index into a `pandas.DataFrame` and return the data.

   ```python
       data = pd.DataFrame(sample_values, index=timestamps, columns=["A", "B"])
       return data
   ```

1. Optional: Test out your function by calling it and displaying the data.

   ```python
   data = get_recent_data(datetime.now() - timedelta(seconds=60))
   data
   ```

   Save your `app.py` file to see the preview. Delete these two lines when finished.

### Initialize Session State values for your app

Since you will dynamically change the `run_every` parameter of `@st.fragment()`, you'll need to initialize the associated variables and Session State values before defining your fragment function. Your fragment function will also read and update values in Session State, so you can define those now to make the fragment function easier to understand.

1. Initialize your data for the first app load in a session.

   ```python
   if "data" not in st.session_state:
       st.session_state.data = get_recent_data(datetime.now() - timedelta(seconds=60))
   ```

   Your app will display this initial data in a static line chart before a user starts streaming data.

1. Initialize `"stream"` in Session State to turn streaming on and off. Set the default to off (`False`).

   ```python
   if "stream" not in st.session_state:
       st.session_state.stream = False
   ```

1. Create a callback function to toggle `"stream"` between `True` and `False`.

   ```python
   def toggle_streaming():
       st.session_state.stream = not st.session_state.stream
   ```

1. Add a title to your app.

   ```python
   st.title("Data feed")
   ```

1. Add a slider to the sidebar to set how frequently to check for data while streaming.

   ```python
   st.sidebar.slider(
       "Check for updates every: (seconds)", 0.5, 5.0, value=1.0, key="run_every"
   )
   ```

1. Add buttons to the sidebar to turn streaming on and off.

   ```python
   st.sidebar.button(
       "Start streaming", disabled=st.session_state.stream, on_click=toggle_streaming
   )
   st.sidebar.button(
       "Stop streaming", disabled=not st.session_state.stream, on_click=toggle_streaming
   )
   ```

   Both functions use the same callback to toggle `"stream"` in Session State. Use the current value `"stream"` to disable one of the buttons. This ensures the buttons are always consistent with the current state; "**Start streaming**" is only clickable when streaming is off, and "**Stop streaming**" is only clickable when streaming is on. The buttons also provide status to the user by highlighting which action is available to them.

1. Create and set a new variable, `run_every`, that will determine whether or not the fragment function will rerun automatically (and how fast).

   ```python
   if st.session_state.stream is True:
       run_every = st.session_state.run_every
   else:
       run_every = None
   ```

### Build a fragment function to stream data

To allow the user to turn data streaming on and off, you must set the `run_every` parameter in the `@st.fragment()` decorator.

<Collapse title="Complete function to show and stream data" expanded={false}>

```python
@st.fragment(run_every=run_every)
def show_latest_data():
    last_timestamp = st.session_state.data.index[-1]
    st.session_state.data = pd.concat(
        [st.session_state.data, get_recent_data(last_timestamp)]
    )
    st.session_state.data = st.session_state.data[-100:]
    st.line_chart(st.session_state.data)
```

</Collapse>

1. Use an [`@st.fragment`] decorator and start your function definition.

   ```python
    @st.fragment(run_every=run_every)
    def show_latest_data():
   ```

   Use the `run_every` variable declared above to set the parameter of the same name.

1. Retrieve the timestamp of the last datapoint in Session State.

   ```python
       last_timestamp = st.session_state.data.index[-1]
   ```

1. Update the data in Session State and trim to keep only the last 100 timestamps.

   ```python
       st.session_state.data = pd.concat(
           [st.session_state.data, get_recent_data(last_timestamp)]
       )
       st.session_state.data = st.session_state.data[-100:]
   ```

1. Show the data in a line chart.

   ```python
       st.line_chart(st.session_state.data)
   ```

   Your fragment-function definition is complete.

### Call and test out your fragment function

1. Call your function at the bottom of your code.

   ```python
   show_latest_data()
   ```

1. Test out your app by clicking "**Start streaming**." Try adjusting the frequency of updates.

## Next steps

Try adjusting the frequency of data generation or how much data is kept in Session State. Within `get_recent_data` try setting `sample_time` with a widget.

Try using [st.plotly_chart] or [st.altair_chart] to add labels to your chart.


################################################
Section 2.3 - fragments\trigger-a-full-script-rerun-from-a-fragment.md
################################################


---
title: Trigger a full-script rerun from inside a fragment
slug: /develop/tutorials/execution-flow/trigger-a-full-script-rerun-from-a-fragment
---

# Trigger a full-script rerun from inside a fragment

Streamlit lets you turn functions into [fragments], which can rerun independently from the full script. When a user interacts with a widget inside a fragment, only the fragment reruns. Sometimes, you may want to trigger a full-script rerun from inside a fragment. To do this, call [`st.rerun`] inside the fragment.

## Applied concepts

- Use a fragment to rerun part or all of your app, depending on user input.

## Prerequisites

- The following must be installed in your Python environment:

  ```text
  streamlit>=1.37.0
  ```

- You should have a clean working directory called `your-repository`.
- You should have a basic understanding of fragments and `st.rerun`.

## Summary

In this example, you'll build an app to display sales data. The app has two sets of elements that depend on a date selection. One set of elements displays information for the selected day. The other set of elements displays information for the associated month. If the user changes days within a month, Streamlit only needs to update the first set of elements. If the user selects a day in a different month, Streamlit needs to update all the elements.

You'll collect the day-specific elements into a fragment to avoid rerunning the full app when a user changes days within the same month. If you want to jump ahead to the fragment function definition, see [Build a function to show daily sales data](#build-a-function-to-show-daily-sales-data).

<div style={{ maxWidth: '60%', margin: 'auto' }}>
<Image alt="Execution flow of example Streamlit app showing daily sales on the left and monthly sales on the right" src="/images/tutorials/fragment-rerun-tutorial-execution-flow.png" />
</div>

Here's a look at what you'll build:

<Collapse title="Complete code" expanded={false}>

```python
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import string
import time


@st.cache_data
def get_data():
    """Generate random sales data for Widget A through Widget Z"""

    product_names = ["Widget " + letter for letter in string.ascii_uppercase]
    average_daily_sales = np.random.normal(1_000, 300, len(product_names))
    products = dict(zip(product_names, average_daily_sales))

    data = pd.DataFrame({})
    sales_dates = np.arange(date(2023, 1, 1), date(2024, 1, 1), timedelta(days=1))
    for product, sales in products.items():
        data[product] = np.random.normal(sales, 300, len(sales_dates)).round(2)
    data.index = sales_dates
    data.index = data.index.date
    return data


@st.fragment
def show_daily_sales(data):
    time.sleep(1)
    with st.container(height=100):
        selected_date = st.date_input(
            "Pick a day ",
            value=date(2023, 1, 1),
            min_value=date(2023, 1, 1),
            max_value=date(2023, 12, 31),
            key="selected_date",
        )

    if "previous_date" not in st.session_state:
        st.session_state.previous_date = selected_date
    previous_date = st.session_state.previous_date
    st.session_state.previous_date = selected_date
    is_new_month = selected_date.replace(day=1) != previous_date.replace(day=1)
    if is_new_month:
        st.rerun()

    with st.container(height=510):
        st.header(f"Best sellers, {selected_date:%m/%d/%y}")
        top_ten = data.loc[selected_date].sort_values(ascending=False)[0:10]
        cols = st.columns([1, 4])
        cols[0].dataframe(top_ten)
        cols[1].bar_chart(top_ten)

    with st.container(height=510):
        st.header(f"Worst sellers, {selected_date:%m/%d/%y}")
        bottom_ten = data.loc[selected_date].sort_values()[0:10]
        cols = st.columns([1, 4])
        cols[0].dataframe(bottom_ten)
        cols[1].bar_chart(bottom_ten)


def show_monthly_sales(data):
    time.sleep(1)
    selected_date = st.session_state.selected_date
    this_month = selected_date.replace(day=1)
    next_month = (selected_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    st.container(height=100, border=False)
    with st.container(height=510):
        st.header(f"Daily sales for all products, {this_month:%B %Y}")
        monthly_sales = data[(data.index < next_month) & (data.index >= this_month)]
        st.write(monthly_sales)
    with st.container(height=510):
        st.header(f"Total sales for all products, {this_month:%B %Y}")
        st.bar_chart(monthly_sales.sum())


st.set_page_config(layout="wide")

st.title("Daily vs monthly sales, by product")
st.markdown("This app shows the 2023 daily sales for Widget A through Widget Z.")

data = get_data()
daily, monthly = st.columns(2)
with daily:
    show_daily_sales(data)
with monthly:
    show_monthly_sales(data)
```

</Collapse>

![Example Streamlit app showing daily sales on the left and monthly sales on the right](/images/tutorials/fragment-rerun-tutorial-app.jpg)

[Click here to see the example live on Community Cloud.]()

## Build the example

### Initialize your app

1. In `your_repository`, create a file named `app.py`.
1. In a terminal, change directories to `your_repository` and start your app.

   ```bash
   streamlit run app.py
   ```

   Your app will be blank since you still need to add code.

1. In `app.py`, write the following:

   ```python
   import streamlit as st
   import pandas as pd
   import numpy as np
   from datetime import date, timedelta
   import string
   import time
   ```

   You'll be using these libraries as follows:

   - You'll work with sales data in a `pandas.DataFrame`.
   - You'll generate random sales numbers with `numpy`.
   - The data will have `datetime.date` index values.
   - The products sold will be "Widget A" through "Widget Z," so you'll use `string` for easy access to an alphabetical string.
   - Optional: To help add emphasis at the end, you'll use `time.sleep()` to slow things down and see the fragment working.

1. Save your `app.py` file and view your running app.
1. Click "**Always rerun**" or hit your "**A**" key in your running app.

   Your running preview will automatically update as you save changes to `app.py`. Your preview will still be blank. Return to your code.

### Build a function to create random sales data

To begin with, you'll define a function to randomly generate some sales data. It's okay to skip this section if you just want to copy the function.

<Collapse title="Complete function to randomly generate sales data" expanded={false}>

```python
@st.cache_data
def get_data():
    """Generate random sales data for Widget A through Widget Z"""

    product_names = ["Widget " + letter for letter in string.ascii_uppercase]
    average_daily_sales = np.random.normal(1_000, 300, len(product_names))
    products = dict(zip(product_names, average_daily_sales))

    data = pd.DataFrame({})
    sales_dates = np.arange(date(2023, 1, 1), date(2024, 1, 1), timedelta(days=1))
    for product, sales in products.items():
        data[product] = np.random.normal(sales, 300, len(sales_dates)).round(2)
    data.index = sales_dates
    data.index = data.index.date
    return data
```

</Collapse>

1. Use an `@st.cache_data` decorator and start your function definition.

   ```python
   @st.cache_data
   def get_data():
       """Generate random sales data for Widget A through Widget Z"""
   ```

   You don't need to keep re-randomizing the data, so the caching decorator will randomly generate the data once and save it in Streamlit's cache. As your app reruns, it will use the cached value instead of recomputing new data.

1. Define the list of product names and assign an average daily sales value to each.

   ```python
       product_names = ["Widget " + letter for letter in string.ascii_uppercase]
       average_daily_sales = np.random.normal(1_000, 300, len(product_names))
       products = dict(zip(product_names, average_daily_sales))
   ```

1. For each product, use its average daily sales to randomly generate daily sales values for an entire year.

   ```python
       data = pd.DataFrame({})
       sales_dates = np.arange(date(2023, 1, 1), date(2024, 1, 1), timedelta(days=1))
       for product, sales in products.items():
           data[product] = np.random.normal(sales, 300, len(sales_dates)).round(2)
       data.index = sales_dates
       data.index = data.index.date
   ```

   In the last line, `data.index.date` strips away the timestamp, so the index will show clean dates.

1. Return the random sales data.

   ```python
       return data
   ```

1. Optional: Test out your function by calling it and displaying the data.

   ```python
   data = get_data()
   data
   ```

   Save your `app.py` file to see the preview. Delete these two lines or keep them at the end of your app to be updated as you continue.

### Build a function to show daily sales data

Since the daily sales data updates with every new date selection, you'll turn this function into a fragment. As a fragment, it can rerun independently from the rest of your app. You'll include an `st.date_input` widget inside this fragment and watch for a date selection that changes the month. When the fragment detects a change in the selected month, it will trigger a full app rerun so everything can update.

<Collapse title="Complete function to display daily sales data" expanded={false}>

```python
@st.fragment
def show_daily_sales(data):
    time.sleep(1)
    selected_date = st.date_input(
        "Pick a day ",
        value=date(2023, 1, 1),
        min_value=date(2023, 1, 1),
        max_value=date(2023, 12, 31),
        key="selected_date",
    )

    if "previous_date" not in st.session_state:
        st.session_state.previous_date = selected_date
    previous_date = st.session_state.previous_date
    st.session_state.previous_date = selected_date
    is_new_month = selected_date.replace(day=1) != previous_date.replace(day=1)
    if is_new_month:
        st.rerun()

    st.header(f"Best sellers, {selected_date:%m/%d/%y}")
    top_ten = data.loc[selected_date].sort_values(ascending=False)[0:10]
    cols = st.columns([1, 4])
    cols[0].dataframe(top_ten)
    cols[1].bar_chart(top_ten)

    st.header(f"Worst sellers, {selected_date:%m/%d/%y}")
    bottom_ten = data.loc[selected_date].sort_values()[0:10]
    cols = st.columns([1, 4])
    cols[0].dataframe(bottom_ten)
    cols[1].bar_chart(bottom_ten)
```

</Collapse>

1. Use an [`@st.fragment`] decorator and start your function definition.

   ```python
   @st.fragment
   def show_daily_sales(data):
   ```

   Since your data will not change during a fragment rerun, you can pass the data into the fragment as an argument.

1. Optional: Add `time.sleep(1)` to slow down the function and show off how the fragment works.

   ```python
       time.sleep(1)
   ```

1. Add an `st.date_input` widget.

   ```python
       selected_date = st.date_input(
           "Pick a day ",
           value=date(2023, 1, 1),
           min_value=date(2023, 1, 1),
           max_value=date(2023, 12, 31),
           key="selected_date",
       )
   ```

   Your random data is for 2023, so set the minimun and maximum dates to match. Use a key for the widget because elements outside the fragment will need this date value. When working with a fragment, it's best to use Session State to pass information in and out of the fragment.

1. Initialize `"previous_date"` in Session State to compare each date selection.

   ```python
       if "previous_date" not in st.session_state:
           st.session_state.previous_date = selected_date
   ```

1. Save the previous date selection into a new variable and update `"previous_date"` in Session State.

   ```python
       previous_date = st.session_state.previous_date
       st.session_state.previous_date = selected_date
   ```

1. Call `st.rerun()` if the month changed.

   ```python
       is_new_month = selected_date.replace(day=1) != previous_date.replace(day=1)
       if is_new_month:
           st.rerun()
   ```

1. Show the best sellers from the selected date.

   ```python
       st.header(f"Best sellers, {selected_date:%m/%d/%y}")
       top_ten = data.loc[selected_date].sort_values(ascending=False)[0:10]
       cols = st.columns([1, 4])
       cols[0].dataframe(top_ten)
       cols[1].bar_chart(top_ten)
   ```

1. Show the worst sellers from the selected date.

   ```python
       st.header(f"Worst sellers, {selected_date:%m/%d/%y}")
       bottom_ten = data.loc[selected_date].sort_values()[0:10]
       cols = st.columns([1, 4])
       cols[0].dataframe(bottom_ten)
       cols[1].bar_chart(bottom_ten)
   ```

1. Optional: Test out your function by calling it and displaying the data.

   ```python
   data = get_data()
   show_daily_sales(data)
   ```

   Save your `app.py` file to see the preview. Delete these two lines or keep them at the end of your app to be updated as you continue.

### Build a function to show monthly sales data

Finally, let's build a function to display monthly sales data. It will be similar to your `show_daily_sales` function but doesn't need to be fragment. You only need to rerun this function when the whole app is rerunning.

<Collapse title="Complete function to display daily sales data" expanded={false}>

```python
def show_monthly_sales(data):
    time.sleep(1)
    selected_date = st.session_state.selected_date
    this_month = selected_date.replace(day=1)
    next_month = (selected_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    st.header(f"Daily sales for all products, {this_month:%B %Y}")
    monthly_sales = data[(data.index < next_month) & (data.index >= this_month)]
    st.write(monthly_sales)

    st.header(f"Total sales for all products, {this_month:%B %Y}")
    st.bar_chart(monthly_sales.sum())
```

</Collapse>

1. Start your function definition.

   ```python
   def show_monthly_sales(data):
   ```

1. Optional: Add `time.sleep(1)` to slow down the function and show off how the fragment works.

   ```python
       time.sleep(1)
   ```

1. Get the selected date from Session State and compute the first days of this and next month.

   ```python
       selected_date = st.session_state.selected_date
       this_month = selected_date.replace(day=1)
       next_month = (selected_date.replace(day=28) + timedelta(days=4)).replace(day=1)
   ```

1. Show the daily sales values for all products within the selected month.

   ```python
       st.header(f"Daily sales for all products, {this_month:%B %Y}")
       monthly_sales = data[(data.index < next_month) & (data.index >= this_month)]
       st.write(monthly_sales)
   ```

1. Show the total sales of each product within the selected month.

   ```python
       st.header(f"Total sales for all products, {this_month:%B %Y}")
       st.bar_chart(monthly_sales.sum())
   ```

1. Optional: Test out your function by calling it and displaying the data.

   ```python
   data = get_data()
   show_daily_sales(data)
   show_monthly_sales(data)
   ```

   Save your `app.py` file to see the preview. Delete these three lines when finished.

### Put the functions together together to create an app

Let's show these elements side-by-side. You'll display the daily data on the left and the monthly data on the right.

1. If you added optional lines at the end of your code to test your functions, clear them out now.

1. Give your app a wide layout.

   ```python
   st.set_page_config(layout="wide")
   ```

1. Get your data.

   ```python
   data = get_data()
   ```

1. Add a title and description for your app.

   ```python
   st.title("Daily vs monthly sales, by product")
   st.markdown("This app shows the 2023 daily sales for Widget A through Widget Z.")
   ```

1. Create columns and call the functions to display data.

   ```python
   daily, monthly = st.columns(2)
   with daily:
       show_daily_sales(data)
   with monthly:
       show_monthly_sales(data)
   ```

### Make it pretty

Now, you have a functioning app that uses a fragment to prevent unnecessarily redrawing the monthly data. However, things aren't aligned on the page, so you can insert a few containers to make it pretty. Add three containers into each of the display functions.

1. Add three containers to fix the height of elements in the `show_daily_sales` function.

   ```python
   @st.fragment
   def show_daily_sales(data):
       time.sleep(1)
       with st.container(height=100): ### ADD CONTAINER ###
           selected_date = st.date_input(
               "Pick a day ",
               value=date(2023, 1, 1),
               min_value=date(2023, 1, 1),
               max_value=date(2023, 12, 31),
               key="selected_date",
           )

       if "previous_date" not in st.session_state:
           st.session_state.previous_date = selected_date
       previous_date = st.session_state.previous_date
       previous_date = st.session_state.previous_date
       st.session_state.previous_date = selected_date
       is_new_month = selected_date.replace(day=1) != previous_date.replace(day=1)
       if is_new_month:
           st.rerun()

       with st.container(height=510): ### ADD CONTAINER ###
           st.header(f"Best sellers, {selected_date:%m/%d/%y}")
           top_ten = data.loc[selected_date].sort_values(ascending=False)[0:10]
           cols = st.columns([1, 4])
           cols[0].dataframe(top_ten)
           cols[1].bar_chart(top_ten)

       with st.container(height=510): ### ADD CONTAINER ###
           st.header(f"Worst sellers, {selected_date:%m/%d/%y}")
           bottom_ten = data.loc[selected_date].sort_values()[0:10]
           cols = st.columns([1, 4])
           cols[0].dataframe(bottom_ten)
           cols[1].bar_chart(bottom_ten)
   ```

1. Add three containers to fix the height of elements in the `show_monthly_sales` function.

   ```python
   def show_monthly_sales(data):
       time.sleep(1)
       selected_date = st.session_state.selected_date
       this_month = selected_date.replace(day=1)
       next_month = (selected_date.replace(day=28) + timedelta(days=4)).replace(day=1)

       st.container(height=100, border=False) ### ADD CONTAINER ###

       with st.container(height=510): ### ADD CONTAINER ###
           st.header(f"Daily sales for all products, {this_month:%B %Y}")
           monthly_sales = data[(data.index < next_month) & (data.index >= this_month)]
           st.write(monthly_sales)

       with st.container(height=510): ### ADD CONTAINER ###
           st.header(f"Total sales for all products, {this_month:%B %Y}")
           st.bar_chart(monthly_sales.sum())
   ```

   The first container creates space to coordinate with the input widget in the `show_daily_sales` function.

## Next steps

Continue beautifying the example. Try using [`st.plotly_chart`] or [`st.altair_chart`] to add labels to your charts and adjust their height.




------------------------------------------------------------------------------------------------
CHAPTER 3: llms.md
------------------------------------------------------------------------------------------------

################################################
Section 3.1 - conversational-apps.md
################################################


---
title: Build a basic LLM chat app
slug: /develop/tutorials/llms/build-conversational-apps
---

# Build a basic LLM chat app

## Introduction

The advent of large language models like GPT has revolutionized the ease of developing chat-based applications. Streamlit offers several [Chat elements], enabling you to build Graphical User Interfaces (GUIs) for conversational agents or chatbots. Leveraging [session state] along with these elements allows you to construct anything from a basic chatbot to a more advanced, ChatGPT-like experience using purely Python code.

In this tutorial, we'll start by walking through Streamlit's chat elements, `st.chat_message` and `st.chat_input`. Then we'll proceed to construct three distinct applications, each showcasing an increasing level of complexity and functionality:

1. First, we'll [Build a bot that mirrors your input](#build-a-bot-that-mirrors-your-input) to get a feel for the chat elements and how they work. We'll also introduce [session state] and how it can be used to store the chat history. This section will serve as a foundation for the rest of the tutorial.
2. Next, you'll learn how to [Build a simple chatbot GUI with streaming](#build-a-simple-chatbot-gui-with-streaming).
3. Finally, we'll [Build a ChatGPT-like app](#build-a-chatgpt-like-app) that leverages session state to remember conversational context, all within less than 50 lines of code.

Here's a sneak peek of the LLM-powered chatbot GUI with streaming we'll build in this tutorial:

<Cloud name="doc-chat-llm" height="700px" />

Play around with the above demo to get a feel for what we'll build in this tutorial. A few things to note:

- There's a chat input at the bottom of the screen that's always visible. It contains some placeholder text. You can type in a message and press Enter or click the run button to send it.
- When you enter a message, it appears as a chat message in the container above. The container is scrollable, so you can scroll up to see previous messages. A default avatar is displayed to your messages' left.
- The assistant's responses are streamed to the frontend and are displayed with a different default avatar.

Before we start building, let's take a closer look at the chat elements we'll use.

## Chat elements

Streamlit offers several commands to help you build conversational apps. These chat elements are designed to be used in conjunction with each other, but you can also use them separately.

[`st.chat_message`] lets you insert a chat message container into the app so you can display messages from the user or the app. Chat containers can contain other Streamlit elements, including charts, tables, text, and more. [`st.chat_input`] lets you display a chat input widget so the user can type in a message.

For an overview of the API, check out this video tutorial by Chanin Nantasenamat ([@dataprofessor]()), a Senior Developer Advocate at Streamlit.

<YouTube videoId="4sPnOqeUDmk" />

### st.chat_message

`st.chat_message` lets you insert a multi-element chat message container into your app. The returned container can contain any Streamlit element, including charts, tables, text, and more. To add elements to the returned container, you can use `with` notation.

`st.chat_message`'s first parameter is the `name` of the message author, which can be either `"user"` or `"assistant"` to enable preset styling and avatars, like in the demo above. You can also pass in a custom string to use as the author name. Currently, the name is not shown in the UI but is only set as an accessibility label. For accessibility reasons, you should not use an empty string.

Here's an minimal example of how to use `st.chat_message` to display a welcome message:

```python
import streamlit as st

with st.chat_message("user"):
    st.write("Hello 👋")
```

<Image src="/images/knowledge-base/chat-message-hello.png" clean />
<br />

Notice the message is displayed with a default avatar and styling since we passed in `"user"` as the author name. You can also pass in `"assistant"` as the author name to use a different default avatar and styling, or pass in a custom name and avatar. See the [API reference] for more details.

```python
import streamlit as st
import numpy as np

with st.chat_message("assistant"):
    st.write("Hello human")
    st.bar_chart(np.random.randn(30, 3))
```

<Cloud name="doc-chat-message-user1" height="450px" />

While we've used the preferred `with` notation in the above examples, you can also just call methods directly in the returned objects. The below example is equivalent to the one above:

```python
import streamlit as st
import numpy as np

message = st.chat_message("assistant")
message.write("Hello human")
message.bar_chart(np.random.randn(30, 3))
```

So far, we've displayed predefined messages. But what if we want to display messages based on user input?

### st.chat_input

`st.chat_input` lets you display a chat input widget so the user can type in a message. The returned value is the user's input, which is `None` if the user hasn't sent a message yet. You can also pass in a default prompt to display in the input widget. Here's an example of how to use `st.chat_input` to display a chat input widget and show the user's input:

```python
import streamlit as st

prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User has sent the following prompt: {prompt}")
```

<Cloud name="doc-chat-input" height="350px" />

Pretty straightforward, right? Now let's combine `st.chat_message` and `st.chat_input` to build a bot the mirrors or echoes your input.

## Build a bot that mirrors your input

In this section, we'll build a bot that mirrors or echoes your input. More specifically, the bot will respond to your input with the same message. We'll use `st.chat_message` to display the user's input and `st.chat_input` to accept user input. We'll also use [session state] to store the chat history so we can display it in the chat message container.

First, let's think about the different components we'll need to build our bot:

- Two chat message containers to display messages from the user and the bot, respectively.
- A chat input widget so the user can type in a message.
- A way to store the chat history so we can display it in the chat message containers. We can use a list to store the messages, and append to it every time the user or bot sends a message. Each entry in the list will be a dictionary with the following keys: `role` (the author of the message), and `content` (the message content).

```python
import streamlit as st

st.title("Echo Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```

In the above snippet, we've added a title to our app and a for loop to iterate through the chat history and display each message in the chat message container (with the author role and message content). We've also added a check to see if the `messages` key is in `st.session_state`. If it's not, we initialize it to an empty list. This is because we'll be adding messages to the list later on, and we don't want to overwrite the list every time the app reruns.

Now let's accept user input with `st.chat_input`, display the user's message in the chat message container, and add it to the chat history.

```python
# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
```

We used the `:=` operator to assign the user's input to the `prompt` variable and checked if it's not `None` in the same line. If the user has sent a message, we display the message in the chat message container and append it to the chat history.

All that's left to do is add the chatbot's responses within the `if` block. We'll use the same logic as before to display the bot's response (which is just the user's prompt) in the chat message container and add it to the history.

```python
response = f"Echo: {prompt}"
# Display assistant response in chat message container
with st.chat_message("assistant"):
    st.markdown(response)
# Add assistant response to chat history
st.session_state.messages.append({"role": "assistant", "content": response})
```

Putting it all together, here's the full code for our simple chatbot GUI and the result:

<Collapse title="View full code" expanded={false}>

```python
import streamlit as st

st.title("Echo Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Echo: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
```

</Collapse>

<Cloud name="doc-chat-echo" height="700px" />

While the above example is very simple, it's a good starting point for building more complex conversational apps. Notice how the bot responds instantly to your input. In the next section, we'll add a delay to simulate the bot "thinking" before responding.

## Build a simple chatbot GUI with streaming

In this section, we'll build a simple chatbot GUI that responds to user input with a random message from a list of pre-determind responses. In the [next section](#build-a-chatgpt-like-app), we'll convert this simple toy example into a ChatGPT-like experience using OpenAI.

Just like previously, we still require the same components to build our chatbot. Two chat message containers to display messages from the user and the bot, respectively. A chat input widget so the user can type in a message. And a way to store the chat history so we can display it in the chat message containers.

Let's just copy the code from the previous section and add a few tweaks to it.

```python
import streamlit as st
import random
import time

st.title("Simple chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
```

The only difference so far is we've changed the title of our app and added imports for `random` and `time`. We'll use `random` to randomly select a response from a list of responses and `time` to add a delay to simulate the chatbot "thinking" before responding.

All that's left to do is add the chatbot's responses within the `if` block. We'll use a list of responses and randomly select one to display. We'll also add a delay to simulate the chatbot "thinking" before responding (or stream its response). Let's make a helper function for this and insert it at the top of our app.

```python
# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)
```

Back to writing the response in our chat interface, we'll use `st.write_stream` to write out the streamed response with a typewriter effect.

```python
# Display assistant response in chat message container
with st.chat_message("assistant"):
    response = st.write_stream(response_generator())
# Add assistant response to chat history
st.session_state.messages.append({"role": "assistant", "content": response})
```

Above, we've added a placeholder to display the chatbot's response. We've also added a for loop to iterate through the response and display it one word at a time. We've added a delay of 0.05 seconds between each word to simulate the chatbot "thinking" before responding. Finally, we append the chatbot's response to the chat history. As you've probably guessed, this is a naive implementation of streaming. We'll see how to implement streaming with OpenAI in the [next section](#build-a-chatgpt-like-app).

Putting it all together, here's the full code for our simple chatbot GUI and the result:

<Collapse title="View full code" expanded={false}>

```python
import streamlit as st
import random
import time


# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.title("Simple chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator())
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
```

</Collapse>

<Cloud name="doc-chat-simple" height="700px" />

Play around with the above demo to get a feel for what we've built. It's a very simple chatbot GUI, but it has all the components of a more sophisticated chatbot. In the next section, we'll see how to build a ChatGPT-like app using OpenAI.

## Build a ChatGPT-like app

Now that you've understood the basics of Streamlit's chat elements, let's make a few tweaks to it to build our own ChatGPT-like app. You'll need to install the [OpenAI Python library]() and get an [API key]() to follow along.

### Install dependencies

First let's install the dependencies we'll need for this section:

```bash
pip install openai streamlit
```

### Add OpenAI API key to Streamlit secrets

Next, let's add our OpenAI API key to [Streamlit secrets]. We do this by creating `.streamlit/secrets.toml` file in our project directory and adding the following lines to it:

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "YOUR_API_KEY"
```

### Write the app

Now let's write the app. We'll use the same code as before, but we'll replace the list of responses with a call to the OpenAI API. We'll also add a few more tweaks to make the app more ChatGPT-like.

```python
import streamlit as st
from openai import OpenAI

st.title("ChatGPT-like clone")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
```

All that's changed is that we've added a default model to `st.session_state` and set our OpenAI API key from Streamlit secrets. Here's where it gets interesting. We can replace our emulated stream with the model's responses from OpenAI:

```python
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
```

Above, we've replaced the list of responses with a call to [`OpenAI().chat.completions.create`](). We've set `stream=True` to stream the responses to the frontend. In the API call, we pass the model name we hardcoded in session state and pass the chat history as a list of messages. We also pass the `role` and `content` of each message in the chat history. Finally, OpenAI returns a stream of responses (split into chunks of tokens), which we iterate through and display each chunk.

Putting it all together, here's the full code for our ChatGPT-like app and the result:

<Collapse title="View full code" expanded={false}>

```python
from openai import OpenAI
import streamlit as st

st.title("ChatGPT-like clone")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
```

<Image src="/images/knowledge-base/chatgpt-clone.gif" clean />

</Collapse>

<Cloud name="doc-chat-llm" height="700px" />

Congratulations! You've built your own ChatGPT-like app in less than 50 lines of code.

We're very excited to see what you'll build with Streamlit's chat elements. Experiment with different models and tweak the code to build your own conversational apps. If you build something cool, let us know on the [Forum]() or check out some other [Generative AI apps]() for inspiration. 🎈


################################################
Section 3.2 - llm-quickstart.md
################################################


---
title: Build an LLM app using LangChain
slug: /develop/tutorials/llms/llm-quickstart
---

# Build an LLM app using LangChain

## OpenAI, LangChain, and Streamlit in 18 lines of code

In this tutorial, you will build a Streamlit LLM app that can generate text from a user-provided prompt. This Python app will use the LangChain framework and Streamlit. Optionally, you can deploy your app to [Streamlit Community Cloud]() when you're done.

_This tutorial is adapted from a blog post by Chanin Nantesanamat: [LangChain tutorial #1: Build an LLM-powered app in 18 lines of code]()._

<Cloud name="doc-tutorial-llm-18-lines-of-code" height="600px" />

## Objectives

1. Get an OpenAI key from the end user.
2. Validate the user's OpenAI key.
3. Get a text prompt from the user.
4. Authenticate OpenAI with the user's key.
5. Send the user's prompt to OpenAI's API.
6. Get a response and display it.

Bonus: Deploy the app on Streamlit Community Cloud!

## Prerequisites

- Python 3.9+
- Streamlit
- LangChain
- [OpenAI API key](?ref=blog.streamlit.io)

## Setup coding environment

In your IDE (integrated coding environment), open the terminal and install the following two Python libraries:

```python
pip install streamlit langchain-openai
```

Create a `requirements.txt` file located in the root of your working directory and save these dependencies. This is necessary for deploying the app to the Streamlit Community Cloud later.

```python
streamlit
openai
langchain
```

## Building the app

The app is only 18 lines of code:

```python
import streamlit as st
from langchain_openai.chat_models import ChatOpenAI

st.title("🦜🔗 Quickstart App")

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")


def generate_response(input_text):
    model = ChatOpenAI(temperature=0.7, api_key=openai_api_key)
    st.info(model.invoke(input_text))


with st.form("my_form"):
    text = st.text_area(
        "Enter text:",
        "What are the three key pieces of advice for learning how to code?",
    )
    submitted = st.form_submit_button("Submit")
    if not openai_api_key.startswith("sk-"):
        st.warning("Please enter your OpenAI API key!", icon="⚠")
    if submitted and openai_api_key.startswith("sk-"):
        generate_response(text)

```

To start, create a new Python file and save it as `streamlit_app.py` in the root of your working directory.

1. Import the necessary Python libraries.

   ```python
   import streamlit as st
   from langchain_openai.chat_models import ChatOpenAI
   ```

2. Create the app's title using `st.title`.

   ```python
   st.title("🦜🔗 Quickstart App")
   ```

3. Add a text input box for the user to enter their OpenAI API key.

   ```python
   openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
   ```

4. Define a function to authenticate to OpenAI API with the user's key, send a prompt, and get an AI-generated response. This function accepts the user's prompt as an argument and displays the AI-generated response in a blue box using `st.info`.

   ```python
   def generate_response(input_text):
   model = ChatOpenAI(temperature=0.7, api_key=openai_api_key)
       st.info(model.invoke(input_text))
   ```

5. Finally, use `st.form()` to create a text box (`st.text_area()`) for user input. When the user clicks `Submit`, the `generate-response()` function is called with the user's input as an argument.

   ```python
   with st.form("my_form"):
       text = st.text_area(
           "Enter text:",
           "What are the three key pieces of advice for learning how to code?",
       )
       submitted = st.form_submit_button("Submit")
       if not openai_api_key.startswith("sk-"):
           st.warning("Please enter your OpenAI API key!", icon="⚠")
       if submitted and openai_api_key.startswith("sk-"):
           generate_response(text)
   ```

6. Remember to save your file!
7. Return to your computer's terminal to run the app.

   ```bash
   streamlit run streamlit_app.py
   ```

## Deploying the app

To deploy the app to the Streamlit Cloud, follow these steps:

1. Create a GitHub repository for the app. Your repository should contain two files:

   ```
   your-repository/
   ├── streamlit_app.py
   └── requirements.txt
   ```

1. Go to [Streamlit Community Cloud](), click the `New app` button from your workspace, then specify the repository, branch, and main file path. Optionally, you can customize your app's URL by choosing a custom subdomain.
1. Click the `Deploy!` button.

Your app will now be deployed to Streamlit Community Cloud and can be accessed from around the world! 🌎

## Conclusion

Congratulations on building an LLM-powered Streamlit app in 18 lines of code! 🥳 You can use this app to generate text from any prompt that you provide. The app is limited by the capabilities of the OpenAI LLM, but it can still be used to generate some creative and interesting text.

We hope you found this tutorial helpful! Check out [more examples]() to see the power of Streamlit and LLM. 💖

Happy Streamlit-ing! 🎈




------------------------------------------------------------------------------------------------
CHAPTER 4: multipage-apps.md
------------------------------------------------------------------------------------------------

################################################
Section 4.1 - custom-navigation.md
################################################


---
title: Build a custom navigation menu with `st.page_link`
slug: /develop/tutorials/multipage/st.page_link-nav
description: Streamlit makes it easy to build a custom navigation menu in your multipage app.
---

# Build a custom navigation menu with `st.page_link`

Streamlit lets you build custom navigation menus and elements with `st.page_link`. Introduced in Streamlit version 1.31.0, `st.page_link` can link to other pages in your multipage app or to external sites. When linked to another page in your app, `st.page_link` will show a highlight effect to indicate the current page. When combined with the [`client.showSidebarNavigation`] configuration option, you can build sleek, dynamic navigation in your app.

## Prerequisites

Create a new working directory in your development environment. We'll call this directory `your-repository`.

## Summary

In this example, we'll build a dynamic navigation menu for a multipage app that depends on the current user's role. We've abstracted away the use of username and creditials to simplify the example. Instead, we'll use a selectbox on the main page of the app to switch between roles. Session State will carry this selection between pages. The app will have a main page (`app.py`) which serves as the abstracted log-in page. There will be three additional pages which will be hidden or accessible, depending on the current role. The file structure will be as follows:

```
your-repository/
├── .streamlit/
│   └── config.toml
├── pages/
│   ├── admin.py
│   ├── super-admin.py
│   └── user.py
├── menu.py
└── app.py
```

Here's a look at what we'll build:

<Cloud name="doc-custom-navigation" height="400px" />

## Build the example

### Hide the default sidebar navigation

When creating a custom navigation menu, you need to hide the default sidebar navigation using `client.showSidebarNavigation`. Add the following `.streamlit/config.toml` file to your working directory:

```toml
[client]
showSidebarNavigation = false
```

### Create a menu function

You can write different menu logic for different pages or you can create a single menu function to call on multiple pages. In this example, we'll use the same menu logic on all pages, including a redirect to the main page when a user isn't logged in. We'll build a few helper functions to do this.

- `menu_with_redirect()` checks if a user is logged in, then either redirects them to the main page or renders the menu.
- `menu()` will call the correct helper function to render the menu based on whether the user is logged in or not.
- `authenticated_menu()` will display a menu based on an authenticated user's role.
- `unauthenticated_menu()` will display a menu for unauthenticated users.

We'll call `menu()` on the main page and call `menu_with_redirect()` on the other pages. `st.session_state.role` will store the current selected role. If this value does not exist or is set to `None`, then the user is not logged in. Otherwise, it will hold the user's role as a string: `"user"`, `"admin"`, or `"super-admin"`.

Add the following `menu.py` file to your working directory. (We'll describe the functions in more detail below.)

```python
import streamlit as st


def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("app.py", label="Switch accounts")
    st.sidebar.page_link("pages/user.py", label="Your profile")
    if st.session_state.role in ["admin", "super-admin"]:
        st.sidebar.page_link("pages/admin.py", label="Manage users")
        st.sidebar.page_link(
            "pages/super-admin.py",
            label="Manage admin access",
            disabled=st.session_state.role != "super-admin",
        )


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("app.py", label="Log in")


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        st.switch_page("app.py")
    menu()
```

Let's take a closer look at `authenticated_menu()`. When this function is called, `st.session_state.role` exists and has a value other than `None`.

```python
def authenticated_menu():
    # Show a navigation menu for authenticated users
```

The first two pages in the navigation menu are available to all users. Since we know a user is logged in when this function is called, we'll use the label "Switch accounts" for the main page. (If you don't use the `label` parameter, the page name will be derived from the file name like it is with the default sidebar navigation.)

```python
    st.sidebar.page_link("app.py", label="Switch accounts")
    st.sidebar.page_link("pages/user.py", label="Your profile")
```

We only want to show the next two pages to admins. Furthermore, we've chosen to disable&mdash;but not hide&mdash;the super-admin page when the admin user is not a super-admin. We do this using the `disabled` parameter. (`disabled=True` when the role is not `"super-admin"`.)

```
    if st.session_state.role in ["admin", "super-admin"]:
        st.sidebar.page_link("pages/admin.py", label="Manage users")
        st.sidebar.page_link(
            "pages/super-admin.py",
            label="Manage admin access",
            disabled=st.session_state.role != "super-admin",
        )
```

It's that simple! `unauthenticated_menu()` will only show a link to the main page of the app with the label "Log in." `menu()` does a simple inspection of `st.session_state.role` to switch between the two menu-rendering functions. Finally, `menu_with_redirect()` extends `menu()` to redirect users to `app.py` if they aren't logged in.

<Tip>

If you want to include emojis in your page labels, you can use the `icon` parameter. There's no need to include emojis in your file name or the `label` parameter.

</Tip>

### Create the main file of your app

The main `app.py` file will serve as a pseudo-login page. The user can choose a role from the `st.selectbox` widget. A few bits of logic will save that role into Session State to preserve it while navigating between pages&mdash;even when returning to `app.py`.

Add the following `app.py` file to your working directory:

```python
import streamlit as st
from menu import menu

# Initialize st.session_state.role to None
if "role" not in st.session_state:
    st.session_state.role = None

# Retrieve the role from Session State to initialize the widget
st.session_state._role = st.session_state.role

def set_role():
    # Callback function to save the role selection to Session State
    st.session_state.role = st.session_state._role


# Selectbox to choose role
st.selectbox(
    "Select your role:",
    [None, "user", "admin", "super-admin"],
    key="_role",
    on_change=set_role,
)
menu() # Render the dynamic menu!
```

### Add other pages to your app

Add the following `pages/user.py` file:

```python
import streamlit as st
from menu import menu_with_redirect

# Redirect to app.py if not logged in, otherwise show the navigation menu
menu_with_redirect()

st.title("This page is available to all users")
st.markdown(f"You are currently logged with the role of {st.session_state.role}.")
```

Session State resets if a user manually navigates to a page by URL. Therefore, if a user tries to access an admin page in this example, Session State will be cleared, and they will be redirected to the main page as an unauthenicated user. However, it's still good practice to include a check of the role at the top of each restricted page. You can use `st.stop` to halt an app if a role is not whitelisted.

`pages/admin.py`:

```python
import streamlit as st
from menu import menu_with_redirect

# Redirect to app.py if not logged in, otherwise show the navigation menu
menu_with_redirect()

# Verify the user's role
if st.session_state.role not in ["admin", "super-admin"]:
    st.warning("You do not have permission to view this page.")
    st.stop()

st.title("This page is available to all admins")
st.markdown(f"You are currently logged with the role of {st.session_state.role}.")
```

`pages/super-admin.py`:

```python
import streamlit as st
from menu import menu_with_redirect

# Redirect to app.py if not logged in, otherwise show the navigation menu
menu_with_redirect()

# Verify the user's role
if st.session_state.role not in ["super-admin"]:
    st.warning("You do not have permission to view this page.")
    st.stop()

st.title("This page is available to super-admins")
st.markdown(f"You are currently logged with the role of {st.session_state.role}.")
```

As noted above, the redirect in `menu_with_redirect()` will prevent a user from ever seeing the warning messages on the admin pages. If you want to see the warning, just add another `st.page_link("pages/admin.py")` button at the bottom of `app.py` so you can navigate to the admin page after selecting the "user" role. 😉


################################################
Section 4.2 - dynamic-navigation.md
################################################


---
title: Create a dynamic navigation menu
slug: /develop/tutorials/multipage/dynamic-navigation
description: Streamlit makes it easy to build a custom navigation menu in your multipage app.
---

# Create a dynamic navigation menu

`st.navigation` makes it easy to build dynamic navigation menus. You can change the set of pages passed to `st.navigation` with each rerun, which changes the navigation menu to match. This is a convenient feature for creating custom, role-based navigation menus.

This tutorial uses `st.navigation` and `st.Page`, which were introduced in Streamlit version 1.36.0. For an older workaround using the `pages/` directory and `st.page_link`, see [Build a custom navigation menu with `st.page_link`].

## Applied concepts

- Use `st.navigation` and `st.Page` to define a multipage app.
- Create a dynamic, role-based navigation menu.

## Prerequisites

- The following must be installed in your Python environment:

  ```
  streamlit>=1.36.0
  ```

- You should have a clean working directory called `your-repository`.
- You should have a basic understanding of `st.navigation` and `st.Page`.

## Summary

In this example, we'll build a dynamic navigation menu for a multipage app that depends on the current user's role. You'll abstract away the use of username and credentials to simplify the example. Instead, you'll use a selectbox to let users choose a role and log in.

The entrypoint file, `streamlit_app.py` will handle user authentication. The other pages will be stubs representing account management (`settings.py`) and specific pages associated to three roles: Requester, Responder, and Admin. Requesters can access the account and request pages. Responders can access the account and respond pages. Admins can access all pages.

Here's a look at what we'll build:

<Collapse title="Complete code" expanded={false}>

**Directory structure:**

```
your-repository/
├── admin
│   ├── admin_1.py
│   └── admin_2.py
├── images
│   ├── horizontal_blue.png
│   └── icon_blue.png
├── request
│   ├── request_1.py
│   └── request_2.py
├── respond
│   ├── respond_1.py
│   └── respond_2.py
├── settings.py
└── streamlit_app.py
```

**`streamlit_app.py`:**

```python
import streamlit as st

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "Requester", "Responder", "Admin"]


def login():

    st.header("Log in")
    role = st.selectbox("Choose your role", ROLES)

    if st.button("Log in"):
        st.session_state.role = role
        st.rerun()


def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
request_1 = st.Page(
    "request/request_1.py",
    title="Request 1",
    icon=":material/help:",
    default=(role == "Requester"),
)
request_2 = st.Page(
    "request/request_2.py", title="Request 2", icon=":material/bug_report:"
)
respond_1 = st.Page(
    "respond/respond_1.py",
    title="Respond 1",
    icon=":material/healing:",
    default=(role == "Responder"),
)
respond_2 = st.Page(
    "respond/respond_2.py", title="Respond 2", icon=":material/handyman:"
)
admin_1 = st.Page(
    "admin/admin_1.py",
    title="Admin 1",
    icon=":material/person_add:",
    default=(role == "Admin"),
)
admin_2 = st.Page("admin/admin_2.py", title="Admin 2", icon=":material/security:")

account_pages = [logout_page, settings]
request_pages = [request_1, request_2]
respond_pages = [respond_1, respond_2]
admin_pages = [admin_1, admin_2]

st.title("Request manager")
st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")

page_dict = {}
if st.session_state.role in ["Requester", "Admin"]:
    page_dict["Request"] = request_pages
if st.session_state.role in ["Responder", "Admin"]:
    page_dict["Respond"] = respond_pages
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()
```

</Collapse>

<Cloud name="doc-dynamic-navigation" height="600px" />

## Build the example

### Initialize your app

1. In `your_repository`, create a file named `streamlit_app.py`.
1. In a terminal, change directories to `your_repository` and start your app.

   ```bash
   streamlit run streamlit_app.py
   ```

   Your app will be blank since you still need to add code.

1. In `streamlit_app.py`, write the following:

   ```python
   import streamlit as st
   ```

1. Save your `streamlit_app.py` file and view your running app.
1. Click "**Always rerun**" or hit your "**A**" key in your running app.

   Your running preview will automatically update as you save changes to `streamlit_app.py`. Your preview will still be blank. Return to your code.

### Add your page and image files

1. In `your_repositoy`, create a file named `settings.py`.

1. In `settings.py` add the following stub.

   ```python
   import streamlit as st

   st.header("Settings")
   st.write(f"You are logged in as {st.session_state.role}.")
   ```

   In later steps, you'll create an authentication method that saves the current user's role to `st.session_state.role`. Since you'll be blocking access to this page until a user is logged in, you don't need to initialize the `"role"` key in Session State for this page.

1. Create similar stubs by changing the value of `st.header` for the following six pages:

   ```
   your-repository/
   ├── admin
   │   ├── admin_1.py
   │   └── admin_2.py
   ├── request
   │   ├── request_1.py
   │   └── request_2.py
   └── respond
       ├── respond_1.py
       └── respond_2.py
   ```

   For example, `admin/admin_1.py` should be the following:

   ```python
   import streamlit as st

   st.header("Admin 1")
   st.write(f"You are logged in as {st.session_state.role}.")
   ```

1. Create an `images` subdirectory in `your-repository` and add the following two files:

   - [horizontal_blue.png](/images/horizontal_blue.png)
   - [icon_blue.png](/images/icon_blue.png)

   You now have all the files needed to build your app.

### Initialize global values

1. Return to `streamlit_app.py` and initialize `"role"` in Session State.

   ```python
   if "role" not in st.session_state:
       st.session_state.role = None
   ```

   You will use this value to gatekeep access to your app. This represents the role of the current, authenticated user.

1. Define the available roles.

   ```python
   ROLES = [None, "Requester", "Responder", "Admin"]
   ```

   `None` is included as a role since that is the value corresponding to an unauthenticated user.

### Define your user authentication pages

`st.navigation` lets you define pages from Python functions. Here, you'll define the login and logout pages from Python functions.

1. Begin your login page (function definition).

   ```python
   def login():
   ```

1. Add a header for the page.

   ```python
       st.header("Log in")
   ```

1. Create a selectbox for the user to choose a role.

   ```python
       role = st.selectbox("Choose your role", ROLES)
   ```

1. Add a button to commit the user role to Session State.

   ```python
       if st.button("Log in"):
           st.session_state.role = role
           st.rerun()
   ```

   This is an abstraction of an authentication workflow. When a user clicks the button, Streamlit saves the role to Session State and reruns the app. In later steps, you'll add logic to direct users to a role's default page when the value changes in `st.session_state.role`. This completes your login page function.

1. Begin your logout page (function definition).

   ```python
   def logout():
   ```

1. Immediately set the role to `None` and rerun the app.

   ```python
       st.session_state.role = None
       st.rerun()
   ```

   Since the lougout page function immediately updates Session State and reruns, a user will never view this page. The page will execute in a fraction of a second and, upon rerunning, the app will send the user to the login page. Therefore, no additional elements are rendered on the page. If desired, you can change this page to also include a button, similar to the login page. A button would allow users to confirm they really intend to log out.

### Define all your pages

1. As a convenience, save `st.session_state.role` to a variable.

   ```python
   role = st.session_state.role
   ```

1. Define your account pages.

   ```python
   logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
   settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
   ```

   This gives each page a nice title and icon to make your navigation menu look neat and clean.

1. Define your request pages.

   ```python
   request_1 = st.Page(
       "request/request_1.py",
       title="Request 1",
       icon=":material/help:",
       default=(role == "Requester"),
   )
   request_2 = st.Page(
       "request/request_2.py", title="Request 2", icon=":material/bug_report:"
   )
   ```

   If you don't manually declare a default page in `st.navigation`, then the first page will automatically be the default. The first page in the menu will be "Log out" within an "Account" section of the menu. Therefore, you'll need to tell Streamlit what page each user should be directed to by default.

   This code dynamically sets `default=True` when the role is "Requester" and sets it to `False`, otherwise.

1. Define your remaining pages.

   ```python
   respond_1 = st.Page(
       "respond/respond_1.py",
       title="Respond 1",
       icon=":material/healing:",
       default=(role == "Responder"),
   )
   respond_2 = st.Page(
       "respond/respond_2.py", title="Respond 2", icon=":material/handyman:"
   )
   admin_1 = st.Page(
       "admin/admin_1.py",
       title="Admin 1",
       icon=":material/person_add:",
       default=(role == "Admin"),
   )
   admin_2 = st.Page("admin/admin_2.py", title="Admin 2", icon=":material/security:")
   ```

   Similar to the request pages, the `default` parameter is set for the other roles' default pages.

1. Group your pages into convenient lists.

   ```python
   account_pages = [logout_page, settings]
   request_pages = [request_1, request_2]
   respond_pages = [respond_1, respond_2]
   admin_pages = [admin_1, admin_2]
   ```

   These are all the pages available to logged-in users.

### Define your common elements and navigation

1. Add a title to show on all pages.

   ```python
   st.title("Request manager")
   ```

   Since you're calling the title command in your entrypoint file, this title will be visible on all pages. Elements created in your entrypoint file create a frame of common elements around all your pages.

1. Add a logo to your app.

   ```python
   st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")
   ```

   Once again, since you're calling this command in your entrypoint file, you won't need to also call it within each page.

1. Initialize a dictionary of page lists.

   ```python
   page_dict = {}
   ```

   In the next step, you'll check the user's role and add pages to the dictionary that the user is allowed to access. When `st.navigation` receives a dictionary of page lists, it creates a navigation menu with groups of pages and section headers.

1. Build the dictionary of allowed pages by checking the user's role.

   ```python
   if st.session_state.role in ["Requester", "Admin"]:
       page_dict["Request"] = request_pages
   if st.session_state.role in ["Responder", "Admin"]:
       page_dict["Respond"] = respond_pages
   if st.session_state.role == "Admin":
       page_dict["Admin"] = admin_pages
   ```

1. Check if the user is allowed to access any pages and add the account pages if they are.

   ```python
   if len(page_dict) > 0:
       pg = st.navigation({"Account": account_pages} | page_dict)
   ```

   If `page_dict` is not empty, then the user is logged in. The `|` operator merges the two dictionaries, adding the account pages to the beginning.

1. Fallback to the login page if the user isn't logged in.

   ```python
   else:
       pg = st.navigation([st.Page(login)])
   ```

1. Execute the page returned by `st.navigation`.

   ```python
   pg.run()
   ```

1. Save your `streamlit_app.py` file and view your app!

   Try logging in, switching pages, and logging out. Try again with a different role.




