Understanding Streamlit's client-server architecture
Streamlit apps have a client-server structure. The Python backend of your app is the server. The frontend you view through a browser is the client. When you develop an app locally, your computer runs both the server and the client. If someone views your app across a local or global network, the server and client run on different machines. If you intend to share or deploy your app, it's important to understand this client-server structure to avoid common pitfalls.

Python backend (server)
When you execute the command streamlit run your_app.py, your computer uses Python to start up a Streamlit server. This server is the brains of your app and performs the computations for all users who view your app. Whether users view your app across a local network or the internet, the Streamlit server runs on the one machine where the app was initialized with streamlit run. The machine running your Streamlit server is also called a host.

Browser frontend (client)
When someone views your app through a browser, their device is a Streamlit client. When you view your app from the same computer where you are running or developing your app, then server and client are coincidentally running on the same machine. However, when users view your app across a local network or the internet, the client runs on a different machine from the server.

Server-client impact on app design
Keep in mind the following considerations when building your Streamlit app:

The computer running or hosting your Streamlit app is responsible for providing the compute and storage necessary to run your app for all users and must be sized appropriately to handle concurrent users.
Your app will not have access to a user's files, directories, or OS. Your app can only work with specific files a user has uploaded to your app through a widget like st.file_uploader.
If your app communicates with any peripheral devices (like cameras), you must use Streamlit commands or custom components that will access those devices through the user's browser and correctly communicate between the client (frontend) and server (backend).
If your app opens or uses any program or process outside of Python, they will run on the server. For example, you may want to use webrowser to open a browser for the user, but this will not work as expected when viewing your app over a network; it will open a browser on the Streamlit server, unseen by the user.


---


push_pin
Note
Documentation for the deprecated @st.cache decorator can be found in Optimize performance with st.cache.

Caching overview
Streamlit runs your script from top to bottom at every user interaction or code change. This execution model makes development super easy. But it comes with two major challenges:

Long-running functions run again and again, which slows down your app.
Objects get recreated again and again, which makes it hard to persist them across reruns or sessions.
But don't worry! Streamlit lets you tackle both issues with its built-in caching mechanism. Caching stores the results of slow function calls, so they only need to run once. This makes your app much faster and helps with persisting objects across reruns. Cached values are available to all users of your app. If you need to save results that should only be accessible within a session, use Session State instead.

Table of contents
expand_more
Minimal example
Basic usage
Advanced usage
Migrating from st.cache
Minimal example
To cache a function in Streamlit, you must decorate it with one of two decorators (st.cache_data or st.cache_resource):

@st.cache_data
def long_running_function(param1, param2):
    return …
In this example, decorating long_running_function with @st.cache_data tells Streamlit that whenever the function is called, it checks two things:

The values of the input parameters (in this case, param1 and param2).
The code inside the function.
If this is the first time Streamlit sees these parameter values and function code, it runs the function and stores the return value in a cache. The next time the function is called with the same parameters and code (e.g., when a user interacts with the app), Streamlit will skip executing the function altogether and return the cached value instead. During development, the cache updates automatically as the function code changes, ensuring that the latest changes are reflected in the cache.

As mentioned, there are two caching decorators:

st.cache_data is the recommended way to cache computations that return data: loading a DataFrame from CSV, transforming a NumPy array, querying an API, or any other function that returns a serializable data object (str, int, float, DataFrame, array, list, …). It creates a new copy of the data at each function call, making it safe against mutations and race conditions. The behavior of st.cache_data is what you want in most cases – so if you're unsure, start with st.cache_data and see if it works!
st.cache_resource is the recommended way to cache global resources like ML models or database connections – unserializable objects that you don't want to load multiple times. Using it, you can share these resources across all reruns and sessions of an app without copying or duplication. Note that any mutations to the cached return value directly mutate the object in the cache (more details below).
Streamlit's two caching decorators and their use cases. Use st.cache_data for anything you'd store in a database. Use st.cache_resource for anything you can't store in a database, like a connection to a database or a machine learning model.
Streamlit's two caching decorators and their use cases.

Basic usage
st.cache_data
st.cache_data is your go-to command for all functions that return data – whether DataFrames, NumPy arrays, str, int, float, or other serializable types. It's the right command for almost all use cases! Within each user session, an @st.cache_data-decorated function returns a copy of the cached return value (if the value is already cached).

Usage

Let's look at an example of using st.cache_data. Suppose your app loads the Uber ride-sharing dataset – a CSV file of 50 MB – from the internet into a DataFrame:

def load_data(url):
    df = pd.read_csv(url)  # 👈 Download the data
    return df

df = load_data("https://github.com/plotly/datasets/raw/master/uber-rides-data1.csv")
st.dataframe(df)

st.button("Rerun")
Running the load_data function takes 2 to 30 seconds, depending on your internet connection. (Tip: if you are on a slow connection, use this 5 MB dataset instead). Without caching, the download is rerun each time the app is loaded or with user interaction. Try it yourself by clicking the button we added! Not a great experience… 😕

Now let's add the @st.cache_data decorator on load_data:

@st.cache_data  # 👈 Add the caching decorator
def load_data(url):
    df = pd.read_csv(url)
    return df

df = load_data("https://github.com/plotly/datasets/raw/master/uber-rides-data1.csv")
st.dataframe(df)

st.button("Rerun")
Run the app again. You'll notice that the slow download only happens on the first run. Every subsequent rerun should be almost instant! 💨

Behavior

How does this work? Let's go through the behavior of st.cache_data step by step:

On the first run, Streamlit recognizes that it has never called the load_data function with the specified parameter value (the URL of the CSV file) So it runs the function and downloads the data.
Now our caching mechanism becomes active: the returned DataFrame is serialized (converted to bytes) via pickle and stored in the cache (together with the value of the url parameter).
On the next run, Streamlit checks the cache for an entry of load_data with the specific url. There is one! So it retrieves the cached object, deserializes it to a DataFrame, and returns it instead of re-running the function and downloading the data again.
This process of serializing and deserializing the cached object creates a copy of our original DataFrame. While this copying behavior may seem unnecessary, it's what we want when caching data objects since it effectively prevents mutation and concurrency issues. Read the section “Mutation and concurrency issues" below to understand this in more detail.

priority_high
Warning
st.cache_data implicitly uses the pickle module, which is known to be insecure. Anything your cached function returns is pickled and stored, then unpickled on retrieval. Ensure your cached functions return trusted values because it is possible to construct malicious pickle data that will execute arbitrary code during unpickling. Never load data that could have come from an untrusted source in an unsafe mode or that could have been tampered with. Only load data you trust.

Examples

DataFrame transformations

In the example above, we already showed how to cache loading a DataFrame. It can also be useful to cache DataFrame transformations such as df.filter, df.apply, or df.sort_values. Especially with large DataFrames, these operations can be slow.

@st.cache_data
def transform(df):
    df = df.filter(items=['one', 'three'])
    df = df.apply(np.sum, axis=0)
	return df
Array computations

Similarly, it can make sense to cache computations on NumPy arrays:

@st.cache_data
def add(arr1, arr2):
	return arr1 + arr2
Database queries

You usually make SQL queries to load data into your app when working with databases. Repeatedly running these queries can be slow, cost money, and degrade the performance of your database. We strongly recommend caching any database queries in your app. See also our guides on connecting Streamlit to different databases for in-depth examples.

connection = database.connect()

@st.cache_data
def query():
    return pd.read_sql_query("SELECT * from table", connection)
star
Tip
You should set a ttl (time to live) to get new results from your database. If you set st.cache_data(ttl=3600), Streamlit invalidates any cached values after 1 hour (3600 seconds) and runs the cached function again. See details in Controlling cache size and duration.

API calls

Similarly, it makes sense to cache API calls. Doing so also avoids rate limits.

@st.cache_data
def api_call():
    response = requests.get('https://jsonplaceholder.typicode.com/posts/1')
    return response.json()
Running ML models (inference)

Running complex machine learning models can use significant time and memory. To avoid rerunning the same computations over and over, use caching.

@st.cache_data
def run_model(inputs):
    return model(inputs)
st.cache_resource
st.cache_resource is the right command to cache “resources" that should be available globally across all users, sessions, and reruns. It has more limited use cases than st.cache_data, especially for caching database connections and ML models. Within each user session, an @st.cache_resource-decorated function returns the cached instance of the return value (if the value is already cached). Therefore, objects cached by st.cache_resource act like singletons and can mutate.

Usage
As an example for st.cache_resource, let's look at a typical machine learning app. As a first step, we need to load an ML model. We do this with Hugging Face's transformers library:

from transformers import pipeline
model = pipeline("sentiment-analysis")  # 👈 Load the model
If we put this code into a Streamlit app directly, the app will load the model at each rerun or user interaction. Repeatedly loading the model poses two problems:

Loading the model takes time and slows down the app.
Each session loads the model from scratch, which takes up a huge amount of memory.
Instead, it would make much more sense to load the model once and use that same object across all users and sessions. That's exactly the use case for st.cache_resource! Let's add it to our app and process some text the user entered:

