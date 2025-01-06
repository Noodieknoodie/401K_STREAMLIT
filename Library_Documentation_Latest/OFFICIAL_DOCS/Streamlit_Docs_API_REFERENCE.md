******** Streamlit Official Documentation 2024: API_REFERENCE ********

------------------------------------------------------------------------------------------------
CHAPTER 1: caching-and-state.md
------------------------------------------------------------------------------------------------

################################################
Section 1.1 - cache-data.md
################################################

st.cache_data - st.cache_data is used to cache functions that return data (e.g. dataframe transforms, database queries, ML inference).

Note: This page only contains information on the `st.cache_data` API. For a deeper dive into caching and how to use it, check out Caching.

Function: st.cache_data (previously experimental)

WARNING: `st.cache_data` implicitly uses the `pickle` module, which is known to be insecure. Anything your cached function returns is pickled and stored, then unpickled on retrieval. Ensure your cached functions return trusted values because it is possible to construct malicious pickle data that will execute arbitrary code during unpickling. Never load data that could have come from an untrusted source in an unsafe mode or that could have been tampered with. **Only load data you trust**.

#### Example

In the example below, pressing the "Clear All" button will clear memoized values from all functions decorated with `@st.cache_data`.

```python
import streamlit as st

@st.cache_data
def square(x):
    return x**2

@st.cache_data
def cube(x):
    return x**3

if st.button("Clear All"):
    # Clear values from *all* all in-memory and on-disk data caches:
    # i.e. clear values from both square and cube
    st.cache_data.clear()
```

## Using Streamlit commands in cached functions

### Static elements

Since version 1.16.0, cached functions can contain Streamlit commands! For example, you can do this:

```python
@st.cache_data
def get_api_data():
    data = api.get(...)
    st.success("Fetched data from API!")  # 👈 Show a success message
    return data
```

As we know, Streamlit only runs this function if it hasn’t been cached before. On this first run, the `st.success` message will appear in the app. But what happens on subsequent runs? It still shows up! Streamlit realizes that there is an `st.` command inside the cached function, saves it during the first run, and replays it on subsequent runs. Replaying static elements works for both caching decorators.

You can also use this functionality to cache entire parts of your UI:

```python
@st.cache_data
def show_data():
    st.header("Data analysis")
    data = api.get(...)
    st.success("Fetched data from API!")
    st.write("Here is a plot of the data:")
    st.line_chart(data)
    st.write("And here is the raw data:")
    st.dataframe(data)
```

### Input widgets

You can also use interactive input widgets like `st.slider` or `st.text_input` in cached functions. Widget replay is an experimental feature at the moment. To enable it, you need to set the `experimental_allow_widgets` parameter:

```python
@st.cache_data(experimental_allow_widgets=True)  # 👈 Set the parameter
def get_data():
    num_rows = st.slider("Number of rows to get")  # 👈 Add a slider
    data = api.get(..., num_rows)
    return data
```

Streamlit treats the slider like an additional input parameter to the cached function. If you change the slider position, Streamlit will see if it has already cached the function for this slider value. If yes, it will return the cached value. If not, it will rerun the function using the new slider value.

Using widgets in cached functions is extremely powerful because it lets you cache entire parts of your app. But it can be dangerous! Since Streamlit treats the widget value as an additional input parameter, it can easily lead to excessive memory usage. Imagine your cached function has five sliders and returns a 100 MB DataFrame. Then we’ll add 100 MB to the cache for _every permutation_ of these five slider values – even if the sliders do not influence the returned data! These additions can make your cache explode very quickly. Please be aware of this limitation if you use widgets in cached functions. We recommend using this feature only for isolated parts of your UI where the widgets directly influence the cached return value.

WARNING: Support for widgets in cached functions is currently experimental. We may change or remove it anytime without warning. Please use it with care!

Note: Two widgets are currently not supported in cached functions: `st.file_uploader` and `st.camera_input`. We may support them in the future. Feel free to open a GitHub issue if you need them!

################################################
Section 1.2 - cache-resource.md
################################################

st.cache_resource - st.cache_resource is used to cache functions that return shared global resources (e.g. database connections, ML models).

Note: This page only contains information on the `st.cache_resource` API. For a deeper dive into caching and how to use it, check out Caching.

Function: st.cache_resource (previously experimental)

#### Example

In the example below, pressing the "Clear All" button will clear _all_ cache_resource caches. i.e. Clears cached global resources from all functions decorated with `@st.cache_resource`.

```python
import streamlit as st
from transformers import BertModel

@st.cache_resource
 def get_database_session(url):
     # Create a database session object that points to the URL.
     return session

@st.cache_resource
def get_model(model_type):
    # Create a model of the specified type.
    return BertModel.from_pretrained(model_type)

if st.button("Clear All"):
    # Clears all st.cache_resource caches:
    st.cache_resource.clear()
```

## Using Streamlit commands in cached functions

### Static elements

Since version 1.16.0, cached functions can contain Streamlit commands! For example, you can do this:

```python
from transformers import pipeline

@st.cache_resource
def load_model():
    model = pipeline("sentiment-analysis")
    st.success("Loaded NLP model from Hugging Face!")  # 👈 Show a success message
    return model
```

As we know, Streamlit only runs this function if it hasn’t been cached before. On this first run, the `st.success` message will appear in the app. But what happens on subsequent runs? It still shows up! Streamlit realizes that there is an `st.` command inside the cached function, saves it during the first run, and replays it on subsequent runs. Replaying static elements works for both caching decorators.

You can also use this functionality to cache entire parts of your UI:

```python
@st.cache_resource
def load_model():
    st.header("Data analysis")
    model = torchvision.models.resnet50(weights=ResNet50_Weights.DEFAULT)
    st.success("Loaded model!")
    st.write("Turning on evaluation mode...")
    model.eval()
    st.write("Here's the model:")
    return model
```

### Input widgets

You can also use interactive input widgets like `st.slider` or `st.text_input` in cached functions. Widget replay is an experimental feature at the moment. To enable it, you need to set the `experimental_allow_widgets` parameter:

```python
@st.cache_resource(experimental_allow_widgets=True)  # 👈 Set the parameter
def load_model():
    pretrained = st.checkbox("Use pre-trained model:")  # 👈 Add a checkbox
    model = torchvision.models.resnet50(weights=ResNet50_Weights.DEFAULT, pretrained=pretrained)
    return model
```

Streamlit treats the checkbox like an additional input parameter to the cached function. If you uncheck it, Streamlit will see if it has already cached the function for this checkbox state. If yes, it will return the cached value. If not, it will rerun the function using the new slider value.

Using widgets in cached functions is extremely powerful because it lets you cache entire parts of your app. But it can be dangerous! Since Streamlit treats the widget value as an additional input parameter, it can easily lead to excessive memory usage. Imagine your cached function has five sliders and returns a 100 MB DataFrame. Then we’ll add 100 MB to the cache for _every permutation_ of these five slider values – even if the sliders do not influence the returned data! These additions can make your cache explode very quickly. Please be aware of this limitation if you use widgets in cached functions. We recommend using this feature only for isolated parts of your UI where the widgets directly influence the cached return value.

WARNING: Support for widgets in cached functions is currently experimental. We may change or remove it anytime without warning. Please use it with care!

Note: Two widgets are currently not supported in cached functions: `st.file_uploader` and `st.camera_input`. We may support them in the future. Feel free to open a GitHub issue if you need them!

################################################
Section 1.3 - experimental-memo.md
################################################

st.experimental_memo - st.experimental_memo is used to memoize function executions.

IMPORTANT: This is an experimental feature. Experimental features and their APIs may change or be removed at any time. To learn more, click here.

st.experimental_memo was deprecated in version 1.18.0. Use <code>st.cache_data instead. Learn more in Caching."/>

Persistent memo caches currently don't support TTL. `ttl` will be ignored if `persist` is specified:

```python
import streamlit as st

@st.experimental_memo(ttl=60, persist="disk")
def load_data():
    return 42

st.write(load_data())
```

And a warning will be logged to your terminal:

```bash
streamlit run app.py

  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.1.1:8501

2022-09-22 13:35:41.587 The memoized function 'load_data' has a TTL that will be ignored. Persistent memo caches currently don't support TTL.
```

st.experimental_memo.clear was deprecated in version 1.18.0. Use <code>st.cache_data.clear instead. Learn more in Caching."/>

#### Example

In the example below, pressing the "Clear All" button will clear memoized values from all functions decorated with `@st.experimental_memo`.

```python
import streamlit as st

@st.experimental_memo
def square(x):
    return x**2

@st.experimental_memo
def cube(x):
    return x**3

if st.button("Clear All"):
    # Clear values from *all* memoized functions:
    # i.e. clear values from both square and cube
    st.experimental_memo.clear()
```

