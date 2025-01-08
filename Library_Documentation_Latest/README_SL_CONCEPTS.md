The .add_rows() method
Animate and update elements
Sometimes you display a chart or dataframe and want to modify it live as the app runs (for example, in a loop). Some elements have built-in methods to allow you to update them in-place without rerunning the app.

Updatable elements include the following:

st.empty containers can be written to in sequence and will always show the last thing written. They can also be cleared with an additional .empty() called like a method.
st.dataframe, st.table, and many chart elements can be updated with the .add_rows() method which appends data.
st.progress elements can be updated with additional .progress() calls. They can also be cleared with a .empty() method call.
st.status containers have an .update() method to change their labels, expanded state, and status.
st.toast messages can be updated in place with additional .toast() calls.
st.empty containers
st.empty can hold a single element. When you write any element to an st.empty container, Streamlit discards its previous content displays the new element. You can also st.empty containers by calling .empty() as a method. If you want to update a set of elements, use a plain container (st.container()) inside st.empty and write contents to the plain container. Rewrite the plain container and its contents as often as desired to update your app's display.

The .add_rows() method
st.dataframe, st.table, and all chart functions can be mutated using the .add_rows() method on their output. In the following example, we use my_data_element = st.line_chart(df). You can try the example with st.table, st.dataframe, and most of the other simple charts by just swapping out st.line_chart. Note that st.dataframe only shows the first ten rows by default and enables scrolling for additional rows. This means adding rows is not as visually apparent as it is with st.table or the chart elements.

import streamlit as st
import pandas as pd
import numpy as np
import time

df = pd.DataFrame(np.random.randn(15, 3), columns=(["A", "B", "C"]))
my_data_element = st.line_chart(df)

for tick in range(10):
    time.sleep(.5)
    add_df = pd.DataFrame(np.random.randn(1, 3), columns=(["A", "B", "C"]))
    my_data_element.add_rows(add_df)

st.button("Regenerate")


---


Button behavior and examples
Summary
Buttons created with st.button do not retain state. They return True on the script rerun resulting from their click and immediately return to False on the next script rerun. If a displayed element is nested inside if st.button('Click me'):, the element will be visible when the button is clicked and disappear as soon as the user takes their next action. This is because the script reruns and the button return value becomes False.

In this guide, we will illustrate the use of buttons and explain common misconceptions. Read on to see a variety of examples that expand on st.button using st.session_state. Anti-patterns are included at the end. Go ahead and pull up your favorite code editor so you can streamlit run the examples as you read. Check out Streamlit's Basic concepts if you haven't run your own Streamlit scripts yet.

When to use if st.button()
When code is conditioned on a button's value, it will execute once in response to the button being clicked and not again (until the button is clicked again).

Good to nest inside buttons:

Transient messages that immediately disappear.
Once-per-click processes that saves data to session state, a file, or a database.
Bad to nest inside buttons:

Displayed items that should persist as the user continues.
Other widgets which cause the script to rerun when used.
Processes that neither modify session state nor write to a file/database.*
* This can be appropriate when disposable results are desired. If you have a "Validate" button, that could be a process conditioned directly on a button. It could be used to create an alert to say 'Valid' or 'Invalid' with no need to keep that info.

Common logic with buttons
Show a temporary message with a button
If you want to give the user a quick button to check if an entry is valid, but not keep that check displayed as the user continues.

In this example, a user can click a button to check if their animal string is in the animal_shelter list. When the user clicks "Check availability" they will see "We have that animal!" or "We don't have that animal." If they change the animal in st.text_input, the script reruns and the message disappears until they click "Check availability" again.

import streamlit as st

animal_shelter = ['cat', 'dog', 'rabbit', 'bird']

animal = st.text_input('Type an animal')

if st.button('Check availability'):
    have_it = animal.lower() in animal_shelter
    'We have that animal!' if have_it else 'We don\'t have that animal.'
Note: The above example uses magic to render the message on the frontend.

Stateful button
If you want a clicked button to continue to be True, create a value in st.session_state and use the button to set that value to True in a callback.

import streamlit as st

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.button('Click me', on_click=click_button)

if st.session_state.clicked:
    # The message and nested widget will remain on the page
    st.write('Button clicked!')
    st.slider('Select a value')
Toggle button
If you want a button to work like a toggle switch, consider using st.checkbox. Otherwise, you can use a button with a callback function to reverse a boolean value saved in st.session_state.

In this example, we use st.button to toggle another widget on and off. By displaying st.slider conditionally on a value in st.session_state, the user can interact with the slider without it disappearing.

import streamlit as st

if 'button' not in st.session_state:
    st.session_state.button = False

def click_button():
    st.session_state.button = not st.session_state.button

st.button('Click me', on_click=click_button)

if st.session_state.button:
    # The message and nested widget will remain on the page
    st.write('Button is on!')
    st.slider('Select a value')
else:
    st.write('Button is off!')
Alternatively, you can use the value in st.session_state on the slider's disabled parameter.

import streamlit as st

if 'button' not in st.session_state:
    st.session_state.button = False

def click_button():
    st.session_state.button = not st.session_state.button

st.button('Click me', on_click=click_button)

st.slider('Select a value', disabled=st.session_state.button)
Buttons to continue or control stages of a process
Another alternative to nesting content inside a button is to use a value in st.session_state that designates the "step" or "stage" of a process. In this example, we have four stages in our script:

Before the user begins.
User enters their name.
User chooses a color.
User gets a thank-you message.
A button at the beginning advances the stage from 0 to 1. A button at the end resets the stage from 3 to 0. The other widgets used in stage 1 and 2 have callbacks to set the stage. If you have a process with dependant steps and want to keep previous stages visible, such a callback forces a user to retrace subsequent stages if they change an earlier widget.

import streamlit as st

if 'stage' not in st.session_state:
    st.session_state.stage = 0

def set_state(i):
    st.session_state.stage = i

if st.session_state.stage == 0:
    st.button('Begin', on_click=set_state, args=[1])

if st.session_state.stage >= 1:
    name = st.text_input('Name', on_change=set_state, args=[2])

