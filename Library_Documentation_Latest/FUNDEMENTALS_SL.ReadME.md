Basic concepts of Streamlit
Working with Streamlit is simple. First you sprinkle a few Streamlit commands into a normal Python script, then you run it with streamlit run:

streamlit run your_script.py [-- script args]
As soon as you run the script as shown above, a local Streamlit server will spin up and your app will open in a new tab in your default web browser. The app is your canvas, where you'll draw charts, text, widgets, tables, and more.

What gets drawn in the app is up to you. For example st.text writes raw text to your app, and st.line_chart draws — you guessed it — a line chart. Refer to our API documentation to see all commands that are available to you.

push_pin
Note
When passing your script some custom arguments, they must be passed after two dashes. Otherwise the arguments get interpreted as arguments to Streamlit itself.

Another way of running Streamlit is to run it as a Python module. This can be useful when configuring an IDE like PyCharm to work with Streamlit:

# Running
python -m streamlit run your_script.py

# is equivalent to:
streamlit run your_script.py
star
Tip
You can also pass a URL to streamlit run! This is great when combined with GitHub Gists. For example:

streamlit run https://raw.githubusercontent.com/streamlit/demo-uber-nyc-pickups/master/streamlit_app.py
Development flow
Every time you want to update your app, save the source file. When you do that, Streamlit detects if there is a change and asks you whether you want to rerun your app. Choose "Always rerun" at the top-right of your screen to automatically update your app every time you change its source code.

This allows you to work in a fast interactive loop: you type some code, save it, try it out live, then type some more code, save it, try it out, and so on until you're happy with the results. This tight loop between coding and viewing results live is one of the ways Streamlit makes your life easier.

star
Tip
While developing a Streamlit app, it's recommended to lay out your editor and browser windows side by side, so the code and the app can be seen at the same time. Give it a try!

As of Streamlit version 1.10.0 and higher, Streamlit apps cannot be run from the root directory of Linux distributions. If you try to run a Streamlit app from the root directory, Streamlit will throw a FileNotFoundError: [Errno 2] No such file or directory error. For more information, see GitHub issue #5239.

If you are using Streamlit version 1.10.0 or higher, your main script should live in a directory other than the root directory. When using Docker, you can use the WORKDIR command to specify the directory where your main script lives. For an example of how to do this, read Create a Dockerfile.

Data flow
Streamlit's architecture allows you to write apps the same way you write plain Python scripts. To unlock this, Streamlit apps have a unique data flow: any time something must be updated on the screen, Streamlit reruns your entire Python script from top to bottom.

This can happen in two situations:

Whenever you modify your app's source code.

Whenever a user interacts with widgets in the app. For example, when dragging a slider, entering text in an input box, or clicking a button.

Whenever a callback is passed to a widget via the on_change (or on_click) parameter, the callback will always run before the rest of your script. For details on the Callbacks API, please refer to our Session State API Reference Guide.

And to make all of this fast and seamless, Streamlit does some heavy lifting for you behind the scenes. A big player in this story is the @st.cache_data decorator, which allows developers to skip certain costly computations when their apps rerun. We'll cover caching later in this page.

Display and style data
There are a few ways to display data (tables, arrays, data frames) in Streamlit apps. Below, you will be introduced to magic and st.write(), which can be used to write anything from text to tables. After that, let's take a look at methods designed specifically for visualizing data.

Use magic
You can also write to your app without calling any Streamlit methods. Streamlit supports "magic commands," which means you don't have to use st.write() at all! To see this in action try this snippet:

"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

df
Any time that Streamlit sees a variable or a literal value on its own line, it automatically writes that to your app using st.write(). For more information, refer to the documentation on magic commands.

Write a data frame
Along with magic commands, st.write() is Streamlit's "Swiss Army knife". You can pass almost anything to st.write(): text, data, Matplotlib figures, Altair charts, and more. Don't worry, Streamlit will figure it out and render things the right way.

import streamlit as st
import pandas as pd

st.write("Here's our first attempt at using data to create a table:")
st.write(pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))
There are other data specific functions like st.dataframe() and st.table() that you can also use for displaying data. Let's understand when to use these features and how to add colors and styling to your data frames.