## Replay static `st` elements in cache-decorated functions

Functions decorated with `@st.experimental_memo` can contain static `st` elements. When a cache-decorated function is executed, we record the element and block messages produced, so the elements will appear in the app even when execution of the function is skipped because the result was cached.

In the example below, the `@st.experimental_memo` decorator is used to cache the execution of the `load_data` function, that returns a pandas DataFrame. Notice the cached function also contains a `st.area_chart` command, which will be replayed when the function is skipped because the result was cached.

```python
import numpy as np
import pandas as pd
import streamlit as st

@st.experimental_memo
def load_data(rows):
    chart_data = pd.DataFrame(
        np.random.randn(rows, 10),
        columns=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
    )
    # Contains a static element st.area_chart
    st.area_chart(chart_data) # This will be recorded and displayed even when the function is skipped
    return chart_data

df = load_data(20)
st.dataframe(df)
```

Supported static `st` elements in cache-decorated functions include:

- `st.alert`
- `st.altair_chart`
- `st.area_chart`
- `st.audio`
- `st.bar_chart`
- `st.ballons`
- `st.bokeh_chart`
- `st.caption`
- `st.code`
- `st.components.v1.html`
- `st.components.v1.iframe`
- `st.container`
- `st.dataframe`
- `st.echo`
- `st.empty`
- `st.error`
- `st.exception`
- `st.expander`
- `st.experimental_get_query_params`
- `st.experimental_set_query_params`
- `st.form`
- `st.form_submit_button`
- `st.graphviz_chart`
- `st.help`
- `st.image`
- `st.info`
- `st.json`
- `st.latex`
- `st.line_chart`
- `st.markdown`
- `st.metric`
- `st.plotly_chart`
- `st.progress`
- `st.pydeck_chart`
- `st.snow`
- `st.spinner`
- `st.success`
- `st.table`
- `st.text`
- `st.vega_lite_chart`
- `st.video`
- `st.warning`

## Replay input widgets in cache-decorated functions

In addition to static elements, functions decorated with `@st.experimental_memo` can also contain input widgets! Replaying input widgets is disabled by default. To enable it, you can set the `experimental_allow_widgets` parameter for `@st.experimental_memo` to `True`. The example below enables widget replaying, and shows the use of a checkbox widget within a cache-decorated function.

```python
import streamlit as st

# Enable widget replay
@st.experimental_memo(experimental_allow_widgets=True)
def func():
    # Contains an input widget
    st.checkbox("Works!")

func()
```

If the cache decorated function contains input widgets, but `experimental_allow_widgets` is set to `False` or unset, Streamlit will throw a `CachedStFunctionWarning`, like the one below:

```python
import streamlit as st

# Widget replay is disabled by default
@st.experimental_memo
def func():
    # Streamlit will throw a CachedStFunctionWarning
    st.checkbox("Doesn't work")

func()
```

### How widget replay works

Let's demystify how widget replay in cache-decorated functions works and gain a conceptual understanding. Widget values are treated as additional inputs to the function, and are used to determine whether the function should be executed or not. Consider the following example:

```python
import streamlit as st

@st.experimental_memo(experimental_allow_widgets=True)
def plus_one(x):
    y = x + 1
    if st.checkbox("Nuke the value 💥"):
        st.write("Value was nuked, returning 0")
        y = 0
    return y

st.write(plus_one(2))
```

The `plus_one` function takes an integer `x` as input, and returns `x + 1`. The function also contains a checkbox widget, which is used to "nuke" the value of `x`. i.e. the return value of `plus_one` depends on the state of the checkbox: if it is checked, the function returns `0`, otherwise it returns `3`.

In order to know which value the cache should return (in case of a cache hit), Streamlit treats the checkbox state (checked / unchecked) as an additional input to the function `plus_one` (just like `x`). If the user checks the checkbox (thereby changing its state), we look up the cache for the same value of `x` (2) and the same checkbox state (checked). If the cache contains a value for this combination of inputs, we return it. Otherwise, we execute the function and store the result in the cache.

Let's now understand how enabling and disabling widget replay changes the behavior of the function.

### Widget replay disabled

- Widgets in cached functions throw a `CachedStFunctionWarning` and are ignored.
- Other static elements in cached functions replay as expected.

### Widget replay enabled

- Widgets in cached functions don't lead to a warning, and are replayed as expected.
- Interacting with a widget in a cached function will cause the function to be executed again, and the cache to be updated.
- Widgets in cached functions retain their state across reruns.
- Each unique combination of widget values is treated as a separate input to the function, and is used to determine whether the function should be executed or not. i.e. Each unique combination of widget values has its own cache entry; the cached function runs the first time and the saved value is used afterwards.
- Calling a cached function multiple times in one script run with the same arguments triggers a `DuplicateWidgetID` error.
- If the arguments to a cached function change, widgets from that function that render again retain their state.
- Changing the source code of a cached function invalidates the cache.
- Both `st.experimental_memo` and `st.experimental_singleton` support widget replay.
- Fundamentally, the behavior of a function with (supported) widgets in it doesn't change when it is decorated with `@st.experimental_memo` or `@st.experimental_singleton`. The only difference is that the function is only executed when we detect a cache "miss".

### Supported widgets

All input widgets are supported in cache-decorated functions. The following is an exhaustive list of supported widgets:

- `st.button`
- `st.camera_input`
- `st.checkbox`
- `st.color_picker`
- `st.date_input`
- `st.download_button`
- `st.file_uploader`
- `st.multiselect`
- `st.number_input`
- `st.radio`
- `st.selectbox`
- `st.select_slider`
- `st.slider`
- `st.text_area`
- `st.text_input`
- `st.time_input`

################################################
Section 1.4 - experimental-singleton.md
################################################

st.experimental_singleton - st.experimental_singleton is a function decorator used to store singleton objects.

IMPORTANT: This is an experimental feature. Experimental features and their APIs may change or be removed at any time. To learn more, click here.

st.experimental_singleton was deprecated in version 1.18.0. Use <code>st.cache_resource instead. Learn more in Caching."/>

st.experimental_singleton.clear was deprecated in version 1.18.0. Use <code>st.cache_resource.clear instead. Learn more in Caching."/>

#### Example

In the example below, pressing the "Clear All" button will clear _all_ singleton caches. i.e. Clears cached singleton objects from all functions decorated with `@st.experimental_singleton`.

```python
import streamlit as st
from transformers import BertModel

@st.experimental_singleton
 def get_database_session(url):
     # Create a database session object that points to the URL.
     return session

@st.experimental_singleton
def get_model(model_type):
    # Create a model of the specified type.
    return BertModel.from_pretrained(model_type)

if st.button("Clear All"):
    # Clears all singleton caches:
    st.experimental_singleton.clear()
```

## Validating the cache

The `@st.experimental_singleton` decorator is used to cache the output of a function, so that it only needs to be executed once. This can improve performance in certain situations, such as when a function takes a long time to execute or makes a network request.

However, in some cases, the cached output may become invalid over time, such as when a database connection times out. To handle this, the `@st.experimental_singleton` decorator supports an optional `validate` parameter, which accepts a validation function that is called each time the cached output is accessed. If the validation function returns False, the cached output is discarded and the decorated function is executed again.

### Best Practices

- Use the `validate` parameter when the cached output may become invalid over time, such as when a database connection or an API key expires.
- Use the `validate` parameter judiciously, as it will add an additional overhead of calling the validation function each time the cached output is accessed.
- Make sure that the validation function is as fast as possible, as it will be called each time the cached output is accessed.
- Consider to validate cached data periodically, instead of each time it is accessed, to mitigate the performance impact.
- Handle errors that may occur during validation and provide a fallback mechanism if the validation fails.

## Replay static `st` elements in cache-decorated functions

Functions decorated with `@st.experimental_singleton` can contain static `st` elements. When a cache-decorated function is executed, we record the element and block messages produced, so the elements will appear in the app even when execution of the function is skipped because the result was cached.

In the example below, the `@st.experimental_singleton` decorator is used to cache the execution of the `get_model` function, that returns a 🤗 Hugging Face Transformers model. Notice the cached function also contains a `st.bar_chart` command, which will be replayed when the function is skipped because the result was cached.

```python
import numpy as np
import pandas as pd
import streamlit as st
from transformers import AutoModel

@st.experimental_singleton
def get_model(model_type):
    # Contains a static element st.bar_chart
    st.bar_chart(
        np.random.rand(10, 1)
    )  # This will be recorded and displayed even when the function is skipped

    # Create a model of the specified type
    return AutoModel.from_pretrained(model_type)

bert_model = get_model("distilbert-base-uncased")
st.help(bert_model) # Display the model's docstring
```