if st.session_state.stage >= 2:
    st.write(f'Hello {name}!')
    color = st.selectbox(
        'Pick a Color',
        [None, 'red', 'orange', 'green', 'blue', 'violet'],
        on_change=set_state, args=[3]
    )
    if color is None:
        set_state(2)

if st.session_state.stage >= 3:
    st.write(f':{color}[Thank you!]')
    st.button('Start Over', on_click=set_state, args=[0])
Buttons to modify st.session_state
If you modify st.session_state inside of a button, you must consider where that button is within the script.

A slight problem
In this example, we access st.session_state.name both before and after the buttons which modify it. When a button ("Jane" or "John") is clicked, the script reruns. The info displayed before the buttons lags behind the info written after the button. The data in st.session_state before the button is not updated. When the script executes the button function, that is when the conditional code to update st.session_state creates the change. Thus, this change is reflected after the button.

import streamlit as st
import pandas as pd

if 'name' not in st.session_state:
    st.session_state['name'] = 'John Doe'

st.header(st.session_state['name'])

if st.button('Jane'):
    st.session_state['name'] = 'Jane Doe'

if st.button('John'):
    st.session_state['name'] = 'John Doe'

st.header(st.session_state['name'])
Logic used in a callback
Callbacks are a clean way to modify st.session_state. Callbacks are executed as a prefix to the script rerunning, so the position of the button relative to accessing data is not important.

import streamlit as st
import pandas as pd

if 'name' not in st.session_state:
    st.session_state['name'] = 'John Doe'

def change_name(name):
    st.session_state['name'] = name

st.header(st.session_state['name'])

st.button('Jane', on_click=change_name, args=['Jane Doe'])
st.button('John', on_click=change_name, args=['John Doe'])

st.header(st.session_state['name'])
Logic nested in a button with a rerun
Although callbacks are often preferred to avoid extra reruns, our first 'John Doe'/'Jane Doe' example can be modified by adding st.rerun instead. If you need to acces data in st.session_state before the button that modifies it, you can include st.rerun to rerun the script after the change has been committed. This means the script will rerun twice when a button is clicked.

import streamlit as st
import pandas as pd

if 'name' not in st.session_state:
    st.session_state['name'] = 'John Doe'

st.header(st.session_state['name'])

if st.button('Jane'):
    st.session_state['name'] = 'Jane Doe'
    st.rerun()

if st.button('John'):
    st.session_state['name'] = 'John Doe'
    st.rerun()

st.header(st.session_state['name'])
Buttons to modify or reset other widgets
When a button is used to modify or reset another widget, it is the same as the above examples to modify st.session_state. However, an extra consideration exists: you cannot modify a key-value pair in st.session_state if the widget with that key has already been rendered on the page for the current script run.

priority_high
Important
Don't do this!

import streamlit as st

st.text_input('Name', key='name')

# These buttons will error because their nested code changes
# a widget's state after that widget within the script.
if st.button('Clear name'):
    st.session_state.name = ''
if st.button('Streamlit!'):
    st.session_state.name = ('Streamlit')
Option 1: Use a key for the button and put the logic before the widget
If you assign a key to a button, you can condition code on a button's state by using its value in st.session_state. This means that logic depending on your button can be in your script before that button. In the following example, we use the .get() method on st.session_state because the keys for the buttons will not exist when the script runs for the first time. The .get() method will return False if it can't find the key. Otherwise, it will return the value of the key.

import streamlit as st

# Use the get method since the keys won't be in session_state
# on the first script run
if st.session_state.get('clear'):
    st.session_state['name'] = ''
if st.session_state.get('streamlit'):
    st.session_state['name'] = 'Streamlit'

st.text_input('Name', key='name')

st.button('Clear name', key='clear')
st.button('Streamlit!', key='streamlit')
Option 2: Use a callback
import streamlit as st

st.text_input('Name', key='name')

def set_name(name):
    st.session_state.name = name

st.button('Clear name', on_click=set_name, args=[''])
st.button('Streamlit!', on_click=set_name, args=['Streamlit'])
Option 3: Use containers
By using st.container you can have widgets appear in different orders in your script and frontend view (webpage).

import streamlit as st

begin = st.container()

if st.button('Clear name'):
    st.session_state.name = ''
if st.button('Streamlit!'):
    st.session_state.name = ('Streamlit')

# The widget is second in logic, but first in display
begin.text_input('Name', key='name')
Buttons to add other widgets dynamically
When dynamically adding widgets to the page, make sure to use an index to keep the keys unique and avoid a DuplicateWidgetID error. In this example, we define a function display_input_row which renders a row of widgets. That function accepts an index as a parameter. The widgets rendered by display_input_row use index within their keys so that dispaly_input_row can be executed multiple times on a single script rerun without repeating any widget keys.

import streamlit as st

def display_input_row(index):
    left, middle, right = st.columns(3)
    left.text_input('First', key=f'first_{index}')
    middle.text_input('Middle', key=f'middle_{index}')
    right.text_input('Last', key=f'last_{index}')

if 'rows' not in st.session_state:
    st.session_state['rows'] = 0

def increase_rows():
    st.session_state['rows'] += 1

st.button('Add person', on_click=increase_rows)

for i in range(st.session_state['rows']):
    display_input_row(i)

# Show the results
st.subheader('People')
for i in range(st.session_state['rows']):
    st.write(
        f'Person {i+1}:',
        st.session_state[f'first_{i}'],
        st.session_state[f'middle_{i}'],
        st.session_state[f'last_{i}']
    )
Buttons to handle expensive or file-writing processes
When you have expensive processes, set them to run upon clicking a button and save the results into st.session_state. This allows you to keep accessing the results of the process without re-executing it unnecessarily. This is especially helpful for processes that save to disk or write to a database. In this example, we have an expensive_process that depends on two parameters: option and add. Functionally, add changes the output, but option does not—option is there to provide a parameter

import streamlit as st
import pandas as pd
import time

def expensive_process(option, add):
    with st.spinner('Processing...'):
        time.sleep(5)
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C':[7, 8, 9]}) + add
    return (df, add)

cols = st.columns(2)
option = cols[0].selectbox('Select a number', options=['1', '2', '3'])
add = cols[1].number_input('Add a number', min_value=0, max_value=10)