from transformers import pipeline

@st.cache_resource  # 👈 Add the caching decorator
def load_model():
    return pipeline("sentiment-analysis")

model = load_model()

query = st.text_input("Your query", value="I love Streamlit! 🎈")
if query:
    result = model(query)[0]  # 👈 Classify the query text
    st.write(result)
If you run this app, you'll see that the app calls load_model only once – right when the app starts. Subsequent runs will reuse that same model stored in the cache, saving time and memory!

Behavior

Using st.cache_resource is very similar to using st.cache_data. But there are a few important differences in behavior:

st.cache_resource does not create a copy of the cached return value but instead stores the object itself in the cache. All mutations on the function's return value directly affect the object in the cache, so you must ensure that mutations from multiple sessions do not cause problems. In short, the return value must be thread-safe.

priority_high
Warning
Using st.cache_resource on objects that are not thread-safe might lead to crashes or corrupted data. Learn more below under Mutation and concurrency issues.

Not creating a copy means there's just one global instance of the cached return object, which saves memory, e.g. when using a large ML model. In computer science terms, we create a singleton.

Return values of functions do not need to be serializable. This behavior is great for types not serializable by nature, e.g., database connections, file handles, or threads. Caching these objects with st.cache_data is not possible.

Examples

Database connections

st.cache_resource is useful for connecting to databases. Usually, you're creating a connection object that you want to reuse globally for every query. Creating a new connection object at each run would be inefficient and might lead to connection errors. That's exactly what st.cache_resource can do, e.g., for a Postgres database:

@st.cache_resource
def init_connection():
    host = "hh-pgsql-public.ebi.ac.uk"
    database = "pfmegrnargs"
    user = "reader"
    password = "NWDMCE5xdipIjRrp"
    return psycopg2.connect(host=host, database=database, user=user, password=password)

conn = init_connection()
Of course, you can do the same for any other database. Have a look at our guides on how to connect Streamlit to databases for in-depth examples.

Loading ML models

Your app should always cache ML models, so they are not loaded into memory again for every new session. See the example above for how this works with 🤗 Hugging Face models. You can do the same thing for PyTorch, TensorFlow, etc. Here's an example for PyTorch:

@st.cache_resource
def load_model():
    model = torchvision.models.resnet50(weights=ResNet50_Weights.DEFAULT)
    model.eval()
    return model

model = load_model()
Deciding which caching decorator to use

The sections above showed many common examples for each caching decorator. But there are edge cases for which it's less trivial to decide which caching decorator to use. Eventually, it all comes down to the difference between “data" and “resource":

Data are serializable objects (objects that can be converted to bytes via pickle) that you could easily save to disk. Imagine all the types you would usually store in a database or on a file system – basic types like str, int, and float, but also arrays, DataFrames, images, or combinations of these types (lists, tuples, dicts, and so on).
Resources are unserializable objects that you usually would not save to disk or a database. They are often more complex, non-permanent objects like database connections, ML models, file handles, threads, etc.
From the types listed above, it should be obvious that most objects in Python are “data." That's also why st.cache_data is the correct command for almost all use cases. st.cache_resource is a more exotic command that you should only use in specific situations.

Or if you're lazy and don't want to think too much, look up your use case or return type in the table below 😉:

Use case	Typical return types	Caching decorator
Reading a CSV file with pd.read_csv	pandas.DataFrame	st.cache_data
Reading a text file	str, list of str	st.cache_data
Transforming pandas dataframes	pandas.DataFrame, pandas.Series	st.cache_data
Computing with numpy arrays	numpy.ndarray	st.cache_data
Simple computations with basic types	str, int, float, …	st.cache_data
Querying a database	pandas.DataFrame	st.cache_data
Querying an API	pandas.DataFrame, str, dict	st.cache_data
Running an ML model (inference)	pandas.DataFrame, str, int, dict, list	st.cache_data
Creating or processing images	PIL.Image.Image, numpy.ndarray	st.cache_data
Creating charts	matplotlib.figure.Figure, plotly.graph_objects.Figure, altair.Chart	st.cache_data (but some libraries require st.cache_resource, since the chart object is not serializable – make sure not to mutate the chart after creation!)
Loading ML models	transformers.Pipeline, torch.nn.Module, tensorflow.keras.Model	st.cache_resource
Initializing database connections	pyodbc.Connection, sqlalchemy.engine.base.Engine, psycopg2.connection, mysql.connector.MySQLConnection, sqlite3.Connection	st.cache_resource
Opening persistent file handles	_io.TextIOWrapper	st.cache_resource
Opening persistent threads	threading.thread	st.cache_resource
Advanced usage
Controlling cache size and duration
If your app runs for a long time and constantly caches functions, you might run into two problems:

The app runs out of memory because the cache is too large.
Objects in the cache become stale, e.g. because you cached old data from a database.
You can combat these problems with the ttl and max_entries parameters, which are available for both caching decorators.

The ttl (time-to-live) parameter

ttl sets a time to live on a cached function. If that time is up and you call the function again, the app will discard any old, cached values, and the function will be rerun. The newly computed value will then be stored in the cache. This behavior is useful for preventing stale data (problem 2) and the cache from growing too large (problem 1). Especially when pulling data from a database or API, you should always set a ttl so you are not using old data. Here's an example:

@st.cache_data(ttl=3600)  # 👈 Cache data for 1 hour (=3600 seconds)
def get_api_data():
    data = api.get(...)
    return data
star
Tip
You can also set ttl values using timedelta, e.g., ttl=datetime.timedelta(hours=1).

The max_entries parameter

max_entries sets the maximum number of entries in the cache. An upper bound on the number of cache entries is useful for limiting memory (problem 1), especially when caching large objects. The oldest entry will be removed when a new entry is added to a full cache. Here's an example:

@st.cache_data(max_entries=1000)  # 👈 Maximum 1000 entries in the cache
def get_large_array(seed):
    np.random.seed(seed)
    arr = np.random.rand(100000)
    return arr
Customizing the spinner
By default, Streamlit shows a small loading spinner in the app when a cached function is running. You can modify it easily with the show_spinner parameter, which is available for both caching decorators:

@st.cache_data(show_spinner=False)  # 👈 Disable the spinner
def get_api_data():
    data = api.get(...)
    return data

@st.cache_data(show_spinner="Fetching data from API...")  # 👈 Use custom text for spinner
def get_api_data():
    data = api.get(...)
    return data
Excluding input parameters
In a cached function, all input parameters must be hashable. Let's quickly explain why and what it means. When the function is called, Streamlit looks at its parameter values to determine if it was cached before. Therefore, it needs a reliable way to compare the parameter values across function calls. Trivial for a string or int – but complex for arbitrary objects! Streamlit uses hashing to solve that. It converts the parameter to a stable key and stores that key. At the next function call, it hashes the parameter again and compares it with the stored hash key.

Unfortunately, not all parameters are hashable! E.g., you might pass an unhashable database connection or ML model to your cached function. In this case, you can exclude input parameters from caching. Simply prepend the parameter name with an underscore (e.g., _param1), and it will not be used for caching. Even if it changes, Streamlit will return a cached result if all the other parameters match up.

Here's an example:

@st.cache_data
def fetch_data(_db_connection, num_rows):  # 👈 Don't hash _db_connection
    data = _db_connection.fetch(num_rows)
    return data

connection = init_connection()
fetch_data(connection, 10)
But what if you want to cache a function that takes an unhashable parameter? For example, you might want to cache a function that takes an ML model as input and returns the layer names of that model. Since the model is the only input parameter, you cannot exclude it from caching. In this case you can use the hash_funcs parameter to specify a custom hashing function for the model.

The hash_funcs parameter
As described above, Streamlit's caching decorators hash the input parameters and cached function's signature to determine whether the function has been run before and has a return value stored ("cache hit") or needs to be run ("cache miss"). Input parameters that are not hashable by Streamlit's hashing implementation can be ignored by prepending an underscore to their name. But there two rare cases where this is undesirable. i.e. where you want to hash the parameter that Streamlit is unable to hash:

When Streamlit's hashing mechanism fails to hash a parameter, resulting in a UnhashableParamError being raised.
When you want to override Streamlit's default hashing mechanism for a parameter.
Let's discuss each of these cases in turn with examples.

Example 1: Hashing a custom class
Streamlit does not know how to hash custom classes. If you pass a custom class to a cached function, Streamlit will raise a UnhashableParamError. For example, let's define a custom class MyCustomClass that accepts an initial integer score. Let's also define a cached function multiply_score that multiplies the score by a multiplier:

import streamlit as st

class MyCustomClass:
    def __init__(self, initial_score: int):
        self.my_score = initial_score

@st.cache_data
def multiply_score(obj: MyCustomClass, multiplier: int) -> int:
    return obj.my_score * multiplier

initial_score = st.number_input("Enter initial score", value=15)