You might be asking yourself, "why wouldn't I always use st.write()?" There are a few reasons:

Magic and st.write() inspect the type of data that you've passed in, and then decide how to best render it in the app. Sometimes you want to draw it another way. For example, instead of drawing a dataframe as an interactive table, you may want to draw it as a static table by using st.table(df).
The second reason is that other methods return an object that can be used and modified, either by adding data to it or replacing it.
Finally, if you use a more specific Streamlit method you can pass additional arguments to customize its behavior.
For example, let's create a data frame and change its formatting with a Pandas Styler object. In this example, you'll use Numpy to generate a random sample, and the st.dataframe() method to draw an interactive table.

push_pin
Note
This example uses Numpy to generate a random sample, but you can use Pandas DataFrames, Numpy arrays, or plain Python arrays.

import streamlit as st
import numpy as np

dataframe = np.random.randn(10, 20)
st.dataframe(dataframe)
Let's expand on the first example using the Pandas Styler object to highlight some elements in the interactive table.

import streamlit as st
import numpy as np
import pandas as pd

dataframe = pd.DataFrame(
    np.random.randn(10, 20),
    columns=('col %d' % i for i in range(20)))

st.dataframe(dataframe.style.highlight_max(axis=0))
Streamlit also has a method for static table generation: st.table().

import streamlit as st
import numpy as np
import pandas as pd

dataframe = pd.DataFrame(
    np.random.randn(10, 20),
    columns=('col %d' % i for i in range(20)))
st.table(dataframe)
Draw charts and maps
Streamlit supports several popular data charting libraries like Matplotlib, Altair, deck.gl, and more. In this section, you'll add a bar chart, line chart, and a map to your app.

Draw a line chart
You can easily add a line chart to your app with st.line_chart(). We'll generate a random sample using Numpy and then chart it.

import streamlit as st
import numpy as np
import pandas as pd

chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

st.line_chart(chart_data)
Plot a map
With st.map() you can display data points on a map. Let's use Numpy to generate some sample data and plot it on a map of San Francisco.

import streamlit as st
import numpy as np
import pandas as pd

map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)
Widgets
When you've got the data or model into the state that you want to explore, you can add in widgets like st.slider(), st.button() or st.selectbox(). It's really straightforward — treat widgets as variables:

import streamlit as st
x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)
On first run, the app above should output the text "0 squared is 0". Then every time a user interacts with a widget, Streamlit simply reruns your script from top to bottom, assigning the current state of the widget to your variable in the process.

For example, if the user moves the slider to position 10, Streamlit will rerun the code above and set x to 10 accordingly. So now you should see the text "10 squared is 100".

Widgets can also be accessed by key, if you choose to specify a string to use as the unique key for the widget:

import streamlit as st
st.text_input("Your name", key="name")

# You can access the value at any point with:
st.session_state.name
Every widget with a key is automatically added to Session State. For more information about Session State, its association with widget state, and its limitations, see Session State API Reference Guide.

Use checkboxes to show/hide data
One use case for checkboxes is to hide or show a specific chart or section in an app. st.checkbox() takes a single argument, which is the widget label. In this sample, the checkbox is used to toggle a conditional statement.

import streamlit as st
import numpy as np
import pandas as pd

if st.checkbox('Show dataframe'):
    chart_data = pd.DataFrame(
       np.random.randn(20, 3),
       columns=['a', 'b', 'c'])

    chart_data
Use a selectbox for options
Use st.selectbox to choose from a series. You can write in the options you want, or pass through an array or data frame column.

Let's use the df data frame we created earlier.

import streamlit as st
import pandas as pd

df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
    })

option = st.selectbox(
    'Which number do you like best?',
     df['first column'])

'You selected: ', option
Layout
Streamlit makes it easy to organize your widgets in a left panel sidebar with st.sidebar. Each element that's passed to st.sidebar is pinned to the left, allowing users to focus on the content in your app while still having access to UI controls.

For example, if you want to add a selectbox and a slider to a sidebar, use st.sidebar.slider and st.sidebar.selectbox instead of st.slider and st.selectbox:

import streamlit as st

# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)