if 'processed' not in st.session_state:
    st.session_state.processed = {}

# Process and save results
if st.button('Process'):
    result = expensive_process(option, add)
    st.session_state.processed[option] = result

if option in st.session_state.processed:
    st.write(f'Option {option} processed with add {add}')
    st.write(st.session_state.processed[option][0])
Astute observers may think, "This feels a little like caching." We are only saving results relative to one parameter, but the pattern could easily be expanded to save results relative to both parameters. In that sense, yes, it has some similarities to caching, but also some important differences. When you save results in st.session_state, the results are only available to the current user in their current session. If you use st.cache_data instead, the results are available to all users across all sessions. Furthermore, if you want to update a saved result, you have to clear all saved results for that function to do so.

Anti-patterns
Here are some simplified examples of how buttons can go wrong. Be on the lookout for these common mistakes.

Buttons nested inside buttons
import streamlit as st

if st.button('Button 1'):
    st.write('Button 1 was clicked')
    if st.button('Button 2'):
        # This will never be executed.
        st.write('Button 2 was clicked')
Other widgets nested inside buttons
import streamlit as st

if st.button('Sign up'):
    name = st.text_input('Name')

    if name:
        # This will never be executed.
        st.success(f'Welcome {name}')
Nesting a process inside a button without saving to session state
import streamlit as st
import pandas as pd

file = st.file_uploader("Upload a file", type="csv")

if st.button('Get data'):
    df = pd.read_csv(file)
    # This display will go away with the user's next action.
    st.write(df)

if st.button('Save'):
    # This will always error.
    df.to_csv('data.csv')
	
	
	---
	
	
	Dataframes
Dataframes are a great way to display and edit data in a tabular format. Working with Pandas DataFrames and other tabular data structures is key to data science workflows. If developers and data scientists want to display this data in Streamlit, they have multiple options: st.dataframe and st.data_editor. If you want to solely display data in a table-like UI, st.dataframe is the way to go. If you want to interactively edit data, use st.data_editor. We explore the use cases and advantages of each option in the following sections.

Display dataframes with st.dataframe
Streamlit can display dataframes in a table-like UI via st.dataframe :

import streamlit as st
import pandas as pd

df = pd.DataFrame(
    [
        {"command": "st.selectbox", "rating": 4, "is_widget": True},
        {"command": "st.balloons", "rating": 5, "is_widget": False},
        {"command": "st.time_input", "rating": 3, "is_widget": True},
    ]
)

st.dataframe(df, use_container_width=True)

Built with Streamlit 🎈
Fullscreen
open_in_new
st.dataframe UI features
st.dataframe provides additional functionality by using glide-data-grid under the hood:

Column sorting: Sort columns by clicking on their headers.
Column resizing: Resize columns by dragging and dropping column header borders.
Table resizing: Resize tables by dragging and dropping the bottom right corner.
Fullscreen view: Enlarge tables to fullscreen by clicking the fullscreen icon (fullscreen) in the toolbar.
Search: Click the search icon (search) in the toolbar or use hotkeys (⌘+F or Ctrl+F) to search through the data.
Download: Click the download icon in the toolbar to download the data as a CSV file.
Copy to clipboard: Select one or multiple cells, copy them to the clipboard (⌘+C or Ctrl+C), and paste them into your favorite spreadsheet software.

Try out all the UI features using the embedded app from the prior section.

In addition to Pandas DataFrames, st.dataframe also supports other common Python types, e.g., list, dict, or numpy array. It also supports Snowpark and PySpark DataFrames, which allow you to lazily evaluate and pull data from databases. This can be useful for working with large datasets.

Edit data with st.data_editor
Streamlit supports editable dataframes via the st.data_editor command. Check out its API in st.data_editor. It shows the dataframe in a table, similar to st.dataframe. But in contrast to st.dataframe, this table isn't static! The user can click on cells and edit them. The edited data is then returned on the Python side. Here's an example:

df = pd.DataFrame(
    [
        {"command": "st.selectbox", "rating": 4, "is_widget": True},
        {"command": "st.balloons", "rating": 5, "is_widget": False},
        {"command": "st.time_input", "rating": 3, "is_widget": True},
    ]
)

edited_df = st.data_editor(df) # 👈 An editable dataframe

favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
st.markdown(f"Your favorite command is **{favorite_command}** 🎈")

Built with Streamlit 🎈
Fullscreen
open_in_new
Try it out by double-clicking on any cell. You'll notice you can edit all cell values. Try editing the values in the rating column and observe how the text output at the bottom changes:

st.data_editor UI features
st.data_editor also supports a few additional things:

Add and delete rows: You can do this by setting num_rows= "dynamic" when calling st.data_editor. This will allow users to add and delete rows as needed.
Copy and paste support: Copy and paste both between st.data_editor and spreadsheet software like Google Sheets and Excel.
Access edited data: Access only the individual edits instead of the entire edited data structure via Session State.
Bulk edits: Similar to Excel, just drag a handle to edit neighboring cells.
Automatic input validation: Column Configuration provides strong data type support and other configurable options. For example, there's no way to enter letters into a number cell. Number cells can have a designated min and max.
Edit common data structures: st.data_editor supports lists, dicts, NumPy ndarray, and more!

Add and delete rows
With st.data_editor, viewers can add or delete rows via the table UI. This mode can be activated by setting the num_rows parameter to "dynamic":

edited_df = st.data_editor(df, num_rows="dynamic")
To add new rows, click the plus icon (add) in the toolbar. Alternatively, click inside a shaded cell below the bottom row of the table.
To delete rows, select one or more rows using the checkboxes on the left. Click the delete icon (delete) or press the delete key on your keyboard.

Built with Streamlit 🎈
Fullscreen
open_in_new
Copy and paste support
The data editor supports pasting in tabular data from Google Sheets, Excel, Notion, and many other similar tools. You can also copy-paste data between st.data_editor instances. This functionality, powered by the Clipboard API, can be a huge time saver for users who need to work with data across multiple platforms. To try it out:

Copy data from this Google Sheets document to your clipboard.
Single click any cell in the name column in the app above. Paste it in using hotkeys (⌘+V or Ctrl+V).
push_pin
Note
Every cell of the pasted data will be evaluated individually and inserted into the cells if the data is compatible with the column type. For example, pasting in non-numerical text data into a number column will be ignored.