score = MyCustomClass(initial_score)
multiplier = 2

st.write(multiply_score(score, multiplier))
If you run this app, you'll see that Streamlit raises a UnhashableParamError since it does not know how to hash MyCustomClass:

UnhashableParamError: Cannot hash argument 'obj' (of type __main__.MyCustomClass) in 'multiply_score'.
To fix this, we can use the hash_funcs parameter to tell Streamlit how to hash MyCustomClass. We do this by passing a dictionary to hash_funcs that maps the name of the parameter to a hash function. The choice of hash function is up to the developer. In this case, let's define a custom hash function hash_func that takes the custom class as input and returns the score. We want the score to be the unique identifier of the object, so we can use it to deterministically hash the object:

import streamlit as st

class MyCustomClass:
    def __init__(self, initial_score: int):
        self.my_score = initial_score

def hash_func(obj: MyCustomClass) -> int:
    return obj.my_score  # or any other value that uniquely identifies the object

@st.cache_data(hash_funcs={MyCustomClass: hash_func})
def multiply_score(obj: MyCustomClass, multiplier: int) -> int:
    return obj.my_score * multiplier

initial_score = st.number_input("Enter initial score", value=15)

score = MyCustomClass(initial_score)
multiplier = 2

st.write(multiply_score(score, multiplier))
Now if you run the app, you'll see that Streamlit no longer raises a UnhashableParamError and the app runs as expected.

Let's now consider the case where multiply_score is an attribute of MyCustomClass and we want to hash the entire object:

import streamlit as st

class MyCustomClass:
    def __init__(self, initial_score: int):
        self.my_score = initial_score

    @st.cache_data
    def multiply_score(self, multiplier: int) -> int:
        return self.my_score * multiplier

initial_score = st.number_input("Enter initial score", value=15)

score = MyCustomClass(initial_score)
multiplier = 2

st.write(score.multiply_score(multiplier))
If you run this app, you'll see that Streamlit raises a UnhashableParamError since it cannot hash the argument 'self' (of type __main__.MyCustomClass) in 'multiply_score'. A simple fix here could be to use Python's hash() function to hash the object:

import streamlit as st

class MyCustomClass:
    def __init__(self, initial_score: int):
        self.my_score = initial_score

    @st.cache_data(hash_funcs={"__main__.MyCustomClass": lambda x: hash(x.my_score)})
    def multiply_score(self, multiplier: int) -> int:
        return self.my_score * multiplier

initial_score = st.number_input("Enter initial score", value=15)

score = MyCustomClass(initial_score)
multiplier = 2

st.write(score.multiply_score(multiplier))
Above, the hash function is defined as lambda x: hash(x.my_score). This creates a hash based on the my_score attribute of the MyCustomClass instance. As long as my_score remains the same, the hash remains the same. Thus, the result of multiply_score can be retrieved from the cache without recomputation.

As an astute Pythonista, you may have been tempted to use Python's id() function to hash the object like so:

import streamlit as st

class MyCustomClass:
    def __init__(self, initial_score: int):
        self.my_score = initial_score

    @st.cache_data(hash_funcs={"__main__.MyCustomClass": id})
    def multiply_score(self, multiplier: int) -> int:
        return self.my_score * multiplier

initial_score = st.number_input("Enter initial score", value=15)

score = MyCustomClass(initial_score)
multiplier = 2

st.write(score.multiply_score(multiplier))
If you run the app, you'll notice that Streamlit recomputes multiply_score each time even if my_score hasn't changed! Puzzled? In Python, id() returns the identity of an object, which is unique and constant for the object during its lifetime. This means that even if the my_score value is the same between two instances of MyCustomClass, id() will return different values for these two instances, leading to different hash values. As a result, Streamlit considers these two different instances as needing separate cached values, thus it recomputes the multiply_score each time even if my_score hasn't changed.

This is why we discourage using it as hash func, and instead encourage functions that return deterministic, true hash values. That said, if you know what you're doing, you can use id() as a hash function. Just be aware of the consequences. For example, id is often the correct hash func when you're passing the result of an @st.cache_resource function as the input param to another cached function. There's a whole class of object types that aren’t otherwise hashable.

Example 2: Hashing a Pydantic model
Let's consider another example where we want to hash a Pydantic model:

import streamlit as st
from pydantic import BaseModel

class Person(BaseModel):
    name: str

@st.cache_data
def identity(person: Person):
    return person

person = identity(Person(name="Lee"))
st.write(f"The person is {person.name}")
Above, we define a custom class Person using Pydantic's BaseModel with a single attribute name. We also define an identity function which accepts an instance of Person as an arg and returns it without modification. This function is intended to cache the result, therefore, if called multiple times with the same Person instance, it won't recompute but return the cached instance.

If you run the app, however, you'll run into a UnhashableParamError: Cannot hash argument 'person' (of type __main__.Person) in 'identity'. error. This is because Streamlit does not know how to hash the Person class. To fix this, we can use the hash_funcs kwarg to tell Streamlit how to hash Person.

In the version below, we define a custom hash function hash_func that takes the Person instance as input and returns the name attribute. We want the name to be the unique identifier of the object, so we can use it to deterministically hash the object:

import streamlit as st
from pydantic import BaseModel

class Person(BaseModel):
    name: str

@st.cache_data(hash_funcs={Person: lambda p: p.name})
def identity(person: Person):
    return person

person = identity(Person(name="Lee"))
st.write(f"The person is {person.name}")
Example 3: Hashing a ML model
There may be cases where you want to pass your favorite machine learning model to a cached function. For example, let's say you want to pass a TensorFlow model to a cached function, based on what model the user selects in the app. You might try something like this:

import streamlit as st
import tensorflow as tf

@st.cache_resource
def load_base_model(option):
    if option == 1:
        return tf.keras.applications.ResNet50(include_top=False, weights="imagenet")
    else:
        return tf.keras.applications.MobileNetV2(include_top=False, weights="imagenet")

@st.cache_resource
def load_layers(base_model):
    return [layer.name for layer in base_model.layers]

option = st.radio("Model 1 or 2", [1, 2])

base_model = load_base_model(option)

layers = load_layers(base_model)

st.write(layers)
In the above app, the user can select one of two models. Based on the selection, the app loads the corresponding model and passes it to load_layers. This function then returns the names of the layers in the model. If you run the app, you'll see that Streamlit raises a UnhashableParamError since it cannot hash the argument 'base_model' (of type keras.engine.functional.Functional) in 'load_layers'.

If you disable hashing for base_model by prepending an underscore to its name, you'll observe that regardless of which base model is chosen, the layers displayed are same. This subtle bug is due to the fact that the load_layers function is not re-run when the base model changes. This is because Streamlit does not hash the base_model argument, so it does not know that the function needs to be re-run when the base model changes.

To fix this, we can use the hash_funcs kwarg to tell Streamlit how to hash the base_model argument. In the version below, we define a custom hash function hash_func: Functional: lambda x: x.name. Our choice of hash func is informed by our knowledge that the name attribute of a Functional object or model uniquely identifies it. As long as the name attribute remains the same, the hash remains the same. Thus, the result of load_layers can be retrieved from the cache without recomputation.

import streamlit as st
import tensorflow as tf
from keras.engine.functional import Functional

@st.cache_resource
def load_base_model(option):
    if option == 1:
        return tf.keras.applications.ResNet50(include_top=False, weights="imagenet")
    else:
        return tf.keras.applications.MobileNetV2(include_top=False, weights="imagenet")

@st.cache_resource(hash_funcs={Functional: lambda x: x.name})
def load_layers(base_model):
    return [layer.name for layer in base_model.layers]

option = st.radio("Model 1 or 2", [1, 2])

base_model = load_base_model(option)

layers = load_layers(base_model)

st.write(layers)
In the above case, we could also have used hash_funcs={Functional: id} as the hash function. This is because id is often the correct hash func when you're passing the result of an @st.cache_resource function as the input param to another cached function.

Example 4: Overriding Streamlit's default hashing mechanism
Let's consider another example where we want to override Streamlit's default hashing mechanism for a pytz-localized datetime object:

from datetime import datetime
import pytz
import streamlit as st

tz = pytz.timezone("Europe/Berlin")

@st.cache_data
def load_data(dt):
    return dt

now = datetime.now()
st.text(load_data(dt=now))

now_tz = tz.localize(datetime.now())
st.text(load_data(dt=now_tz))
It may be surprising to see that although now and now_tz are of the same <class 'datetime.datetime'> type, Streamlit does not how to hash now_tz and raises a UnhashableParamError. In this case, we can override Streamlit's default hashing mechanism for datetime objects by passing a custom hash function to the hash_funcs kwarg:

from datetime import datetime

import pytz
import streamlit as st

tz = pytz.timezone("Europe/Berlin")

@st.cache_data(hash_funcs={datetime: lambda x: x.strftime("%a %d %b %Y, %I:%M%p")})
def load_data(dt):
    return dt