Supported static `st` elements in cache-decorated functions include:

- `st.alert`
- `st.altair_chart`
- `st.area_chart`
- `st.audio`
- `st.bar_chart`
- `st.ballons`
- `st.bokeh_chart`
- `st.caption`
- `st.code`
- `st.components.v1.html`
- `st.components.v1.iframe`
- `st.container`
- `st.dataframe`
- `st.echo`
- `st.empty`
- `st.error`
- `st.exception`
- `st.expander`
- `st.experimental_get_query_params`
- `st.experimental_set_query_params`
- `st.form`
- `st.form_submit_button`
- `st.graphviz_chart`
- `st.help`
- `st.image`
- `st.info`
- `st.json`
- `st.latex`
- `st.line_chart`
- `st.markdown`
- `st.metric`
- `st.plotly_chart`
- `st.progress`
- `st.pydeck_chart`
- `st.snow`
- `st.spinner`
- `st.success`
- `st.table`
- `st.text`
- `st.vega_lite_chart`
- `st.video`
- `st.warning`

## Replay input widgets in cache-decorated functions

In addition to static elements, functions decorated with `@st.experimental_singleton` can also contain input widgets! Replaying input widgets is disabled by default. To enable it, you can set the `experimental_allow_widgets` parameter for `@st.experimental_singleton` to `True`. The example below enables widget replaying, and shows the use of a checkbox widget within a cache-decorated function.

```python
import streamlit as st

# Enable widget replay
@st.experimental_singleton(experimental_allow_widgets=True)
def func():
    # Contains an input widget
    st.checkbox("Works!")

func()
```

If the cache decorated function contains input widgets, but `experimental_allow_widgets` is set to `False` or unset, Streamlit will throw a `CachedStFunctionWarning`, like the one below:

```python
import streamlit as st

# Widget replay is disabled by default
@st.experimental_singleton
def func():
    # Streamlit will throw a CachedStFunctionWarning
    st.checkbox("Doesn't work")

func()
```

### How widget replay works

Let's demystify how widget replay in cache-decorated functions works and gain a conceptual understanding. Widget values are treated as additional inputs to the function, and are used to determine whether the function should be executed or not. Consider the following example:

```python
import streamlit as st

@st.experimental_singleton(experimental_allow_widgets=True)
def plus_one(x):
    y = x + 1
    if st.checkbox("Nuke the value 💥"):
        st.write("Value was nuked, returning 0")
        y = 0
    return y

st.write(plus_one(2))
```

The `plus_one` function takes an integer `x` as input, and returns `x + 1`. The function also contains a checkbox widget, which is used to "nuke" the value of `x`. i.e. the return value of `plus_one` depends on the state of the checkbox: if it is checked, the function returns `0`, otherwise it returns `3`.

In order to know which value the cache should return (in case of a cache hit), Streamlit treats the checkbox state (checked / unchecked) as an additional input to the function `plus_one` (just like `x`). If the user checks the checkbox (thereby changing its state), we look up the cache for the same value of `x` (2) and the same checkbox state (checked). If the cache contains a value for this combination of inputs, we return it. Otherwise, we execute the function and store the result in the cache.

Let's now understand how enabling and disabling widget replay changes the behavior of the function.

### Widget replay disabled

- Widgets in cached functions throw a `CachedStFunctionWarning` and are ignored.
- Other static elements in cached functions replay as expected.

### Widget replay enabled

- Widgets in cached functions don't lead to a warning, and are replayed as expected.
- Interacting with a widget in a cached function will cause the function to be executed again, and the cache to be updated.
- Widgets in cached functions retain their state across reruns.
- Each unique combination of widget values is treated as a separate input to the function, and is used to determine whether the function should be executed or not. i.e. Each unique combination of widget values has its own cache entry; the cached function runs the first time and the saved value is used afterwards.
- Calling a cached function multiple times in one script run with the same arguments triggers a `DuplicateWidgetID` error.
- If the arguments to a cached function change, widgets from that function that render again retain their state.
- Changing the source code of a cached function invalidates the cache.
- Both `st.experimental_singleton` and `st.experimental_memo` support widget replay.
- Fundamentally, the behavior of a function with (supported) widgets in it doesn't change when it is decorated with `@st.experimental_singleton` or `@st.experimental_memo`. The only difference is that the function is only executed when we detect a cache "miss".

### Supported widgets

All input widgets are supported in cache-decorated functions. The following is an exhaustive list of supported widgets:

- `st.button`
- `st.camera_input`
- `st.checkbox`
- `st.color_picker`
- `st.date_input`
- `st.download_button`
- `st.file_uploader`
- `st.multiselect`
- `st.number_input`
- `st.radio`
- `st.selectbox`
- `st.select_slider`
- `st.slider`
- `st.text_area`
- `st.text_input`
- `st.time_input`

################################################
Section 1.5 - experimental_get_query_params.md
################################################

st.experimental_get_query_params - st.experimental_get_query_params returns query parameters currently showing in the browser's URL bar.

st.experimental_get_query_params was deprecated in version 1.30.0. Use <code>st.query_params instead." />

################################################
Section 1.6 - experimental_set_query_params.md
################################################

st.experimental_set_query_params - st.experimental_set_query_params sets query parameters shown in the browser's URL bar.

st.experimental_set_query_params was deprecated in version 1.30.0. Use <code>st.query_params instead." />

################################################
Section 1.7 - query_params.md
################################################

st.query_params - st.query_params reads and manipulates query parameters in the browser's URL bar.

## st.query_params

`st.query_params` provides a dictionary-like interface to access query parameters in your app's URL and is available as of Streamlit 1.30.0. It behaves similarly to `st.session_state` with the notable exception that keys may be repeated in an app's URL. Handling of repeated keys requires special consideration as explained below.

`st.query_params` can be used with both key and attribute notation. For example, `st.query_params.my_key` and `st.query_params["my_key"]`. All keys and values will be set and returned as strings. When you write to `st.query_params`, key-value pair prefixed with `?` is added to the end of your app's URL. Each additional pair is prefixed with `&` instead of `?`. Query parameters are cleared when navigating between pages in a multipage app.

For example, consider the following URL:

```javascript
https://your_app.streamlit.app/?first_key=1&second_key=two&third_key=true
```

The parameters in the URL above will be accessible in `st.query_params` as:

```python
{
    "first_key" : "1",
    "second_key" : "two",
    "third_key" : "true"
}
```

This means you can use those parameters in your app like this:

```python
# You can read query params using key notation
if st.query_params["first_key"] == "1":
    do_something()

# ...or using attribute notation
if st.query_params.second_key == "two":
    do_something_else()

# And you can change a param by just writing to it
st.query_params.first_key = 2  # This gets converted to str automatically
```

### Repeated keys

When a key is repeated in your app's URL (`?a=1&a=2&a=3`), dict-like methods will return only the last value. In this example, `st.query_params["a"]` returns `"3"`. To get all keys as a list, use the `.get_all()` method shown below. To set the value of a repeated key, assign the values as a list. For example, `st.query_params.a = ["1", "2", "3"]` produces the repeated key given at the beginning of this paragraph.

### Limitation

`st.query_params` can't get or set embedding settings as described in Embed your app. `st.query_params.embed` and `st.query_params.embed_options` will raise an `AttributeError` or `StreamlitAPIException` when trying to get or set their values, respectively.

################################################
Section 1.8 - session_state.md
################################################

Session State - st.session_state is a way to share variables between reruns, for each user session.

# Session State

Session State is a way to share variables between reruns, for each user session. In addition to the ability to store and persist state, Streamlit also exposes the ability to manipulate state using Callbacks. Session state also persists across apps inside a multipage app.

Check out this Session State basics tutorial video by Streamlit Developer Advocate Dr. Marisa Smith to get started:

Tutorial video available: VideoId=92jUAXBmZyU

### Initialize values in Session State

The Session State API follows a field-based API, which is very similar to Python dictionaries:

```python
# Initialization
if 'key' not in st.session_state:
    st.session_state['key'] = 'value'

# Session State also supports attribute based syntax
if 'key' not in st.session_state:
    st.session_state.key = 'value'
```

### Reads and updates

Read the value of an item in Session State and display it by passing to `st.write` :

```python
# Read
st.write(st.session_state.key)

# Outputs: value
```

Update an item in Session State by assigning it a value:

```python
st.session_state.key = 'value2'     # Attribute API
st.session_state['key'] = 'value2'  # Dictionary like API
```

Curious about what is in Session State? Use `st.write` or magic:

```python
st.write(st.session_state)

# With magic:
st.session_state
```

Streamlit throws a handy exception if an uninitialized variable is accessed:

```python
st.write(st.session_state['value'])

# Throws an exception!
```

!state-uninitialized-exception

### Delete items

Delete items in Session State using the syntax to delete items in any Python dictionary:

```python
# Delete a single key-value pair
del st.session_state[key]

# Delete all the items in Session state
for key in st.session_state.keys():
    del st.session_state[key]
```

Session State can also be cleared by going to Settings → Clear Cache, followed by Rerunning the app.

!state-clear-cache

### Session State and Widget State association

Every widget with a key is automatically added to Session State:

```python
st.text_input("Your name", key="name")

# This exists now:
st.session_state.name
```

### Use Callbacks to update Session State

A callback is a python function which gets called when an input widget changes.

**Order of execution**: When updating Session state in response to **events**, a callback function gets executed first, and then the app is executed from top to bottom.

Callbacks can be used with widgets using the parameters `on_change` (or `on_click`), `args`, and `kwargs`:

**Parameters**

- **on_change** or **on_click** - The function name to be used as a callback
- **args** (_tuple_) - List of arguments to be passed to the callback function
- **kwargs** (_dict_) - Named arguments to be passed to the callback function

Widgets which support the `on_change` event:

- `st.checkbox`
- `st.color_picker`
- `st.date_input`
- `st.data_editor`
- `st.file_uploader`
- `st.multiselect`
- `st.number_input`
- `st.radio`
- `st.select_slider`
- `st.selectbox`
- `st.slider`
- `st.text_area`
- `st.text_input`
- `st.time_input`
- `st.toggle`

Widgets which support the `on_click` event:

- `st.button`
- `st.download_button`
- `st.form_submit_button`

To add a callback, define a callback function **above** the widget declaration and pass it to the widget via the `on_change` (or `on_click` ) parameter.

### Forms and Callbacks

Widgets inside a form can have their values be accessed and set via the Session State API. `st.form_submit_button` can have a callback associated with it. The callback gets executed upon clicking on the submit button. For example:

```python
def form_callback():
    st.write(st.session_state.my_slider)
    st.write(st.session_state.my_checkbox)

with st.form(key='my_form'):
    slider_input = st.slider('My slider', 0, 10, 5, key='my_slider')
    checkbox_input = st.checkbox('Yes or No', key='my_checkbox')
    submit_button = st.form_submit_button(label='Submit', on_click=form_callback)
```

### Serializable Session State

Serialization refers to the process of converting an object or data structure into a format that can be persisted and shared, and allowing you to recover the data’s original structure. Python’s built-in pickle module serializes Python objects to a byte stream ("pickling") and deserializes the stream into an object ("unpickling").

By default, Streamlit’s Session State allows you to persist any Python object for the duration of the session, irrespective of the object’s pickle-serializability. This property lets you store Python primitives such as integers, floating-point numbers, complex numbers and booleans, dataframes, and even lambdas returned by functions. However, some execution environments may require serializing all data in Session State, so it may be useful to detect incompatibility during development, or when the execution environment will stop supporting it in the future.

To that end, Streamlit provides a `runner.enforceSerializableSessionState` configuration option that, when set to `true`, only allows pickle-serializable objects in Session State. To enable the option, either create a global or project config file with the following or use it as a command-line flag:

```toml
# .streamlit/config.toml
[runner]
enforceSerializableSessionState = true
```

By "_pickle-serializable_", we mean calling `pickle.dumps(obj)` should not raise a `PicklingError` exception. When the config option is enabled, adding unserializable data to session state should result in an exception. E.g.,

```python
import streamlit as st

def unserializable_data():
		return lambda x: x

#👇 results in an exception when enforceSerializableSessionState is on
st.session_state.unserializable = unserializable_data()
```

WARNING: When `runner.enforceSerializableSessionState` is set to `true`, Session State implicitly uses the `pickle` module, which is known to be insecure. Ensure all data saved and retrieved from Session State is trusted because it is possible to construct malicious pickle data that will execute arbitrary code during unpickling. Never load data that could have come from an untrusted source in an unsafe mode or that could have been tampered with. **Only load data you trust**.

### Caveats and limitations

- Only the `st.form_submit_button` has a callback in forms. Other widgets inside a form are not allowed to have callbacks.
- `on_change` and `on_click` events are only supported on input type widgets.
- Modifying the value of a widget via the Session state API, after instantiating it, is not allowed and will raise a `StreamlitAPIException`. For example:

  ```python
  slider = st.slider(
      label='My Slider', min_value=1,
      max_value=10, value=5, key='my_slider')

  st.session_state.my_slider = 7

  # Throws an exception!
  ```

  !state-modified-instantiated-exception

- Setting the widget state via the Session State API and using the `value` parameter in the widget declaration is not recommended, and will throw a warning on the first run. For example:

  ```python
  st.session_state.my_slider = 7

  slider = st.slider(
      label='Choose a Value', min_value=1,
      max_value=10, value=5, key='my_slider')
  ```

  !state-value-api-exception

- Setting the state of button-like widgets: `st.button`, `st.download_button`, and `st.file_uploader` via the Session State API is not allowed. Such type of widgets are by default _False_ and have ephemeral _True_ states which are only valid for a single run. For example:

  ```python
  if 'my_button' not in st.session_state:
      st.session_state.my_button = True

  st.button('My button', key='my_button')

  # Throws an exception!
  ```

  !state-button-exception

------------------------------------------------------------------------------------------------
CHAPTER 2: charts.md
------------------------------------------------------------------------------------------------

################################################
Section 2.1 - altair_chart.md
################################################

st.altair_chart - st.altair_chart displays a chart using the Altair library.

## Chart selections

## Theming

Altair charts are displayed using the Streamlit theme by default. This theme is sleek, user-friendly, and incorporates Streamlit's color palette. The added benefit is that your charts better integrate with the rest of your app's design.

The Streamlit theme is available from Streamlit 1.16.0 through the `theme="streamlit"` keyword argument. To disable it, and use Altair's native theme, use `theme=None` instead.

Let's look at an example of charts with the Streamlit theme and the native Altair theme:

```python
import altair as alt
from vega_datasets import data

source = data.cars()

chart = alt.Chart(source).mark_circle().encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin',
).interactive()

tab1, tab2 = st.tabs(["Streamlit theme (default)", "Altair native theme"])

with tab1:
    # Use the Streamlit theme.
    # This is the default. So you can also omit the theme argument.
    st.altair_chart(chart, theme="streamlit", use_container_width=True)
with tab2:
    # Use the native Altair theme.
    st.altair_chart(chart, theme=None, use_container_width=True)
```

Click the tabs in the interactive app below to see the charts with the Streamlit theme enabled and disabled.

If you're wondering if your own customizations will still be taken into account, don't worry! You can still make changes to your chart configurations. In other words, although we now enable the Streamlit theme by default, you can overwrite it with custom colors or fonts. For example, if you want a chart line to be green instead of the default red, you can do it!

Here's an example of an Altair chart where manual color passing is done and reflected:

```python
import altair as alt
import streamlit as st
from vega_datasets import data

source = data.seattle_weather()

scale = alt.Scale(
    domain=["sun", "fog", "drizzle", "rain", "snow"],
    range=["#e7ba52", "#a7a7a7", "#aec7e8", "#1f77b4", "#9467bd"],
)
color = alt.Color("weather:N", scale=scale)

# We create two selections:
# - a brush that is active on the top panel
# - a multi-click that is active on the bottom panel
brush = alt.selection_interval(encodings=["x"])
click = alt.selection_multi(encodings=["color"])

# Top panel is scatter plot of temperature vs time
points = (
    alt.Chart()
    .mark_point()
    .encode(
        alt.X("monthdate(date):T", title="Date"),
        alt.Y(
            "temp_max:Q",
            title="Maximum Daily Temperature (C)",
            scale=alt.Scale(domain=[-5, 40]),
        ),
        color=alt.condition(brush, color, alt.value("lightgray")),
        size=alt.Size("precipitation:Q", scale=alt.Scale(range=[5, 200])),
    )
    .properties(width=550, height=300)
    .add_selection(brush)
    .transform_filter(click)
)

# Bottom panel is a bar chart of weather type
bars = (
    alt.Chart()
    .mark_bar()
    .encode(
        x="count()",
        y="weather:N",
        color=alt.condition(click, color, alt.value("lightgray")),
    )
    .transform_filter(brush)
    .properties(
        width=550,
    )
    .add_selection(click)
)

chart = alt.vconcat(points, bars, data=source, title="Seattle Weather: 2012-2015")

tab1, tab2 = st.tabs(["Streamlit theme (default)", "Altair native theme"])

with tab1:
    st.altair_chart(chart, theme="streamlit", use_container_width=True)
with tab2:
    st.altair_chart(chart, theme=None, use_container_width=True)
```