star
Tip
If you embed your apps with iframes, you'll need to allow the iframe to access the clipboard if you want to use the copy-paste functionality. To do so, give the iframe clipboard-write and clipboard-read permissions. E.g.

<iframe allow="clipboard-write;clipboard-read;" ... src="https://your-app-url"></iframe>
As developers, ensure the app is served with a valid, trusted certificate when using TLS. If users encounter issues with copying and pasting data, direct them to check if their browser has activated clipboard access permissions for the Streamlit application, either when prompted or through the browser's site settings.

Access edited data
Sometimes, it is more convenient to know which cells have been changed rather than getting the entire edited dataframe back. Streamlit makes this easy through the use of Session State. If a key parameter is set, Streamlit will store any changes made to the dataframe in Session State.

This snippet shows how you can access changed data using Session State:

st.data_editor(df, key="my_key", num_rows="dynamic") # 👈 Set a key
st.write("Here's the value in Session State:")
st.write(st.session_state["my_key"]) # 👈 Show the value in Session State
In this code snippet, the key parameter is set to "my_key". After the data editor is created, the value associated to "my_key" in Session State is displayed in the app using st.write. This shows the additions, edits, and deletions that were made.

This can be useful when working with large dataframes and you only need to know which cells have changed, rather than access the entire edited dataframe.


Built with Streamlit 🎈
Fullscreen
open_in_new
Use all we've learned so far and apply them to the above embedded app. Try editing cells, adding new rows, and deleting rows.

Notice how edits to the table are reflected in Session State. When you make any edits, a rerun is triggered which sends the edits to the backend. The widget's state is a JSON object containing three properties: edited_rows, added_rows, and deleted rows:.

priority_high
Warning
When going from st.experimental_data_editor to st.data_editor in 1.23.0, the data editor's representation in st.session_state was changed. The edited_cells dictionary is now called edited_rows and uses a different format ({0: {"column name": "edited value"}} instead of {"0:1": "edited value"}). You may need to adjust your code if your app uses st.experimental_data_editor in combination with st.session_state."

edited_rows is a dictionary containing all edits. Keys are zero-based row indices and values are dictionaries that map column names to edits (e.g. {0: {"col1": ..., "col2": ...}}).
added_rows is a list of newly added rows. Each value is a dictionary with the same format as above (e.g. [{"col1": ..., "col2": ...}]).
deleted_rows is a list of row numbers that have been deleted from the table (e.g. [0, 2]).
st.data_editor does not support reordering rows, so added rows will always be appended to the end of the dataframe with any edits and deletions applicable to the original rows.

Bulk edits
The data editor includes a feature that allows for bulk editing of cells. Similar to Excel, you can drag a handle across a selection of cells to edit their values in bulk. You can even apply commonly used keyboard shortcuts in spreadsheet software. This is useful when you need to make the same change across multiple cells, rather than editing each cell individually.

Edit common data structures
Editing doesn't just work for Pandas DataFrames! You can also edit lists, tuples, sets, dictionaries, NumPy arrays, or Snowpark & PySpark DataFrames. Most data types will be returned in their original format. But some types (e.g. Snowpark and PySpark) are converted to Pandas DataFrames. To learn about all the supported types, read the st.data_editor API.

For example, you can easily let the user add items to a list:

edited_list = st.data_editor(["red", "green", "blue"], num_rows= "dynamic")
st.write("Here are all the colors you entered:")
st.write(edited_list)
Or numpy arrays:

import numpy as np

st.data_editor(np.array([
	["st.text_area", "widget", 4.92],
	["st.markdown", "element", 47.22]
]))
Or lists of records:

st.data_editor([
    {"name": "st.text_area", "type": "widget"},
    {"name": "st.markdown", "type": "element"},
])
Or dictionaries and many more types!

st.data_editor({
	"st.text_area": "widget",
	"st.markdown": "element"
})
Automatic input validation
The data editor includes automatic input validation to help prevent errors when editing cells. For example, if you have a column that contains numerical data, the input field will automatically restrict the user to only entering numerical data. This helps to prevent errors that could occur if the user were to accidentally enter a non-numerical value. Additional input validation can be configured through the Column configuration API. Keep reading below for an overview of column configuration, including validation options.

Configuring columns
You can configure the display and editing behavior of columns in st.dataframe and st.data_editor via the Column configuration API. We have developed the API to let you add images, charts, and clickable URLs in dataframe and data editor columns. Additionally, you can make individual columns editable, set columns as categorical and specify which options they can take, hide the index of the dataframe, and much more.

Column configuration includes the following column types: Text, Number, Checkbox, Selectbox, Date, Time, Datetime, List, Link, Image, Line chart, Bar chart, and Progress. There is also a generic Column option. See the embedded app below to view these different column types. Each column type is individually previewed in the Column configuration API documentation.


Built with Streamlit 🎈
Fullscreen
open_in_new
Format values
A format parameter is available in column configuration for Text, Date, Time, and Datetime columns. Chart-like columns can also be formatted. Line chart and Bar chart columns have a y_min and y_max parameters to set the vertical bounds. For a Progress column, you can declare the horizontal bounds with min_value and max_value.

Validate input
When specifying a column configuration, you can declare not only the data type of the column but also value restrictions. All column configuration elements allow you to make a column required with the keyword parameter required=True.

For Text and Link columns, you can specify the maximum number of characters with max_chars or use regular expressions to validate entries through validate. Numerical columns, including Number, Date, Time, and Datetime have min_value and max_value parameters. Selectbox columns have a configurable list of options.

The data type for Number columns is float by default. Passing a value of type int to any of min_value, max_value, step, or default will set the type for the column as int.

Configure an empty dataframe
You can use st.data_editor to collect tabular input from a user. When starting from an empty dataframe, default column types are text. Use column configuration to specify the data types you want to collect from users.

import streamlit as st
import pandas as pd

df = pd.DataFrame(columns=['name','age','color'])
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
config = {
    'name' : st.column_config.TextColumn('Full Name (required)', width='large', required=True),
    'age' : st.column_config.NumberColumn('Age (years)', min_value=0, max_value=122),
    'color' : st.column_config.SelectboxColumn('Favorite Color', options=colors)
}