now = datetime.now()
st.text(load_data(dt=now))

now_tz = tz.localize(datetime.now())
st.text(load_data(dt=now_tz))
Let's now consider a case where we want to override Streamlit's default hashing mechanism for NumPy arrays. While Streamlit natively hashes Pandas and NumPy objects, there may be cases where you want to override Streamlit's default hashing mechanism for these objects.

For example, let's say we create a cache-decorated show_data function that accepts a NumPy array and returns it without modification. In the bellow app, data = df["str"].unique() (which is a NumPy array) is passed to the show_data function.

import time
import numpy as np
import pandas as pd
import streamlit as st

@st.cache_data
def get_data():
    df = pd.DataFrame({"num": [112, 112, 2, 3], "str": ["be", "a", "be", "c"]})
    return df

@st.cache_data
def show_data(data):
    time.sleep(2)  # This makes the function take 2s to run
    return data

df = get_data()
data = df["str"].unique()

st.dataframe(show_data(data))
st.button("Re-run")
Since data is always the same, we expect the show_data function to return the cached value. However, if you run the app, and click the Re-run button, you'll notice that the show_data function is re-run each time. We can assume this behavior is a consequence of Streamlit's default hashing mechanism for NumPy arrays.

To work around this, let's define a custom hash function hash_func that takes a NumPy array as input and returns a string representation of the array:

import time
import numpy as np
import pandas as pd
import streamlit as st

@st.cache_data
def get_data():
    df = pd.DataFrame({"num": [112, 112, 2, 3], "str": ["be", "a", "be", "c"]})
    return df

@st.cache_data(hash_funcs={np.ndarray: str})
def show_data(data):
    time.sleep(2)  # This makes the function take 2s to run
    return data

df = get_data()
data = df["str"].unique()

st.dataframe(show_data(data))
st.button("Re-run")
Now if you run the app, and click the Re-run button, you'll notice that the show_data function is no longer re-run each time. It's important to note here that our choice of hash function was very naive and not necessarily the best choice. For example, if the NumPy array is large, converting it to a string representation may be expensive. In such cases, it is up to you as the developer to define what a good hash function is for your use case.

Static elements
Since version 1.16.0, cached functions can contain Streamlit commands! For example, you can do this:

@st.cache_data
def get_api_data():
    data = api.get(...)
    st.success("Fetched data from API!")  # 👈 Show a success message
    return data
As we know, Streamlit only runs this function if it hasn't been cached before. On this first run, the st.success message will appear in the app. But what happens on subsequent runs? It still shows up! Streamlit realizes that there is an st. command inside the cached function, saves it during the first run, and replays it on subsequent runs. Replaying static elements works for both caching decorators.

You can also use this functionality to cache entire parts of your UI:

@st.cache_data
def show_data():
    st.header("Data analysis")
    data = api.get(...)
    st.success("Fetched data from API!")
    st.write("Here is a plot of the data:")
    st.line_chart(data)
    st.write("And here is the raw data:")
    st.dataframe(data)
Input widgets
You can also use interactive input widgets like st.slider or st.text_input in cached functions. Widget replay is an experimental feature at the moment. To enable it, you need to set the experimental_allow_widgets parameter:

@st.cache_data(experimental_allow_widgets=True)  # 👈 Set the parameter
def get_data():
    num_rows = st.slider("Number of rows to get")  # 👈 Add a slider
    data = api.get(..., num_rows)
    return data
Streamlit treats the slider like an additional input parameter to the cached function. If you change the slider position, Streamlit will see if it has already cached the function for this slider value. If yes, it will return the cached value. If not, it will rerun the function using the new slider value.

Using widgets in cached functions is extremely powerful because it lets you cache entire parts of your app. But it can be dangerous! Since Streamlit treats the widget value as an additional input parameter, it can easily lead to excessive memory usage. Imagine your cached function has five sliders and returns a 100 MB DataFrame. Then we'll add 100 MB to the cache for every permutation of these five slider values – even if the sliders do not influence the returned data! These additions can make your cache explode very quickly. Please be aware of this limitation if you use widgets in cached functions. We recommend using this feature only for isolated parts of your UI where the widgets directly influence the cached return value.

priority_high
Warning
Support for widgets in cached functions is experimental. We may change or remove it anytime without warning. Please use it with care!

push_pin
Note
Two widgets are currently not supported in cached functions: st.file_uploader and st.camera_input. We may support them in the future. Feel free to open a GitHub issue if you need them!

Dealing with large data
As we explained, you should cache data objects with st.cache_data. But this can be slow for extremely large data, e.g., DataFrames or arrays with >100 million rows. That's because of the copying behavior of st.cache_data: on the first run, it serializes the return value to bytes and deserializes it on subsequent runs. Both operations take time.

If you're dealing with extremely large data, it can make sense to use st.cache_resource instead. It does not create a copy of the return value via serialization/deserialization and is almost instant. But watch out: any mutation to the function's return value (such as dropping a column from a DataFrame or setting a value in an array) directly manipulates the object in the cache. You must ensure this doesn't corrupt your data or lead to crashes. See the section on Mutation and concurrency issues below.

When benchmarking st.cache_data on pandas DataFrames with four columns, we found that it becomes slow when going beyond 100 million rows. The table shows runtimes for both caching decorators at different numbers of rows (all with four columns):

10M rows	50M rows	100M rows	200M rows
st.cache_data	First run*	0.4 s	3 s	14 s	28 s
Subsequent runs	0.2 s	1 s	2 s	7 s
st.cache_resource	First run*	0.01 s	0.1 s	0.2 s	1 s
Subsequent runs	0 s	0 s	0 s	0 s
*For the first run, the table only shows the overhead time of using the caching decorator. It does not include the runtime of the cached function itself.
Mutation and concurrency issues
In the sections above, we talked a lot about issues when mutating return objects of cached functions. This topic is complicated! But it's central to understanding the behavior differences between st.cache_data and st.cache_resource. So let's dive in a bit deeper.

First, we should clearly define what we mean by mutations and concurrency:

By mutations, we mean any changes made to a cached function's return value after that function has been called. I.e. something like this:

@st.cache_data
def create_list():
    l = [1, 2, 3]

l = create_list()  # 👈 Call the function
l[0] = 2  # 👈 Mutate its return value
By concurrency, we mean that multiple sessions can cause these mutations at the same time. Streamlit is a web framework that needs to handle many users and sessions connecting to an app. If two people view an app at the same time, they will both cause the Python script to rerun, which may manipulate cached return objects at the same time – concurrently.

Mutating cached return objects can be dangerous. It can lead to exceptions in your app and even corrupt your data (which can be worse than a crashed app!). Below, we'll first explain the copying behavior of st.cache_data and show how it can avoid mutation issues. Then, we'll show how concurrent mutations can lead to data corruption and how to prevent it.

Copying behavior
st.cache_data creates a copy of the cached return value each time the function is called. This avoids most mutations and concurrency issues. To understand it in detail, let's go back to the Uber ridesharing example from the section on st.cache_data above. We are making two modifications to it:

We are using st.cache_resource instead of st.cache_data. st.cache_resource does not create a copy of the cached object, so we can see what happens without the copying behavior.
After loading the data, we manipulate the returned DataFrame (in place!) by dropping the column "Lat".
Here's the code:

@st.cache_resource   # 👈 Turn off copying behavior
def load_data(url):
    df = pd.read_csv(url)
    return df

df = load_data("https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data1.csv")
st.dataframe(df)

df.drop(columns=['Lat'], inplace=True)  # 👈 Mutate the dataframe inplace

st.button("Rerun")
Let's run it and see what happens! The first run should work fine. But in the second run, you see an exception: KeyError: "['Lat'] not found in axis". Why is that happening? Let's go step by step:

On the first run, Streamlit runs load_data and stores the resulting DataFrame in the cache. Since we're using st.cache_resource, it does not create a copy but stores the original DataFrame.
Then we drop the column "Lat" from the DataFrame. Note that this is dropping the column from the original DataFrame stored in the cache. We are manipulating it!
On the second run, Streamlit returns that exact same manipulated DataFrame from the cache. It does not have the column "Lat" anymore! So our call to df.drop results in an exception. Pandas cannot drop a column that doesn't exist.
The copying behavior of st.cache_data prevents this kind of mutation error. Mutations can only affect a specific copy and not the underlying object in the cache. The next rerun will get its own, unmutated copy of the DataFrame. You can try it yourself, just replace st.cache_resource with st.cache_data above, and you'll see that everything works.

Because of this copying behavior, st.cache_data is the recommended way to cache data transforms and computations – anything that returns a serializable object.

Concurrency issues
Now let's look at what can happen when multiple users concurrently mutate an object in the cache. Let's say you have a function that returns a list. Again, we are using st.cache_resource to cache it so that we are not creating a copy:

@st.cache_resource
def create_list():
    l = [1, 2, 3]
    return l

l = create_list()
first_list_value = l[0]
l[0] = first_list_value + 1