Notice how the custom colors are still reflected in the chart, even when the Streamlit theme is enabled 👇

For many more examples of Altair charts with and without the Streamlit theme, check out the altair.streamlit.app.

################################################
Section 2.2 - area_chart.md
################################################

st.area_chart - st.area_chart displays an area chart.

################################################
Section 2.3 - bar_chart.md
################################################

st.bar_chart - st.bar_chart displays a bar chart.

################################################
Section 2.4 - bokeh_chart.md
################################################

st.bokeh_chart - st.bokeh_chart displays an interactive Bokeh chart.

################################################
Section 2.5 - graphviz_chart.md
################################################

st.graphviz_chart - st.graphviz_chart displays a graph using the dagre-d3 library.

################################################
Section 2.6 - line_chart.md
################################################

st.line_chart - st.line_chart displays a line chart.

################################################
Section 2.7 - map.md
################################################

st.map - st.map displays a map with points on it.

################################################
Section 2.8 - plotly_chart.md
################################################

st.plotly_chart - st.plotly_chart displays an interactive Plotly chart.

## Chart selections

## Theming

Plotly charts are displayed using the Streamlit theme by default. This theme is sleek, user-friendly, and incorporates Streamlit's color palette. The added benefit is that your charts better integrate with the rest of your app's design.

The Streamlit theme is available from Streamlit 1.16.0 through the `theme="streamlit"` keyword argument. To disable it, and use Plotly's native theme, use `theme=None` instead.

Let's look at an example of charts with the Streamlit theme and the native Plotly theme:

```python
import plotly.express as px
import streamlit as st

df = px.data.gapminder()

fig = px.scatter(
    df.query("year==2007"),
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    hover_name="country",
    log_x=True,
    size_max=60,
)

tab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])
with tab1:
    # Use the Streamlit theme.
    # This is the default. So you can also omit the theme argument.
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
with tab2:
    # Use the native Plotly theme.
    st.plotly_chart(fig, theme=None, use_container_width=True)
```

Click the tabs in the interactive app below to see the charts with the Streamlit theme enabled and disabled.

If you're wondering if your own customizations will still be taken into account, don't worry! You can still make changes to your chart configurations. In other words, although we now enable the Streamlit theme by default, you can overwrite it with custom colors or fonts. For example, if you want a chart line to be green instead of the default red, you can do it!

Here's an example of an Plotly chart where a custom color scale is defined and reflected:

```python
import plotly.express as px
import streamlit as st

st.subheader("Define a custom colorscale")
df = px.data.iris()
fig = px.scatter(
    df,
    x="sepal_width",
    y="sepal_length",
    color="sepal_length",
    color_continuous_scale="reds",
)

tab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])
with tab1:
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
with tab2:
    st.plotly_chart(fig, theme=None, use_container_width=True)
```

Notice how the custom color scale is still reflected in the chart, even when the Streamlit theme is enabled 👇

For many more examples of Plotly charts with and without the Streamlit theme, check out the plotly.streamlit.app.

################################################
Section 2.9 - pydeck_chart.md
################################################

st.pydeck_chart - st.pydeck_chart displays a chart using the PyDeck library.

## Chart selections

################################################
Section 2.10 - pyplot.md
################################################

st.pyplot - st.pyplot displays a matplotlib.pyplot figure.

WARNING: Matplotlib doesn't work well with threads. So if you're using Matplotlib you should wrap your code with locks as shown in the snippet below. This Matplotlib bug is more prominent when you deploy and share your app apps since you're more likely to get concurrent users then.

    ```python
    from matplotlib.backends.backend_agg import RendererAgg
    _lock = RendererAgg.lock

    with _lock:
        fig.title('This is a figure)')
        fig.plot([1,20,3,40])
        st.pyplot(fig)
    ```

################################################
Section 2.11 - scatter_chart.md
################################################

st.scatter_chart - st.scatter_chart displays an scatter chart.

################################################
Section 2.12 - vega_lite_chart.md
################################################

st.vega_lite_chart - st.vega_lite_chart displays a chart using the Vega-Lite library.

## Chart selections

## Theming

Vega-Lite charts are displayed using the Streamlit theme by default. This theme is sleek, user-friendly, and incorporates Streamlit's color palette. The added benefit is that your charts better integrate with the rest of your app's design.

The Streamlit theme is available from Streamlit 1.16.0 through the `theme="streamlit"` keyword argument. To disable it, and use Vega-Lite's native theme, use `theme=None` instead.

Let's look at an example of charts with the Streamlit theme and the native Vega-Lite theme:

```python
import streamlit as st
from vega_datasets import data

source = data.cars()

chart = {
    "mark": "point",
    "encoding": {
        "x": {
            "field": "Horsepower",
            "type": "quantitative",
        },
        "y": {
            "field": "Miles_per_Gallon",
            "type": "quantitative",
        },
        "color": {"field": "Origin", "type": "nominal"},
        "shape": {"field": "Origin", "type": "nominal"},
    },
}

tab1, tab2 = st.tabs(["Streamlit theme (default)", "Vega-Lite native theme"])

with tab1:
    # Use the Streamlit theme.
    # This is the default. So you can also omit the theme argument.
    st.vega_lite_chart(
        source, chart, theme="streamlit", use_container_width=True
    )
with tab2:
    st.vega_lite_chart(
        source, chart, theme=None, use_container_width=True
    )
```

Click the tabs in the interactive app below to see the charts with the Streamlit theme enabled and disabled.

If you're wondering if your own customizations will still be taken into account, don't worry! You can still make changes to your chart configurations. In other words, although we now enable the Streamlit theme by default, you can overwrite it with custom colors or fonts. For example, if you want a chart line to be green instead of the default red, you can do it!

------------------------------------------------------------------------------------------------
CHAPTER 3: chat.md
------------------------------------------------------------------------------------------------

################################################
Section 3.1 - chat-input.md
################################################

st.chat_input - st.chat_input displays a chat input widget.

Note: Read the Build a basic LLM chat app tutorial to learn how to use `st.chat_message` and `st.chat_input` to build chat-based apps.

For an overview of the `st.chat_input` and `st.chat_message` API, check out this video tutorial by Chanin Nantasenamat (@dataprofessor), a Senior Developer Advocate at Streamlit.

Tutorial video available: VideoId=4sPnOqeUDmk

################################################
Section 3.2 - chat-message.md
################################################

st.chat_message - st.chat_message inserts a chat message container into the app.

Note: Read the Build a basic LLM chat app tutorial to learn how to use `st.chat_message` and `st.chat_input` to build chat-based apps.

For an overview of the `st.chat_message` and `st.chat_input` API, check out this video tutorial by Chanin Nantasenamat (@dataprofessor), a Senior Developer Advocate at Streamlit.

Tutorial video available: VideoId=4sPnOqeUDmk

------------------------------------------------------------------------------------------------
CHAPTER 4: command-line.md
------------------------------------------------------------------------------------------------

################################################
Section 4.1 - run.md
################################################

streamlit run - st.get_option retrieves a single configuration option.

################################################
Section 4.2 - set_option.md
################################################

st.set_option - st.set_option updates a single configuration option.

################################################
Section 4.3 - set_page_config.md
################################################

st.set_page_config - st.set_page_config configures the default settings of the page.

------------------------------------------------------------------------------------------------
CHAPTER 6: connections.md
------------------------------------------------------------------------------------------------

################################################
Section 6.1 - connection.md
################################################

st.connection - st.dialog opens a multi-element modal overlay
keywords: popup, modal, overlay

Function: st.dialog (previously experimental)

################################################
Section 6.2 - experimental_rerun.md
################################################

st.experimental_rerun - st.experimental_rerun will rerun the script immediately.

st.experimental_rerun was deprecated in version 1.27.0. Use <code>st.rerun instead."/>

################################################
Section 6.3 - form.md
################################################

st.form - st.form creates a form that batches elements together with a “Submit" button.

Note: This page only contains information on the `st.forms` API. For a deeper dive into creating and using forms within Streamlit apps, read our guide on Using forms.

################################################
Section 6.4 - form_submit_button.md
################################################

st.form_submit_button - st.form_submit_button displays a form submit button.

################################################
Section 6.5 - fragment.md
################################################

st.fragment - st.fragment is a decorator that allows a function to rerun independently

Function: st.fragment (previously experimental)

################################################
Section 6.6 - rerun.md
################################################

st.rerun - st.rerun will rerun the script immediately.