result = st.data_editor(df, column_config = config, num_rows='dynamic')

if st.button('Get results'):
    st.write(result)

Built with Streamlit 🎈
Fullscreen
open_in_new
Additional formatting options
In addition to column configuration, st.dataframe and st.data_editor have a few more parameters to customize the display of your dataframe.

hide_index : Set to True to hide the dataframe's index.
column_order : Pass a list of column labels to specify the order of display.
disabled : Pass a list of column labels to disable them from editing. This let's you avoid disabling them individually.
Handling large datasets
st.dataframe and st.data_editor have been designed to theoretically handle tables with millions of rows thanks to their highly performant implementation using the glide-data-grid library and HTML canvas. However, the maximum amount of data that an app can realistically handle will depend on several other factors, including:

The maximum size of WebSocket messages: Streamlit's WebSocket messages are configurable via the server.maxMessageSize config option, which limits the amount of data that can be transferred via the WebSocket connection at once.
The server memory: The amount of data that your app can handle will also depend on the amount of memory available on your server. If the server's memory is exceeded, the app may become slow or unresponsive.
The user's browser memory: Since all the data needs to be transferred to the user's browser for rendering, the amount of memory available on the user's device can also affect the app's performance. If the browser's memory is exceeded, it may crash or become unresponsive.
In addition to these factors, a slow network connection can also significantly slow down apps that handle large datasets.

When handling large datasets with more than 150,000 rows, Streamlit applies additional optimizations and disables column sorting. This can help to reduce the amount of data that needs to be processed at once and improve the app's performance.

Limitations
Streamlit casts all column names to strings internally, so st.data_editor will return a DataFrame where all column names are strings.
The dataframe toolbar is not currently configurable.
While Streamlit's data editing capabilities offer a lot of functionality, editing is enabled for a limited set of column types (TextColumn, NumberColumn, LinkColumn, CheckboxColumn, SelectboxColumn, DateColumn, TimeColumn, and DatetimeColumn). We are actively working on supporting editing for other column types as well, such as images, lists, and charts.
Almost all editable datatypes are supported for index editing. However, pandas.CategoricalIndex and pandas.MultiIndex are not supported for editing.
Sorting is not supported for st.data_editor when num_rows="dynamic".
Sorting is deactivated to optimize performance on large datasets with more than 150,000 rows.
We are continually working to improve Streamlit's handling of DataFrame and add functionality to data editing, so keep an eye out for updates.


---


Using custom Python classes in your Streamlit app
If you are building a complex Streamlit app or working with existing code, you may have custom Python classes defined in your script. Common examples include the following:

Defining a @dataclass to store related data within your app.
Defining an Enum class to represent a fixed set of options or values.
Defining custom interfaces to external services or databases not covered by st.connection.
Because Streamlit reruns your script after every user interaction, custom classes may be redefined multiple times within the same Streamlit session. This may result in unwanted effects, especially with class and instance comparisons. Read on to understand this common pitfall and how to avoid it.

We begin by covering some general-purpose patterns you can use for different types of custom classes, and follow with a few more technical details explaining why this matters. Finally, we go into more detail about Using Enum classes specifically, and describe a configuration option which can make them more convenient.

Patterns to define your custom classes
Pattern 1: Define your class in a separate module
This is the recommended, general solution. If possible, move class definitions into their own module file and import them into your app script. As long as you are not editing the file where your class is defined, Streamlit will not re-import it with each rerun. Therefore, if a class is defined in an external file and imported into your script, the class will not be redefined during the session.

Example: Move your class definition
Try running the following Streamlit app where MyClass is defined within the page's script. isinstance() will return True on the first script run then return False on each rerun thereafter.

# app.py
import streamlit as st

# MyClass gets redefined every time app.py reruns
class MyClass:
    def __init__(self, var1, var2):
        self.var1 = var1
        self.var2 = var2

if "my_instance" not in st.session_state:
  st.session_state.my_instance = MyClass("foo", "bar")

# Displays True on the first run then False on every rerun
st.write(isinstance(st.session_state.my_instance, MyClass))

st.button("Rerun")
If you move the class definition out of app.py into another file, you can make isinstance() consistently return True. Consider the following file structure:

myproject/
├── my_class.py
└── app.py
# my_class.py
class MyClass:
    def __init__(self, var1, var2):
        self.var1 = var1
        self.var2 = var2
# app.py
import streamlit as st
from my_class import MyClass # MyClass doesn't get redefined with each rerun

if "my_instance" not in st.session_state:
  st.session_state.my_instance = MyClass("foo", "bar")

# Displays True on every rerun
st.write(isinstance(st.session_state.my_instance, MyClass))

st.button("Rerun")
Streamlit only reloads code in imported modules when it detects the code has changed. Thus, if you are actively editing the file where your class is defined, you may need to stop and restart your Streamlit server to avoid an undesirable class redefinition mid-session.

Pattern 2: Force your class to compare internal values
For classes that store data (like dataclasses), you may be more interested in comparing the internally stored values rather than the class itself. If you define a custom __eq__ method, you can force comparisons to be made on the internally stored values.

Example: Define __eq__
Try running the following Streamlit app and observe how the comparison is True on the first run then False on every rerun thereafter.

import streamlit as st
from dataclasses import dataclass

@dataclass
class MyDataclass:
    var1: int
    var2: float

if "my_dataclass" not in st.session_state:
    st.session_state.my_dataclass = MyDataclass(1, 5.5)

# Displays True on the first run the False on every rerun
st.session_state.my_dataclass == MyDataclass(1, 5.5)

st.button("Rerun")
Since MyDataclass gets redefined with each rerun, the instance stored in Session State will not be equal to any instance defined in a later script run. You can fix this by forcing a comparison of internal values as follows:

import streamlit as st
from dataclasses import dataclass

@dataclass
class MyDataclass:
    var1: int
    var2: float

    def __eq__(self, other):
        # An instance of MyDataclass is equal to another object if the object
        # contains the same fields with the same values
        return (self.var1, self.var2) == (other.var1, other.var2)