st.write("l[0] is:", l[0])
Let's say user A runs the app. They will see the following output:

l[0] is: 2
Let's say another user, B, visits the app right after. In contrast to user A, they will see the following output:

l[0] is: 3
Now, user A reruns the app immediately after user B. They will see the following output:

l[0] is: 4
What is happening here? Why are all outputs different?

When user A visits the app, create_list() is called, and the list [1, 2, 3] is stored in the cache. This list is then returned to user A. The first value of the list, 1, is assigned to first_list_value , and l[0] is changed to 2.
When user B visits the app, create_list() returns the mutated list from the cache: [2, 2, 3]. The first value of the list, 2, is assigned to first_list_value and l[0] is changed to 3.
When user A reruns the app, create_list() returns the mutated list again: [3, 2, 3]. The first value of the list, 3, is assigned to first_list_value, and l[0] is changed to 4.
If you think about it, this makes sense. Users A and B use the same list object (the one stored in the cache). And since the list object is mutated, user A's change to the list object is also reflected in user B's app.

This is why you must be careful about mutating objects cached with st.cache_resource, especially when multiple users access the app concurrently. If we had used st.cache_data instead of st.cache_resource, the app would have copied the list object for each user, and the above example would have worked as expected – users A and B would have both seen:

l[0] is: 2
push_pin
Note
This toy example might seem benign. But data corruption can be extremely dangerous! Imagine we had worked with the financial records of a large bank here. You surely don't want to wake up with less money on your account just because someone used the wrong caching decorator 😉

Migrating from st.cache
We introduced the caching commands described above in Streamlit 1.18.0. Before that, we had one catch-all command st.cache. Using it was often confusing, resulted in weird exceptions, and was slow. That's why we replaced st.cache with the new commands in 1.18.0 (read more in this blog post). The new commands provide a more intuitive and efficient way to cache your data and resources and are intended to replace st.cache in all new development.

If your app is still using st.cache, don't despair! Here are a few notes on migrating:

Streamlit will show a deprecation warning if your app uses st.cache.
We will not remove st.cache soon, so you don't need to worry about your 2-year-old app breaking. But we encourage you to try the new commands going forward – they will be way less annoying!
Switching code to the new commands should be easy in most cases. To decide whether to use st.cache_data or st.cache_resource, read Deciding which caching decorator to use. Streamlit will also recognize common use cases and show hints right in the deprecation warnings.
Most parameters from st.cache are also present in the new commands, with a few exceptions:
allow_output_mutation does not exist anymore. You can safely delete it. Just make sure you use the right caching command for your use case.
suppress_st_warning does not exist anymore. You can safely delete it. Cached functions can now contain Streamlit commands and will replay them. If you want to use widgets inside cached functions, set experimental_allow_widgets=True. See Input widgets for an example.
If you have any questions or issues during the migration process, please contact us on the forum, and we will be happy to assist you. 🎈



---


Add statefulness to apps
What is State?
We define access to a Streamlit app in a browser tab as a session. For each browser tab that connects to the Streamlit server, a new session is created. Streamlit reruns your script from top to bottom every time you interact with your app. Each reruns takes place in a blank slate: no variables are shared between runs.

Session State is a way to share variables between reruns, for each user session. In addition to the ability to store and persist state, Streamlit also exposes the ability to manipulate state using Callbacks. Session state also persists across pages inside a multipage app.

In this guide, we will illustrate the usage of Session State and Callbacks as we build a stateful Counter app.

For details on the Session State and Callbacks API, please refer to our Session State API Reference Guide.

Also, check out this Session State basics tutorial video by Streamlit Developer Advocate Dr. Marisa Smith to get started:


Build a Counter
Let's call our script counter.py. It initializes a count variable and has a button to increment the value stored in the count variable:

import streamlit as st

st.title('Counter Example')
count = 0

increment = st.button('Increment')
if increment:
    count += 1

st.write('Count = ', count)
No matter how many times we press the Increment button in the above app, the count remains at 1. Let's understand why:

Each time we press the Increment button, Streamlit reruns counter.py from top to bottom, and with every run, count gets initialized to 0 .
Pressing Increment subsequently adds 1 to 0, thus count=1 no matter how many times we press Increment.
As we'll see later, we can avoid this issue by storing count as a Session State variable. By doing so, we're indicating to Streamlit that it should maintain the value stored inside a Session State variable across app reruns.

Let's learn more about the API to use Session State.

Initialization
The Session State API follows a field-based API, which is very similar to Python dictionaries:

import streamlit as st

# Check if 'key' already exists in session_state
# If not, then initialize it
if 'key' not in st.session_state:
    st.session_state['key'] = 'value'

# Session State also supports the attribute based syntax
if 'key' not in st.session_state:
    st.session_state.key = 'value'
Reads and updates
Read the value of an item in Session State by passing the item to st.write :

import streamlit as st

if 'key' not in st.session_state:
    st.session_state['key'] = 'value'

# Reads
st.write(st.session_state.key)

# Outputs: value
Update an item in Session State by assigning it a value:

import streamlit as st

if 'key' not in st.session_state:
    st.session_state['key'] = 'value'

# Updates
st.session_state.key = 'value2'     # Attribute API
st.session_state['key'] = 'value2'  # Dictionary like API
Streamlit throws an exception if an uninitialized variable is accessed:

import streamlit as st

st.write(st.session_state['value'])

# Throws an exception!
state-uninitialized-exception
Let's now take a look at a few examples that illustrate how to add Session State to our Counter app.

Example 1: Add Session State
Now that we've got a hang of the Session State API, let's update our Counter app to use Session State:

import streamlit as st

st.title('Counter Example')
if 'count' not in st.session_state:
    st.session_state.count = 0

increment = st.button('Increment')
if increment:
    st.session_state.count += 1

st.write('Count = ', st.session_state.count)
As you can see in the above example, pressing the Increment button updates the count each time.

Example 2: Session State and Callbacks
Now that we've built a basic Counter app using Session State, let's move on to something a little more complex. The next example uses Callbacks with Session State.

Callbacks: A callback is a Python function which gets called when an input widget changes. Callbacks can be used with widgets using the parameters on_change (or on_click), args, and kwargs. The full Callbacks API can be found in our Session State API Reference Guide.

import streamlit as st

st.title('Counter Example using Callbacks')
if 'count' not in st.session_state:
    st.session_state.count = 0

def increment_counter():
    st.session_state.count += 1

st.button('Increment', on_click=increment_counter)

st.write('Count = ', st.session_state.count)
Now, pressing the Increment button updates the count each time by calling the increment_counter() function.

Example 3: Use args and kwargs in Callbacks
Callbacks also support passing arguments using the args parameter in a widget:

import streamlit as st

st.title('Counter Example using Callbacks with args')
if 'count' not in st.session_state:
    st.session_state.count = 0

increment_value = st.number_input('Enter a value', value=0, step=1)

def increment_counter(increment_value):
    st.session_state.count += increment_value

increment = st.button('Increment', on_click=increment_counter,
    args=(increment_value, ))

st.write('Count = ', st.session_state.count)
Additionally, we can also use the kwargs parameter in a widget to pass named arguments to the callback function as shown below:

import streamlit as st

st.title('Counter Example using Callbacks with kwargs')
if 'count' not in st.session_state:
    st.session_state.count = 0

def increment_counter(increment_value=0):
    st.session_state.count += increment_value

def decrement_counter(decrement_value=0):
    st.session_state.count -= decrement_value

st.button('Increment', on_click=increment_counter,
	kwargs=dict(increment_value=5))

st.button('Decrement', on_click=decrement_counter,
	kwargs=dict(decrement_value=1))

st.write('Count = ', st.session_state.count)
Example 4: Forms and Callbacks
Say we now want to not only increment the count, but also store when it was last updated. We illustrate doing this using Callbacks and st.form:

import streamlit as st
import datetime

st.title('Counter Example')
if 'count' not in st.session_state:
    st.session_state.count = 0
    st.session_state.last_updated = datetime.time(0,0)

def update_counter():
    st.session_state.count += st.session_state.increment_value
    st.session_state.last_updated = st.session_state.update_time

with st.form(key='my_form'):
    st.time_input(label='Enter the time', value=datetime.datetime.now().time(), key='update_time')
    st.number_input('Enter a value', value=0, step=1, key='increment_value')
    submit = st.form_submit_button(label='Update', on_click=update_counter)

st.write('Current Count = ', st.session_state.count)
st.write('Last Updated = ', st.session_state.last_updated)
Advanced concepts
Session State and Widget State association
Session State provides the functionality to store variables across reruns. Widget state (i.e. the value of a widget) is also stored in a session.

For simplicity, we have unified this information in one place. i.e. the Session State. This convenience feature makes it super easy to read or write to the widget's state anywhere in the app's code. Session State variables mirror the widget value using the key argument.

We illustrate this with the following example. Let's say we have an app with a slider to represent temperature in Celsius. We can set and get the value of the temperature widget by using the Session State API, as follows:

import streamlit as st

if "celsius" not in st.session_state:
    # set the initial default value of the slider widget
    st.session_state.celsius = 50.0

st.slider(
    "Temperature in Celsius",
    min_value=-100.0,
    max_value=100.0,
    key="celsius"
)

# This will get the value of the slider widget
st.write(st.session_state.celsius)
There is a limitation to setting widget values using the Session State API.

priority_high
Important
Streamlit does not allow setting widget values via the Session State API for st.button and st.file_uploader.

The following example will raise a StreamlitAPIException on trying to set the state of st.button via the Session State API:

import streamlit as st

if 'my_button' not in st.session_state:
    st.session_state.my_button = True
    # Streamlit will raise an Exception on trying to set the state of button

st.button('Submit', key='my_button')
state-button-exception
Serializable Session State
Serialization refers to the process of converting an object or data structure into a format that can be persisted and shared, and allowing you to recover the data’s original structure. Python’s built-in pickle module serializes Python objects to a byte stream ("pickling") and deserializes the stream into an object ("unpickling").

By default, Streamlit’s Session State allows you to persist any Python object for the duration of the session, irrespective of the object’s pickle-serializability. This property lets you store Python primitives such as integers, floating-point numbers, complex numbers and booleans, dataframes, and even lambdas returned by functions. However, some execution environments may require serializing all data in Session State, so it may be useful to detect incompatibility during development, or when the execution environment will stop supporting it in the future.

To that end, Streamlit provides a runner.enforceSerializableSessionState configuration option that, when set to true, only allows pickle-serializable objects in Session State. To enable the option, either create a global or project config file with the following or use it as a command-line flag:

# .streamlit/config.toml
[runner]
enforceSerializableSessionState = true
By "pickle-serializable", we mean calling pickle.dumps(obj) should not raise a PicklingError exception. When the config option is enabled, adding unserializable data to session state should result in an exception. E.g.,

import streamlit as st

def unserializable_data():
		return lambda x: x

#👇 results in an exception when enforceSerializableSessionState is on
st.session_state.unserializable = unserializable_data()
UnserializableSessionStateError
priority_high
Warning
When runner.enforceSerializableSessionState is set to true, Session State implicitly uses the pickle module, which is known to be insecure. Ensure all data saved and retrieved from Session State is trusted because it is possible to construct malicious pickle data that will execute arbitrary code during unpickling. Never load data that could have come from an untrusted source in an unsafe mode or that could have been tampered with. Only load data you trust.

Caveats and limitations
Here are some limitations to keep in mind when using Session State:

Session State exists for as long as the tab is open and connected to the Streamlit server. As soon as you close the tab, everything stored in Session State is lost.
Session State is not persisted. If the Streamlit server crashes, then everything stored in Session State gets wiped
For caveats and limitations with the Session State API, please see the API limitations.


---

Using forms
When you don't want to rerun your script with each input made by a user, st.form is here to help! Forms make it easy to batch user input into a single rerun. This guide to using forms provides examples and explains how users interact with forms.

Example
In the following example, a user can set multiple parameters to update the map. As the user changes the parameters, the script will not rerun and the map will not update. When the user submits the form with the button labeled "Update map", the script reruns and the map updates.

If at any time the user clicks "Generate new points" which is outside of the form, the script will rerun. If the user has any unsubmitted changes within the form, these will not be sent with the rerun. All changes made to a form will only be sent to the Python backend when the form itself is submitted.

View source code
expand_more

Built with Streamlit 🎈
Fullscreen
open_in_new
User interaction
If a widget is not in a form, that widget will trigger a script rerun whenever a user changes its value. For widgets with keyed input (st.number_input, st.text_input, st.text_area), a new value triggers a rerun when the user clicks or tabs out of the widget. A user can also submit a change by pressing Enter while thier cursor is active in the widget.

On the other hand if a widget is inside of a form, the script will not rerun when a user clicks or tabs out of that widget. For widgets inside a form, the script will rerun when the form is submitted and all widgets within the form will send their updated values to the Python backend.

Forms
A user can submit a form using Enter on their keyboard if their cursor active in a widget that accepts keyed input. Within st.number_input and st.text_input a user presses Enter to submit the form. Within st.text_area a user presses Ctrl+Enter/⌘+Enter to submit the form.

Keyboard-submit forms
Widget values
Before a form is submitted, all widgets within that form will have default values, just like widgets outside of a form have default values.

import streamlit as st

with st.form("my_form"):
   st.write("Inside the form")
   my_number = st.slider('Pick a number', 1, 10)
   my_color = st.selectbox('Pick a color', ['red','orange','green','blue','violet'])
   st.form_submit_button('Submit my picks')

# This is outside the form
st.write(my_number)
st.write(my_color)

Built with Streamlit 🎈
Fullscreen
open_in_new
Forms are containers
When st.form is called, a container is created on the frontend. You can write to that container like you do with other container elements. That is, you can use Python's with statement as shown in the example above, or you can assign the form container to a variable and call methods on it directly. Additionally, you can place st.form_submit_button anywhere in the form container.

import streamlit as st

animal = st.form('my_animal')

# This is writing directly to the main body. Since the form container is
# defined above, this will appear below everything written in the form.
sound = st.selectbox('Sounds like', ['meow','woof','squeak','tweet'])

# These methods called on the form container, so they appear inside the form.
submit = animal.form_submit_button(f'Say it with {sound}!')
sentence = animal.text_input('Your sentence:', 'Where\'s the tuna?')
say_it = sentence.rstrip('.,!?') + f', {sound}!'
if submit:
    animal.subheader(say_it)
else:
    animal.subheader('&nbsp;')

Built with Streamlit 🎈
Fullscreen
open_in_new
Processing form submissions
The purpose of a form is to override the default behavior of Streamlit which reruns a script as soon as the user makes a change. For widgets outside of a form, the logical flow is:

The user changes a widget's value on the frontend.
The widget's value in st.session_state and in the Python backend (server) is updated.
The script rerun begins.
If the widget has a callback, it is executed as a prefix to the page rerun.
When the updated widget's function is executed during the rerun, it outputs the new value.
For widgets inside a form, any changes made by a user (step 1) do not get passed to the Python backend (step 2) until the form is submitted. Furthermore, the only widget inside a form that can have a callback function is the st.form_submit_button. If you need to execute a process using newly submitted values, you have three major patterns for doing so.

Execute the process after the form
If you need to execute a one-time process as a result of a form submission, you can condition that process on the st.form_submit_button and execute it after the form. If you need results from your process to display above the form, you can use containers to control where the form displays relative to your output.

import streamlit as st

col1,col2 = st.columns([1,2])
col1.title('Sum:')

with st.form('addition'):
    a = st.number_input('a')
    b = st.number_input('b')
    submit = st.form_submit_button('add')

if submit:
    col2.title(f'{a+b:.2f}')

Built with Streamlit 🎈
Fullscreen
open_in_new
Use a callback with session state
You can use a callback to execute a process as a prefix to the script rerunning.

priority_high
Important
When processing newly updated values within a callback, do not pass those values to the callback directly through the args or kwargs parameters. You need to assign a key to any widget whose value you use within the callback. If you look up the value of that widget from st.session_state within the body of the callback, you will be able to access the newly submitted value. See the example below.

import streamlit as st

if 'sum' not in st.session_state:
    st.session_state.sum = ''

def sum():
    result = st.session_state.a + st.session_state.b
    st.session_state.sum = result

col1,col2 = st.columns(2)
col1.title('Sum:')
if isinstance(st.session_state.sum, float):
    col2.title(f'{st.session_state.sum:.2f}')

with st.form('addition'):
    st.number_input('a', key = 'a')
    st.number_input('b', key = 'b')
    st.form_submit_button('add', on_click=sum)

Built with Streamlit 🎈
Fullscreen
open_in_new
Use st.rerun
If your process affects content above your form, another alternative is using an extra rerun. This can be less resource-efficient though, and may be less desirable that the above options.

import streamlit as st

if 'sum' not in st.session_state:
    st.session_state.sum = ''

col1,col2 = st.columns(2)
col1.title('Sum:')
if isinstance(st.session_state.sum, float):
    col2.title(f'{st.session_state.sum:.2f}')

with st.form('addition'):
    a = st.number_input('a')
    b = st.number_input('b')
    submit = st.form_submit_button('add')

# The value of st.session_state.sum is updated at the end of the script rerun,
# so the displayed value at the top in col2 does not show the new sum. Trigger
# a second rerun when the form is submitted to update the value above.
st.session_state.sum = a + b
if submit:
    st.rerun()

Built with Streamlit 🎈
Fullscreen
open_in_new
Limitations
Every form must contain a st.form_submit_button.
st.button and st.download_button cannot be added to a form.
st.form cannot be embedded inside another st.form.
Callback functions can only be assigned to st.form_submit_button within a form; no other widgets in a form can have a callback.
Interdependent widgets within a form are unlikely to be particularly useful. If you pass widget1's value into widget2 when they are both inside a form, then widget2 will only update when the form is submitted.