Function: st.rerun (previously experimental)

### Caveats for `st.rerun`

`st.rerun` is one of the tools to control the logic of your app. While it is great for prototyping, there can be adverse side effects:

- Additional script runs may be inefficient and slower.
- Excessive reruns may complicate your app's logic and be harder to follow.
- If misused, infinite looping may crash your app.

In many cases where `st.rerun` works, callbacks may be a cleaner alternative. Containers may also be helpful.

### A simple example in three variations

###### Using `st.rerun` to update an earlier header

```python
import streamlit as st

if "value" not in st.session_state:
    st.session_state.value = "Title"

##### Option using st.rerun #####
st.header(st.session_state.value)

if st.button("Foo"):
    st.session_state.value = "Foo"
    st.rerun()
```

###### Using a callback to update an earlier header

```python
##### Option using a callback #####
st.header(st.session_state.value)

def update_value():
    st.session_state.value = "Bar"

st.button("Bar", on_click=update_value)
```

###### Using containers to update an earlier header

```python
##### Option using a container #####
container = st.container()

if st.button("Baz"):
    st.session_state.value = "Baz"

container.header(st.session_state.value)
```

################################################
Section 6.7 - stop.md
################################################

st.stop - st.stop stops the execution immediately.

------------------------------------------------------------------------------------------------
CHAPTER 8: custom-components.md
------------------------------------------------------------------------------------------------

################################################
Section 8.1 - declare_component.md
################################################

st.components.v1.declare_component - st.dataframe displays a dataframe as an interactive table.

Note: Learn more in our Dataframes guide and check out our tutorial, Get dataframe row-selections from users.

## Dataframe selections

## Interactivity

Dataframes displayed with `st.dataframe` are interactive. End users can sort, resize, search, and copy data to their clipboard. For on overview of features, read our Dataframes guide.

## Configuring columns

You can configure the display and editing behavior of columns in `st.dataframe` and `st.data_editor` via the Column configuration API. We have developed the API to let you add images, charts, and clickable URLs in dataframe and data editor columns. Additionally, you can make individual columns editable, set columns as categorical and specify which options they can take, hide the index of the dataframe, and much more.

################################################
Section 8.2 - data_editor.md
################################################

st.data_editor - st.data_editor display a data editor widget that allows you to edit dataframes and many other data structures in a table-like UI.

Note: This page only contains information on the `st.data_editor` API. For an overview of working with dataframes and to learn more about the data editor's capabilities and limitations, read Dataframes.

Function: st.data_editor (previously experimental)

### Configuring columns

You can configure the display and editing behavior of columns in `st.dataframe` and `st.data_editor` via the Column configuration API. We have developed the API to let you add images, charts, and clickable URLs in dataframe and data editor columns. Additionally, you can make individual columns editable, set columns as categorical and specify which options they can take, hide the index of the dataframe, and much more.

################################################
Section 8.3 - experimental_data_editor.md
################################################

st.experimental_data_editor - st.experimental_data_editor display a data editor widget that allows you to edit dataframes and many other data structures in a table-like UI.

st.experimental_data_editor was deprecated in version 1.23.0. Use <code>st.data_editor instead."/>

################################################
Section 8.4 - json.md
################################################

st.json - st.json displays object or string as a pretty-printed JSON string.

################################################
Section 8.5 - metric.md
################################################

st.metric - st.metric displays a metric in big bold font, with an optional indicator of how the metric changed.

################################################
Section 8.6 - table.md
################################################

st.table - st.table displays a static table.

Note: Static tables with `st.table` are the most basic way to display dataframes. For the majority of cases, we recommend using `st.dataframe` to display interactive dataframes, and `st.data_editor` to let users edit dataframes.

################################################
Section 8.7 - column_config\areachartcolumn.md
################################################

st.column_config.AreaChartColumn - st.columns inserts containers laid out as side-by-side columns.

################################################
Section 8.8 - container.md
################################################

st.container - st.container inserts a multi-element container.

################################################
Section 8.9 - empty.md
################################################

st.empty - st.empty inserts a single-element container.

################################################
Section 8.10 - expander.md
################################################

st.expander - st.expander inserts a multi-element container that can be expanded/collapsed.

################################################
Section 8.11 - popover.md
################################################

st.popover - st.popover inserts a multi-element popover container

################################################
Section 8.12 - sidebar.md
################################################

st.sidebar - st.sidebar displays items in a sidebar.

## st.sidebar

## Add widgets to sidebar

Not only can you add interactivity to your app with widgets, you can organize them into a sidebar. Elements can be passed to `st.sidebar` using object notation and `with` notation.

The following two snippets are equivalent:

```python
# Object notation
st.sidebar.[element_name]
```

```python
# "with" notation
with st.sidebar:
    st.[element_name]
```

Each element that's passed to `st.sidebar` is pinned to the left, allowing users to focus on the content in your app.

Note: The sidebar is resizable! Drag and drop the right border of the sidebar to resize it! ↔️

Here's an example of how you'd add a selectbox and a radio button to your sidebar:

```python
import streamlit as st

# Using object notation
add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone")
)

# Using "with" notation
with st.sidebar:
    add_radio = st.radio(
        "Choose a shipping method",
        ("Standard (5-15 days)", "Express (2-5 days)")
    )
```

IMPORTANT: The only elements that aren't supported using object notation are `st.echo`, `st.spinner`, and `st.toast`. To use these elements, you must use `with` notation.

Here's an example of how you'd add `st.echo` and `st.spinner` to your sidebar:

```python
import streamlit as st
import time

with st.sidebar:
    with st.echo():
        st.write("This code will be printed to the sidebar.")

    with st.spinner("Loading..."):
        time.sleep(5)
    st.success("Done!")
```

################################################
Section 8.13 - tabs.md
################################################

st.tabs - st.tabs inserts containers separated into tabs.

------------------------------------------------------------------------------------------------
CHAPTER 11: media.md
------------------------------------------------------------------------------------------------

################################################
Section 11.1 - audio.md
################################################

st.audio - st.audio displays an audio player.

################################################
Section 11.2 - image.md
################################################

st.image - st.image displays an image or list of images.

################################################
Section 11.3 - logo.md
################################################

st.logo - st.logo displays an image in the upper-left corner of your app and its sidebar.

################################################
Section 11.4 - video.md
################################################

st.video - st.video displays a video player.

------------------------------------------------------------------------------------------------
CHAPTER 12: navigation.md
------------------------------------------------------------------------------------------------

################################################
Section 12.1 - navigation.md
################################################

st.navigation - st.navigation declares the set of available pages to select in a multipage app

################################################
Section 12.2 - page.md
################################################

st.Page - st.Page initializes a StreamlitPage object for multipage apps

################################################
Section 12.3 - switch_page.md
################################################

st.switch_page - st.switch_page programmatically switches the active page.

------------------------------------------------------------------------------------------------
CHAPTER 13: status.md
------------------------------------------------------------------------------------------------

################################################
Section 13.1 - balloons.md
################################################

st.balloons - st.balloons displays celebratory balloons!

################################################
Section 13.2 - error.md
################################################

st.error - st.error displays error message.

################################################
Section 13.3 - exception.md
################################################

st.exception - st.exception displays an exception.

################################################
Section 13.4 - info.md
################################################

st.info - st.info displays an informational message.

################################################
Section 13.5 - progress.md
################################################

st.progress - st.progress displays a progress bar.

################################################
Section 13.6 - snow.md
################################################

st.snow - st.snow displays celebratory snowflakes!

################################################
Section 13.7 - spinner.md
################################################

st.spinner - st.spinner temporarily displays a message while executing a block of code.

################################################
Section 13.8 - status.md
################################################

st.status - st.status inserts a mutable expander element

################################################
Section 13.9 - success.md
################################################

st.success - st.success displays a success message.

################################################
Section 13.10 - toast.md
################################################

st.toast - st.toast briefly displays a toast message in the bottom-right corner

When multiple toasts are generated, they will stack. Hovering over a toast will
stop it from disappearing. When hovering ends, the toast will disappear after
four more seconds.

```python
import streamlit as st
import time

if st.button('Three cheers'):
    st.toast('Hip!')
    time.sleep(.5)
    st.toast('Hip!')
    time.sleep(.5)
    st.toast('Hooray!', icon='🎉')
```

Toast messages can also be updated. Assign `st.toast(my_message)` to a variable
and use the `.toast()` method to update it. Note: if a toast has already disappeared
or been dismissed, the update will not be seen.

```python
import streamlit as st
import time

def cook_breakfast():
    msg = st.toast('Gathering ingredients...')
    time.sleep(1)
    msg.toast('Cooking...')
    time.sleep(1)
    msg.toast('Ready!', icon = "🥞")

if st.button('Cook breakfast'):
    cook_breakfast()
```