if "my_dataclass" not in st.session_state:
    st.session_state.my_dataclass = MyDataclass(1, 5.5)

# Displays True on every rerun
st.session_state.my_dataclass == MyDataclass(1, 5.5)

st.button("Rerun")
The default Python __eq__ implementation for a regular class or @dataclass depends on the in-memory ID of the class or class instance. To avoid problems in Streamlit, your custom __eq__ method should not depend the type() of self and other.

Pattern 3: Store your class as serialized data
Another option for classes that store data is to define serialization and deserialization methods like to_str and from_str for your class. You can use these to store class instance data in st.session_state rather than storing the class instance itself. Similar to pattern 2, this is a way to force comparison of the internal data and bypass the changing in-memory IDs.

Example: Save your class instance as a string
Using the same example from pattern 2, this can be done as follows:

import streamlit as st
from dataclasses import dataclass

@dataclass
class MyDataclass:
    var1: int
    var2: float

    def to_str(self):
        return f"{self.var1},{self.var2}"

    @classmethod
    def from_str(cls, serial_str):
        values = serial_str.split(",")
        var1 = int(values[0])
        var2 = float(values[1])
        return cls(var1, var2)

if "my_dataclass" not in st.session_state:
    st.session_state.my_dataclass = MyDataclass(1, 5.5).to_str()

# Displays True on every rerun
MyDataclass.from_str(st.session_state.my_dataclass) == MyDataclass(1, 5.5)

st.button("Rerun")
Pattern 4: Use caching to preserve your class
For classes that are used as resources (database connections, state managers, APIs), consider using the cached singleton pattern. Use @st.cache_resource to decorate a @staticmethod of your class to generate a single, cached instance of the class. For example:

import streamlit as st

class MyResource:
    def __init__(self, api_url: str):
        self._url = api_url

    @st.cache_resource(ttl=300)
    @staticmethod
    def get_resource_manager(api_url: str):
        return MyResource(api_url)

# This is cached until Session State is cleared or 5 minutes has elapsed.
resource_manager = MyResource.get_resource_manager("http://example.com/api/")
When you use one of Streamlit's caching decorators on a function, Streamlit doesn't use the function object to look up cached values. Instead, Streamlit's caching decorators index return values using the function's qualified name and module. So, even though Streamlit redefines MyResource with each script run, st.cache_resource is unaffected by this. get_resource_manager() will return its cached value with each rerun, until the value expires.

Understanding how Python defines and compares classes
So what's really happening here? We'll consider a simple example to illustrate why this is a pitfall. Feel free to skip this section if you don't want to deal more details. You can jump ahead to learn about Using Enum classes.

Example: What happens when you define the same class twice?
Set aside Streamlit for a moment and think about this simple Python script:

from dataclasses import dataclass

@dataclass
class Student:
    student_id: int
    name: str

Marshall_A = Student(1, "Marshall")
Marshall_B = Student(1, "Marshall")

# This is True (because a dataclass will compare two of its instances by value)
Marshall_A == Marshall_B

# Redefine the class
@dataclass
class Student:
    student_id: int
    name: str

Marshall_C = Student(1, "Marshall")

# This is False
Marshall_A == Marshall_C
In this example, the dataclass Student is defined twice. All three Marshalls have the same internal values. If you compare Marshall_A and Marshall_B they will be equal because they were both created from the first definition of Student. However, if you compare Marshall_A and Marshall_C they will not be equal because Marshall_C was created from the second definition of Student. Even though both Student dataclasses are defined exactly the same, they have different in-memory IDs and are therefore different.

What's happening in Streamlit?
In Streamlit, you probably don't have the same class written twice in your page script. However, the rerun logic of Streamlit creates the same effect. Let's use the above example for an analogy. If you define a class in one script run and save an instance in Session State, then a later rerun will redefine the class and you may end up comparing a Mashall_C in your rerun to a Marshall_A in Session State. Since widgets rely on Session State under the hood, this is where things can get confusing.

How Streamlit widgets store options
Several Streamlit UI elements, such as st.selectbox or st.radio, accept multiple-choice options via an options argument. The user of your application can typically select one or more of these options. The selected value is returned by the widget function. For example:

number = st.selectbox("Pick a number, any number", options=[1, 2, 3])
# number == whatever value the user has selected from the UI.
When you call a function like st.selectbox and pass an Iterable to options, the Iterable and current selection are saved into a hidden portion of Session State called the Widget Metadata.

When the user of your application interacts with the st.selectbox widget, the broswer sends the index of their selection to your Streamlit server. This index is used to determine which values from the original options list, saved in the Widget Metadata from the previous page execution, are returned to your application.

The key detail is that the value returned by st.selectbox (or similar widget function) is from an Iterable saved in Session State during a previous execution of the page, NOT the values passed to options on the current execution. There are a number of architectural reasons why Streamlit is designed this way, which we won't go into here. However, this is how we end up comparing instances of different classes when we think we are comparing instances of the same class.

A pathological example
The above explanation might be a bit confusing, so here's a pathological example to illustrate the idea.

import streamlit as st
from dataclasses import dataclass

@dataclass
class Student:
    student_id: int
    name: str

Marshall_A = Student(1, "Marshall")
if "B" not in st.session_state:
    st.session_state.B = Student(1, "Marshall")
Marshall_B = st.session_state.B

options = [Marshall_A,Marshall_B]
selected = st.selectbox("Pick", options)

# This comparison does not return expected results:
selected == Marshall_A
# This comparison evaluates as expected:
selected == Marshall_B
As a final note, we used @dataclass in the example for this section to illustrate a point, but in fact it is possible to encounter these same problems with classes, in general. Any class which checks class identity inside of a comparison operator—such as __eq__ or __gt__—can exhibit these issues.

Using Enum classes in Streamlit
The Enum class from the Python standard library is a powerful way to define custom symbolic names that can be used as options for st.multiselect or st.selectbox in place of str values.

For example, you might add the following to your streamlit page:

from enum import Enum
import streamlit as st

# class syntax
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

selected_colors = set(st.multiselect("Pick colors", options=Color))

if selected_colors == {Color.RED, Color.GREEN}:
    st.write("Hooray, you found the color YELLOW!")