---
Working with fragments
Reruns are a central part of every Streamlit app. When users interact with widgets, your script reruns from top to bottom, and your app's frontend is updated. Streamlit provides several features to help you develop your app within this execution model. Streamlit version 1.37.0 introduced fragments to allow rerunning a portion of your code instead of your full script. As your app grows larger and more complex, these fragment reruns help your app be efficient and performant. Fragments give you finer, easy-to-understand control over your app's execution flow.

Before you read about fragments, we recommend having a basic understanding of caching, Session State, and forms.

Use cases for fragments
Fragments are versatile and applicable to a wide variety of circumstances. Here are just a few, common scenarios where fragments are useful:

Your app has multiple visualizations and each one takes time to load, but you have a filter input that only updates one of them.
You have a dynamic form that doesn't need to update the rest of your app (until the form is complete).
You want to automatically update a single component or group of components to stream data.
Defining and calling a fragment
Streamlit provides a decorator (st.fragment) to turn any function into a fragment function. When you call a fragment function that contains a widget function, a user triggers a fragment rerun instead of a full rerun when they interact with that fragment's widget. During a fragment rerun, only your fragment function is re-executed. Anything within the main body of your fragment is updated on the frontend, while the rest of your app remains the same. We'll describe fragments written across multiple containers later on.

Here is a basic example of defining and calling a fragment function. Just like with caching, remember to call your function after defining it.

import streamlit as st

@st.fragment
def fragment_function():
    if st.button("Hi!"):
        st.write("Hi back!")

fragment_function()
If you want the main body of your fragment to appear in the sidebar or another container, call your fragment function inside a context manager.

with st.sidebar:
    fragment_function()
Fragment execution flow
Consider the following code with the explanation and diagram below.

import streamlit as st

st.title("My Awesome App")

@st.fragment()
def toggle_and_text():
    cols = st.columns(2)
    cols[0].toggle("Toggle")
    cols[1].text_area("Enter text")

@st.fragment()
def filter_and_file():
    cols = st.columns(2)
    cols[0].checkbox("Filter")
    cols[1].file_uploader("Upload image")

toggle_and_text()
cols = st.columns(2)
cols[0].selectbox("Select", [1,2,3], None)
cols[1].button("Update")
filter_and_file()
When a user interacts with an input widget inside a fragment, only the fragment reruns instead of the full script. When a user interacts with an input widget outside a fragment, the full script reruns as usual.

If you run the code above, the full script will run top to bottom on your app's initial load. If you flip the toggle button in your running app, the first fragment (toggle_and_text()) will rerun, redrawing the toggle and text area while leaving everything else unchanged. If you click the checkbox, the second fragment (filter_and_file()) will rerun and consequently redraw the checkbox and file uploader. Everything else remains unchanged. Finally, if you click the update button, the full script will rerun, and Streamlit will redraw everything.

Diagram of fragment execution flow
Fragment return values and interacting with the rest of your app
Streamlit ignores fragment return values during fragment reruns, so defining return values for your fragment functions is not recommended. Instead, if your fragment needs to share data with the rest of your app, use Session State. Fragments are just functions in your script, so they can access Session State, imported modules, and other Streamlit elements like containers. If your fragment writes to any container created outside of itself, note the following difference in behavior:

Elements drawn in the main body of your fragment are cleared and redrawn in place during a fragment rerun. Repeated fragment reruns will not cause additional elements to appear.
Elements drawn to containers outside the main body of fragment will not be cleared with each fragment rerun. Instead, Streamlit will draw them additively and these elements will accumulate until the next full-script rerun.
A fragment can't draw widgets in containers outside of the main body of the fragment. Widgets can only go in the main body of a fragment.
To prevent elements from accumulating in outside containers, use st.empty containers. For a related tutorial, see Create a fragment across multiple containers.

If you need to trigger a full-script rerun from inside a fragment, call st.rerun. For a related tutorial, see Trigger a full-script rerun from inside a fragment.

Automate fragment reruns
st.fragment includes a convenient run_every parameter that causes the fragment to rerun automatically at the specified time interval. These reruns are in addition to any reruns (fragment or full-script) triggered by your user. The automatic fragment reruns will continue even if your user is not interacting with your app. This is a great way to show a live data stream or status on a running background job, efficiently updating your rendered data and only your rendered data.

@st.fragment(run_every="10s")
def auto_function():
		# This will update every 10 seconds!
		df = get_latest_updates()
		st.line_chart(df)

auto_function()
For a related tutorial, see Start and stop a streaming fragment.

Compare fragments to other Streamlit features
Fragments vs forms
Here is a comparison between fragments and forms:

Forms allow users to interact with widgets without rerunning your app. Streamlit does not send user actions within a form to your app's Python backend until the form is submitted. Widgets within a form can not dynamically update other widgets (in or out of the form) in real-time.
Fragments run independently from the rest of your code. As your users interact with fragment widgets, their actions are immediately processed by your app's Python backend and your fragment code is rerun. Widgets within a fragment can dynamically update other widgets within the same fragment in real-time.
A form batches user input without interaction between any widgets. A fragment immediately processes user input but limits the scope of the rerun.

Fragments vs callbacks
Here is a comparison between fragments and callbacks:

Callbacks allow you to execute a function at the beginning of a script rerun. A callback is a single prefix to your script rerun.
Fragments allow you to rerun a portion of your script. A fragment is a repeatable postfix to your script, running each time a user interacts with a fragment widget, or automatically in sequence when run_every is set.
When callbacks render elements to your page, they are rendered before the rest of your page elements. When fragments render elements to your page, they are updated with each fragment rerun (unless they are written to containers outside of the fragment, in which case they accumulate there).

Fragments vs custom components
Here is a comparison between fragments and custom components:

Components are custom frontend code that can interact with the Python code, native elements, and widgets in your Streamlit app. Custom components extend what’s possible with Streamlit. They follow the normal Streamlit execution flow.
Fragments are parts of your app that can rerun independently of the full app. Fragments can be composed of multiple Streamlit elements, widgets, or any Python code.
A fragment can include one or more custom components. A custom component could not easily include a fragment!

Fragments vs caching
Here is a comparison between fragments and caching:

Caching: allows you to skip over a function and return a previously computed value. When you use caching, you execute everything except the cached function (if you've already run it before).
Fragments: allow you to freeze most of your app and just execute the fragment. When you use fragments, you execute only the fragment (when triggering a fragment rerun).
Caching saves you from unnecessarily running a piece of your app while the rest runs. Fragments save you from running your full app when you only want to run one piece.

Limitations and unsupported behavior
Fragments can't detect a change in input values. It is best to use Session State for dynamic input and output for fragment functions.
Using caching and fragments on the same function is unsupported.
Fragments can't render widgets in externally-created containers; widgets can only be in the main body of a fragment.


---

Understanding widget behavior
Widgets (like st.button, st.selectbox, and st.text_input) are at the heart of Streamlit apps. They are the interactive elements of Streamlit that pass information from your users into your Python code. Widgets are magical and often work how you want, but they can have surprising behavior in some situations. Understanding the different parts of a widget and the precise order in which events occur helps you achieve your desired results.

This guide covers advanced concepts about widgets. Generally, it begins with simpler concepts and increases in complexity. For most beginning users, these details won't be important to know right away. When you want to dynamically change widgets or preserve widget information between pages, these concepts will be important to understand. We recommend having a basic understanding of Session State before reading this guide.

🎈 TL;DR
expand_more
Anatomy of a widget
There are four parts to keep in mind when using widgets:

The frontend component as seen by the user.
The backend value or value as seen through st.session_state.
The key of the widget used to access its value via st.session_state.
The return value given by the widget's function.
Widgets are session dependent
Widget states are dependent on a particular session (browser connection). The actions of one user do not affect the widgets of any other user. Furthermore, if a user opens up multiple tabs to access an app, each tab will be a unique session. Changing a widget in one tab will not affect the same widget in another tab.

Widgets return simple Python data types
The value of a widget as seen through st.session_state and returned by the widget function are of simple Python types. For example, st.button returns a boolean value and will have the same boolean value saved in st.session_state if using a key. The first time a widget function is called (before a user interacts with it), it will return its default value. (e.g. st.selectbox returns the first option by default.) Default values are configurable for all widgets with a few special exceptions like st.button and st.file_uploader.

Keys help distinguish widgets and access their values
Widget keys serve two purposes:

Distinguishing two otherwise identical widgets.
Creating a means to access and manipulate the widget's value through st.session_state.
Whenever possible, Streamlit updates widgets incrementally on the frontend instead of rebuilding them with each rerun. This means Streamlit assigns an ID to each widget from the arguments passed to the widget function. A widget's ID is based on parameters such as label, min or max value, default value, placeholder text, help text, and key. The page where the widget appears also factors into a widget's ID. If you have two widgets of the same type with the same arguments on the same page, you will get a DuplicateWidgetID error. In this case, assign unique keys to the two widgets.

Streamlit can't understand two identical widgets on the same page
# This will cause a DuplicateWidgetID error.
st.button("OK")
st.button("OK")
Use keys to distinguish otherwise identical widgets
st.button("OK", key="privacy")
st.button("OK", key="terms")
Order of operations
When a user interacts with a widget, the order of logic is:

Its value in st.session_state is updated.
The callback function (if any) is executed.
The page reruns with the widget function returning its new value.
If the callback function writes anything to the screen, that content will appear above the rest of the page. A callback function runs as a prefix to the script rerunning. Consequently, that means anything written via a callback function will disappear as soon as the user performs their next action. Other widgets should generally not be created within a callback function.

push_pin
Note
If a callback function is passed any args or kwargs, those arguments will be established when the widget is rendered. In particular, if you want to use a widget's new value in its own callback function, you cannot pass that value to the callback function via the args parameter; you will have to assign a key to the widget and look up its new value using a call to st.session_state within the callback function.

Using callback functions with forms
Using a callback function with a form requires consideration of this order of operations.

import streamlit as st

if "attendance" not in st.session_state:
    st.session_state.attendance = set()


def take_attendance():
    if st.session_state.name in st.session_state.attendance:
        st.info(f"{st.session_state.name} has already been counted.")
    else:
        st.session_state.attendance.add(st.session_state.name)


with st.form(key="my_form"):
    st.text_input("Name", key="name")
    st.form_submit_button("I'm here!", on_click=take_attendance)

Built with Streamlit 🎈
Fullscreen
open_in_new
Statefulness of widgets
As long as the defining parameters of a widget remain the same and that widget is continuously rendered on the frontend, then it will be stateful and remember user input.

Changing parameters of a widget will reset it
If any of the defining parameters of a widget change, Streamlit will see it as a new widget and it will reset. The use of manually assigned keys and default values is particularly important in this case. Note that callback functions, callback args and kwargs, label visibility, and disabling a widget do not affect a widget's identity.

In this example, we have a slider whose min and max values are changed. Try interacting with each slider to change its value then change the min or max setting to see what happens.

import streamlit as st

cols = st.columns([2, 1, 2])
minimum = cols[0].number_input("Minimum", 1, 5)
maximum = cols[2].number_input("Maximum", 6, 10, 10)

st.slider("No default, no key", minimum, maximum)
st.slider("No default, with key", minimum, maximum, key="a")
st.slider("With default, no key", minimum, maximum, value=5)
st.slider("With default, with key", minimum, maximum, value=5, key="b")

Built with Streamlit 🎈
Fullscreen
open_in_new
Updating a slider with no default value
For the first two sliders above, as soon as the min or max value is changed, the sliders reset to the min value. The changing of the min or max value makes them "new" widgets from Streamlit's perspective and so they are recreated from scratch when the app reruns with the changed parameters. Since no default value is defined, each widget will reset to its min value. This is the same with or without a key since it's seen as a new widget either way. There is a subtle point to understand about pre-existing keys connecting to widgets. This will be explained further down in Widget life cycle.

Updating a slider with a default value
For the last two sliders above, a change to the min or max value will result in the widgets being seen as "new" and thus recreated like before. Since a default value of 5 is defined, each widget will reset to 5 whenever the min or max is changed. This is again the same (with or without a key).

A solution to Retain statefulness when changing a widget's parameters is provided further on.

Widgets do not persist when not continually rendered
If a widget's function is not called during a script run, then none of its parts will be retained, including its value in st.session_state. If a widget has a key and you navigate away from that widget, its key and associated value in st.session_state will be deleted. Even temporarily hiding a widget will cause it to reset when it reappears; Streamlit will treat it like a new widget. You can either interrupt the Widget clean-up process (described at the end of this page) or save the value to another key.

Save widget values in Session State to preserve them between pages
If you want to navigate away from a widget and return to it while keeping its value, use a separate key in st.session_state to save the information independently from the widget. In this example, a temporary key is used with a widget. The temporary key uses an underscore prefix. Hence, "_my_key" is used as the widget key, but the data is copied to "my_key" to preserve it between pages.

import streamlit as st

def store_value():
    # Copy the value to the permanent key
    st.session_state["my_key"] = st.session_state["_my_key"]

# Copy the saved value to the temporary key
st.session_state["_my_key"] = st.session_state["my_key"]
st.number_input("Number of filters", key="_my_key", on_change=store_value)
If this is functionalized to work with multiple widgets, it could look something like this:

import streamlit as st

def store_value(key):
    st.session_state[key] = st.session_state["_"+key]
def load_value(key):
    st.session_state["_"+key] = st.session_state[key]

load_value("my_key")
st.number_input("Number of filters", key="_my_key", on_change=store_value, args=["my_key"])
Widget life cycle
When a widget function is called, Streamlit will check if it already has a widget with the same parameters. Streamlit will reconnect if it thinks the widget already exists. Otherwise, it will make a new one.

As mentioned earlier, Streamlit determines a widget's ID based on parameters such as label, min or max value, default value, placeholder text, help text, and key. The page name also factors into a widget's ID. On the other hand, callback functions, callback args and kwargs, label visibility, and disabling a widget do not affect a widget's identity.

Calling a widget function when the widget doesn't already exist
If your script rerun calls a widget function with changed parameters or calls a widget function that wasn't used on the last script run:

Streamlit will build the frontend and backend parts of the widget, using its default value.
If the widget has been assigned a key, Streamlit will check if that key already exists in Session State.
a. If it exists and is not currently associated with another widget, Streamlit will assign that key's value to the widget. b. Otherwise, it will assign the default value to the key in st.session_state (creating a new key-value pair or overwriting an existing one).
If there are args or kwargs for a callback function, they are computed and saved at this point in time.
The widget value is then returned by the function.
Step 2 can be tricky. If you have a widget:

st.number_input("Alpha",key="A")
and you change it on a page rerun to:

st.number_input("Beta",key="A")
Streamlit will see that as a new widget because of the label change. The key "A" will be considered part of the widget labeled "Alpha" and will not be attached as-is to the new widget labeled "Beta". Streamlit will destroy st.session_state.A and recreate it with the default value.

If a widget attaches to a pre-existing key when created and is also manually assigned a default value, you will get a warning if there is a disparity. If you want to control a widget's value through st.session_state, initialize the widget's value through st.session_state and avoid the default value argument to prevent conflict.

Calling a widget function when the widget already exists
When rerunning a script without changing a widget's parameters:

Streamlit will connect to the existing frontend and backend parts.
If the widget has a key that was deleted from st.session_state, then Streamlit will recreate the key using the current frontend value. (e.g Deleting a key will not revert the widget to a default value.)
It will return the current value of the widget.
Widget clean-up process
When Streamlit gets to the end of a script run, it will delete the data for any widgets it has in memory that were not rendered on the screen. Most importantly, that means Streamlit will delete all key-value pairs in st.session_state associated with a widget not currently on screen.

Additional examples
As promised, let's address how to retain the statefulness of widgets when changing pages or modifying their parameters. There are two ways to do this.

Use dummy keys to duplicate widget values in st.session_state and protect the data from being deleted along with the widget.
Interrupt the widget clean-up process.
The first method was shown above in Save widget values in Session State to preserve them between pages

Interrupting the widget clean-up process
To retain information for a widget with key="my_key", just add this to the top of every page:

st.session_state.my_key = st.session_state.my_key
When you manually save data to a key in st.session_state, it will become detached from any widget as far as the clean-up process is concerned. If you navigate away from a widget with some key "my_key" and save data to st.session_state.my_key on the new page, you will interrupt the widget clean-up process and prevent the key-value pair from being deleted or overwritten if another widget with the same key exists.

Retain statefulness when changing a widget's parameters
Here is a solution to our earlier example of changing a slider's min and max values. This solution interrupts the clean-up process as described above.

import streamlit as st

# Set default value
if "a" not in st.session_state:
    st.session_state.a = 5

cols = st.columns(2)
minimum = cols[0].number_input("Min", 1, 5, key="min")
maximum = cols[1].number_input("Max", 6, 10, 10, key="max")


def update_value():
    # Helper function to ensure consistency between widget parameters and value
    st.session_state.a = min(st.session_state.a, maximum)
    st.session_state.a = max(st.session_state.a, minimum)


# Validate the slider value before rendering
update_value()
st.slider("A", minimum, maximum, key="a")

Built with Streamlit 🎈
Fullscreen
open_in_new
The update_value() helper function is actually doing two things. On the surface, it's making sure there are no inconsistent changes to the parameters values as described. Importantly, it's also interrupting the widget clean-up process. When the min or max value of the widget changes, Streamlit sees it as a new widget on rerun. Without saving a value to st.session_state.a, the value would be thrown out and replaced by the "new" widget's default value.

---