# Add a slider to the sidebar:
add_slider = st.sidebar.slider(
    'Select a range of values',
    0.0, 100.0, (25.0, 75.0)
)
Beyond the sidebar, Streamlit offers several other ways to control the layout of your app. st.columns lets you place widgets side-by-side, and st.expander lets you conserve space by hiding away large content.

import streamlit as st

left_column, right_column = st.columns(2)
# You can use a column just like st.sidebar:
left_column.button('Press me!')

# Or even better, call Streamlit functions inside a "with" block:
with right_column:
    chosen = st.radio(
        'Sorting hat',
        ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"))
    st.write(f"You are in {chosen} house!")
push_pin
Note
st.echo and st.spinner are not currently supported inside the sidebar or layout options. Rest assured, though, we're currently working on adding support for those too!

Show progress
When adding long running computations to an app, you can use st.progress() to display status in real time.

First, let's import time. We're going to use the time.sleep() method to simulate a long running computation:

import time
Now, let's create a progress bar:

import streamlit as st
import time

'Starting a long computation...'

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress(i + 1)
  time.sleep(0.1)

'...and now we\'re done!'
Previous:
Fundamentals


---

Advanced concepts of Streamlit
Now that you know how a Streamlit app runs and handles data, let's talk about being efficient. Caching allows you to save the output of a function so you can skip over it on rerun. Session State lets you save information for each user that is preserved between reruns. This not only allows you to avoid unecessary recalculation, but also allows you to create dynamic pages and handle progressive processes.

Caching
Caching allows your app to stay performant even when loading data from the web, manipulating large datasets, or performing expensive computations.

The basic idea behind caching is to store the results of expensive function calls and return the cached result when the same inputs occur again. This avoids repeated execution of a function with the same input values.

To cache a function in Streamlit, you need to apply a caching decorator to it. You have two choices:

st.cache_data is the recommended way to cache computations that return data. Use st.cache_data when you use a function that returns a serializable data object (e.g. str, int, float, DataFrame, dict, list). It creates a new copy of the data at each function call, making it safe against mutations and race conditions. The behavior of st.cache_data is what you want in most cases – so if you're unsure, start with st.cache_data and see if it works!
st.cache_resource is the recommended way to cache global resources like ML models or database connections. Use st.cache_resource when your function returns unserializable objects that you don’t want to load multiple times. It returns the cached object itself, which is shared across all reruns and sessions without copying or duplication. If you mutate an object that is cached using st.cache_resource, that mutation will exist across all reruns and sessions.
Example:

@st.cache_data
def long_running_function(param1, param2):
    return …
In the above example, long_running_function is decorated with @st.cache_data. As a result, Streamlit notes the following:

The name of the function ("long_running_function").
The value of the inputs (param1, param2).
The code within the function.
Before running the code within long_running_function, Streamlit checks its cache for a previously saved result. If it finds a cached result for the given function and input values, it will return that cached result and not rerun function's code. Otherwise, Streamlit executes the function, saves the result in its cache, and proceeds with the script run. During development, the cache updates automatically as the function code changes, ensuring that the latest changes are reflected in the cache.

Streamlit's two caching decorators and their use cases. Use st.cache_data for anything you'd store in a database. Use st.cache_resource for anything you can't store in a database, like a connection to a database or a machine learning model.
Streamlit's two caching decorators and their use cases.

For more information about the Streamlit caching decorators, their configuration parameters, and their limitations, see Caching.

Session State
Session State provides a dictionary-like interface where you can save information that is preserved between script reruns. Use st.session_state with key or attribute notation to store and recall values. For example, st.session_state["my_key"] or st.session_state.my_key. Remember that widgets handle their statefulness all by themselves, so you won't always need to use Session State!

What is a session?
A session is a single instance of viewing an app. If you view an app from two different tabs in your browser, each tab will have its own session. So each viewer of an app will have a Session State tied to their specific view. Streamlit maintains this session as the user interacts with the app. If the user refreshes their browser page or reloads the URL to the app, their Session State resets and they begin again with a new session.

Examples of using Session State
Here's a simple app that counts the number of times the page has been run. Every time you click the button, the script will rerun.

import streamlit as st

if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1

st.header(f"This page has run {st.session_state.counter} times.")
st.button("Run it again")
First run: The first time the app runs for each user, Session State is empty. Therefore, a key-value pair is created ("counter":0). As the script continues, the counter is immediately incremented ("counter":1) and the result is displayed: "This page has run 1 times." When the page has fully rendered, the script has finished and the Streamlit server waits for the user to do something. When that user clicks the button, a rerun begins.

Second run: Since "counter" is already a key in Session State, it is not reinitialized. As the script continues, the counter is incremented ("counter":2) and the result is displayed: "This page has run 2 times."

There are a few common scenarios where Session State is helpful. As demonstrated above, Session State is used when you have a progressive process that you want to build upon from one rerun to the next. Session State can also be used to prevent recalculation, similar to caching. However, the differences are important:

Caching associates stored values to specific functions and inputs. Cached values are accessible to all users across all sessions.
Session State associates stored values to keys (strings). Values in session state are only available in the single session where it was saved.
If you have random number generation in your app, you'd likely use Session State. Here's an example where data is generated randomly at the beginning of each session. By saving this random information in Session State, each user gets different random data when they open the app but it won't keep changing on them as they interact with it. If you select different colors with the picker you'll see that the data does not get re-randomized with each rerun. (If you open the app in a new tab to start a new session, you'll see different data!)

import streamlit as st
import pandas as pd
import numpy as np

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(np.random.randn(20, 2), columns=["x", "y"])

st.header("Choose a datapoint color")
color = st.color_picker("Color", "#FF0000")
st.divider()
st.scatter_chart(st.session_state.df, x="x", y="y", color=color)
If you are pulling the same data for all users, you'd likely cache a function that retrieves that data. On the other hand, if you pull data specific to a user, such as querying their personal information, you may want to save that in Session State. That way, the queried data is only available in that one session.

As mentioned in Basic concepts, Session State is also related to widgets. Widgets are magical and handle statefulness quietly on their own. As an advanced feature however, you can manipulate the value of widgets within your code by assigning keys to them. Any key assigned to a widget becomes a key in Session State tied to the value of the widget. This can be used to manipulate the widget. After you finish understanding the basics of Streamlit, check out our guide on Widget behavior to dig in the details if you're interested.

Connections
As hinted above, you can use @st.cache_resource to cache connections. This is the most general solution which allows you to use almost any connection from any Python library. However, Streamlit also offers a convenient way to handle some of the most popular connections, like SQL! st.connection takes care of the caching for you so you can enjoy fewer lines of code. Getting data from your database can be as easy as:

import streamlit as st

conn = st.connection("my_database")
df = conn.query("select * from my_table")
st.dataframe(df)
Of course, you may be wondering where your username and password go. Streamlit has a convenient mechanism for Secrets management. For now, let's just see how st.connection works very nicely with secrets. In your local project directory, you can save a .streamlit/secrets.toml file. You save your secrets in the toml file and st.connection just uses them! For example, if you have an app file streamlit_app.py your project directory may look like this:

your-LOCAL-repository/
├── .streamlit/
│   └── secrets.toml # Make sure to gitignore this!
└── streamlit_app.py
For the above SQL example, your secrets.toml file might look like the following:

[connections.my_database]
    type="sql"
    dialect="mysql"
    username="xxx"
    password="xxx"
    host="example.com" # IP or URL
    port=3306 # Port number
    database="mydb" # Database name
Since you don't want to commit your secrets.toml file to your repository, you'll need to learn how your host handles secrets when you're ready to publish your app. Each host platform may have a different way for you to pass your secrets. If you use Streamlit Community Cloud for example, each deployed app has a settings menu where you can load your secrets. After you've written an app and are ready to deploy, you can read all about how to Deploy your app on Community Cloud.




---


Additional Streamlit features
So you've read all about Streamlit's Basic concepts and gotten a taste of caching and Session State in Advanced concepts. But what about the bells and whistles? Here's a quick look at some extra features to take your app to the next level.

Theming
Streamlit supports Light and Dark themes out of the box. Streamlit will first check if the user viewing an app has a Light or Dark mode preference set by their operating system and browser. If so, then that preference will be used. Otherwise, the Light theme is applied by default.

You can also change the active theme from "⋮" → "Settings".

Changing Themes
Want to add your own theme to an app? The "Settings" menu has a theme editor accessible by clicking on "Edit active theme". You can use this editor to try out different colors and see your app update live.

Editing Themes
When you're happy with your work, themes can be saved by setting config options in the [theme] config section. After you've defined a theme for your app, it will appear as "Custom Theme" in the theme selector and will be applied by default instead of the included Light and Dark themes.

More information about the options available when defining a theme can be found in the theme option documentation.

push_pin
Note
The theme editor menu is available only in local development. If you've deployed your app using Streamlit Community Cloud, the "Edit active theme" button will no longer be displayed in the "Settings" menu.

star
Tip
Another way to experiment with different theme colors is to turn on the "Run on save" option, edit your config.toml file, and watch as your app reruns with the new theme colors applied.

Pages
As apps grow large, it becomes useful to organize them into multiple pages. This makes the app easier to manage as a developer and easier to navigate as a user. Streamlit provides a frictionless way to create multipage apps.

We designed this feature so that building a multipage app is as easy as building a single-page app! Just add more pages to an existing app as follows:

In the folder containing your main script, create a new pages folder. Let’s say your main script is named main_page.py.
Add new .py files in the pages folder to add more pages to your app.
Run streamlit run main_page.py as usual.
That’s it! The main_page.py script will now correspond to the main page of your app. And you’ll see the other scripts from the pages folder in the sidebar page selector. The pages are listed according to filename (without file extensions and disregarding underscores). For example:

main_page.py
import streamlit as st

st.markdown("# Main page 🎈")
st.sidebar.markdown("# Main page 🎈")
pages/page_2.py
import streamlit as st

st.markdown("# Page 2 ❄️")
st.sidebar.markdown("# Page 2 ❄️")
pages/page_3.py
import streamlit as st

st.markdown("# Page 3 🎉")
st.sidebar.markdown("# Page 3 🎉")

Now run streamlit run main_page.py and view your shiny new multipage app!


Our documentation on Multipage apps teaches you how to add pages to your app, including how to define pages, structure and run multipage apps, and navigate between pages. Once you understand the basics, create your first multipage app!

Custom components
If you can't find the right component within the Streamlit library, try out custom components to extend Streamlit's built-in functionality. Explore and browse through popular, community-created components in the Components gallery. If you dabble in frontend development, you can build your own custom component with Streamlit's components API.

Static file serving
As you learned in Streamlit fundamentals, Streamlit runs a server that clients connect to. That means viewers of your app don't have direct access to the files which are local to your app. Most of the time, this doesn't matter because Streamlt commands handle that for you. When you use st.image(<path-to-image>) your Streamlit server will access the file and handle the necessary hosting so your app viewers can see it. However, if you want a direct URL to an image or file you'll need to host it. This requires setting the correct configuration and placing your hosted files in a directory named static. For example, your project could look like:

your-project/
├── static/
│   └── my_hosted-image.png
└── streamlit_app.py
To learn more, read our guide on Static file serving.

App testing
Good development hygeine includes testing your code. Automated testing allows you to write higher quality code, faster! Streamlit has a built-in testing framework that let's you build tests easily. Use your favorite testing framework to run your tests. We like pytest. When you test a Streamlit app, you simulate running the app, declare user input, and inspect the results. You can use GitHub workflows to automate your tests and get instant alerts about breaking changes. Learn more in our guide to App testing.

---


App model summary
Now that you know a little more about all the individual pieces, let's close the loop and review how it works together:

Streamlit apps are Python scripts that run from top to bottom.
Every time a user opens a browser tab pointing to your app, the script is executed and a new session starts.
As the script executes, Streamlit draws its output live in a browser.
Every time a user interacts with a widget, your script is re-executed and Streamlit redraws its output in the browser.
The output value of that widget matches the new value during that rerun.
Scripts use the Streamlit cache to avoid recomputing expensive functions, so updates happen very fast.
Session State lets you save information that persists between reruns when you need more than a simple widget.
Streamlit apps can contain multiple pages, which are defined in separate .py files in a pages folder.
The Streamlit app model