If you're using the latest version of Streamlit, this Streamlit page will work as it appears it should. When a user picks both Color.RED and Color.GREEN, they are shown the special message.

However, if you've read the rest of this page you might notice something tricky going on. Specifically, the Enum class Color gets redefined every time this script is run. In Python, if you define two Enum classes with the same class name, members, and values, the classes and their members are still considered unique from each other. This should cause the above if condition to always evaluate to False. In any script rerun, the Color values returned by st.multiselect would be of a different class than the Color defined in that script run.

If you run the snippet above with Streamlit version 1.28.0 or less, you will not be able see the special message. Thankfully, as of version 1.29.0, Streamlit introduced a configuration option to greatly simplify the problem. That's where the enabled-by-default enumCoercion configuration option comes in.

Understanding the enumCoercion configuration option
When enumCoercion is enabled, Streamlit tries to recognize when you are using an element like st.multiselect or st.selectbox with a set of Enum members as options.

If Streamlit detects this, it will convert the widget's returned values to members of the Enum class defined in the latest script run. This is something we call automatic Enum coercion.

This behavior is configurable via the enumCoercion setting in your Streamlit config.toml file. It is enabled by default, and may be disabled or set to a stricter set of matching criteria.

If you find that you still encounter issues with enumCoercion enabled, consider using the custom class patterns described above, such as moving your Enum class definition to a separate module file.


---


Connecting to data
Most Streamlit apps need some kind of data or API access to be useful - either retrieving data to view or saving the results of some user action. This data or API is often part of some remote service, database, or other data source.

Anything you can do with Python, including data connections, will generally work in Streamlit. Streamlit's tutorials are a great starting place for many data sources. However:

Connecting to data in a Python application is often tedious and annoying.
There are specific considerations for connecting to data from streamlit apps, such as caching and secrets management.
Streamlit provides st.connection() to more easily connect your Streamlit apps to data and APIs with just a few lines of code. This page provides a basic example of using the feature and then focuses on advanced usage.

For a comprehensive overview of this feature, check out this video tutorial by Joshua Carroll, Streamlit's Product Manager for Developer Experience. You'll learn about the feature's utility in creating and managing data connections within your apps by using real-world examples.


Basic usage
For basic startup and usage examples, read up on the relevant data source tutorial. Streamlit has built-in connections to SQL dialects and Snowflake. We also maintain installable connections for Cloud File Storage and Google Sheets.

If you are just starting, the best way to learn is to pick a data source you can access and get a minimal example working from one of the pages above 👆. Here, we will provide an ultra-minimal usage example for using a SQLite database. From there, the rest of this page will focus on advanced usage.

A simple starting point - using a local SQLite database
A local SQLite database could be useful for your app's semi-persistent data storage.

push_pin
Note
Community Cloud apps do not guarantee the persistence of local file storage, so the platform may delete data stored using this technique at any time.

To see the example below running live, check out the interactive demo below:


Built with Streamlit 🎈
Fullscreen
open_in_new
Step 1: Install prerequisite library - SQLAlchemy
All SQLConnections in Streamlit use SQLAlchemy. For most other SQL dialects, you also need to install the driver. But the SQLite driver ships with python3, so it isn't necessary.

pip install SQLAlchemy==1.4.0
Step 2: Set a database URL in your Streamlit secrets.toml file
Create a directory and file .streamlit/secrets.toml in the same directory your app will run from. Add the following to the file.

# .streamlit/secrets.toml

[connections.pets_db]
url = "sqlite:///pets.db"
Step 3: Use the connection in your app
The following app creates a connection to the database, uses it to create a table and insert some data, then queries the data back and displays it in a data frame.

# streamlit_app.py

import streamlit as st

# Create the SQL connection to pets_db as specified in your secrets file.
conn = st.connection('pets_db', type='sql')

# Insert some data with conn.session.
with conn.session as s:
    s.execute('CREATE TABLE IF NOT EXISTS pet_owners (person TEXT, pet TEXT);')
    s.execute('DELETE FROM pet_owners;')
    pet_owners = {'jerry': 'fish', 'barbara': 'cat', 'alex': 'puppy'}
    for k in pet_owners:
        s.execute(
            'INSERT INTO pet_owners (person, pet) VALUES (:owner, :pet);',
            params=dict(owner=k, pet=pet_owners[k])
        )
    s.commit()

# Query and display the data you inserted
pet_owners = conn.query('select * from pet_owners')
st.dataframe(pet_owners)
In this example, we didn't set a ttl= value on the call to conn.query(), meaning Streamlit caches the result indefinitely as long as the app server runs.

Now, on to more advanced topics! 🚀

Advanced topics
Global secrets, managing multiple apps and multiple data stores
Streamlit supports a global secrets file specified in the user's home directory, such as ~/.streamlit/secrets.toml. If you build or manage multiple apps, we recommend using a global credential or secret file for local development across apps. With this approach, you only need to set up and manage your credentials in one place, and connecting a new app to your existing data sources is effectively a one-liner. It also reduces the risk of accidentally checking in your credentials to git since they don't need to exist in the project repository.

For cases where you have multiple similar data sources that you connect to during local development (such as a local vs. staging database), you can define different connection sections in your secrets or credentials file for different environments and then decide which to use at runtime. st.connection supports this with the name=env:<MY_NAME_VARIABLE> syntax.

E.g., say I have a local and a staging MySQL database and want to connect my app to either at different times. I could create a global secrets file like this:

# ~/.streamlit/secrets.toml

[connections.local]
url = "mysql://me:****@localhost:3306/local_db"

[connections.staging]
url = "mysql://jdoe:******@staging.acmecorp.com:3306/staging_db"
Then I can configure my app connection to take its name from a specified environment variable

# streamlit_app.py
import streamlit as st

conn = st.connection("env:DB_CONN", "sql")
df = conn.query("select * from mytable")
# ...
Now I can specify whether to connect to local or staging at runtime by setting the DB_CONN environment variable.

# connect to local
DB_CONN=local streamlit run streamlit_app.py