################################################
Section 13.11 - warning.md
################################################

st.warning - st.warning displays warning message.

------------------------------------------------------------------------------------------------
CHAPTER 14: testing.md
------------------------------------------------------------------------------------------------

################################################
Section 14.1 - st.testing.v1.AppTest.md
################################################

st.testing.v1.AppTest - st.caption displays text in small font.

################################################
Section 14.2 - code.md
################################################

st.code - st.code displays a code block with optional syntax highlighting.

################################################
Section 14.3 - divider.md
################################################

st.divider - st.divider displays a horizontal rule in your app.

Here's what it looks like in action when you have multiple elements in the app:

```python
import streamlit as st

st.write("This is some text.")

st.slider("This is a slider", 0, 100, (25, 75))

st.divider()  # 👈 Draws a horizontal rule

st.write("This text is between the horizontal rules.")

st.divider()  # 👈 Another horizontal rule
```

################################################
Section 14.4 - echo.md
################################################

st.echo - st.echo displays some code on the app, then execute it. Useful for tutorials.

### Display code

Sometimes you want your Streamlit app to contain _both_ your usual
Streamlit graphic elements _and_ the code that generated those elements.
That's where `st.echo()` comes in.

Ok so let's say you have the following file, and you want to make its
app a little bit more self-explanatory by making that middle section
visible in the Streamlit app:

```python
import streamlit as st

def get_user_name():
    return 'John'

# ------------------------------------------------
# Want people to see this part of the code...

def get_punctuation():
    return '!!!'

greeting = "Hi there, "
user_name = get_user_name()
punctuation = get_punctuation()

st.write(greeting, user_name, punctuation)

# ...up to here
# ------------------------------------------------

foo = 'bar'
st.write('Done!')
```

The file above creates a Streamlit app containing the words "Hi there,
`John`", and then "Done!".

Now let's use `st.echo()` to make that middle section of the code visible
in the app:

```python
import streamlit as st

def get_user_name():
    return 'John'

with st.echo():
    # Everything inside this block will be both printed to the screen
    # and executed.

    def get_punctuation():
        return '!!!'

    greeting = "Hi there, "
    value = get_user_name()
    punctuation = get_punctuation()

    st.write(greeting, value, punctuation)

# And now we're back to _not_ printing to the screen
foo = 'bar'
st.write('Done!')
```

It's _that_ simple!

Note: You can have multiple `st.echo()` blocks in the same file.
Use it as often as you wish!

################################################
Section 14.5 - header.md
################################################

st.header - st.header displays text in header formatting.

################################################
Section 14.6 - latex.md
################################################

st.latex - st.latex displays mathematical expressions formatted as LaTeX.

################################################
Section 14.7 - markdown.md
################################################

st.markdown - st.markdown displays string formatted as Markdown.

```python
import streamlit as st

md = st.text_area('Type in your markdown string (without outer quotes)',
                  "Happy Streamlit-ing! :balloon:")

st.code(f"""
import streamlit as st

st.markdown('''{md}''')
""")

st.markdown(md)
```

################################################
Section 14.8 - subheader.md
################################################

st.subheader - st.subheader displays text in subheader formatting.

################################################
Section 14.9 - text.md
################################################

st.text - st.text writes fixed-width and preformatted text.

################################################
Section 14.10 - title.md
################################################

st.title - st.title displays text in title formatting.

------------------------------------------------------------------------------------------------
CHAPTER 16: utilities.md
------------------------------------------------------------------------------------------------

################################################
Section 16.1 - context.md
################################################

st.context - st.context displays a read-only dict of cookies and headers

################################################
Section 16.2 - experimental-user.md
################################################

st.experimental_user - st.experimental_user returns information about the logged-in user of private apps on Streamlit Community Cloud.

IMPORTANT: This is an experimental feature. Experimental features and their APIs may change or be removed at any time. To learn more, click here.

### Examples

The ability to personalize apps for the user viewing the app is a great way to make your app more engaging.

It unlocks a plethora of use-cases for developers, some of which could include: showing additional controls for admins, visualizing a user's Streamlit history, a personalized stock ticker, a chatbot app, and much more. We're excited to see what you build with this feature!

Here's a code snippet that shows extra buttons for admins:

```python
# Show extra buttons for admin users.
ADMIN_USERS = {
    'person1@email.com',
    'person2@email.com',
    'person3@email.com'
}
if st.experimental_user.email in ADMIN_USERS:
    display_the_extra_admin_buttons()
display_the_interface_everyone_sees()
```

Show different content to users based on their email address:

```python
# Show different content based on the user's email address.
if st.experimental_user.email == 'jane@email.com':
    display_jane_content()
elif st.experimental_user.email == 'adam@foocorp.io':
    display_adam_content()
else:
    st.write("Please contact us to get access!")
```

Greet users with their name that's stored in a database:

```python
# Greet the user by their name.
if st.experimental_user.email:
    # Get the user's name from the database.
    name = get_name_from_db(st.experimental_user.email)
    st.write('Hello, %s!' % name)
```

################################################
Section 16.3 - help.md
################################################

st.help - st.help displays object's doc string, nicely formatted.

################################################
Section 16.4 - html.md
################################################

st.html - st.html renders arbitrary HTML strings to your app

------------------------------------------------------------------------------------------------
CHAPTER 17: widgets.md
------------------------------------------------------------------------------------------------

################################################
Section 17.1 - audio_input.md
################################################

st.audio_input - st.audio_input displays a widget to upload audio from a microphone

Function: st.audio_input (previously experimental)

################################################
Section 17.2 - button.md
################################################

st.button - st.button displays a button widget.
keywords: button

### Advanced functionality

Although a button is the simplest of input widgets, it's very common for buttons to be deeply tied to the use of `st.session_state`. Check out our advanced guide on Button behavior and examples.

### Featured videos

Check out our video on how to use one of Streamlit's core functions, the button!

Tutorial video available: VideoId=JSeQSnGovSE

In the video below, we'll take it a step further and learn how to combine a button, checkbox and radio button!

Tutorial video available: VideoId=EnXJBsCIl_A

################################################
Section 17.3 - camera_input.md
################################################

st.camera_input - st.camera_input displays a widget to upload images from a camera

To read the image file buffer as bytes, you can use `getvalue()` on the `UploadedFile` object.

```python
import streamlit as st

img_file_buffer = st.camera_input("Take a picture")

if img_file_buffer is not None:
    # To read image file buffer as bytes:
    bytes_data = img_file_buffer.getvalue()
    # Check the type of bytes_data:
    # Should output: 
    st.write(type(bytes_data))
```

IMPORTANT: `st.camera_input` returns an object of the `UploadedFile` class, which a subclass of BytesIO. Therefore it is a "file-like" object. This means you can pass it anywhere where a file is expected, similar to `st.file_uploader`.

## Image processing examples

You can use the output of `st.camera_input` for various downstream tasks, including image processing. Below, we demonstrate how to use the `st.camera_input` widget with popular image and data processing libraries such as Pillow, NumPy, OpenCV, TensorFlow, torchvision, and PyTorch.

While we provide examples for the most popular use-cases and libraries, you are welcome to adapt these examples to your own needs and favorite libraries.

### Pillow (PIL) and NumPy

Ensure you have installed Pillow and NumPy.

To read the image file buffer as a PIL Image and convert it to a NumPy array:

```python
import streamlit as st
from PIL import Image
import numpy as np

img_file_buffer = st.camera_input("Take a picture")

if img_file_buffer is not None:
    # To read image file buffer as a PIL Image:
    img = Image.open(img_file_buffer)

    # To convert PIL Image to numpy array:
    img_array = np.array(img)

    # Check the type of img_array:
    # Should output: 
    st.write(type(img_array))

    # Check the shape of img_array:
    # Should output shape: (height, width, channels)
    st.write(img_array.shape)
```

### OpenCV (cv2)

Ensure you have installed OpenCV and NumPy.

To read the image file buffer with OpenCV:

```python
import streamlit as st
import cv2
import numpy as np

img_file_buffer = st.camera_input("Take a picture")

if img_file_buffer is not None:
    # To read image file buffer with OpenCV:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # Check the type of cv2_img:
    # Should output: 
    st.write(type(cv2_img))

    # Check the shape of cv2_img:
    # Should output shape: (height, width, channels)
    st.write(cv2_img.shape)
```

### TensorFlow

Ensure you have installed TensorFlow.

To read the image file buffer as a 3 dimensional uint8 tensor with TensorFlow:

```python
import streamlit as st
import tensorflow as tf

img_file_buffer = st.camera_input("Take a picture")

if img_file_buffer is not None:
    # To read image file buffer as a 3D uint8 tensor with TensorFlow:
    bytes_data = img_file_buffer.getvalue()
    img_tensor = tf.io.decode_image(bytes_data, channels=3)

    # Check the type of img_tensor:
    # Should output: 
    st.write(type(img_tensor))

    # Check the shape of img_tensor:
    # Should output shape: (height, width, channels)
    st.write(img_tensor.shape)
```

### Torchvision

Ensure you have installed Torchvision (it is not bundled with PyTorch) and PyTorch.

To read the image file buffer as a 3 dimensional uint8 tensor with `torchvision.io`:

```python
import streamlit as st
import torch
import torchvision

img_file_buffer = st.camera_input("Take a picture")

if img_file_buffer is not None:
    # To read image file buffer as a 3D uint8 tensor with `torchvision.io`:
    bytes_data = img_file_buffer.getvalue()
    torch_img = torchvision.io.decode_image(
        torch.frombuffer(bytes_data, dtype=torch.uint8)
    )

    # Check the type of torch_img:
    # Should output: 
    st.write(type(torch_img))

    # Check the shape of torch_img:
    # Should output shape: torch.Size([channels, height, width])
    st.write(torch_img.shape)
```

### PyTorch

Ensure you have installed PyTorch and NumPy.

To read the image file buffer as a 3 dimensional uint8 tensor with PyTorch:

```python
import streamlit as st
import torch
import numpy as np

img_file_buffer = st.camera_input("Take a picture")

if img_file_buffer is not None:
    # To read image file buffer as a 3D uint8 tensor with PyTorch:
    bytes_data = img_file_buffer.getvalue()
    torch_img = torch.ops.image.decode_image(
        torch.from_numpy(np.frombuffer(bytes_data, np.uint8)), 3
    )

    # Check the type of torch_img:
    # Should output: 
    st.write(type(torch_img))

    # Check the shape of torch_img:
    # Should output shape: torch.Size([channels, height, width])
    st.write(torch_img.shape)
```

################################################
Section 17.4 - checkbox.md
################################################

st.checkbox - st.checkbox displays a checkbox widget.

### Featured videos

Check out our video on how to use one of Streamlit's core functions, the checkbox! ☑

Tutorial video available: VideoId=Jte0Reue7z8

In the video below, we'll take it a step further and learn how to combine a button, checkbox and radio button!

Tutorial video available: VideoId=EnXJBsCIl_A

################################################
Section 17.5 - color_picker.md
################################################

st.color_picker - st.color_picker displays a color picker widget.

################################################
Section 17.6 - date_input.md
################################################

st.date_input - st.date_input displays a date input widget.
keywords: calendar

################################################
Section 17.7 - download_button.md
################################################

st.download_button - st.download_button displays a download button widget.

################################################
Section 17.8 - feedback.md
################################################

st.feedback - Collect user feedback or ratings with st.feedback

################################################
Section 17.9 - file_uploader.md
################################################

st.file_uploader - st.file_uploader displays a file uploader widget.

################################################
Section 17.10 - link_button.md
################################################

st.link_button - st.multiselect displays a multiselect widget. The multiselect widget starts as empty.

################################################
Section 17.11 - number_input.md
################################################

st.number_input - st.number_input displays a numeric input widget.

################################################
Section 17.12 - page_link.md
################################################

st.page_link - st.page_link displays a link to another page in a multipage app or to an external page.

Note: Check out our tutorial to learn about building custom, dynamic menus with `st.page_link`.

################################################
Section 17.13 - pills.md
################################################

st.pills - st.pills displays a select widget where options display as pill buttons.

################################################
Section 17.14 - radio.md
################################################

st.radio - st.radio displays a radio button widget.

Widgets can customize how to hide their labels with the `label_visibility` parameter. If "hidden", the label doesn’t show but there is still empty space for it above the widget (equivalent to `label=""`). If "collapsed", both the label and the space are removed. Default is "visible". Radio buttons can also be disabled with the `disabled` parameter, and oriented horizontally with the `horizontal` parameter:

```python
import streamlit as st

# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False
    st.session_state.horizontal = False

col1, col2 = st.columns(2)

with col1:
    st.checkbox("Disable radio widget", key="disabled")
    st.checkbox("Orient radio options horizontally", key="horizontal")

with col2:
    st.radio(
        "Set label visibility 👇",
        ["visible", "hidden", "collapsed"],
        key="visibility",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        horizontal=st.session_state.horizontal,
    )
```

### Featured videos

Check out our video on how to use one of Streamlit's core functions, the radio button! 🔘

Tutorial video available: VideoId=CVHIMGVAzwA

In the video below, we'll take it a step further and learn how to combine a button, checkbox and radio button!

Tutorial video available: VideoId=EnXJBsCIl_A

################################################
Section 17.15 - segmented_control.md
################################################

st.segmented_control - st.segmented_control displays a select widget where options display in a segmented button.

################################################
Section 17.16 - selectbox.md
################################################

st.selectbox - st.selectbox displays a select widget.

Select widgets can customize how to hide their labels with the `label_visibility` parameter. If "hidden", the label doesn’t show but there is still empty space for it above the widget (equivalent to `label=""`). If "collapsed", both the label and the space are removed. Default is "visible". Select widgets can also be disabled with the `disabled` parameter:

```python
import streamlit as st

# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

col1, col2 = st.columns(2)

with col1:
    st.checkbox("Disable selectbox widget", key="disabled")
    st.radio(
        "Set selectbox label visibility 👉",
        key="visibility",
        options=["visible", "hidden", "collapsed"],
    )

with col2:
    option = st.selectbox(
        "How would you like to be contacted?",
        ("Email", "Home phone", "Mobile phone"),
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
    )
```

################################################
Section 17.17 - select_slider.md
################################################

st.select_slider - st.select_slider displays a slider widget to select items from a list.

### Featured videos

Check out our video on how to use one of Streamlit's core functions, the select slider! 🎈
Tutorial video available: VideoId=MTaL_1UCb2g

In the video below, we'll take it a step further and make a double-ended slider.
Tutorial video available: VideoId=sCvdt79asrE

################################################
Section 17.18 - slider.md
################################################

st.slider - st.slider displays a slider widget.

### Featured videos

Check out our video on how to use one of Streamlit's core functions, the slider!
Tutorial video available: VideoId=tzAdd-MuWPw

In the video below, we'll take it a step further and make a double-ended slider.
Tutorial video available: VideoId=sCvdt79asrE

################################################
Section 17.19 - text_area.md
################################################

st.text_area - st.text_area displays a multi-line text input widget.

################################################
Section 17.20 - text_input.md
################################################

st.text_input - st.text_input displays a single-line text input widget.

Text input widgets can customize how to hide their labels with the `label_visibility` parameter. If "hidden", the label doesn’t show but there is still empty space for it above the widget (equivalent to `label=""`). If "collapsed", both the label and the space are removed. Default is "visible". Text input widgets can also be disabled with the `disabled` parameter, and can display an optional placeholder text when the text input is empty using the `placeholder` parameter:

```python
import streamlit as st

# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

col1, col2 = st.columns(2)

with col1:
    st.checkbox("Disable text input widget", key="disabled")
    st.radio(
        "Set text input label visibility 👉",
        key="visibility",
        options=["visible", "hidden", "collapsed"],
    )
    st.text_input(
        "Placeholder for the other text input widget",
        "This is a placeholder",
        key="placeholder",
    )

with col2:
    text_input = st.text_input(
        "Enter some text 👇",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder=st.session_state.placeholder,
    )

    if text_input:
        st.write("You entered: ", text_input)
```

################################################
Section 17.21 - time_input.md
################################################

st.time_input - st.time_input displays a time input widget.

################################################
Section 17.22 - toggle.md
################################################

st.toggle - st.toggle displays a toggle widget.

------------------------------------------------------------------------------------------------
CHAPTER 18: write-magic.md
------------------------------------------------------------------------------------------------

################################################
Section 18.1 - magic.md
################################################

Magic - st.write writes arguments to the app.

### Featured video

Learn what the `st.write` and magic commands are and how to use them.

Tutorial video available: VideoId=wpDuY9I2fDg

################################################
Section 18.2 - write_stream.md
################################################

st.write_stream - st.write_stream writes arguments to the app using a typewriter effect.

Note: If your stream object is not compatible with `st.write_stream`, define a wrapper around your stream object to create a compatible generator function.

```python
for chunk in unsupported_stream:
    yield preprocess(chunk)
```

For an example, see how we use Replicate with Snowflake Arctic in this code.