# connect to staging
DB_CONN=staging streamlit run streamlit_app.py
Advanced SQLConnection configuration
The SQLConnection configuration uses SQLAlchemy create_engine() function. It will take a single URL argument or attempt to construct a URL from several parts (username, database, host, and so on) using SQLAlchemy.engine.URL.create().

Several popular SQLAlchemy dialects, such as Snowflake and Google BigQuery, can be configured using additional arguments to create_engine() besides the URL. These can be passed as **kwargs to the st.connection call directly or specified in an additional secrets section called create_engine_kwargs.

E.g. snowflake-sqlalchemy takes an additional connect_args argument as a dictionary for configuration that isn’t supported in the URL. These could be specified as follows:

# .streamlit/secrets.toml

[connections.snowflake]
url = "snowflake://<user_login_name>@<account_identifier>/"

[connections.snowflake.create_engine_kwargs.connect_args]
authenticator = "externalbrowser"
warehouse = "xxx"
role = "xxx"
# streamlit_app.py

import streamlit as st

# url and connect_args from secrets.toml above are picked up and used here
conn = st.connection("snowflake", "sql")
# ...
Alternatively, this could be specified entirely in **kwargs.

# streamlit_app.py

import streamlit as st

# secrets.toml is not needed
conn = st.connection(
    "snowflake",
    "sql",
    url = "snowflake://<user_login_name>@<account_identifier>/",
    connect_args = dict(
        authenticator = "externalbrowser",
        warehouse = "xxx",
        role = "xxx",
    )
)
# ...
You can also provide both kwargs and secrets.toml values, and they will be merged (typically, kwargs take precedence).

Connection considerations in frequently used or long-running apps
By default, connection objects are cached without expiration using st.cache_resource. In most cases this is desired. You can do st.connection('myconn', type=MyConnection, ttl=<N>) if you want the connection object to expire after some time.

Many connection types are expected to be long-running or completely stateless, so expiration is unnecessary. Suppose a connection becomes stale (such as a cached token expiring or a server-side connection being closed). In that case, every connection has a reset() method, which will invalidate the cached version and cause Streamlit to recreate the connection the next time it is retrieved

Convenience methods like query() and read() will typically cache results by default using st.cache_data without an expiration. When an app can run many different read operations with large results, it can cause high memory usage over time and results to become stale in a long-running app, the same as with any other usage of st.cache_data. For production use cases, we recommend setting an appropriate ttl on these read operations, such as conn.read('path/to/file', ttl="1d"). Refer to Caching for more information.

For apps that could get significant concurrent usage, ensure that you understand any thread safety implications of your connection, particularly when using a connection built by a third party. Connections built by Streamlit should provide thread-safe operations by default.

Build your own connection
Building your own basic connection implementation using an existing driver or SDK is quite straightforward in most cases. However, you can add more complex functionality with further effort. This custom implementation can be a great way to extend support to a new data source and contribute to the Streamlit ecosystem.

Maintaining a tailored internal Connection implementation across many apps can be a powerful practice for organizations with frequently used access patterns and data sources.

Check out the Build your own Connection page in the st.experimental connection demo app below for a quick tutorial and working implementation. This demo builds a minimal but very functional Connection on top of DuckDB.


Built with Streamlit 🎈
Fullscreen
open_in_new
The typical steps are:

Declare the Connection class, extending ExperimentalBaseConnection with the type parameter bound to the underlying connection object:

from streamlit.connections import ExperimentalBaseConnection
import duckdb

class DuckDBConnection(ExperimentalBaseConnection[duckdb.DuckDBPyConnection])
Implement the _connect method that reads any kwargs, external config/credential locations, and Streamlit secrets to initialize the underlying connection:

def _connect(self, **kwargs) -> duckdb.DuckDBPyConnection:
    if 'database' in kwargs:
        db = kwargs.pop('database')
    else:
        db = self._secrets['database']
    return duckdb.connect(database=db, **kwargs)
Add useful helper methods that make sense for your connection (wrapping them in st.cache_data where caching is desired)

Connection-building best practices
We recommend applying the following best practices to make your Connection consistent with the Connections built into Streamlit and the wider Streamlit ecosystem. These practices are especially important for Connections that you intend to distribute publicly.

Extend existing drivers or SDKs, and default to semantics that makes sense for their existing users.

You should rarely need to implement complex data access logic from scratch when building a Connection. Use existing popular Python drivers and clients whenever possible. Doing so makes your Connection easier to maintain, more secure, and enables users to get the latest features. E.g. SQLConnection extends SQLAlchemy, FileConnection extends fsspec, GsheetsConnection extends gspread, etc.

Consider using access patterns, method/argument naming, and return values that are consistent with the underlying package and familiar to existing users of that package.

Intuitive, easy to use read methods.

Much of the power of st.connection is providing intuitive, easy-to-use read methods that enable app developers to get started quickly. Most connections should expose at least one read method that is:

Named with a simple verb, like read(), query(), or get()
Wrapped by st.cache_data by default, with at least ttl= argument supported
If the result is in a tabular format, it returns a pandas DataFrame
Provides commonly used keyword arguments (such as paging or formatting) with sensible defaults - ideally, the common case requires only 1-2 arguments.
Config, secrets, and precedence in _connect method.

Every Connection should support commonly used connection parameters provided via Streamlit secrets and keyword arguments. The names should match the ones used when initializing or configuring the underlying package.

Additionally, where relevant, Connections should support data source specific configuration through existing standard environment variables or config / credential files. In many cases, the underlying package provides constructors or factory functions that already handle this easily.

When you can specify the same connection parameters in multiple places, we recommend using the following precedence order when possible (highest to lowest):

Keyword arguments specified in the code
Streamlit secrets
data source specific configuration (if relevant)
Handling thread safety and stale connections.

Connections should provide thread-safe operations when practical (which should be most of the time) and clearly document any considerations around this. Most underlying drivers or SDKs should provide thread-safe objects or methods - use these when possible.

If the underlying driver or SDK has a risk of stateful connection objects becoming stale or invalid, consider building a low impact health check or reset/retry pattern into the access methods. The SQLConnection built into Streamlit has a good example of this pattern using tenacity and the built-in Connection.reset() method. An alternate approach is to encourage developers to set an appropriate TTL on the st.connection() call to ensure it periodically reinitializes the connection object.


---


