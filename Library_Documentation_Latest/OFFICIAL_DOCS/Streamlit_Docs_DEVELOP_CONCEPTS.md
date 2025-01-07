******** Streamlit Official Documentation 2024: DEVELOP_CONCEPTS ********
------------------------------------------------------------------------------------------------
CHAPTER 1: app-design.md
------------------------------------------------------------------------------------------------
################################################
Section 1.1 - animate-elements.md
################################################
# Animate and update elements
Sometimes you display a chart or dataframe and want to modify it live as the app
runs (for example, in a loop). Some elements have built-in methods to allow you
to update them in-place without rerunning the app.
Updatable elements include the following:
- `st.empty` containers can be written to in sequence and will always show the last thing written. They can also be cleared with an
additional `.empty()` called like a method.
- `st.dataframe`, `st.table`, and many chart elements can be updated with the `.add_rows()` method which appends data.
- `st.progress` elements can be updated with additional `.progress()` calls. They can also be cleared with a `.empty()` method call.
- `st.status` containers have an `.update()` method to change their labels, expanded state, and status.
- `st.toast` messages can be updated in place with additional `.toast()` calls.
## `st.empty` containers
`st.empty` can hold a single element. When you write any element to an `st.empty` container, Streamlit discards its previous content
displays the new element. You can also `st.empty` containers by calling `.empty()` as a method. If you want to update a set of elements, use
a plain container (`st.container()`) inside `st.empty` and write contents to the plain container. Rewrite the plain container and its
contents as often as desired to update your app's display.
## The `.add_rows()` method
`st.dataframe`, `st.table`, and all chart functions can be mutated using the `.add_rows()` method on their output. In the following example, we use `my_data_element = st.line_chart(df)`. You can try the example with `st.table`, `st.dataframe`, and most of the other simple charts by just swapping out `st.line_chart`. Note that `st.dataframe` only shows the first ten rows by default and enables scrolling for additional rows. This means adding rows is not as visually apparent as it is with `st.table` or the chart elements.
```python
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
```
################################################
Section 1.2 - button-behavior-and-examples.md
################################################
# Button behavior and examples
## Summary
Buttons created with [`st.button`] do not retain state. They return `True` on the script rerun resulting from their click and immediately return to `False` on the next script rerun. If a displayed element is nested inside `if st.button('Click me'):`, the element will be visible when the button is clicked and disappear as soon as the user takes their next action. This is because the script reruns and the button return value becomes `False`.
In this guide, we will illustrate the use of buttons and explain common misconceptions. Read on to see a variety of examples that expand on `st.button` using [`st.session_state`]. [Anti-patterns](#anti-patterns) are included at the end. When code is conditioned on a button's value, it will execute once in response to the button being clicked and not again (until the button is clicked again).
Good to nest inside buttons:
- Transient messages that immediately disappear.
- Once-per-click processes that saves data to session state, a file, or
a database.
Bad to nest inside buttons:
- Displayed items that should persist as the user continues.
- Other widgets which cause the script to rerun when used.
- Processes that neither modify session state nor write to a file/database.\*
\* This can be appropriate when disposable results are desired. If you
have a "Validate" button, that could be a process conditioned directly on a
button. It could be used to create an alert to say 'Valid' or 'Invalid' with no
need to keep that info.
## Common logic with buttons
### Show a temporary message with a button
If you want to give the user a quick button to check if an entry is valid, but not keep that check displayed as the user continues.
In this example, a user can click a button to check if their `animal` string is in the `animal_shelter` list. When the user clicks "**Check availability**" they will see "We have that animal!" or "We don't have that animal." If they change the animal in [`st.text_input`], the script reruns and the message disappears until they click "**Check availability**" again.
```python
import streamlit as st
animal_shelter = ['cat', 'dog', 'rabbit', 'bird']
animal = st.text_input('Type an animal')
if st.button('Check availability'):
have_it = animal.lower() in animal_shelter
'We have that animal!' if have_it else 'We don\'t have that animal.'
```
Note: The above example uses [magic] to render the message on the frontend.
### Stateful button
If you want a clicked button to continue to be `True`, create a value in `st.session_state` and use the button to set that value to `True` in a callback.
```python
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
```
### Toggle button
If you want a button to work like a toggle switch, consider using [`st.checkbox`]. Otherwise, you can use a button with a callback function to reverse a boolean value saved in `st.session_state`.
In this example, we use `st.button` to toggle another widget on and off. By displaying [`st.slider`] conditionally on a value in `st.session_state`, the user can interact with the slider without it disappearing.
```python
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
```
Alternatively, you can use the value in `st.session_state` on the slider's `disabled` parameter.
```python
import streamlit as st
if 'button' not in st.session_state:
st.session_state.button = False
def click_button():
st.session_state.button = not st.session_state.button
st.button('Click me', on_click=click_button)
st.slider('Select a value', disabled=st.session_state.button)
```
### Buttons to continue or control stages of a process
Another alternative to nesting content inside a button is to use a value in `st.session_state` that designates the "step" or "stage" of a process. In this example, we have four stages in our script:
0. Before the user begins.
1. User enters their name.
2. User chooses a color.
3. User gets a thank-you message.
A button at the beginning advances the stage from 0 to 1. A button at the end resets the stage from 3 to 0. The other widgets used in stage 1 and 2 have callbacks to set the stage. If you have a process with dependant steps and want to keep previous stages visible, such a callback forces a user to retrace subsequent stages if they change an earlier widget.
```python
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
```
### Buttons to modify `st.session_state`
If you modify `st.session_state` inside of a button, you must consider where that button is within the script.
#### A slight problem
In this example, we access `st.session_state.name` both before and after the buttons which modify it. When a button ("**Jane**" or "**John**") is clicked, the script reruns. The info displayed before the buttons lags behind the info written after the button. The data in `st.session_state` before the button is not updated. When the script executes the button function, that is when the conditional code to update `st.session_state` creates the change. Thus, this change is reflected after the button.
```python
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
```
#### Logic used in a callback
Callbacks are a clean way to modify `st.session_state`. Callbacks are executed as a prefix to the script rerunning, so the position of the button relative to accessing data is not important.
```python
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
```
#### Logic nested in a button with a rerun
Although callbacks are often preferred to avoid extra reruns, our first 'John Doe'/'Jane Doe' example can be modified by adding [`st.rerun`] instead. If you need to acces data in `st.session_state` before the button that modifies it, you can include `st.rerun` to rerun the script after the change has been committed. This means the script will rerun twice when a button is clicked.
```python
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
```
### Buttons to modify or reset other widgets
When a button is used to modify or reset another widget, it is the same as the above examples to modify `st.session_state`. However, an extra consideration exists: you cannot modify a key-value pair in `st.session_state` if the widget with that key has already been rendered on the page for the current script run.
Note: Don't do this!
```python
import streamlit as st
st.text_input('Name', key='name')
# These buttons will error because their nested code changes
# a widget's state after that widget within the script.
if st.button('Clear name'):
st.session_state.name = ''
if st.button('Streamlit!'):
st.session_state.name = ('Streamlit')
```
#### Option 1: Use a key for the button and put the logic before the widget
If you assign a key to a button, you can condition code on a button's state by using its value in `st.session_state`. This means that logic depending on your button can be in your script before that button. In the following example, we use the `.get()` method on `st.session_state` because the keys for the buttons will not exist when the script runs for the first time. The `.get()` method will return `False` if it can't find the key. Otherwise, it will return the value of the key.
```python
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
```
#### Option 2: Use a callback
```python
import streamlit as st
st.text_input('Name', key='name')
def set_name(name):
st.session_state.name = name
st.button('Clear name', on_click=set_name, args=[''])
st.button('Streamlit!', on_click=set_name, args=['Streamlit'])
```
#### Option 3: Use containers
By using [`st.container`] you can have widgets appear in different orders in your script and frontend view (webpage).
```python
import streamlit as st
begin = st.container()
if st.button('Clear name'):
st.session_state.name = ''
if st.button('Streamlit!'):
st.session_state.name = ('Streamlit')
# The widget is second in logic, but first in display
begin.text_input('Name', key='name')
```
### Buttons to add other widgets dynamically
When dynamically adding widgets to the page, make sure to use an index to keep the keys unique and avoid a `DuplicateWidgetID` error. In this example, we define a function `display_input_row` which renders a row of widgets. That function accepts an `index` as a parameter. The widgets rendered by `display_input_row` use `index` within their keys so that `dispaly_input_row` can be executed multiple times on a single script rerun without repeating any widget keys.
```python
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
```
### Buttons to handle expensive or file-writing processes
When you have expensive processes, set them to run upon clicking a button and save the results into `st.session_state`. This allows you to keep accessing the results of the process without re-executing it unnecessarily. This is especially helpful for processes that save to disk or write to a database. In this example, we have an `expensive_process` that depends on two parameters: `option` and `add`. Functionally, `add` changes the output, but `option` does not&mdash;`option` is there to provide a parameter
```python
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
st.write(f'Option {option} processed with add {add}')
result[0]
```
Astute observers may think, "This feels a little like caching." We are only saving results relative to one parameter, but the pattern could easily be expanded to save results relative to both parameters. In that sense, yes, it has some similarities to caching, but also some important differences. When you save results in `st.session_state`, the results are only available to the current user in their current session. If you use [`st.cache_data`] instead, the results are available to all users across all sessions. Furthermore, if you want to update a saved result, you have to clear all saved results for that function to do so.
## Anti-patterns
Here are some simplified examples of how buttons can go wrong. Be on the lookout for these common mistakes.
### Buttons nested inside buttons
```python
import streamlit as st
if st.button('Button 1'):
st.write('Button 1 was clicked')
if st.button('Button 2'):
# This will never be executed.
st.write('Button 2 was clicked')
```
### Other widgets nested inside buttons
```python
import streamlit as st
if st.button('Sign up'):
name = st.text_input('Name')
if name:
# This will never be executed.
st.success(f'Welcome {name}')
```
### Nesting a process inside a button without saving to session state
```python
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
```
################################################
Section 1.3 - custom-classes.md
################################################
# Using custom Python classes in your Streamlit app
If you are building a complex Streamlit app or working with existing code, you may have custom Python classes defined in your script. Common examples include the following:
- Defining a `@dataclass` to store related data within your app.
- Defining an `Enum` class to represent a fixed set of options or values.
- Defining custom interfaces to external services or databases not covered by [`st.connection`].
Because Streamlit reruns your script after every user interaction, custom classes may be redefined multiple times within the same Streamlit session. This may result in unwanted effects, especially with class and instance comparisons. Read on to understand this common pitfall and how to avoid it.
We begin by covering some general-purpose patterns you can use for different types of custom classes, and follow with a few more technical details explaining why this matters. Finally, we go into more detail about [Using `Enum` classes](#using-enum-classes-in-streamlit) specifically, and describe a configuration option which can make them more convenient.
## Patterns to define your custom classes
### Pattern 1: Define your class in a separate module
This is the recommended, general solution. If possible, move class definitions into their own module file and import them into your app script. As long as you are not editing the file where your class is defined, Streamlit will not re-import it with each rerun. Therefore, if a class is defined in an external file and imported into your script, the class will not be redefined during the session.
#### Example: Move your class definition
Try running the following Streamlit app where `MyClass` is defined within the page's script. `isinstance()` will return `True` on the first script run then return `False` on each rerun thereafter.
```python
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
```
If you move the class definition out of `app.py` into another file, you can make `isinstance()` consistently return `True`. Consider the following file structure:
```
myproject/
├── my_class.py
└── app.py
```
```python
# my_class.py
class MyClass:
def __init__(self, var1, var2):
self.var1 = var1
self.var2 = var2
```
```python
# app.py
import streamlit as st
from my_class import MyClass # MyClass doesn't get redefined with each rerun
if "my_instance" not in st.session_state:
st.session_state.my_instance = MyClass("foo", "bar")
# Displays True on every rerun
st.write(isinstance(st.session_state.my_instance, MyClass))
st.button("Rerun")
```
Streamlit only reloads code in imported modules when it detects the code has changed. Thus, if you are actively editing the file where your class is defined, you may need to stop and restart your Streamlit server to avoid an undesirable class redefinition mid-session.
### Pattern 2: Force your class to compare internal values
For classes that store data (like dataclasses), you may be more interested in comparing the internally stored values rather than the class itself. If you define a custom `__eq__` method, you can force comparisons to be made on the internally stored values.
#### Example: Define `__eq__`
Try running the following Streamlit app and observe how the comparison is `True` on the first run then `False` on every rerun thereafter.
```python
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
```
Since `MyDataclass` gets redefined with each rerun, the instance stored in Session State will not be equal to any instance defined in a later script run. You can fix this by forcing a comparison of internal values as follows:
```python
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
```
The default Python `__eq__` implementation for a regular class or `@dataclass` depends on the in-memory ID of the class or class instance. To avoid problems in Streamlit, your custom `__eq__` method should not depend the `type()` of `self` and `other`.
### Pattern 3: Store your class as serialized data
Another option for classes that store data is to define serialization and deserialization methods like `to_str` and `from_str` for your class. You can use these to store class instance data in `st.session_state` rather than storing the class instance itself. Similar to pattern 2, this is a way to force comparison of the internal data and bypass the changing in-memory IDs.
#### Example: Save your class instance as a string
Using the same example from pattern 2, this can be done as follows:
```python
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
```
### Pattern 4: Use caching to preserve your class
For classes that are used as resources (database connections, state managers, APIs), consider using the cached singleton pattern. Use `@st.cache_resource` to decorate a `@staticmethod` of your class to generate a single, cached instance of the class. For example:
```python
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
```
When you use one of Streamlit's caching decorators on a function, Streamlit doesn't use the function object to look up cached values. Instead, Streamlit's caching decorators index return values using the function's qualified name and module. So, even though Streamlit redefines `MyResource` with each script run, `st.cache_resource` is unaffected by this. `get_resource_manager()` will return its cached value with each rerun, until the value expires.
## Understanding how Python defines and compares classes
So what's really happening here? We'll consider a simple example to illustrate why this is a pitfall. Feel free to skip this section if you don't want to deal more details. You can jump ahead to learn about [Using `Enum` classes](#using-enum-classes-in-streamlit).
### Example: What happens when you define the same class twice?
Set aside Streamlit for a moment and think about this simple Python script:
```python
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
```
In this example, the dataclass `Student` is defined twice. All three Marshalls have the same internal values. If you compare `Marshall_A` and `Marshall_B` they will be equal because they were both created from the first definition of `Student`. However, if you compare `Marshall_A` and `Marshall_C` they will not be equal because `Marshall_C` was created from the _second_ definition of `Student`. Even though both `Student` dataclasses are defined exactly the same, they have different in-memory IDs and are therefore different.
### What's happening in Streamlit?
In Streamlit, you probably don't have the same class written twice in your page script. However, the rerun logic of Streamlit creates the same effect. Let's use the above example for an analogy. If you define a class in one script run and save an instance in Session State, then a later rerun will redefine the class and you may end up comparing a `Mashall_C` in your rerun to a `Marshall_A` in Session State. Since widgets rely on Session State under the hood, this is where things can get confusing.
## How Streamlit widgets store options
Several Streamlit UI elements, such as `st.selectbox` or `st.radio`, accept multiple-choice options via an `options` argument. The user of your application can typically select one or more of these options. The selected value is returned by the widget function. For example:
```python
number = st.selectbox("Pick a number, any number", options=[1, 2, 3])
# number == whatever value the user has selected from the UI.
```
When you call a function like `st.selectbox` and pass an `Iterable` to `options`, the `Iterable` and current selection are saved into a hidden portion of [Session State] called the Widget Metadata.
When the user of your application interacts with the `st.selectbox` widget, the broswer sends the index of their selection to your Streamlit server. This index is used to determine which values from the original `options` list, _saved in the Widget Metadata from the previous page execution_, are returned to your application.
The key detail is that the value returned by `st.selectbox` (or similar widget function) is from an `Iterable` saved in Session State during a _previous_ execution of the page, NOT the values passed to `options` on the _current_ execution. There are a number of architectural reasons why Streamlit is designed this way, which we won't go into here. However, **this** is how we end up comparing instances of different classes when we think we are comparing instances of the same class.
### A pathological example
The above explanation might be a bit confusing, so here's a pathological example to illustrate the idea.
```python
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
```
As a final note, we used `@dataclass` in the example for this section to illustrate a point, but in fact it is possible to encounter these same problems with classes, in general. Any class which checks class identity inside of a comparison operator&mdash;such as `__eq__` or `__gt__`&mdash;can exhibit these issues.
## Using `Enum` classes in Streamlit
The `Enum` class from the Python standard library is a powerful way to define custom symbolic names that can be used as options for `st.multiselect` or `st.selectbox` in place of `str` values.
For example, you might add the following to your streamlit page:
```python
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
```
If you're using the latest version of Streamlit, this Streamlit page will work as it appears it should. When a user picks both `Color.RED` and `Color.GREEN`, they are shown the special message.
However, if you've read the rest of this page you might notice something tricky going on. Specifically, the `Enum` class `Color` gets redefined every time this script is run. In Python, if you define two `Enum` classes with the same class name, members, and values, the classes and their members are still considered unique from each other. This _should_ cause the above `if` condition to always evaluate to `False`. In any script rerun, the `Color` values returned by `st.multiselect` would be of a different class than the `Color` defined in that script run.
If you run the snippet above with Streamlit version 1.28.0 or less, you will not be able see the special message. Thankfully, as of version 1.29.0, Streamlit introduced a configuration option to greatly simplify the problem. That's where the enabled-by-default `enumCoercion` configuration option comes in.
### Understanding the `enumCoercion` configuration option
When `enumCoercion` is enabled, Streamlit tries to recognize when you are using an element like `st.multiselect` or `st.selectbox` with a set of `Enum` members as options.
If Streamlit detects this, it will convert the widget's returned values to members of the `Enum` class defined in the latest script run. This is something we call automatic `Enum` coercion.
This behavior is [configurable] via the `enumCoercion` setting in your Streamlit `config.toml` file. It is enabled by default, and may be disabled or set to a stricter set of matching criteria.
If you find that you still encounter issues with `enumCoercion` enabled, consider using the [custom class patterns](#patterns-to-define-your-custom-classes) described above, such as moving your `Enum` class definition to a separate module file.
################################################
Section 1.4 - dataframes.md
################################################
# Dataframes
Dataframes are a great way to display and edit data in a tabular format. Working with Pandas DataFrames and other tabular data structures is key to data science workflows. If developers and data scientists want to display this data in Streamlit, they have multiple options: `st.dataframe` and `st.data_editor`. If you want to solely display data in a table-like UI, [st.dataframe] is the way to go. If you want to interactively edit data, use [st.data_editor]. We explore the use cases and advantages of each option in the following sections.
## Display dataframes with st.dataframe
Streamlit can display dataframes in a table-like UI via `st.dataframe` :
```python
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
```
<Cloud name="doc-dataframe-basic" height="300px"/>
## `st.dataframe` UI features
`st.dataframe` provides additional functionality by using glide-data-grid under the hood:
- **Column sorting**: Sort columns by clicking on their headers.
- **Column resizing**: Resize columns by dragging and dropping column header borders.
- **Table resizing**: Resize tables by dragging and dropping the bottom right corner.
- **Fullscreen view**: Enlarge tables to fullscreen by clicking the fullscreen icon (<i style={{ verticalAlign: "-.25em" }} className={{ class: "material-icons-sharp" }}>fullscreen</i>) in the toolbar.
- **Search**: Click the search icon (<i style={{ verticalAlign: "-.25em" }} className={{ class: "material-icons-sharp" }}>search</i>) in the toolbar or use hotkeys (`⌘+F` or `Ctrl+F`) to search through the data.
- **Download**: Click the download icon in the toolbar to download the data as a CSV file.
- **Copy to clipboard**: Select one or multiple cells, copy them to the clipboard (`⌘+C` or `Ctrl+C`), and paste them into your favorite spreadsheet software.
<YouTube videoId="nauAnULRG1c" loop autoplay />
Try out all the UI features using the embedded app from the prior section.
In addition to Pandas DataFrames, `st.dataframe` also supports other common Python types, e.g., list, dict, or numpy array. It also supports Snowpark and PySpark DataFrames, which allow you to lazily evaluate and pull data from databases. This can be useful for working with large datasets.
## Edit data with st.data_editor
Streamlit supports editable dataframes via the `st.data_editor` command. ```python
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
```
<Cloud name="doc-data-editor" height="300px"/>
Try it out by double-clicking on any cell. You'll notice you can edit all cell values. Try editing the values in the rating column and observe how the text output at the bottom changes:
## `st.data_editor` UI features
`st.data_editor` also supports a few additional things:
- [**Add and delete rows**](#add-and-delete-rows): You can do this by setting `num_rows= "dynamic"` when calling `st.data_editor`. This will allow users to add and delete rows as needed.
- [**Copy and paste support**](#copy-and-paste-support): Copy and paste both between `st.data_editor` and spreadsheet software like Google Sheets and Excel.
- [**Access edited data**](#access-edited-data): Access only the individual edits instead of the entire edited data structure via Session State.
- [**Bulk edits**](#bulk-edits): Similar to Excel, just drag a handle to edit neighboring cells.
- [**Automatic input validation**](#automatic-input-validation): Column Configuration provides strong data type support and other configurable options. For example, there's no way to enter letters into a number cell. Number cells can have a designated min and max.
- [**Edit common data structures**](#edit-common-data-structures): `st.data_editor` supports lists, dicts, NumPy ndarray, and more!
<YouTube videoId="6tah69LkfxE" loop autoplay />
### Add and delete rows
With `st.data_editor`, viewers can add or delete rows via the table UI. This mode can be activated by setting the `num_rows` parameter to `"dynamic"`:
```python
edited_df = st.data_editor(df, num_rows="dynamic")
```
- To add new rows, click the plus icon (<i style={{ verticalAlign: "-.25em" }} className={{ class: "material-icons-sharp" }}>add</i>) in the toolbar. Alternatively, click inside a shaded cell below the bottom row of the table.
- To delete rows, select one or more rows using the checkboxes on the left. Click the delete icon (<i style={{ verticalAlign: "-.25em" }} className={{ class: "material-icons-sharp" }}>delete</i>) or press the `delete` key on your keyboard.
<Cloud name="doc-data-editor-clipboard" height="400px"/>
### Copy and paste support
The data editor supports pasting in tabular data from Google Sheets, Excel, Notion, and many other similar tools. You can also copy-paste data between `st.data_editor` instances. This functionality, powered by the Clipboard API, can be a huge time saver for users who need to work with data across multiple platforms. To try it out:
1. Copy data from this Google Sheets document to your clipboard.
2. Single click any cell in the `name` column in the app above. Paste it in using hotkeys (`⌘+V` or `Ctrl+V`).
Note: Every cell of the pasted data will be evaluated individually and inserted into the cells if the data is compatible with the column type. For example, pasting in non-numerical text data into a number column will be ignored.
Note: If you embed your apps with iframes, you'll need to allow the iframe to access the clipboard if you want to use the copy-paste functionality. To do so, give the iframe `clipboard-write` and `clipboard-read` permissions. E.g.
```javascript
<iframe allow="clipboard-write;clipboard-read;" ... src="https://your-app-url"></iframe>
```
As developers, ensure the app is served with a valid, trusted certificate when using TLS. If users encounter issues with copying and pasting data, direct them to check if their browser has activated clipboard access permissions for the Streamlit application, either when prompted or through the browser's site settings.
### Access edited data
Sometimes, it is more convenient to know which cells have been changed rather than getting the entire edited dataframe back. Streamlit makes this easy through the use of [Session State]. If a `key` parameter is set, Streamlit will store any changes made to the dataframe in Session State.
This snippet shows how you can access changed data using Session State:
```python
st.data_editor(df, key="my_key", num_rows="dynamic") # 👈 Set a key
st.write("Here's the value in Session State:")
st.write(st.session_state["my_key"]) # 👈 Show the value in Session State
```
In this code snippet, the `key` parameter is set to `"my_key"`. After the data editor is created, the value associated to `"my_key"` in Session State is displayed in the app using `st.write`. This shows the additions, edits, and deletions that were made.
This can be useful when working with large dataframes and you only need to know which cells have changed, rather than access the entire edited dataframe.
<Cloud name="doc-data-editor-changed" height="700px"/>
Use all we've learned so far and apply them to the above embedded app. Try editing cells, adding new rows, and deleting rows.
Notice how edits to the table are reflected in Session State. When you make any edits, a rerun is triggered which sends the edits to the backend. The widget's state is a JSON object containing three properties: **edited_rows**, **added_rows**, and **deleted rows:**.
Note: When going from `st.experimental_data_editor` to `st.data_editor` in 1.23.0, the data editor's representation in `st.session_state` was changed. The `edited_cells` dictionary is now called `edited_rows` and uses a different format (`{0: {"column name": "edited value"}}` instead of `{"0:1": "edited value"}`). You may need to adjust your code if your app uses `st.experimental_data_editor` in combination with `st.session_state`."
- `edited_rows` is a dictionary containing all edits. Keys are zero-based row indices and values are dictionaries that map column names to edits (e.g. `{0: {"col1": ..., "col2": ...}}`).
- `added_rows` is a list of newly added rows. Each value is a dictionary with the same format as above (e.g. `[{"col1": ..., "col2": ...}]`).
- `deleted_rows` is a list of row numbers that have been deleted from the table (e.g. `[0, 2]`).
`st.data_editor` does not support reordering rows, so added rows will always be appended to the end of the dataframe with any edits and deletions applicable to the original rows.
### Bulk edits
The data editor includes a feature that allows for bulk editing of cells. Similar to Excel, you can drag a handle across a selection of cells to edit their values in bulk. You can even apply commonly used keyboard shortcuts in spreadsheet software. This is useful when you need to make the same change across multiple cells, rather than editing each cell individually.
### Edit common data structures
Editing doesn't just work for Pandas DataFrames! You can also edit lists, tuples, sets, dictionaries, NumPy arrays, or Snowpark & PySpark DataFrames. Most data types will be returned in their original format. But some types (e.g. Snowpark and PySpark) are converted to Pandas DataFrames. To learn about all the supported types, read the [st.data_editor] API.
For example, you can easily let the user add items to a list:
```python
edited_list = st.data_editor(["red", "green", "blue"], num_rows= "dynamic")
st.write("Here are all the colors you entered:")
st.write(edited_list)
```
Or numpy arrays:
```python
import numpy as np
st.data_editor(np.array([
["st.text_area", "widget", 4.92],
["st.markdown", "element", 47.22]
]))
```
Or lists of records:
```python
st.data_editor([
{"name": "st.text_area", "type": "widget"},
{"name": "st.markdown", "type": "element"},
])
```
Or dictionaries and many more types!
```python
st.data_editor({
"st.text_area": "widget",
"st.markdown": "element"
})
```
### Automatic input validation
The data editor includes automatic input validation to help prevent errors when editing cells. For example, if you have a column that contains numerical data, the input field will automatically restrict the user to only entering numerical data. This helps to prevent errors that could occur if the user were to accidentally enter a non-numerical value. Additional input validation can be configured through the [Column configuration API]. Keep reading below for an overview of column configuration, including validation options.
## Configuring columns
You can configure the display and editing behavior of columns in `st.dataframe` and `st.data_editor` via the [Column configuration API]. We have developed the API to let you add images, charts, and clickable URLs in dataframe and data editor columns. Additionally, you can make individual columns editable, set columns as categorical and specify which options they can take, hide the index of the dataframe, and much more.
Column configuration includes the following column types: Text, Number, Checkbox, Selectbox, Date, Time, Datetime, List, Link, Image, Line chart, Bar chart, and Progress. There is also a generic Column option. See the embedded app below to view these different column types. Each column type is individually previewed in the [Column configuration API] documentation.
<Cloud name="doc-column-config-overview" query="embed_options=disable_scrolling" height="480px"/>
### Format values
A `format` parameter is available in column configuration for [Text], [Date], [Time], and [Datetime] columns. Chart-like columns can also be formatted. [Line chart] and [Bar chart] columns have a `y_min` and `y_max` parameters to set the vertical bounds. For a [Progress column], you can declare the horizontal bounds with `min_value` and `max_value`.
### Validate input
When specifying a column configuration, you can declare not only the data type of the column but also value restrictions. All column configuration elements allow you to make a column required with the keyword parameter `required=True`.
For Text and Link columns, you can specify the maximum number of characters with `max_chars` or use regular expressions to validate entries through `validate`. Numerical columns, including Number, Date, Time, and Datetime have `min_value` and `max_value` parameters. Selectbox columns have a configurable list of `options`.
The data type for Number columns is `float` by default. Passing a value of type `int` to any of `min_value`, `max_value`, `step`, or `default` will set the type for the column as `int`.
### Configure an empty dataframe
You can use `st.data_editor` to collect tabular input from a user. When starting from an empty dataframe, default column types are text. Use column configuration to specify the data types you want to collect from users.
```python
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
```
<Cloud name="doc-column-config-empty" height="300px"/>
## Additional formatting options
In addition to column configuration, `st.dataframe` and `st.data_editor` have a few more parameters to customize the display of your dataframe.
- `hide_index` : Set to `True` to hide the dataframe's index.
- `column_order` : Pass a list of column labels to specify the order of display.
- `disabled` : Pass a list of column labels to disable them from editing. This let's you avoid disabling them individually.
## Handling large datasets
`st.dataframe` and `st.data_editor` have been designed to theoretically handle tables with millions of rows thanks to their highly performant implementation using the glide-data-grid library and HTML canvas. However, the maximum amount of data that an app can realistically handle will depend on several other factors, including:
1. The maximum size of WebSocket messages: Streamlit's WebSocket messages are configurable via the `server.maxMessageSize` config option, which limits the amount of data that can be transferred via the WebSocket connection at once.
2. The server memory: The amount of data that your app can handle will also depend on the amount of memory available on your server. If the server's memory is exceeded, the app may become slow or unresponsive.
3. The user's browser memory: Since all the data needs to be transferred to the user's browser for rendering, the amount of memory available on the user's device can also affect the app's performance. If the browser's memory is exceeded, it may crash or become unresponsive.
In addition to these factors, a slow network connection can also significantly slow down apps that handle large datasets.
When handling large datasets with more than 150,000 rows, Streamlit applies additional optimizations and disables column sorting. This can help to reduce the amount of data that needs to be processed at once and improve the app's performance.
## Limitations
- Streamlit casts all column names to strings internally, so `st.data_editor` will return a DataFrame where all column names are strings.
- The dataframe toolbar is not currently configurable.
- While Streamlit's data editing capabilities offer a lot of functionality, editing is enabled for a limited set of column types ([TextColumn], [NumberColumn], [LinkColumn], [CheckboxColumn], [SelectboxColumn], [DateColumn], [TimeColumn], and [DatetimeColumn]). We are actively working on supporting editing for other column types as well, such as images, lists, and charts.
- Almost all editable datatypes are supported for index editing. However, `pandas.CategoricalIndex` and `pandas.MultiIndex` are not supported for editing.
- Sorting is not supported for `st.data_editor` when `num_rows="dynamic"`.
- Sorting is deactivated to optimize performance on large datasets with more than 150,000 rows.
We are continually working to improve Streamlit's handling of DataFrame and add functionality to data editing, so keep an eye out for updates.
################################################
Section 1.5 - timezone-handling.md
################################################
# Working with timezones
In general, working with timezones can be tricky. Your Streamlit app users are not necessarily in the same timezone as the server running your app. It is especially true of public apps, where anyone in the world (in any timezone) can access your app. As such, it is crucial to understand how Streamlit handles timezones, so you can avoid unexpected behavior when displaying `datetime` information.
## How Streamlit handles timezones
Streamlit always shows `datetime` information on the frontend with the same information as its corresponding `datetime` instance in the backend. I.e., date or time information does not automatically adjust to the users' timezone. We distinguish between the following two cases:
### **`datetime` instance without a timezone (naive)**
When you provide a `datetime` instance _without specifying a timezone_, the frontend shows the `datetime` instance without timezone information. For example (this also applies to other widgets like [`st.dataframe`]):
```python
import streamlit as st
from datetime import datetime
st.write(datetime(2020, 1, 10, 10, 30))
# Outputs: 2020-01-10 10:30:00
```
Users of the above app always see the output as `2020-01-10 10:30:00`.
### **`datetime` instance with a timezone**
When you provide a `datetime` instance _and specify a timezone_, the frontend shows the `datetime` instance in that same timezone. For example (this also applies to other widgets like [`st.dataframe`]):
```python
import streamlit as st
from datetime import datetime
import pytz
st.write(datetime(2020, 1, 10, 10, 30, tzinfo=pytz.timezone("EST")))
# Outputs: 2020-01-10 10:30:00-05:00
```
Users of the above app always see the output as `2020-01-10 10:30:00-05:00`.
In both cases, neither the date nor time information automatically adjusts to the users' timezone on the frontend. What users see is identical to the corresponding `datetime` instance in the backend. It is currently not possible to automatically adjust the date or time information to the timezone of the users viewing the app.
Note: The legacy version of the `st.dataframe` has issues with timezones. We do not plan to roll out additional fixes or enhancements for the legacy dataframe. If you need stable timezone support, please consider switching to the arrow serialization by changing the [config setting], _config.dataFrameSerialization = "arrow"_.
------------------------------------------------------------------------------------------------
CHAPTER 2: app-testing.md
------------------------------------------------------------------------------------------------
################################################
Section 2.1 - automate-tests.md
################################################
# Automate your tests with CI
One of the key benefits of app testing is that tests can be automated using Continuous Integration (CI). By running tests automatically during development, you can validate that changes to your app don't break existing functionality. You can verify app code as you commit, catch bugs early, and prevent accidental breaks before deployment.
There are many popular CI tools, including GitHub Actions, Jenkins, GitLab CI, Azure DevOps, and Circle CI. Streamlit app testing will integrate easily with any of them similar to any other Python tests.
## GitHub Actions
Since many Streamlit apps (and all Community Cloud apps) are built in GitHub, this page uses examples from GitHub Actions. For more information about GitHub Actions, see:
- Quickstart for GitHub Actions
- GitHub Actions: About continuous integration
- GitHub Actions: Build & test Python
## Streamlit App Action
Streamlit App Action provides an easy way to add automated testing to your app repository in GitHub. It also includes basic smoke testing for each page of your app without you writing any test code.
To install Streamlit App Action, add a workflow `.yml` file to your repository's `.github/workflows/` folder. For example:
```yaml
# .github/workflows/streamlit-app.yml
name: Streamlit app
on:
push:
branches: ["main"]
pull_request:
branches: ["main"]
permissions:
contents: read
jobs:
streamlit:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
with:
python-version: "3.11"
- uses: streamlit/streamlit-app-action@v0.0.3
with:
app-path: streamlit_app.py
```
Let's take a look in more detail at what this action workflow is doing.
### Triggering the workflow
```yaml
on:
push:
branches: ["main"]
pull_request:
branches: ["main"]
```
This workflow will be triggered and execute tests on pull requests targeting the `main` branch, as well as any new commits pushed to the `main` branch. Note that it will also execute the tests on subsequent commits to any open pull requests. See GitHub Actions: Triggering a workflow for more information and examples.
### Setting up the test environment
```yaml
jobs:
streamlit:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
with:
python-version: "3.11"
```
The workflow has a `streamlit` job that executes a series of steps. The job runs on a Docker container with the `ubuntu-latest` image.
- `actions/checkout@v4` checks out the current repository code from GitHub and copies the code to the job environment.
- `actions/setup-python@v5` installs Python version 3.11.
### Running the app tests
```yaml
- uses: streamlit/streamlit-app-action@v0.0.3
with:
app-path: streamlit_app.py
```
Streamlit App Action does the following:
- Install `pytest` and install any dependencies specified in `requirements.txt`.
- Run the built-in app smoke tests.
- Run any other Python tests found in the repository.
Note: If your app doesn't include `requirements.txt` in the repository root directory, you will need to add a step to install dependencies with your chosen package manager before running Streamlit App Action.
The built-in smoke tests have the following behavior:
- Run the app specified at `app-path` as an AppTest.
- Validate that it completes successfully and does not result in an uncaught exception.
- Do the same for any additional `pages/` of the app relative to `app-path`.
If you want to run Streamlit App Action without the smoke tests, you can set `skip-smoke: true`.
### Linting your app code
Linting is the automated checking of source code for programmatic and stylistic errors. This is done by using a lint tool (otherwise known as a linter). Linting is important to reduce errors and improve the overall quality of your code, especially for repositories with multiple developers or public repositories.
You can add automated linting with Ruff by passing `ruff: true` to Streamlit App Action.
```yaml
- uses: streamlit/streamlit-app-action@v0.0.3
with:
app-path: streamlit_app.py
ruff: true
```
Note: You may want to add a pre-commit hook like ruff-pre-commit in your local development environment to fix linting errors before they get to CI.
### Viewing results
If tests fail, the CI workflow will fail and you will see the results in GitHub. Console logs are available by clicking into the workflow run as described here.

For higher-level test results, you can use pytest-results-action. You can combine this with Streamlit App Action as follows:
```yaml
# ... setup as above ...
- uses: streamlit/streamlit-app-action@v0.0.3
with:
app-path: streamlit_app.py
# Add pytest-args to output junit xml
pytest-args: -v --junit-xml=test-results.xml
- if: always()
uses: pmeier/pytest-results-action@v0.6.0
with:
path: test-results.xml
summary: true
display-options: fEX
```

## Writing your own actions
The above is just provided as an example. Streamlit App Action is a quick way to get started. Once you learn the basics of your CI tool of choice, it's easy to build and customize your own automated workflows. This is a great way to improve your overall productivity as a developer and the quality of your apps.
## Working example
As a final working example example, take a look at our `streamlit/llm-examples` Actions, defined in this workflow file.
################################################
Section 2.2 - beyond-the-basics.md
################################################
# Beyond the basics of app testing
Now that you're comfortable with executing a basic test for a Streamlit app let's cover the mutable attributes of [`AppTest`]:
- `AppTest.secrets`
- `AppTest.session_state`
- `AppTest.query_params`
You can read and update values using dict-like syntax for all three attributes. For `.secrets` and `.query_params`, you can use key notation but not attribute notation. For example, the `.secrets` attribute for `AppTest` accepts `at.secrets["my_key"]` but **_not_** `at.secrets.my_key`. This differs from how you can use the associated command in the main library. On the other hand, `.session_state` allows both key notation and attribute notation.
For these attributes, the typical pattern is to declare any values before executing the app's first run. Values can be inspected at any time in a test. There are a few extra considerations for secrets and Session State, which we'll cover now.
## Using secrets with app testing
Be careful not to include secrets directly in your tests. Consider this simple project with `pytest` executed in the project's root directory:
```none
myproject/
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
├── app.py
└── tests/
└── test_app.py
```
```bash
cd myproject
pytest tests/
```
In the above scenario, your simulated app will have access to your `secrets.toml` file. However, since you don't want to commit your secrets to your repository, you may need to write tests where you securely pull your secrets into memory or use dummy secrets.
### Example: declaring secrets in a test
Within a test, declare each secret after initializing your `AppTest` instance but before the first run. (A missing secret may result in an app that doesn't run!) For example, consider the following secrets file and corresponding test initialization to assign the same secrets manually:
Secrets file:
```toml
db_username = "Jane"
db_password = "mypassword"
[my_other_secrets]
things_i_like = ["Streamlit", "Python"]
```
Testing file with equivalent secrets:
```python
# Initialize an AppTest instance.
at = AppTest.from_file("app.py")
# Declare the secrets.
at.secrets["db_username"] = "Jane"
at.secrets["db_password"] = "mypassword"
at.secrets["my_other_secrets.things_i_like"] = ["Streamlit", "Python"]
# Run the app.
at.run()
```
Generally, you want to avoid typing your secrets directly into your test. If you don't need your real secrets for your test, you can declare dummy secrets as in the example above. If your app uses secrets to connect to an external service like a database or API, consider mocking that service in your app tests. If you need to use the real secrets and actually connect, you should use an API to pass them securely and anonymously. If you are automating your tests with GitHub actions, check out their Security guide.
```python
at.secrets["my_key"] = <value provided through API>
```
## Working with Session State in app testing
The `.session_state` attribute for `AppTest` lets you read and update Session State values using key notation (`at.session_state["my_key"]`) and attribute notation (`at.session_state.my_key`). By manually declaring values in Session State, you can directly jump to a specific state instead of simulating many steps to get there. Additionally, the testing framework does not provide native support for multipage apps. An instance of `AppTest` can only test one page. You must manually declare Session State values to simulate a user carrying data from another page.
### Example: testing a multipage app
Consider a simple multipage app where the first page can modify a value in Session State. To test the second page, set Session State manually and run the simulated app within the test:
Project structure:
```none
myproject/
├── pages/
│   └── second.py
├── first.py
└── tests/
└── test_second.py
```
First app page:
```python
"""first.py"""
import streamlit as st
st.session_state.magic_word = st.session_state.get("magic_word", "Streamlit")
new_word = st.text_input("Magic word:")
if st.button("Set the magic word"):
st.session_state.magic_word = new_word
```
Second app page:
```python
"""second.py"""
import streamlit as st
st.session_state.magic_word = st.session_state.get("magic_word", "Streamlit")
if st.session_state.magic_word == "Balloons":
st.markdown(":balloon:")
```
Testing file:
```python
"""test_second.py"""
from streamlit.testing.v1 import AppTest
def test_balloons():
at = AppTest.from_file("pages/second.py")
at.session_state["magic_word"] = "Balloons"
at.run()
assert at.markdown[0].value == ":balloon:"
```
By setting the value `at.session_state["magic_word"] = "Balloons"` within the test, you can simulate a user navigating to `second.py` after entering and saving "Balloons" on `first.py`.
################################################
Section 2.3 - cheat-sheet.md
################################################
# App testing cheat sheet
## Text elements
```python
from streamlit.testing.v1 import AppTest
at = AppTest.from_file("cheatsheet_app.py")
# Headers
assert "My app" in at.title[0].value
assert "New topic" in at.header[0].value
assert "Interesting sub-topic" in at.subheader[0].value
assert len(at.divider) == 2
# Body / code
assert "Hello, world!" in at.markdown[0].value
assert "import streamlit as st" in at.code[0].value
assert "A cool diagram" in at.caption[0].value
assert "Hello again, world!" in at.text[0].value
assert "\int a x^2 \,dx" in at.latex[0].value
```
## Input widgets
```python
from streamlit.testing.v1 import AppTest
at = AppTest.from_file("cheatsheet_app.py")
# button
assert at.button[0].value == False
at.button[0].click().run()
assert at.button[0].value == True
# checkbox
assert at.checkbox[0].value == False
at.checkbox[0].check().run() # uncheck() is also supported
assert at.checkbox[0].value == True
# color_picker
assert at.color_picker[0].value == "#FFFFFF"
at.color_picker[0].pick("#000000").run()
# date_input
assert at.date_input[0].value == datetime.date(2019, 7, 6)
at.date_input[0].set_value(datetime.date(2022, 12, 21)).run()
# form_submit_button - shows up just like a button
assert at.button[0].value == False
at.button[0].click().run()
assert at.button[0].value == True
# multiselect
assert at.multiselect[0].value == ["foo", "bar"]
at.multiselect[0].select("baz").unselect("foo").run()
# number_input
assert at.number_input[0].value == 5
at.number_input[0].increment().run()
# radio
assert at.radio[0].value == "Bar"
assert at.radio[0].index == 3
at.radio[0].set_value("Foo").run()
# selectbox
assert at.selectbox[0].value == "Bar"
assert at.selectbox[0].index == 3
at.selectbox[0].set_value("Foo").run()
# select_slider
assert at.select_slider[0].value == "Feb"
at.select_slider[0].set_value("Mar").run()
at.select_slider[0].set_range("Apr", "Jun").run()
# slider
assert at.slider[0].value == 2
at.slider[0].set_value(3).run()
at.slider[0].set_range(4, 6).run()
# text_area
assert at.text_area[0].value == "Hello, world!"
at.text_area[0].set_value("Hello, yourself!").run()
# text_input
assert at.text_input[0].value == "Hello, world!")
at.text_input[0].set_value("Hello, yourself!").run()
# time_input
assert at.time_input[0].value == datetime.time(8, 45)
at.time_input[0].set_value(datetime.time(12, 30))
# toggle
assert at.toggle[0].value == False
assert at.toggle[0].label == "Debug mode"
at.toggle[0].set_value(True).run()
assert at.toggle[0].value == True
```
## Data elements
```python
from streamlit.testing.v1 import AppTest
at = AppTest.from_file("cheatsheet_app.py")
# dataframe
expected_df = pd.DataFrame([1, 2, 3])
assert at.dataframe[0].value.equals(expected_df)
# metric
assert at.metric[0].value == "9500"
assert at.metric[0].delta == "1000"
# json
assert at.json[0].value == '["hi", {"foo": "bar"}]'
# table
table_df = pd.DataFrame([1, 2, 3])
assert at.table[0].value.equals(table_df)
```
## Layouts and containers
```python
from streamlit.testing.v1 import AppTest
at = AppTest.from_file("cheatsheet_app.py")
# sidebar
at.sidebar.text_input[0].set_value("Jane Doe")
# columns
at.columns[1].markdown[0].value == "Hello, world!"
# tabs
at.tabs[2].markdown[0].value == "Hello, yourself!"
```
## Chat elements
```python
from streamlit.testing.v1 import AppTest
at = AppTest.from_file("cheatsheet_app.py")
# chat_input
at.chat_input[0].set_value("Do you know any jokes?").run()
# Note: chat_input value clears after every re-run (like in a real app)
# chat_message
assert at.chat_message[0].markdown[0].value == "Do you know any jokes?"
assert at.chat_message[0].avatar == "user"
```
## Status elements
```python
from streamlit.testing.v1 import AppTest
at = AppTest.from_file("cheatsheet_app.py")
# exception
assert len(at.exception) == 1
assert "TypeError" in at.exception[0].value
# Other in-line alerts: success, info, warning, error
assert at.success[0].value == "Great job!"
assert at.info[0].value == "Please enter an API key to continue"
assert at.warning[0].value == "Sorry, the passwords didn't match"
assert at.error[0].value == "Something went wrong :("
# toast
assert at.toast[0].value == "That was lit!" and at.toast[0].icon == "🔥"
```
## Limitations
As of Streamlit 1.28, the following Streamlit features are not natively supported by `AppTest`. However, workarounds are possible for many of them by inspecting the underlying proto directly using `AppTest.get()`. We plan to regularly add support for missing elements until all features are supported.
- Chart elements (`st.bar_chart`, `st.line_chart`, etc)
- Media elements (`st.image`, `st.video`, `st.audio`)
- `st.file_uploader`
- `st.data_editor`
- `st.expander`
- `st.status`
- `st.camera_input`
- `st.download_button`
- `st.link_button`
################################################
Section 2.4 - examples.md
################################################
# App testing example
## Testing a login page
Let's consider a login page. In this example, `secrets.toml` is not present. We'll manually declare dummy secrets directly in the tests. To avoid timing attacks, the login script uses `hmac` to compare a user's password to the secret value as a security best practice.
### Project summary
#### Login page behavior
Before diving into the app's code, let's think about what this page is supposed to do. Whether you use test-driven development or you write unit tests after your code, it's a good idea to think about the functionality that needs to be tested. The login page should behave as follows:
- Before a user interacts with the app:
- Their status is "unverified."
- A password prompt is displayed.
- If a user types an incorrect password:
- Their status is "incorrect."
- An error message is displayed.
- The password attempt is cleared from the input.
- If a user types a correct password:
- Their status is "verified."
- A confirmation message is displayed.
- A logout button is displayed (without a login prompt).
- If a logged-in user clicks the **Log out** button:
- Their status is "unverified."
- A password prompt is displayed.
#### Login page project structure
```none
myproject/
├── app.py
└── tests/
└── test_app.py
```
#### Login page Python file
The user's status mentioned in the page's specifications are encoded in `st.session_state.status`. This value is initialized at the beginning of the script as "unverified" and is updated through a callback when the password prompt receives a new entry.
```python
"""app.py"""
import streamlit as st
import hmac
st.session_state.status = st.session_state.get("status", "unverified")
st.title("My login page")
def check_password():
if hmac.compare_digest(st.session_state.password, st.secrets.password):
st.session_state.status = "verified"
else:
st.session_state.status = "incorrect"
st.session_state.password = ""
def login_prompt():
st.text_input("Enter password:", key="password", on_change=check_password)
if st.session_state.status == "incorrect":
st.warning("Incorrect password. Please try again.")
def logout():
st.session_state.status = "unverified"
def welcome():
st.success("Login successful.")
st.button("Log out", on_click=logout)
if st.session_state.status != "verified":
login_prompt()
st.stop()
welcome()
```
#### Login page test file
These tests closely follow the app's specifications above. In each test, a dummy secret is set before running the app and proceeding with further simulations and checks.
```python
from streamlit.testing.v1 import AppTest
def test_no_interaction():
at = AppTest.from_file("app.py")
at.secrets["password"] = "streamlit"
at.run()
assert at.session_state["status"] == "unverified"
assert len(at.text_input) == 1
assert len(at.warning) == 0
assert len(at.success) == 0
assert len(at.button) == 0
assert at.text_input[0].value == ""
def test_incorrect_password():
at = AppTest.from_file("app.py")
at.secrets["password"] = "streamlit"
at.run()
at.text_input[0].input("balloon").run()
assert at.session_state["status"] == "incorrect"
assert len(at.text_input) == 1
assert len(at.warning) == 1
assert len(at.success) == 0
assert len(at.button) == 0
assert at.text_input[0].value == ""
assert "Incorrect password" in at.warning[0].value
def test_correct_password():
at = AppTest.from_file("app.py")
at.secrets["password"] = "streamlit"
at.run()
at.text_input[0].input("streamlit").run()
assert at.session_state["status"] == "verified"
assert len(at.text_input) == 0
assert len(at.warning) == 0
assert len(at.success) == 1
assert len(at.button) == 1
assert "Login successful" in at.success[0].value
assert at.button[0].label == "Log out"
def test_log_out():
at = AppTest.from_file("app.py")
at.secrets["password"] = "streamlit"
at.session_state["status"] = "verified"
at.run()
at.button[0].click().run()
assert at.session_state["status"] == "unverified"
assert len(at.text_input) == 1
assert len(at.warning) == 0
assert len(at.success) == 0
assert len(at.button) == 0
assert at.text_input[0].value == ""
```
See how Session State was modified in the last test? Instead of fully simulating a user logging in, the test jumps straight to a logged-in state by setting `at.session_state["status"] = "verified"`. After running the app, the test proceeds to simulate the user logging out.
### Automating your tests
If `myproject/` was pushed to GitHub as a repository, you could add GitHub Actions test automation with Streamlit App Action. This is as simple as adding a workflow file at `myproject/.github/workflows/`:
```yaml
# .github/workflows/streamlit-app.yml
name: Streamlit app
on:
push:
branches: ["main"]
pull_request:
branches: ["main"]
permissions:
contents: read
jobs:
streamlit:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
with:
python-version: "3.11"
- uses: streamlit/streamlit-app-action@v0.0.3
with:
app-path: app.py
```
################################################
Section 2.5 - get-started.md
################################################
# Get started with app testing
This guide will cover a simple example of how tests are structured within a project and how to execute them with `pytest`. After seeing the big picture, keep reading to learn about the [Fundamentals of app testing](#fundamentals-of-app-testing):
- Initializing and running a simulated app
- Retrieving elements
- Manipulating widgets
- Inspecting the results
Streamlit's app testing framework is not tied to any particular testing tool, but we'll use `pytest` for our examples since it is one of the most common Python test frameworks. To try out the examples in this guide, be sure to install `pytest` into your Streamlit development environment before you begin:
```bash
pip install pytest
```
## A simple testing example with `pytest`
This section explains how a simple test is structured and executed with `pytest`. For a comprehensive introduction to `pytest`, check out Real Python's guide to Effective Python testing with pytest.
### How `pytest` is structured
`pytest` uses a naming convention for files and functions to execute tests conveniently. Name your test scripts of the form `test_<name>.py` or `<name>_test.py`. For example, you can use `test_myapp.py` or `myapp_test.py`. Within your test scripts, each test is written as a function. Each function is named to begin or end with `test`. We will prefix all our test scripts and test functions with `test_` for our examples in this guide.
You can write as many tests (functions) within a single test script as you want. When calling `pytest` in a directory, all `test_<name>.py` files within it will be used for testing. This includes files within subdirectories. Each `test_<something>` function within those files will be executed as a test. You can place test files anywhere in your project directory, but it is common to collect tests into a designated `tests/` directory. For other ways to structure and execute tests, check out How to invoke pytest in the `pytest` docs.
### Example project with app testing
Consider the following project:
```none
myproject/
├── app.py
└── tests/
└── test_app.py
```
Main app file:
```python
"""app.py"""
import streamlit as st
# Initialize st.session_state.beans
st.session_state.beans = st.session_state.get("beans", 0)
st.title("Bean counter :paw_prints:")
addend = st.number_input("Beans to add", 0, 10)
if st.button("Add"):
st.session_state.beans += addend
st.markdown(f"Beans counted: {st.session_state.beans}")
```
Testing file:
```python
"""test_app.py"""
from streamlit.testing.v1 import AppTest
def test_increment_and_add():
"""A user increments the number input, then clicks Add"""
at = AppTest.from_file("app.py").run()
at.number_input[0].increment().run()
at.button[0].click().run()
assert at.markdown[0].value == "Beans counted: 1"
```
Let's take a quick look at what's in this app and test before we run it. The main app file (`app.py`) contains four elements when rendered: `st.title`, `st.number_input`, `st.button`, and `st.markdown`. The test script (`test_app.py`) includes a single test (the function named `test_increment_and_add`). We'll cover test syntax in more detail in the latter half of this guide, but here's a brief explanation of what this test does:
1. Initialize the simulated app and execute the first script run.
```python
at = AppTest.from_file("app.py").run()
```
2. Simulate a user clicking the plus icon (<i style={{ verticalAlign: "-.25em" }} className={{ class: "material-icons-sharp" }}>add</i>) to increment the number input (and the resulting script rerun).
```python
at.number_input[0].increment().run()
```
3. Simulate a user clicking the "**Add**" button (and the resulting script rerun).
```python
at.button[0].click().run()
```
4. Check if the correct message is displayed at the end.
```python
assert at.markdown[0].value == "Beans counted: 1"
```
Assertions are the heart of tests. When the assertion is true, the test passes. When the assertion is false, the test fails. A test can have multiple assertions, but keeping tests tightly focused is good practice. When tests focus on a single behavior, it is easier to understand and respond to failure.
### Try out a simple test with `pytest`
1. Copy the files above into a new "myproject" directory.
2. Open a terminal and change directory to your project.
```bash
cd myproject
```
3. Execute `pytest`:
```bash
pytest
```
The test should execute successfully. Your terminal should show something like this:

By executing `pytest` at the root of your project directory, all Python files with the test prefix (`test_<name>.py`) will be scanned for test functions. Within each test file, each function with the test prefix will be executed as a test. `pytest` then counts successes and itemizes failures. You can also direct `pytest` to only scan your testing directory. For example, from the root of your project directory, execute:
```bash
pytest tests/
```
### Handling file paths and imports with `pytest`
Imports and paths within a test script should be relative to the directory where `pytest` is called. That is why the test function uses the path `app.py` instead of `../app.py` even though the app file is one directory up from the test script. You'll usually call `pytest` from the directory containing your main app file. This is typically the root of your project directory.
Additionally, if `.streamlit/` is present in the directory where you call `pytest`, any `config.toml` and `secrets.toml` within it will be accessible to your simulated app. For example, your simulated app will have access to the `config.toml` and `secrets.toml` files in this common setup:
Project structure:
```none
myproject/
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
├── app.py
└── tests/
└── test_app.py
```
Initialization within `test_app.py`:
```python
# Path to app file is relative to myproject/
at = AppTest.from_file("app.py").run()
```
Command to execute tests:
```bash
cd myproject
pytest tests/
```
## Fundamentals of app testing
Now that you understand the basics of `pytest` let's dive into using Streamlit's app testing framework. Every test begins with initializing and running your simulated app. Additional commands are used to retrieve, manipulate, and inspect elements.
On the next page, we'll go [Beyond the basics] and cover more advanced scenarios like working with secrets, Session State, or multipage apps.
### How to initialize and run a simulated app
To test a Streamlit app, you must first initialize an instance of [`AppTest`] with the code for one page of your app. There are three methods for initializing a simulated app. These are provided as class methods to `AppTest`. We will focus on `AppTest.from_file()` which allows you to provide a path to a page of your app. This is the most common scenario for building automated tests during app development. `AppTest.from_string()` and `AppTest.from_function()` may be helpful for some simple or experimental scenarios.
Let's continue with the [example from above](#example-project-with-app-testing).
Recall the testing file:
```python
"""test_app.py"""
from streamlit.testing.v1 import AppTest
def test_increment_and_add():
"""A user increments the number input, then clicks Add"""
at = AppTest.from_file("app.py").run()
at.number_input[0].increment().run()
at.button[0].click().run()
assert at.markdown[0].value == "Beans counted: 1"
```
Look at the first line in the test function:
```python
at = AppTest.from_file("app.py").run()
```
This is doing two things and is equivalent to:
```python
# Initialize the app.
at = AppTest.from_file("app.py")
# Run the app.
at.run()
```
`AppTest.from_file()` returns an instance of `AppTest`, initialized with the contents of `app.py`. The `.run()` method is used to run the app for the first time. Looking at the test, notice that the `.run()` method manually executes each script run. A test must explicitly run the app each time. This applies to the app's first run and any rerun resulting from simulated user input.
### How to retrieve elements
The attributes of the `AppTest` class return sequences of elements. The elements are sorted according to display order in the rendered app. Specific elements can be retrieved by index. Additionally, widgets with keys can be retrieved by key.
#### Retrieve elements by index
Each attribute of `AppTest` returns a sequence of the associated element type. Specific elements can be retrieved by index. In the above example, `at.number_input` returns a sequence of all `st.number_input` elements in the app. Thus, `at.number_input[0]` is the first such element in the app. Similarly, `at.markdown` returns a collection of all `st.markdown` elements where `at.markdown[0]` is the first such element.
The returned sequence of elements is ordered by appearance on the page. If containers are used to insert elements in a different order, these sequences may not match the order within your code. Consider the following example where containers are used to switch the order of two buttons on the page:
```python
import streamlit as st
first = st.container()
second = st.container()
second.button("A")
first.button("B")
```
If the above app was tested, the first button (`at.button[0]`) would be labeled "B" and the second button (`at.button[1]`) would be labeled "A." As true assertions, these would be:
```python
assert at.button[0].label == "B"
assert at.button[1].label == "A"
```
#### Retrieve widgets by key
You can retrieve keyed widgets by their keys instead of their order on the page. The key of the widget is passed as either an arg or kwarg. For example, look at this app and the following (true) assertions:
```python
import streamlit as st
st.button("Next", key="submit")
st.button("Back", key="cancel")
```
```python
assert at.button(key="submit").label == "Next"
assert at.button("cancel").label == "Back"
```
#### Retrieve containers
You can also narrow down your sequences of elements by retrieving specific containers. Each retrieved container has the same attributes as `AppTest`. For example, `at.sidebar.checkbox` returns a sequence of all checkboxes in the sidebar. `at.main.selectbox` returns the sequence of all selectboxes in the main body of the app (not in the sidebar).
For `AppTest.columns` and `AppTest.tabs`, a sequence of containers is returned. So `at.columns[0].button` would be the sequence of all buttons in the first column appearing in the app.
### How to manipulate widgets
All widgets have a universal `.set_value()` method. Additionally, many widgets have specific methods for manipulating their value. The names of [Testing element classes] closely match the names of the `AppTest` attributes. For example, look at the return type of [`AppTest.button`] to see the corresponding class of [`Button`]. Aside from setting the value of a button with `.set_value()`, you can also use `.click()`. ### How to inspect elements
All elements, including widgets, have a universal `.value` property. This returns the contents of the element. For widgets, this is the same as the return value or value in Session State. For non-input elements, this will be the value of the primary contents argument. For example, `.value` returns the value of `body` for `st.markdown` or `st.error`. It returns the value of `data` for `st.dataframe` or `st.table`.
Additionally, you can check many other details for widgets like labels or disabled status. Many parameters are available for inspection, but not all. Use linting software to see what is currently supported. Here's an example:
```python
import streamlit as st
st.selectbox("A", [1,2,3], None, help="Pick a number", placeholder="Pick me")
```
```python
assert at.selectbox[0].value == None
assert at.selectbox[0].label == "A"
assert at.selectbox[0].options == ["1","2","3"]
assert at.selectbox[0].index == None
assert at.selectbox[0].help == "Pick a number"
assert at.selectbox[0].placeholder == "Pick me"
assert at.selectbox[0].disabled == False
```
Note: Note that the `options` for `st.selectbox` were declared as integers but asserted as strings. As noted in the documentation for [`st.selectbox`], options are cast internally to strings. If you ever find yourself getting unexpected results, check the documentation carefully for any notes about recasting types internally.
------------------------------------------------------------------------------------------------
CHAPTER 3: architecture.md
------------------------------------------------------------------------------------------------
################################################
Section 3.1 - app-chrome.md
################################################
# The app chrome
Your Streamlit app has a few widgets in the top right to help you as you develop. These widgets also help your viewers as they use your app. We call this things “the app chrome”. The chrome includes a status area, toolbar, and app menu.
Your app menu is configurable. By default, you can access developer options from the app menu when viewing an app locally or on Streamlit Community Cloud while logged into an account with administrative access. While viewing an app, click the icon in the upper-right corner to access the menu.

## Menu options
The menu is split into two sections. The upper section contains options available to all viewers and the lower section contains options for developers. ### Rerun
You can manually trigger a rerun of your app by clicking "**Rerun**" from the app menu. This rerun will not reset your session. Your widget states and values stored in [`st.session_state`] will be preserved. As a shortcut, without opening the app menu, you can rerun your app by pressing "**R**" on your keyboard (if you aren't currently focused on an input element).
### Settings
With the "**Settings**" option, you can control the appearance of your app while it is running. If viewing the app locally, you can set how your app responds to changes in your source code. See more about development flow in [Basic concepts](/get-started/fundamentals/main-concepts#development-flow). You can also force your app to appear in wide mode, even if not set within the script using [`st.set_page_config`].
#### Theme settings
After clicking "**Settings**" from the app menu, you can choose between "**Light**", "**Dark**", or "**Use system setting**" for the app's base theme. Click "**Edit active theme**" to modify the theme, color-by-color.

### Print
Click "**Print**" or use keyboard shortcuts (`⌘+P` or `Ctrl+P`) to open a print dialog. This option uses your browser's built-in print-to-pdf function. To modify the appearance of your print, you can do the following:
- Expand or collapse the sidebar before printing to respectively include or exclude it from the print.
- Resize the sidebar in your app by clicking and dragging its right border to achieve your desired width.
- You may need to enable "**Background graphics**" in your print dialog if you are printing in dark mode.
- You may need to disable wide mode in [Settings](#settings) or adjust the print scale to prevent elements from clipping off the page.
### Record a screencast
You can easily make screen recordings right from your app! Screen recording is supported in the latest versions of Chrome, Edge, and Firefox. Ensure your browser is up-to-date for compatibility. Depending on your current settings, you may need to grant permission to your browser to record your screen or to use your microphone if recording a voiceover.
1. While viewing your app, open the app menu from the upper-right corner.
2. Click "**Record a screencast**."
3. If you want to record audio through your microphone, check "**Also record audio**."
4. Click "**Start recording**." (You may be prompted by your OS to permit your browser to record your screen or use your microphone.)

5. Select which tab, window, or monitor you want to record from the listed options. The interface will vary depending on your browser.

6. Click "**Share**."

7. While recording, you will see a red circle on your app's tab and on the app menu icon. If you want to cancel the recording, click "**Stop sharing**" at the bottom of your app.

8. When you are done recording, press "**Esc**" on your keyboard or click "**Stop recording**" from your app's menu.

9. Follow your browser's instructions to save your recording. Your saved recording will be available where your browser saves downloads.
The whole process looks like this:

### About
You can conveniently check what version of Streamlit is running from the "**About**" option. Developers also have the option to customize the message shown here using [`st.set_page_config`].
## Developer options
By default, developer options only show when viewing an app locally or when viewing a Community Cloud app while logged in with administrative permission. You can [customize the menu](#customize-the-menu) if you want to make these options available for all users.
### Clear cache
Reset your app's cache by clicking "**Clear cache**" from the app's menu or by pressing "**C**" on your keyboard while not focused on an input element. This will remove all cached entries for [`@st.cache_data`] and [`@st.cache_resource`].
### Deploy this app
If you are running an app locally from within a git repo, you can deploy your app to Streamlit Community Cloud in a few easy clicks! Make sure your work has been pushed to your online GitHub repository before beginning. For the greatest convenience, make sure you have already created your [Community Cloud account](/deploy/streamlit-community-cloud/get-started/create-your-account) and are signed in.
1. Click "**Deploy**" next to the app menu icon (<i style={{ verticalAlign: "-.25em" }} className={{ class: "material-icons-sharp" }}>more_vert</i>).

2. Click "**Deploy now**."

3. You will be taken to Community Cloud's "Deploy an app" page. Your app's repository, branch, and file name will be prefilled to match your current app! Learn more about [deploying an app](/deploy/streamlit-community-cloud/deploy-your-app) on Streamlit Community Cloud.
The whole process looks like this:

## Customize the menu
Using `client.toolbarMode` in your app's [configuration], you can make the app menu appear in the following ways:
- `"developer"` &mdash; Show the developer options to all viewers.
- `"viewer"` &mdash; Hide the developer options from all viewers.
- `"minimal"` &mdash; Show only those options set externally. These options can be declared through [`st.set_page_config`] or populated through Streamlit Community Cloud.
- `"auto"` &mdash; This is the default and will show the developer options when accessed through localhost or through Streamlit Community Cloud when logged into an administrative account for the app. Otherwise, the developer options will not show.
################################################
Section 3.2 - architecture.md
################################################
# Understanding Streamlit's client-server architecture
Streamlit apps have a client-server structure. The Python backend of your app is the server. The frontend you view through a browser is the client. When you develop an app locally, your computer runs both the server and the client. If someone views your app across a local or global network, the server and client run on different machines. If you intend to share or deploy your app, it's important to understand this client-server structure to avoid common pitfalls.
## Python backend (server)
When you execute the command `streamlit run your_app.py`, your computer uses Python to start up a Streamlit server. This server is the brains of your app and performs the computations for all users who view your app. Whether users view your app across a local network or the internet, the Streamlit server runs on the one machine where the app was initialized with `streamlit run`. The machine running your Streamlit server is also called a host.
## Browser frontend (client)
When someone views your app through a browser, their device is a Streamlit client. When you view your app from the same computer where you are running or developing your app, then server and client are coincidentally running on the same machine. However, when users view your app across a local network or the internet, the client runs on a different machine from the server.
## Server-client impact on app design
Keep in mind the following considerations when building your Streamlit app:
- The computer running or hosting your Streamlit app is responsible for providing the compute and storage necessary to run your app for all users and must be sized appropriately to handle concurrent users.
- Your app will not have access to a user's files, directories, or OS. Your app can only work with specific files a user has uploaded to your app through a widget like `st.file_uploader`.
- If your app communicates with any peripheral devices (like cameras), you must use Streamlit commands or custom components that will access those devices _through the user's browser_ and correctly communicate between the client (frontend) and server (backend).
- If your app opens or uses any program or process outside of Python, they will run on the server. For example, you may want to use `webrowser` to open a browser for the user, but this will not work as expected when viewing your app over a network; it will open a browser on the Streamlit server, unseen by the user.
################################################
Section 3.3 - caching.md
################################################
# Caching overview
Note: Documentation for the deprecated `@st.cache` decorator can be found in [Optimize performance with st.cache].
# Caching overview
Streamlit runs your script from top to bottom at every user interaction or code change. This execution model makes development super easy. But it comes with two major challenges:
1. Long-running functions run again and again, which slows down your app.
2. Objects get recreated again and again, which makes it hard to persist them across reruns or sessions.
But don't worry! Streamlit lets you tackle both issues with its built-in caching mechanism. Caching stores the results of slow function calls, so they only need to run once. This makes your app much faster and helps with persisting objects across reruns. Cached values are available to all users of your app. If you need to save results that should only be accessible within a session, use [Session State] instead.
<Collapse title="Table of contents" expanded={true}>
1. [Minimal example](#minimal-example)
2. [Basic usage](#basic-usage)
3. [Advanced usage](#advanced-usage)
4. [Migrating from st.cache](#migrating-from-stcache)
</Collapse>
## Minimal example
To cache a function in Streamlit, you must decorate it with one of two decorators (`st.cache_data` or `st.cache_resource`):
```python
@st.cache_data
def long_running_function(param1, param2):
return …
```
In this example, decorating `long_running_function` with `@st.cache_data` tells Streamlit that whenever the function is called, it checks two things:
1. The values of the input parameters (in this case, `param1` and `param2`).
2. The code inside the function.
If this is the first time Streamlit sees these parameter values and function code, it runs the function and stores the return value in a cache. The next time the function is called with the same parameters and code (e.g., when a user interacts with the app), Streamlit will skip executing the function altogether and return the cached value instead. During development, the cache updates automatically as the function code changes, ensuring that the latest changes are reflected in the cache.
As mentioned, there are two caching decorators:
- `st.cache_data` is the recommended way to cache computations that return data: loading a DataFrame from CSV, transforming a NumPy array, querying an API, or any other function that returns a serializable data object (str, int, float, DataFrame, array, list, …). It creates a new copy of the data at each function call, making it safe against [mutations and race conditions](#mutation-and-concurrency-issues). The behavior of `st.cache_data` is what you want in most cases – so if you're unsure, start with `st.cache_data` and see if it works!
- `st.cache_resource` is the recommended way to cache global resources like ML models or database connections – unserializable objects that you don't want to load multiple times. Using it, you can share these resources across all reruns and sessions of an app without copying or duplication. Note that any mutations to the cached return value directly mutate the object in the cache (more details below).

## Basic usage
### st.cache_data
`st.cache_data` is your go-to command for all functions that return data – whether DataFrames, NumPy arrays, str, int, float, or other serializable types. It's the right command for almost all use cases! Within each user session, an `@st.cache_data`-decorated function returns a _copy_ of the cached return value (if the value is already cached).
#### Usage
Let's look at an example of using `st.cache_data`. Suppose your app loads the Uber ride-sharing dataset – a CSV file of 50 MB – from the internet into a DataFrame:
```python
def load_data(url):
df = pd.read_csv(url)  # 👈 Download the data
return df
df = load_data("https://github.com/plotly/datasets/raw/master/uber-rides-data1.csv")
st.dataframe(df)
st.button("Rerun")
```
Running the `load_data` function takes 2 to 30 seconds, depending on your internet connection. (Tip: if you are on a slow connection, use this 5 MB dataset instead). Without caching, the download is rerun each time the app is loaded or with user interaction. Try it yourself by clicking the button we added! Not a great experience… 😕
Now let's add the `@st.cache_data` decorator on `load_data`:
```python
@st.cache_data  # 👈 Add the caching decorator
def load_data(url):
df = pd.read_csv(url)
return df
df = load_data("https://github.com/plotly/datasets/raw/master/uber-rides-data1.csv")
st.dataframe(df)
st.button("Rerun")
```
Run the app again. You'll notice that the slow download only happens on the first run. Every subsequent rerun should be almost instant! 💨
#### Behavior
How does this work? Let's go through the behavior of `st.cache_data` step by step:
- On the first run, Streamlit recognizes that it has never called the `load_data` function with the specified parameter value (the URL of the CSV file) So it runs the function and downloads the data.
- Now our caching mechanism becomes active: the returned DataFrame is serialized (converted to bytes) via pickle and stored in the cache (together with the value of the `url` parameter).
- On the next run, Streamlit checks the cache for an entry of `load_data` with the specific `url`. There is one! So it retrieves the cached object, deserializes it to a DataFrame, and returns it instead of re-running the function and downloading the data again.
This process of serializing and deserializing the cached object creates a copy of our original DataFrame. While this copying behavior may seem unnecessary, it's what we want when caching data objects since it effectively prevents mutation and concurrency issues. Read the section “[Mutation and concurrency issues](#mutation-and-concurrency-issues)" below to understand this in more detail.
Note: `st.cache_data` implicitly uses the `pickle` module, which is known to be insecure. Anything your cached function returns is pickled and stored, then unpickled on retrieval. Ensure your cached functions return trusted values because it is possible to construct malicious pickle data that will execute arbitrary code during unpickling. Never load data that could have come from an untrusted source in an unsafe mode or that could have been tampered with. **Only load data you trust**.
#### Examples
**DataFrame transformations**
In the example above, we already showed how to cache loading a DataFrame. It can also be useful to cache DataFrame transformations such as `df.filter`, `df.apply`, or `df.sort_values`. Especially with large DataFrames, these operations can be slow.
```python
@st.cache_data
def transform(df):
df = df.filter(items=['one', 'three'])
df = df.apply(np.sum, axis=0)
return df
```
**Array computations**
Similarly, it can make sense to cache computations on NumPy arrays:
```python
@st.cache_data
def add(arr1, arr2):
return arr1 + arr2
```
**Database queries**
You usually make SQL queries to load data into your app when working with databases. Repeatedly running these queries can be slow, cost money, and degrade the performance of your database. We strongly recommend caching any database queries in your app. See also [our guides on connecting Streamlit to different databases] for in-depth examples.
```python
connection = database.connect()
@st.cache_data
def query():
return pd.read_sql_query("SELECT * from table", connection)
```
Note: You should set a `ttl` (time to live) to get new results from your database. If you set `st.cache_data(ttl=3600)`, Streamlit invalidates any cached values after 1 hour (3600 seconds) and runs the cached function again. See details in [Controlling cache size and duration](#controlling-cache-size-and-duration).
**API calls**
Similarly, it makes sense to cache API calls. Doing so also avoids rate limits.
```python
@st.cache_data
def api_call():
response = requests.get('https://jsonplaceholder.typicode.com/posts/1')
return response.json()
```
**Running ML models (inference)**
Running complex machine learning models can use significant time and memory. To avoid rerunning the same computations over and over, use caching.
```python
@st.cache_data
def run_model(inputs):
return model(inputs)
```
### st.cache_resource
`st.cache_resource` is the right command to cache “resources" that should be available globally across all users, sessions, and reruns. It has more limited use cases than `st.cache_data`, especially for caching database connections and ML models. Within each user session, an `@st.cache_resource`-decorated function returns the cached instance of the return value (if the value is already cached). Therefore, objects cached by `st.cache_resource` act like singletons and can mutate.
#### Usage
As an example for `st.cache_resource`, let's look at a typical machine learning app. As a first step, we need to load an ML model. We do this with Hugging Face's transformers library:
```python
from transformers import pipeline
model = pipeline("sentiment-analysis")  # 👈 Load the model
```
If we put this code into a Streamlit app directly, the app will load the model at each rerun or user interaction. Repeatedly loading the model poses two problems:
- Loading the model takes time and slows down the app.
- Each session loads the model from scratch, which takes up a huge amount of memory.
Instead, it would make much more sense to load the model once and use that same object across all users and sessions. That's exactly the use case for `st.cache_resource`! Let's add it to our app and process some text the user entered:
```python
from transformers import pipeline
@st.cache_resource  # 👈 Add the caching decorator
def load_model():
return pipeline("sentiment-analysis")
model = load_model()
query = st.text_input("Your query", value="I love Streamlit! 🎈")
if query:
result = model(query)[0]  # 👈 Classify the query text
st.write(result)
```
If you run this app, you'll see that the app calls `load_model` only once – right when the app starts. Subsequent runs will reuse that same model stored in the cache, saving time and memory!
#### Behavior
Using `st.cache_resource` is very similar to using `st.cache_data`. But there are a few important differences in behavior:
- `st.cache_resource` does **not** create a copy of the cached return value but instead stores the object itself in the cache. All mutations on the function's return value directly affect the object in the cache, so you must ensure that mutations from multiple sessions do not cause problems. In short, the return value must be thread-safe.
Note:   Using `st.cache_resource` on objects that are not thread-safe might lead to crashes or corrupted data. Learn more below under [Mutation and concurrency issues](#mutation-and-concurrency-issues).
</Warning>
- Not creating a copy means there's just one global instance of the cached return object, which saves memory, e.g. when using a large ML model. In computer science terms, we create a singleton.
- Return values of functions do not need to be serializable. This behavior is great for types not serializable by nature, e.g., database connections, file handles, or threads. Caching these objects with `st.cache_data` is not possible.
#### Examples
**Database connections**
`st.cache_resource` is useful for connecting to databases. Usually, you're creating a connection object that you want to reuse globally for every query. Creating a new connection object at each run would be inefficient and might lead to connection errors. That's exactly what `st.cache_resource` can do, e.g., for a Postgres database:
```python
@st.cache_resource
def init_connection():
host = "hh-pgsql-public.ebi.ac.uk"
database = "pfmegrnargs"
user = "reader"
password = "NWDMCE5xdipIjRrp"
return psycopg2.connect(host=host, database=database, user=user, password=password)
conn = init_connection()
```
Of course, you can do the same for any other database. Have a look at [our guides on how to connect Streamlit to databases] for in-depth examples.
**Loading ML models**
Your app should always cache ML models, so they are not loaded into memory again for every new session. See the [example](#usage-1) above for how this works with 🤗 Hugging Face models. You can do the same thing for PyTorch, TensorFlow, etc. Here's an example for PyTorch:
```python
@st.cache_resource
def load_model():
model = torchvision.models.resnet50(weights=ResNet50_Weights.DEFAULT)
model.eval()
return model
model = load_model()
```
### Deciding which caching decorator to use
The sections above showed many common examples for each caching decorator. But there are edge cases for which it's less trivial to decide which caching decorator to use. Eventually, it all comes down to the difference between “data" and “resource":
- Data are serializable objects (objects that can be converted to bytes via pickle) that you could easily save to disk. Imagine all the types you would usually store in a database or on a file system – basic types like str, int, and float, but also arrays, DataFrames, images, or combinations of these types (lists, tuples, dicts, and so on).
- Resources are unserializable objects that you usually would not save to disk or a database. They are often more complex, non-permanent objects like database connections, ML models, file handles, threads, etc.
From the types listed above, it should be obvious that most objects in Python are “data." That's also why `st.cache_data` is the correct command for almost all use cases. `st.cache_resource` is a more exotic command that you should only use in specific situations.
Or if you're lazy and don't want to think too much, look up your use case or return type in the table below 😉:
| Use case                             |                                                                                                       Typical return types |                                                                                                                                            Caching decorator |
| :----------------------------------- | -------------------------------------------------------------------------------------------------------------------------: | -----------------------------------------------------------------------------------------------------------------------------------------------------------: |
| Reading a CSV file with pd.read_csv  |                                                                                                           pandas.DataFrame |                                                                                                                                                st.cache_data |
| Reading a text file                  |                                                                                                           str, list of str |                                                                                                                                                st.cache_data |
| Transforming pandas dataframes       |                                                                                            pandas.DataFrame, pandas.Series |                                                                                                                                                st.cache_data |
| Computing with numpy arrays          |                                                                                                              numpy.ndarray |                                                                                                                                                st.cache_data |
| Simple computations with basic types |                                                                                                         str, int, float, … |                                                                                                                                                st.cache_data |
| Querying a database                  |                                                                                                           pandas.DataFrame |                                                                                                                                                st.cache_data |
| Querying an API                      |                                                                                                pandas.DataFrame, str, dict |                                                                                                                                                st.cache_data |
| Running an ML model (inference)      |                                                                                     pandas.DataFrame, str, int, dict, list |                                                                                                                                                st.cache_data |
| Creating or processing images        |                                                                                             PIL.Image.Image, numpy.ndarray |                                                                                                                                                st.cache_data |
| Creating charts                      |                                                        matplotlib.figure.Figure, plotly.graph_objects.Figure, altair.Chart | st.cache_data (but some libraries require st.cache_resource, since the chart object is not serializable – make sure not to mutate the chart after creation!) |
| Loading ML models                    |                                                             transformers.Pipeline, torch.nn.Module, tensorflow.keras.Model |                                                                                                                                            st.cache_resource |
| Initializing database connections    | pyodbc.Connection, sqlalchemy.engine.base.Engine, psycopg2.connection, mysql.connector.MySQLConnection, sqlite3.Connection |                                                                                                                                            st.cache_resource |
| Opening persistent file handles      |                                                                                                         \_io.TextIOWrapper |                                                                                                                                            st.cache_resource |
| Opening persistent threads           |                                                                                                           threading.thread |                                                                                                                                            st.cache_resource |
## Advanced usage
### Controlling cache size and duration
If your app runs for a long time and constantly caches functions, you might run into two problems:
1. The app runs out of memory because the cache is too large.
2. Objects in the cache become stale, e.g. because you cached old data from a database.
You can combat these problems with the `ttl` and `max_entries` parameters, which are available for both caching decorators.
**The `ttl` (time-to-live) parameter**
`ttl` sets a time to live on a cached function. If that time is up and you call the function again, the app will discard any old, cached values, and the function will be rerun. The newly computed value will then be stored in the cache. This behavior is useful for preventing stale data (problem 2) and the cache from growing too large (problem 1). Especially when pulling data from a database or API, you should always set a `ttl` so you are not using old data. Here's an example:
```python
@st.cache_data(ttl=3600)  # 👈 Cache data for 1 hour (=3600 seconds)
def get_api_data():
data = api.get(...)
return data
```
<Tip>
You can also set `ttl` values using `timedelta`, e.g., `ttl=datetime.timedelta(hours=1)`.
</Tip>
**The `max_entries` parameter**
`max_entries` sets the maximum number of entries in the cache. An upper bound on the number of cache entries is useful for limiting memory (problem 1), especially when caching large objects. The oldest entry will be removed when a new entry is added to a full cache. Here's an example:
```python
@st.cache_data(max_entries=1000)  # 👈 Maximum 1000 entries in the cache
def get_large_array(seed):
np.random.seed(seed)
arr = np.random.rand(100000)
return arr
```
### Customizing the spinner
By default, Streamlit shows a small loading spinner in the app when a cached function is running. You can modify it easily with the `show_spinner` parameter, which is available for both caching decorators:
```python
@st.cache_data(show_spinner=False)  # 👈 Disable the spinner
def get_api_data():
data = api.get(...)
return data
@st.cache_data(show_spinner="Fetching data from API...")  # 👈 Use custom text for spinner
def get_api_data():
data = api.get(...)
return data
```
### Excluding input parameters
In a cached function, all input parameters must be hashable. Let's quickly explain why and what it means. When the function is called, Streamlit looks at its parameter values to determine if it was cached before. Therefore, it needs a reliable way to compare the parameter values across function calls. Trivial for a string or int – but complex for arbitrary objects! Streamlit uses hashing to solve that. It converts the parameter to a stable key and stores that key. At the next function call, it hashes the parameter again and compares it with the stored hash key.
Unfortunately, not all parameters are hashable! E.g., you might pass an unhashable database connection or ML model to your cached function. In this case, you can exclude input parameters from caching. Simply prepend the parameter name with an underscore (e.g., `_param1`), and it will not be used for caching. Even if it changes, Streamlit will return a cached result if all the other parameters match up.
Here's an example:
```python
@st.cache_data
def fetch_data(_db_connection, num_rows):  # 👈 Don't hash _db_connection
data = _db_connection.fetch(num_rows)
return data
connection = init_connection()
fetch_data(connection, 10)
```
But what if you want to cache a function that takes an unhashable parameter? For example, you might want to cache a function that takes an ML model as input and returns the layer names of that model. Since the model is the only input parameter, you cannot exclude it from caching. In this case you can use the `hash_funcs` parameter to specify a custom hashing function for the model.
### The `hash_funcs` parameter
As described above, Streamlit's caching decorators hash the input parameters and cached function's signature to determine whether the function has been run before and has a return value stored ("cache hit") or needs to be run ("cache miss"). Input parameters that are not hashable by Streamlit's hashing implementation can be ignored by prepending an underscore to their name. But there two rare cases where this is undesirable. i.e. where you want to hash the parameter that Streamlit is unable to hash:
1. When Streamlit's hashing mechanism fails to hash a parameter, resulting in a `UnhashableParamError` being raised.
2. When you want to override Streamlit's default hashing mechanism for a parameter.
Let's discuss each of these cases in turn with examples.
#### Example 1: Hashing a custom class
Streamlit does not know how to hash custom classes. If you pass a custom class to a cached function, Streamlit will raise a `UnhashableParamError`. For example, let's define a custom class `MyCustomClass` that accepts an initial integer score. Let's also define a cached function `multiply_score` that multiplies the score by a multiplier:
```python
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
```
If you run this app, you'll see that Streamlit raises a `UnhashableParamError` since it does not know how to hash `MyCustomClass`:
```python
UnhashableParamError: Cannot hash argument 'obj' (of type __main__.MyCustomClass) in 'multiply_score'.
```
To fix this, we can use the `hash_funcs` parameter to tell Streamlit how to hash `MyCustomClass`. We do this by passing a dictionary to `hash_funcs` that maps the name of the parameter to a hash function. The choice of hash function is up to the developer. In this case, let's define a custom hash function `hash_func` that takes the custom class as input and returns the score. We want the score to be the unique identifier of the object, so we can use it to deterministically hash the object:
```python
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
```
Now if you run the app, you'll see that Streamlit no longer raises a `UnhashableParamError` and the app runs as expected.
Let's now consider the case where `multiply_score` is an attribute of `MyCustomClass` and we want to hash the entire object:
```python
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
```
If you run this app, you'll see that Streamlit raises a `UnhashableParamError` since it cannot hash the argument `'self' (of type __main__.MyCustomClass) in 'multiply_score'`. A simple fix here could be to use Python's `hash()` function to hash the object:
```python
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
```
Above, the hash function is defined as `lambda x: hash(x.my_score)`. This creates a hash based on the `my_score` attribute of the `MyCustomClass` instance. As long as `my_score` remains the same, the hash remains the same. Thus, the result of `multiply_score` can be retrieved from the cache without recomputation.
As an astute Pythonista, you may have been tempted to use Python's `id()` function to hash the object like so:
```python
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
```
If you run the app, you'll notice that Streamlit recomputes `multiply_score` each time even if `my_score` hasn't changed! Puzzled? In Python, `id()` returns the identity of an object, which is unique and constant for the object during its lifetime. This means that even if the `my_score` value is the same between two instances of `MyCustomClass`, `id()` will return different values for these two instances, leading to different hash values. As a result, Streamlit considers these two different instances as needing separate cached values, thus it recomputes the `multiply_score` each time even if `my_score` hasn't changed.
This is why we discourage using it as hash func, and instead encourage functions that return deterministic, true hash values. That said, if you know what you're doing, you can use `id()` as a hash function. Just be aware of the consequences. For example, `id` is often the _correct_ hash func when you're passing the result of an `@st.cache_resource` function as the input param to another cached function. There's a whole class of object types that aren’t otherwise hashable.
#### Example 2: Hashing a Pydantic model
Let's consider another example where we want to hash a Pydantic model:
```python
import streamlit as st
from pydantic import BaseModel
class Person(BaseModel):
name: str
@st.cache_data
def identity(person: Person):
return person
person = identity(Person(name="Lee"))
st.write(f"The person is {person.name}")
```
Above, we define a custom class `Person` using Pydantic's `BaseModel` with a single attribute name. We also define an `identity` function which accepts an instance of `Person` as an arg and returns it without modification. This function is intended to cache the result, therefore, if called multiple times with the same `Person` instance, it won't recompute but return the cached instance.
If you run the app, however, you'll run into a `UnhashableParamError: Cannot hash argument 'person' (of type __main__.Person) in 'identity'.` error. This is because Streamlit does not know how to hash the `Person` class. To fix this, we can use the `hash_funcs` kwarg to tell Streamlit how to hash `Person`.
In the version below, we define a custom hash function `hash_func` that takes the `Person` instance as input and returns the name attribute. We want the name to be the unique identifier of the object, so we can use it to deterministically hash the object:
```python
import streamlit as st
from pydantic import BaseModel
class Person(BaseModel):
name: str
@st.cache_data(hash_funcs={Person: lambda p: p.name})
def identity(person: Person):
return person
person = identity(Person(name="Lee"))
st.write(f"The person is {person.name}")
```
#### Example 3: Hashing a ML model
There may be cases where you want to pass your favorite machine learning model to a cached function. For example, let's say you want to pass a TensorFlow model to a cached function, based on what model the user selects in the app. You might try something like this:
```python
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
```
In the above app, the user can select one of two models. Based on the selection, the app loads the corresponding model and passes it to `load_layers`. This function then returns the names of the layers in the model. If you run the app, you'll see that Streamlit raises a `UnhashableParamError` since it cannot hash the argument `'base_model' (of type keras.engine.functional.Functional) in 'load_layers'`.
If you disable hashing for `base_model` by prepending an underscore to its name, you'll observe that regardless of which base model is chosen, the layers displayed are same. This subtle bug is due to the fact that the `load_layers` function is not re-run when the base model changes. This is because Streamlit does not hash the `base_model` argument, so it does not know that the function needs to be re-run when the base model changes.
To fix this, we can use the `hash_funcs` kwarg to tell Streamlit how to hash the `base_model` argument. In the version below, we define a custom hash function `hash_func`: `Functional: lambda x: x.name`. Our choice of hash func is informed by our knowledge that the `name` attribute of a `Functional` object or model uniquely identifies it. As long as the `name` attribute remains the same, the hash remains the same. Thus, the result of `load_layers` can be retrieved from the cache without recomputation.
```python
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
```
In the above case, we could also have used `hash_funcs={Functional: id}` as the hash function. This is because `id` is often the _correct_ hash func when you're passing the result of an `@st.cache_resource` function as the input param to another cached function.
#### Example 4: Overriding Streamlit's default hashing mechanism
Let's consider another example where we want to override Streamlit's default hashing mechanism for a pytz-localized datetime object:
```python
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
```
It may be surprising to see that although `now` and `now_tz` are of the same `<class 'datetime.datetime'>` type, Streamlit does not how to hash `now_tz` and raises a `UnhashableParamError`. In this case, we can override Streamlit's default hashing mechanism for `datetime` objects by passing a custom hash function to the `hash_funcs` kwarg:
```python
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
```
Let's now consider a case where we want to override Streamlit's default hashing mechanism for NumPy arrays. While Streamlit natively hashes Pandas and NumPy objects, there may be cases where you want to override Streamlit's default hashing mechanism for these objects.
For example, let's say we create a cache-decorated `show_data` function that accepts a NumPy array and returns it without modification. In the bellow app, `data = df["str"].unique()` (which is a NumPy array) is passed to the `show_data` function.
```python
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
```
Since `data` is always the same, we expect the `show_data` function to return the cached value. However, if you run the app, and click the `Re-run` button, you'll notice that the `show_data` function is re-run each time. We can assume this behavior is a consequence of Streamlit's default hashing mechanism for NumPy arrays.
To work around this, let's define a custom hash function `hash_func` that takes a NumPy array as input and returns a string representation of the array:
```python
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
```
Now if you run the app, and click the `Re-run` button, you'll notice that the `show_data` function is no longer re-run each time. It's important to note here that our choice of hash function was very naive and not necessarily the best choice. For example, if the NumPy array is large, converting it to a string representation may be expensive. In such cases, it is up to you as the developer to define what a good hash function is for your use case.
#### Static elements
Since version 1.16.0, cached functions can contain Streamlit commands! For example, you can do this:
```python
@st.cache_data
def get_api_data():
data = api.get(...)
st.success("Fetched data from API!")  # 👈 Show a success message
return data
```
As we know, Streamlit only runs this function if it hasn't been cached before. On this first run, the `st.success` message will appear in the app. But what happens on subsequent runs? It still shows up! Streamlit realizes that there is an `st.` command inside the cached function, saves it during the first run, and replays it on subsequent runs. Replaying static elements works for both caching decorators.
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
#### Input widgets
You can also use [interactive input widgets] like `st.slider` or `st.text_input` in cached functions. Widget replay is an experimental feature at the moment. To enable it, you need to set the `experimental_allow_widgets` parameter:
```python
@st.cache_data(experimental_allow_widgets=True)  # 👈 Set the parameter
def get_data():
num_rows = st.slider("Number of rows to get")  # 👈 Add a slider
data = api.get(..., num_rows)
return data
```
Streamlit treats the slider like an additional input parameter to the cached function. If you change the slider position, Streamlit will see if it has already cached the function for this slider value. If yes, it will return the cached value. If not, it will rerun the function using the new slider value.
Using widgets in cached functions is extremely powerful because it lets you cache entire parts of your app. But it can be dangerous! Since Streamlit treats the widget value as an additional input parameter, it can easily lead to excessive memory usage. Imagine your cached function has five sliders and returns a 100 MB DataFrame. Then we'll add 100 MB to the cache for _every permutation_ of these five slider values – even if the sliders do not influence the returned data! These additions can make your cache explode very quickly. Please be aware of this limitation if you use widgets in cached functions. We recommend using this feature only for isolated parts of your UI where the widgets directly influence the cached return value.
<Warning>
Support for widgets in cached functions is experimental. We may change or remove it anytime without warning. Please use it with care!
</Warning>
<Note>
Two widgets are currently not supported in cached functions: `st.file_uploader` and `st.camera_input`. We may support them in the future. Feel free to open a GitHub issue if you need them!
</Note>
### Dealing with large data
As we explained, you should cache data objects with `st.cache_data`. But this can be slow for extremely large data, e.g., DataFrames or arrays with >100 million rows. That's because of the [copying behavior](#copying-behavior) of `st.cache_data`: on the first run, it serializes the return value to bytes and deserializes it on subsequent runs. Both operations take time.
If you're dealing with extremely large data, it can make sense to use `st.cache_resource` instead. It does not create a copy of the return value via serialization/deserialization and is almost instant. But watch out: any mutation to the function's return value (such as dropping a column from a DataFrame or setting a value in an array) directly manipulates the object in the cache. You must ensure this doesn't corrupt your data or lead to crashes. See the section on [Mutation and concurrency issues](#mutation-and-concurrency-issues) below.
When benchmarking `st.cache_data` on pandas DataFrames with four columns, we found that it becomes slow when going beyond 100 million rows. The table shows runtimes for both caching decorators at different numbers of rows (all with four columns):
|                   |                 | 10M rows | 50M rows | 100M rows | 200M rows |
| ----------------- | --------------- | :------: | :------: | :-------: | :-------: |
| st.cache_data     | First run\*     |  0.4 s   |   3 s    |   14 s    |   28 s    |
|                   | Subsequent runs |  0.2 s   |   1 s    |    2 s    |    7 s    |
| st.cache_resource | First run\*     |  0.01 s  |  0.1 s   |   0.2 s   |    1 s    |
|                   | Subsequent runs |   0 s    |   0 s    |    0 s    |    0 s    |
|                                                                                                                                                              |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| _\*For the first run, the table only shows the overhead time of using the caching decorator. It does not include the runtime of the cached function itself._ |
### Mutation and concurrency issues
In the sections above, we talked a lot about issues when mutating return objects of cached functions. This topic is complicated! But it's central to understanding the behavior differences between `st.cache_data` and `st.cache_resource`. So let's dive in a bit deeper.
First, we should clearly define what we mean by mutations and concurrency:
- By **mutations**, we mean any changes made to a cached function's return value _after_ that function has been called. I.e. something like this:
```python
@st.cache_data
def create_list():
l = [1, 2, 3]
l = create_list()  # 👈 Call the function
l[0] = 2  # 👈 Mutate its return value
```
- By **concurrency**, we mean that multiple sessions can cause these mutations at the same time. Streamlit is a web framework that needs to handle many users and sessions connecting to an app. If two people view an app at the same time, they will both cause the Python script to rerun, which may manipulate cached return objects at the same time – concurrently.
Mutating cached return objects can be dangerous. It can lead to exceptions in your app and even corrupt your data (which can be worse than a crashed app!). Below, we'll first explain the copying behavior of `st.cache_data` and show how it can avoid mutation issues. Then, we'll show how concurrent mutations can lead to data corruption and how to prevent it.
#### Copying behavior
`st.cache_data` creates a copy of the cached return value each time the function is called. This avoids most mutations and concurrency issues. To understand it in detail, let's go back to the [Uber ridesharing example](#usage) from the section on `st.cache_data` above. We are making two modifications to it:
1. We are using `st.cache_resource` instead of `st.cache_data`. `st.cache_resource` does **not** create a copy of the cached object, so we can see what happens without the copying behavior.
2. After loading the data, we manipulate the returned DataFrame (in place!) by dropping the column `"Lat"`.
Here's the code:
```python
@st.cache_resource   # 👈 Turn off copying behavior
def load_data(url):
df = pd.read_csv(url)
return df
df = load_data("https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data1.csv")
st.dataframe(df)
df.drop(columns=['Lat'], inplace=True)  # 👈 Mutate the dataframe inplace
st.button("Rerun")
```
Let's run it and see what happens! The first run should work fine. But in the second run, you see an exception: `KeyError: "['Lat'] not found in axis"`. Why is that happening? Let's go step by step:
- On the first run, Streamlit runs `load_data` and stores the resulting DataFrame in the cache. Since we're using `st.cache_resource`, it does **not** create a copy but stores the original DataFrame.
- Then we drop the column `"Lat"` from the DataFrame. Note that this is dropping the column from the _original_ DataFrame stored in the cache. We are manipulating it!
- On the second run, Streamlit returns that exact same manipulated DataFrame from the cache. It does not have the column `"Lat"` anymore! So our call to `df.drop` results in an exception. Pandas cannot drop a column that doesn't exist.
The copying behavior of `st.cache_data` prevents this kind of mutation error. Mutations can only affect a specific copy and not the underlying object in the cache. The next rerun will get its own, unmutated copy of the DataFrame. You can try it yourself, just replace `st.cache_resource` with `st.cache_data` above, and you'll see that everything works.
Because of this copying behavior, `st.cache_data` is the recommended way to cache data transforms and computations – anything that returns a serializable object.
#### Concurrency issues
Now let's look at what can happen when multiple users concurrently mutate an object in the cache. Let's say you have a function that returns a list. Again, we are using `st.cache_resource` to cache it so that we are not creating a copy:
```python
@st.cache_resource
def create_list():
l = [1, 2, 3]
return l
l = create_list()
first_list_value = l[0]
l[0] = first_list_value + 1
st.write("l[0] is:", l[0])
```
Let's say user A runs the app. They will see the following output:
```python
l[0] is: 2
```
Let's say another user, B, visits the app right after. In contrast to user A, they will see the following output:
```python
l[0] is: 3
```
Now, user A reruns the app immediately after user B. They will see the following output:
```python
l[0] is: 4
```
What is happening here? Why are all outputs different?
- When user A visits the app, `create_list()` is called, and the list `[1, 2, 3]` is stored in the cache. This list is then returned to user A. The first value of the list, `1`, is assigned to `first_list_value` , and `l[0]` is changed to `2`.
- When user B visits the app, `create_list()` returns the mutated list from the cache: `[2, 2, 3]`. The first value of the list, `2`, is assigned to `first_list_value` and `l[0]` is changed to `3`.
- When user A reruns the app, `create_list()` returns the mutated list again: `[3, 2, 3]`. The first value of the list, `3`, is assigned to `first_list_value,` and `l[0]` is changed to 4.
If you think about it, this makes sense. Users A and B use the same list object (the one stored in the cache). And since the list object is mutated, user A's change to the list object is also reflected in user B's app.
This is why you must be careful about mutating objects cached with `st.cache_resource`, especially when multiple users access the app concurrently. If we had used `st.cache_data` instead of `st.cache_resource`, the app would have copied the list object for each user, and the above example would have worked as expected – users A and B would have both seen:
```python
l[0] is: 2
```
<Note>
This toy example might seem benign. But data corruption can be extremely dangerous! Imagine we had worked with the financial records of a large bank here. You surely don't want to wake up with less money on your account just because someone used the wrong caching decorator 😉
</Note>
## Migrating from st.cache
We introduced the caching commands described above in Streamlit 1.18.0. Before that, we had one catch-all command `st.cache`. Using it was often confusing, resulted in weird exceptions, and was slow. That's why we replaced `st.cache` with the new commands in 1.18.0 (read more in this blog post). The new commands provide a more intuitive and efficient way to cache your data and resources and are intended to replace `st.cache` in all new development.
If your app is still using `st.cache`, don't despair! Here are a few notes on migrating:
- Streamlit will show a deprecation warning if your app uses `st.cache`.
- We will not remove `st.cache` soon, so you don't need to worry about your 2-year-old app breaking. But we encourage you to try the new commands going forward – they will be way less annoying!
- Switching code to the new commands should be easy in most cases. To decide whether to use `st.cache_data` or `st.cache_resource`, read [Deciding which caching decorator to use](#deciding-which-caching-decorator-to-use). Streamlit will also recognize common use cases and show hints right in the deprecation warnings.
- Most parameters from `st.cache` are also present in the new commands, with a few exceptions:
- `allow_output_mutation` does not exist anymore. You can safely delete it. Just make sure you use the right caching command for your use case.
- `suppress_st_warning` does not exist anymore. You can safely delete it. Cached functions can now contain Streamlit commands and will replay them. If you want to use widgets inside cached functions, set `experimental_allow_widgets=True`. See [Input widgets](#input-widgets) for an example.
If you have any questions or issues during the migration process, please contact us on the forum, and we will be happy to assist you. 🎈
################################################
Section 3.4 - forms.md
################################################
# Using forms
When you don't want to rerun your script with each input made by a user, [`st.form`] is here to help! Forms make it easy to batch user input into a single rerun. This guide to using forms provides examples and explains how users interact with forms.
## Example
In the following example, a user can set multiple parameters to update the map. As the user changes the parameters, the script will not rerun and the map will not update. When the user submits the form with the button labeled "**Update map**", the script reruns and the map updates.
If at any time the user clicks "**Generate new points**" which is outside of the form, the script will rerun. If the user has any unsubmitted changes within the form, these will _not_ be sent with the rerun. All changes made to a form will only be sent to the Python backend when the form itself is submitted.
<Collapse title="View source code" expanded={false} >
```python
import streamlit as st
import pandas as pd
import numpy as np
def get_data():
df = pd.DataFrame({
"lat": np.random.randn(200) / 50 + 37.76,
"lon": np.random.randn(200) / 50 + -122.4,
"team": ['A','B']*100
})
return df
if st.button('Generate new points'):
st.session_state.df = get_data()
if 'df' not in st.session_state:
st.session_state.df = get_data()
df = st.session_state.df
with st.form("my_form"):
header = st.columns([1,2,2])
header[0].subheader('Color')
header[1].subheader('Opacity')
header[2].subheader('Size')
row1 = st.columns([1,2,2])
colorA = row1[0].color_picker('Team A', '#0000FF')
opacityA = row1[1].slider('A opacity', 20, 100, 50, label_visibility='hidden')
sizeA = row1[2].slider('A size', 50, 200, 100, step=10, label_visibility='hidden')
row2 = st.columns([1,2,2])
colorB = row2[0].color_picker('Team B', '#FF0000')
opacityB = row2[1].slider('B opacity', 20, 100, 50, label_visibility='hidden')
sizeB = row2[2].slider('B size', 50, 200, 100, step=10, label_visibility='hidden')
st.form_submit_button('Update map')
alphaA = int(opacityA*255/100)
alphaB = int(opacityB*255/100)
df['color'] = np.where(df.team=='A',colorA+f'{alphaA:02x}',colorB+f'{alphaB:02x}')
df['size'] = np.where(df.team=='A',sizeA, sizeB)
st.map(df, size='size', color='color')
```
</Collapse>
<Cloud name="doc-forms-overview" height="800px"/>
## User interaction
If a widget is not in a form, that widget will trigger a script rerun whenever a user changes its value. For widgets with keyed input (`st.number_input`, `st.text_input`, `st.text_area`), a new value triggers a rerun when the user clicks or tabs out of the widget. A user can also submit a change by pressing `Enter` while thier cursor is active in the widget.
On the other hand if a widget is inside of a form, the script will not rerun when a user clicks or tabs out of that widget. For widgets inside a form, the script will rerun when the form is submitted and all widgets within the form will send their updated values to the Python backend.

A user can submit a form using **Enter** on their keyboard if their cursor active in a widget that accepts keyed input. Within `st.number_input` and `st.text_input` a user presses **Enter** to submit the form. Within `st.text_area` a user presses **Ctrl+Enter**/**⌘+Enter** to submit the form.

## Widget values
Before a form is submitted, all widgets within that form will have default values, just like widgets outside of a form have default values.
```python
import streamlit as st
with st.form("my_form"):
st.write("Inside the form")
my_number = st.slider('Pick a number', 1, 10)
my_color = st.selectbox('Pick a color', ['red','orange','green','blue','violet'])
st.form_submit_button('Submit my picks')
# This is outside the form
st.write(my_number)
st.write(my_color)
```
<Cloud name="doc-forms-default" height="450px"/>
## Forms are containers
When `st.form` is called, a container is created on the frontend. You can write to that container like you do with other [container elements]. That is, you can use Python's `with` statement as shown in the example above, or you can assign the form container to a variable and call methods on it directly. Additionally, you can place `st.form_submit_button` anywhere in the form container.
```python
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
```
<Cloud name="doc-forms-container" height="375px"/>
## Processing form submissions
The purpose of a form is to override the default behavior of Streamlit which reruns a script as soon as the user makes a change. For widgets outside of a form, the logical flow is:
1. The user changes a widget's value on the frontend.
2. The widget's value in `st.session_state` and in the Python backend (server) is updated.
3. The script rerun begins.
4. If the widget has a callback, it is executed as a prefix to the page rerun.
5. When the updated widget's function is executed during the rerun, it outputs the new value.
For widgets inside a form, any changes made by a user (step 1) do not get passed to the Python backend (step 2) until the form is submitted. Furthermore, the only widget inside a form that can have a callback function is the `st.form_submit_button`. If you need to execute a process using newly submitted values, you have three major patterns for doing so.
### Execute the process after the form
If you need to execute a one-time process as a result of a form submission, you can condition that process on the `st.form_submit_button` and execute it after the form. If you need results from your process to display above the form, you can use containers to control where the form displays relative to your output.
```python
import streamlit as st
col1,col2 = st.columns([1,2])
col1.title('Sum:')
with st.form('addition'):
a = st.number_input('a')
b = st.number_input('b')
submit = st.form_submit_button('add')
if submit:
col2.title(f'{a+b:.2f}')
```
<Cloud name="doc-forms-process1" height="400px"/>
### Use a callback with session state
You can use a callback to execute a process as a prefix to the script rerunning.
<Important>
When processing newly updated values within a callback, do not pass those values to the callback directly through the `args` or `kwargs` parameters. You need to assign a key to any widget whose value you use within the callback. If you look up the value of that widget from `st.session_state` within the body of the callback, you will be able to access the newly submitted value. See the example below.
</Important>
```python
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
```
<Cloud name="doc-forms-process2" height="400px"/>
### Use `st.rerun`
If your process affects content above your form, another alternative is using an extra rerun. This can be less resource-efficient though, and may be less desirable that the above options.
```python
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
```
<Cloud name="doc-forms-process3" height="400px"/>
## Limitations
- Every form must contain a `st.form_submit_button`.
- `st.button` and `st.download_button` cannot be added to a form.
- `st.form` cannot be embedded inside another `st.form`.
- Callback functions can only be assigned to `st.form_submit_button` within a form; no other widgets in a form can have a callback.
- Interdependent widgets within a form are unlikely to be particularly useful. If you pass `widget1`'s value into `widget2` when they are both inside a form, then `widget2` will only update when the form is submitted.
################################################
Section 3.5 - fragments.md
################################################
# Working with fragments
Reruns are a central part of every Streamlit app. When users interact with widgets, your script reruns from top to bottom, and your app's frontend is updated. Streamlit provides several features to help you develop your app within this execution model. Streamlit version 1.37.0 introduced fragments to allow rerunning a portion of your code instead of your full script. As your app grows larger and more complex, these fragment reruns help your app be efficient and performant. Fragments give you finer, easy-to-understand control over your app's execution flow.
Before you read about fragments, we recommend having a basic understanding of [caching], [Session State](/concepts/architecture/session-state), and [forms].
## Use cases for fragments
Fragments are versatile and applicable to a wide variety of circumstances. Here are just a few, common scenarios where fragments are useful:
- Your app has multiple visualizations and each one takes time to load, but you have a filter input that only updates one of them.
- You have a dynamic form that doesn't need to update the rest of your app (until the form is complete).
- You want to automatically update a single component or group of components to stream data.
## Defining and calling a fragment
Streamlit provides a decorator ([`st.fragment`]) to turn any function into a fragment function. When you call a fragment function that contains a widget function, a user triggers a _fragment rerun_ instead of a full rerun when they interact with that fragment's widget. During a fragment rerun, only your fragment function is re-executed. Anything within the main body of your fragment is updated on the frontend, while the rest of your app remains the same. We'll describe fragments written across multiple containers later on.
Here is a basic example of defining and calling a fragment function. Just like with caching, remember to call your function after defining it.
```python
import streamlit as st
@st.fragment
def fragment_function():
if st.button("Hi!"):
st.write("Hi back!")
fragment_function()
```
If you want the main body of your fragment to appear in the sidebar or another container, call your fragment function inside a context manager.
```python
with st.sidebar:
fragment_function()
```
### Fragment execution flow
Consider the following code with the explanation and diagram below.
```python
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
```
When a user interacts with an input widget inside a fragment, only the fragment reruns instead of the full script. When a user interacts with an input widget outside a fragment, the full script reruns as usual.
If you run the code above, the full script will run top to bottom on your app's initial load. If you flip the toggle button in your running app, the first fragment (`toggle_and_text()`) will rerun, redrawing the toggle and text area while leaving everything else unchanged. If you click the checkbox, the second fragment (`filter_and_file()`) will rerun and consequently redraw the checkbox and file uploader. Everything else remains unchanged. Finally, if you click the update button, the full script will rerun, and Streamlit will redraw everything.

## Fragment return values and interacting with the rest of your app
Streamlit ignores fragment return values during fragment reruns, so defining return values for your fragment functions is not recommended. Instead, if your fragment needs to share data with the rest of your app, use Session State. Fragments are just functions in your script, so they can access Session State, imported modules, and other Streamlit elements like containers. If your fragment writes to any container created outside of itself, note the following difference in behavior:
- Elements drawn in the main body of your fragment are cleared and redrawn in place during a fragment rerun. Repeated fragment reruns will not cause additional elements to appear.
- Elements drawn to containers outside the main body of fragment will not be cleared with each fragment rerun. Instead, Streamlit will draw them additively and these elements will accumulate until the next full-script rerun.
- A fragment can't draw widgets in containers outside of the main body of the fragment. Widgets can only go in the main body of a fragment.
To prevent elements from accumulating in outside containers, use [`st.empty`] containers. For a related tutorial, see [Create a fragment across multiple containers].
If you need to trigger a full-script rerun from inside a fragment, call [`st.rerun`]. For a related tutorial, see [Trigger a full-script rerun from inside a fragment].
## Automate fragment reruns
`st.fragment` includes a convenient `run_every` parameter that causes the fragment to rerun automatically at the specified time interval. These reruns are in addition to any reruns (fragment or full-script) triggered by your user. The automatic fragment reruns will continue even if your user is not interacting with your app. This is a great way to show a live data stream or status on a running background job, efficiently updating your rendered data and _only_ your rendered data.
```python
@st.fragment(run_every="10s")
def auto_function():
# This will update every 10 seconds!
df = get_latest_updates()
st.line_chart(df)
auto_function()
```
For a related tutorial, see [Start and stop a streaming fragment].
## Compare fragments to other Streamlit features
### Fragments vs forms
Here is a comparison between fragments and forms:
- **Forms** allow users to interact with widgets without rerunning your app. Streamlit does not send user actions within a form to your app's Python backend until the form is submitted. Widgets within a form can not dynamically update other widgets (in or out of the form) in real-time.
- **Fragments** run independently from the rest of your code. As your users interact with fragment widgets, their actions are immediately processed by your app's Python backend and your fragment code is rerun. Widgets within a fragment can dynamically update other widgets within the same fragment in real-time.
A form batches user input without interaction between any widgets. A fragment immediately processes user input but limits the scope of the rerun.
### Fragments vs callbacks
Here is a comparison between fragments and callbacks:
- **Callbacks** allow you to execute a function at the beginning of a script rerun. A callback is a _single prefix_ to your script rerun.
- **Fragments** allow you to rerun a portion of your script. A fragment is a _repeatable postfix_ to your script, running each time a user interacts with a fragment widget, or automatically in sequence when `run_every` is set.
When callbacks render elements to your page, they are rendered before the rest of your page elements. When fragments render elements to your page, they are updated with each fragment rerun (unless they are written to containers outside of the fragment, in which case they accumulate there).
### Fragments vs custom components
Here is a comparison between fragments and custom components:
- **Components** are custom frontend code that can interact with the Python code, native elements, and widgets in your Streamlit app. Custom components extend what’s possible with Streamlit. They follow the normal Streamlit execution flow.
- **Fragments** are parts of your app that can rerun independently of the full app. Fragments can be composed of multiple Streamlit elements, widgets, or any Python code.
A fragment can include one or more custom components. A custom component could not easily include a fragment!
### Fragments vs caching
Here is a comparison between fragments and caching:
- **Caching:** allows you to skip over a function and return a previously computed value. When you use caching, you execute everything except the cached function (if you've already run it before).
- **Fragments:** allow you to freeze most of your app and just execute the fragment. When you use fragments, you execute only the fragment (when triggering a fragment rerun).
Caching saves you from unnecessarily running a piece of your app while the rest runs. Fragments save you from running your full app when you only want to run one piece.
## Limitations and unsupported behavior
- Fragments can't detect a change in input values. It is best to use Session State for dynamic input and output for fragment functions.
- Using caching and fragments on the same function is unsupported.
- Fragments can't render widgets in externally-created containers; widgets can only be in the main body of a fragment.
################################################
Section 3.6 - run-your-app.md
################################################
# Run your Streamlit app
Working with Streamlit is simple. First you sprinkle a few Streamlit commands into a normal Python script, and then you run it. We list few ways to run your script, depending on your use case.
## Use streamlit run
Once you've created your script, say `your_script.py`, the easiest way to run it is with `streamlit run`:
```bash
streamlit run your_script.py
```
As soon as you run the script as shown above, a local Streamlit server will spin up and your app will open in a new tab in your default web browser.
### Pass arguments to your script
When passing your script some custom arguments, they must be passed after two dashes. Otherwise the arguments get interpreted as arguments to Streamlit itself:
```bash
streamlit run your_script.py [-- script args]
```
### Pass a URL to streamlit run
You can also pass a URL to `streamlit run`! This is great when your script is hosted remotely, such as a GitHub Gist. For example:
```bash
streamlit run https://raw.githubusercontent.com/streamlit/demo-uber-nyc-pickups/master/streamlit_app.py
```
## Run Streamlit as a Python module
Another way of running Streamlit is to run it as a Python module. This is useful when configuring an IDE like PyCharm to work with Streamlit:
```bash
# Running
python -m streamlit run your_script.py
```
```bash
# is equivalent to:
streamlit run your_script.py
```
################################################
Section 3.7 - session-state.md
################################################
# Add statefulness to apps
## What is State?
We define access to a Streamlit app in a browser tab as a **session**. For each browser tab that connects to the Streamlit server, a new session is created. Streamlit reruns your script from top to bottom every time you interact with your app. Each reruns takes place in a blank slate: no variables are shared between runs.
Session State is a way to share variables between reruns, for each user session. In addition to the ability to store and persist state, Streamlit also exposes the ability to manipulate state using Callbacks. Session state also persists across pages inside a [multipage app].
In this guide, we will illustrate the usage of **Session State** and **Callbacks** as we build a stateful Counter app.
For details on the Session State and Callbacks API, please refer to our [Session State API Reference Guide].
Also, check out this Session State basics tutorial video by Streamlit Developer Advocate Dr. Marisa Smith to get started:
<YouTube videoId="92jUAXBmZyU" />
## Build a Counter
Let's call our script `counter.py`. It initializes a `count` variable and has a button to increment the value stored in the `count` variable:
```python
import streamlit as st
st.title('Counter Example')
count = 0
increment = st.button('Increment')
if increment:
count += 1
st.write('Count = ', count)
```
No matter how many times we press the **_Increment_** button in the above app, the `count` remains at 1. Let's understand why:
- Each time we press the **_Increment_** button, Streamlit reruns `counter.py` from top to bottom, and with every run, `count` gets initialized to `0` .
- Pressing **_Increment_** subsequently adds 1 to 0, thus `count=1` no matter how many times we press **_Increment_**.
As we'll see later, we can avoid this issue by storing `count` as a Session State variable. By doing so, we're indicating to Streamlit that it should maintain the value stored inside a Session State variable across app reruns.
Let's learn more about the API to use Session State.
### Initialization
The Session State API follows a field-based API, which is very similar to Python dictionaries:
```python
import streamlit as st
# Check if 'key' already exists in session_state
# If not, then initialize it
if 'key' not in st.session_state:
st.session_state['key'] = 'value'
# Session State also supports the attribute based syntax
if 'key' not in st.session_state:
st.session_state.key = 'value'
```
### Reads and updates
Read the value of an item in Session State by passing the item to `st.write` :
```python
import streamlit as st
if 'key' not in st.session_state:
st.session_state['key'] = 'value'
# Reads
st.write(st.session_state.key)
# Outputs: value
```
Update an item in Session State by assigning it a value:
```python
import streamlit as st
if 'key' not in st.session_state:
st.session_state['key'] = 'value'
# Updates
st.session_state.key = 'value2'     # Attribute API
st.session_state['key'] = 'value2'  # Dictionary like API
```
Streamlit throws an exception if an uninitialized variable is accessed:
```python
import streamlit as st
st.write(st.session_state['value'])
# Throws an exception!
```

Let's now take a look at a few examples that illustrate how to add Session State to our Counter app.
### Example 1: Add Session State
Now that we've got a hang of the Session State API, let's update our Counter app to use Session State:
```python
import streamlit as st
st.title('Counter Example')
if 'count' not in st.session_state:
st.session_state.count = 0
increment = st.button('Increment')
if increment:
st.session_state.count += 1
st.write('Count = ', st.session_state.count)
```
As you can see in the above example, pressing the **_Increment_** button updates the `count` each time.
### Example 2: Session State and Callbacks
Now that we've built a basic Counter app using Session State, let's move on to something a little more complex. The next example uses Callbacks with Session State.
**Callbacks**: A callback is a Python function which gets called when an input widget changes. Callbacks can be used with widgets using the parameters `on_change` (or `on_click`), `args`, and `kwargs`. The full Callbacks API can be found in our [Session State API Reference Guide].
```python
import streamlit as st
st.title('Counter Example using Callbacks')
if 'count' not in st.session_state:
st.session_state.count = 0
def increment_counter():
st.session_state.count += 1
st.button('Increment', on_click=increment_counter)
st.write('Count = ', st.session_state.count)
```
Now, pressing the **_Increment_** button updates the count each time by calling the `increment_counter()` function.
### Example 3: Use args and kwargs in Callbacks
Callbacks also support passing arguments using the `args` parameter in a widget:
```python
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
```
Additionally, we can also use the `kwargs` parameter in a widget to pass named arguments to the callback function as shown below:
```python
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
```
### Example 4: Forms and Callbacks
Say we now want to not only increment the `count`, but also store when it was last updated. We illustrate doing this using Callbacks and `st.form`:
```python
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
```
## Advanced concepts
### Session State and Widget State association
Session State provides the functionality to store variables across reruns. Widget state (i.e. the value of a widget) is also stored in a session.
For simplicity, we have _unified_ this information in one place. i.e. the Session State. This convenience feature makes it super easy to read or write to the widget's state anywhere in the app's code. Session State variables mirror the widget value using the `key` argument.
We illustrate this with the following example. Let's say we have an app with a slider to represent temperature in Celsius. We can **set** and **get** the value of the temperature widget by using the Session State API, as follows:
```python
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
```
There is a limitation to setting widget values using the Session State API.
<Important>
Streamlit **does not allow** setting widget values via the Session State API for `st.button` and `st.file_uploader`.
</Important>
The following example will raise a `StreamlitAPIException` on trying to set the state of `st.button` via the Session State API:
```python
import streamlit as st
if 'my_button' not in st.session_state:
st.session_state.my_button = True
# Streamlit will raise an Exception on trying to set the state of button
st.button('Submit', key='my_button')
```

### Serializable Session State
Serialization refers to the process of converting an object or data structure into a format that can be persisted and shared, and allowing you to recover the data’s original structure. Python’s built-in pickle module serializes Python objects to a byte stream ("pickling") and deserializes the stream into an object ("unpickling").
By default, Streamlit’s Session State] allows you to persist any Python object for the duration of the session, irrespective of the object’s pickle-serializability. This property lets you store Python primitives such as integers, floating-point numbers, complex numbers and booleans, dataframes, and even [lambdas returned by functions. However, some execution environments may require serializing all data in Session State, so it may be useful to detect incompatibility during development, or when the execution environment will stop supporting it in the future.
To that end, Streamlit provides a `runner.enforceSerializableSessionState` [configuration option] that, when set to `true`, only allows pickle-serializable objects in Session State. To enable the option, either create a global or project config file with the following or use it as a command-line flag:
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

<Warning>
When `runner.enforceSerializableSessionState` is set to `true`, Session State implicitly uses the `pickle` module, which is known to be insecure. Ensure all data saved and retrieved from Session State is trusted because it is possible to construct malicious pickle data that will execute arbitrary code during unpickling. Never load data that could have come from an untrusted source in an unsafe mode or that could have been tampered with. **Only load data you trust**.
### Caveats and limitations
Here are some limitations to keep in mind when using Session State:
- Session State exists for as long as the tab is open and connected to the Streamlit server. As soon as you close the tab, everything stored in Session State is lost.
- Session State is not persisted. If the Streamlit server crashes, then everything stored in Session State gets wiped
- For caveats and limitations with the Session State API, please see the [API limitations].
################################################
Section 3.8 - widget-behavior.md
################################################
# Widget behavior
# Understanding widget behavior
Widgets (like `st.button`, `st.selectbox`, and `st.text_input`) are at the heart of Streamlit apps. They are the interactive elements of Streamlit that pass information from your users into your Python code. Widgets are magical and often work how you want, but they can have surprising behavior in some situations. Understanding the different parts of a widget and the precise order in which events occur helps you achieve your desired results.
This guide covers advanced concepts about widgets. Generally, it begins with simpler concepts and increases in complexity. For most beginning users, these details won't be important to know right away. When you want to dynamically change widgets or preserve widget information between pages, these concepts will be important to understand. We recommend having a basic understanding of [Session State] before reading this guide.
<Collapse title="🎈 TL;DR" expanded={false}>
1. The actions of one user do not affect the widgets of any other user.
2. A widget function call returns the widget's current value, which is a simple Python type. (e.g. `st.button` returns a boolean value.)
3. Widgets return their default values on their first call before a user interacts with them.
4. A widget's identity depends on the arguments passed to the widget function. Changing a widget's label, min or max value, default value, placeholder text, help text, or key will cause it to reset.
5. If you don't call a widget function in a script run, Streamlit will delete the widget's information&mdash;_including its key-value pair in Session State_. If you call the same widget function later, Streamlit treats it as a new widget.
The last two points (widget identity and widget deletion) are the most relevant when dynamically changing widgets or working with multi-page applications. This is covered in detail later in this guide: [Statefulness of widgets](#statefulness-of-widgets) and [Widget life cycle](#widget-life-cycle).
</Collapse>
## Anatomy of a widget
There are four parts to keep in mind when using widgets:
1. The frontend component as seen by the user.
2. The backend value or value as seen through `st.session_state`.
3. The key of the widget used to access its value via `st.session_state`.
4. The return value given by the widget's function.
### Widgets are session dependent
Widget states are dependent on a particular session (browser connection). The actions of one user do not affect the widgets of any other user. Furthermore, if a user opens up multiple tabs to access an app, each tab will be a unique session. Changing a widget in one tab will not affect the same widget in another tab.
### Widgets return simple Python data types
The value of a widget as seen through `st.session_state` and returned by the widget function are of simple Python types. For example, `st.button` returns a boolean value and will have the same boolean value saved in `st.session_state` if using a key. The first time a widget function is called (before a user interacts with it), it will return its default value. (e.g. `st.selectbox` returns the first option by default.) Default values are configurable for all widgets with a few special exceptions like `st.button` and `st.file_uploader`.
### Keys help distinguish widgets and access their values
Widget keys serve two purposes:
1. Distinguishing two otherwise identical widgets.
2. Creating a means to access and manipulate the widget's value through `st.session_state`.
Whenever possible, Streamlit updates widgets incrementally on the frontend instead of rebuilding them with each rerun. This means Streamlit assigns an ID to each widget from the arguments passed to the widget function. A widget's ID is based on parameters such as label, min or max value, default value, placeholder text, help text, and key. The page where the widget appears also factors into a widget's ID. If you have two widgets of the same type with the same arguments on the same page, you will get a `DuplicateWidgetID` error. In this case, assign unique keys to the two widgets.
#### Streamlit can't understand two identical widgets on the same page
```python
# This will cause a DuplicateWidgetID error.
st.button("OK")
st.button("OK")
```
#### Use keys to distinguish otherwise identical widgets
```python
st.button("OK", key="privacy")
st.button("OK", key="terms")
```
## Order of operations
When a user interacts with a widget, the order of logic is:
1. Its value in `st.session_state` is updated.
2. The callback function (if any) is executed.
3. The page reruns with the widget function returning its new value.
If the callback function writes anything to the screen, that content will appear above the rest of the page. A callback function runs as a _prefix_ to the script rerunning. Consequently, that means anything written via a callback function will disappear as soon as the user performs their next action. Other widgets should generally not be created within a callback function.
Note: If a callback function is passed any args or kwargs, those arguments will be established when the widget is rendered. In particular, if you want to use a widget's new value in its own callback function, you cannot pass that value to the callback function via the `args` parameter; you will have to assign a key to the widget and look up its new value using a call to `st.session_state` _within the callback function_.
### Using callback functions with forms
Using a callback function with a form requires consideration of this order of operations.
```python
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
```
<Cloud name="doc-guide-widgets-form-callbacks" height="250px"/>
## Statefulness of widgets
As long as the defining parameters of a widget remain the same and that widget is continuously rendered on the frontend, then it will be stateful and remember user input.
### Changing parameters of a widget will reset it
If any of the defining parameters of a widget change, Streamlit will see it as a new widget and it will reset. The use of manually assigned keys and default values is particularly important in this case. _Note that callback functions, callback args and kwargs, label visibility, and disabling a widget do not affect a widget's identity._
In this example, we have a slider whose min and max values are changed. Try interacting with each slider to change its value then change the min or max setting to see what happens.
```python
import streamlit as st
cols = st.columns([2, 1, 2])
minimum = cols[0].number_input("Minimum", 1, 5)
maximum = cols[2].number_input("Maximum", 6, 10, 10)
st.slider("No default, no key", minimum, maximum)
st.slider("No default, with key", minimum, maximum, key="a")
st.slider("With default, no key", minimum, maximum, value=5)
st.slider("With default, with key", minimum, maximum, value=5, key="b")
```
<Cloud name="doc-guide-widgets-change-parameters" height="550px"/>
#### Updating a slider with no default value
For the first two sliders above, as soon as the min or max value is changed, the sliders reset to the min value. The changing of the min or max value makes them "new" widgets from Streamlit's perspective and so they are recreated from scratch when the app reruns with the changed parameters. Since no default value is defined, each widget will reset to its min value. This is the same with or without a key since it's seen as a new widget either way. There is a subtle point to understand about pre-existing keys connecting to widgets. This will be explained further down in [Widget life cycle](#widget-life-cycle).
#### Updating a slider with a default value
For the last two sliders above, a change to the min or max value will result in the widgets being seen as "new" and thus recreated like before. Since a default value of 5 is defined, each widget will reset to 5 whenever the min or max is changed. This is again the same (with or without a key).
A solution to [Retain statefulness when changing a widget's parameters](#retain-statefulness-when-changing-a-widgets-parameters) is provided further on.
### Widgets do not persist when not continually rendered
If a widget's function is not called during a script run, then none of its parts will be retained, including its value in `st.session_state`. If a widget has a key and you navigate away from that widget, its key and associated value in `st.session_state` will be deleted. Even temporarily hiding a widget will cause it to reset when it reappears; Streamlit will treat it like a new widget. You can either interrupt the [Widget clean-up process](#widget-clean-up-process) (described at the end of this page) or save the value to another key.
#### Save widget values in Session State to preserve them between pages
If you want to navigate away from a widget and return to it while keeping its value, use a separate key in `st.session_state` to save the information independently from the widget. In this example, a temporary key is used with a widget. The temporary key uses an underscore prefix. Hence, `"_my_key"` is used as the widget key, but the data is copied to `"my_key"` to preserve it between pages.
```python
import streamlit as st
def store_value():
# Copy the value to the permanent key
st.session_state["my_key"] = st.session_state["_my_key"]
# Copy the saved value to the temporary key
st.session_state["_my_key"] = st.session_state["my_key"]
st.number_input("Number of filters", key="_my_key", on_change=store_value)
```
If this is functionalized to work with multiple widgets, it could look something like this:
```python
import streamlit as st
def store_value(key):
st.session_state[key] = st.session_state["_"+key]
def load_value(key):
st.session_state["_"+key] = st.session_state[key]
load_value("my_key")
st.number_input("Number of filters", key="_my_key", on_change=store_value, args=["my_key"])
```
## Widget life cycle
When a widget function is called, Streamlit will check if it already has a widget with the same parameters. Streamlit will reconnect if it thinks the widget already exists. Otherwise, it will make a new one.
As mentioned earlier, Streamlit determines a widget's ID based on parameters such as label, min or max value, default value, placeholder text, help text, and key. The page name also factors into a widget's ID. On the other hand, callback functions, callback args and kwargs, label visibility, and disabling a widget do not affect a widget's identity.
### Calling a widget function when the widget doesn't already exist
If your script rerun calls a widget function with changed parameters or calls a widget function that wasn't used on the last script run:
1. Streamlit will build the frontend and backend parts of the widget, using its default value.
2. If the widget has been assigned a key, Streamlit will check if that key already exists in Session State.

a. If it exists and is not currently associated with another widget, Streamlit will assign that key's value to the widget.
b. Otherwise, it will assign the default value to the key in `st.session_state` (creating a new key-value pair or overwriting an existing one).
3. If there are args or kwargs for a callback function, they are computed and saved at this point in time.
4. The widget value is then returned by the function.
Step 2 can be tricky. If you have a widget:
```python
st.number_input("Alpha",key="A")
```
and you change it on a page rerun to:
```python
st.number_input("Beta",key="A")
```
Streamlit will see that as a new widget because of the label change. The key `"A"` will be considered part of the widget labeled `"Alpha"` and will not be attached as-is to the new widget labeled `"Beta"`. Streamlit will destroy `st.session_state.A` and recreate it with the default value.
If a widget attaches to a pre-existing key when created and is also manually assigned a default value, you will get a warning if there is a disparity. If you want to control a widget's value through `st.session_state`, initialize the widget's value through `st.session_state` and avoid the default value argument to prevent conflict.
### Calling a widget function when the widget already exists
When rerunning a script without changing a widget's parameters:
1. Streamlit will connect to the existing frontend and backend parts.
2. If the widget has a key that was deleted from `st.session_state`, then Streamlit will recreate the key using the current frontend value. (e.g Deleting a key will not revert the widget to a default value.)
3. It will return the current value of the widget.
### Widget clean-up process
When Streamlit gets to the end of a script run, it will delete the data for any widgets it has in memory that were not rendered on the screen. Most importantly, that means Streamlit will delete all key-value pairs in `st.session_state` associated with a widget not currently on screen.
## Additional examples
As promised, let's address how to retain the statefulness of widgets when changing pages or modifying their parameters. There are two ways to do this.
1. Use dummy keys to duplicate widget values in `st.session_state` and protect the data from being deleted along with the widget.
2. Interrupt the widget clean-up process.
The first method was shown above in [Save widget values in Session State to preserve them between pages](#save-widget-values-in-session-state-to-preserve-them-between-pages)
### Interrupting the widget clean-up process
To retain information for a widget with `key="my_key"`, just add this to the top of every page:
```python
st.session_state.my_key = st.session_state.my_key
```
When you manually save data to a key in `st.session_state`, it will become detached from any widget as far as the clean-up process is concerned. If you navigate away from a widget with some key `"my_key"` and save data to `st.session_state.my_key` on the new page, you will interrupt the widget clean-up process and prevent the key-value pair from being deleted or overwritten if another widget with the same key exists.
### Retain statefulness when changing a widget's parameters
Here is a solution to our earlier example of changing a slider's min and max values. This solution interrupts the clean-up process as described above.
```python
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
```
<Cloud name="doc-guide-widgets-change-parameters-solution" height="250px"/>
The `update_value()` helper function is actually doing two things. On the surface, it's making sure there are no inconsistent changes to the parameters values as described. Importantly, it's also interrupting the widget clean-up process. When the min or max value of the widget changes, Streamlit sees it as a new widget on rerun. Without saving a value to `st.session_state.a`, the value would be thrown out and replaced by the "new" widget's default value.
------------------------------------------------------------------------------------------------
CHAPTER 4: configuration.md
------------------------------------------------------------------------------------------------
################################################
Section 4.1 - https.md
################################################
# HTTPS support
Many apps need to be accessed with SSL / TLS protocol or `https://`.
We recommend performing SSL termination in a reverse proxy or load balancer for self-hosted and production use cases, not directly in the app. [Streamlit Community Cloud](/deploy/streamlit-community-cloud) uses this approach, and every major cloud and app hosting platform should allow you to configure it and provide extensive documentation. You can find some of these platforms in our [Deployment tutorials](/deploy/tutorials).
To terminate SSL in your Streamlit app, you must configure `server.sslCertFile` and `server.sslKeyFile`. Learn how to set config options in [Configuration].
## Details on usage
- The configuration value should be a local file path to a cert file and key file. These must be available at the time the app starts.
- Both `server.sslCertFile` and `server.sslKeyFile` must be specified. If only one is specified, your app will exit with an error.
- This feature will not work in Community Cloud. Community Cloud already serves your app with TLS.
Note: In a production environment, we recommend performing SSL termination by the load balancer or the reverse proxy, not using this option. The use of this option in Streamlit has not gone through extensive security audits or performance tests.
## Example usage
```toml
# .streamlit/config.toml
[server]
sslCertFile = '/path/to/certchain.pem'
sslKeyFile = '/path/to/private.key'
```
################################################
Section 4.2 - options.md
################################################
# Working with configuration options
Streamlit provides four different ways to set configuration options. This list is in reverse order of precedence, i.e. command line flags take precedence over environment variables when the same configuration option is provided multiple times.
Note: If you change theme settings in `.streamlit/config.toml` _while_ the app is running, these changes will reflect immediately. If you change non-theme settings in `.streamlit/config.toml` _while_ the app is running, the server needs to be restarted for changes to be reflected in the app.
1. In a **global config file** at `~/.streamlit/config.toml` for macOS/Linux or `%userprofile%/.streamlit/config.toml` for Windows:
```toml
[server]
port = 80
```
2. In a **per-project config file** at `$CWD/.streamlit/config.toml`, where
`$CWD` is the folder you're running Streamlit from.
3. Through `STREAMLIT_*` **environment variables**, such as:
```bash
export STREAMLIT_SERVER_PORT=80
export STREAMLIT_SERVER_COOKIE_SECRET=dontforgottochangeme
```
4. As **flags on the command line** when running `streamlit run`:
```bash
streamlit run your_script.py --server.port 80
```
## Available options
All available configuration options are documented in [`config.toml`]. These options may be declared in a TOML file, as environment variables, or as command line options.
When using environment variables to override `config.toml`, convert the variable (including its section header) to upper snake case and add a `STREAMLIT_` prefix. For example, `STREAMLIT_CLIENT_SHOW_ERROR_DETAILS` is equivalent to the following in TOML:
```toml
[client]
showErrorDetails = true
```
When using command line options to override `config.toml` and environment variables, use the same case as you would in the TOML file and include the section header as a period-separated prefix. For example, the command line option `--server.enableStaticServing true` is equivalent to the following:
```toml
[server]
enableStaticServing = true
```
## Telemetry
As mentioned during the installation process, Streamlit collects usage statistics. You can find out
more by reading our Privacy Notice, but the high-level
summary is that although we collect telemetry data we cannot see and do not store information
contained in Streamlit apps.
If you'd like to opt out of usage statistics, add the following to your config file:
```toml
[browser]
gatherUsageStats = false
```
## Theming
You can change the base colors of your app using the `[theme]` section of the configuration system.
To learn more, see [Theming.]
## View all configuration options
As described in [Command-line options], you can
view all available configuration options using:
```bash
streamlit config show
```
################################################
Section 4.3 - static-file-serving.md
################################################
# Static file serving
Streamlit apps can host and serve small, static media files to support media embedding use cases that
won't work with the normal [media elements].
To enable this feature, set `enableStaticServing = true` under `[server]` in your config file,
or environment variable `STREAMLIT_SERVER_ENABLE_STATIC_SERVING=true`.
Media stored in the folder `./static/` relative to the running app file is served at path
`app/static/[filename]`, such as `http://localhost:8501/app/static/cat.png`.
## Details on usage
- Files with the following extensions will be served normally: `".jpg", ".jpeg", ".png", ".gif"`. Any other
file will be sent with header `Content-Type:text/plain` which will cause browsers to render in plain text.
This is included for security - other file types that need to render should be hosted outside the app.
- Streamlit also sets `X-Content-Type-Options:nosniff` for all files rendered from the static directory.
- For apps running on Streamlit Community Cloud:
- Files available in the Github repo will always be served. Any files generated while the app is running,
such as based on user interaction (file upload, etc), are not guaranteed to persist across user sessions.
- Apps which store and serve many files, or large files, may run into resource limits and be shut down.
## Example usage
- Put an image `cat.png` in the folder `./static/`
- Add `enableStaticServing = true` under `[server]` in your `.streamlit/config.toml`
- Any media in the `./static/` folder is served at the relative URL like `app/static/cat.png`
```toml
# .streamlit/config.toml
[server]
enableStaticServing = true
```
```python
# app.py
import streamlit as st
with st.echo():
st.title("CAT")
st.markdown("")
```
Additional resources:
- https://docs.streamlit.io/develop/concepts/configuration
- https://static-file-serving.streamlit.app/
<Cloud name="static-file-serving" height="1000px" />
################################################
Section 4.4 - theming.md
################################################
# Theming
In this guide, we provide examples of how Streamlit page elements are affected
by the various theme config options. For a more high-level overview of
Streamlit themes, see the Themes section of the
[main concepts documentation](/get-started/fundamentals/additional-features#themes).
Streamlit themes are defined using regular config options: a theme can be set
via command line flag when starting your app using `streamlit run` or by
defining it in the `[theme]` section of a `.streamlit/config.toml` file. For
more information on setting config options, please refer to the
[Streamlit configuration documentation].
The following config options show the default Streamlit Light theme recreated
in the `[theme]` section of a `.streamlit/config.toml` file.
```toml
[theme]
primaryColor="#FF4B4B"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#31333F"
font="sans serif"
```
Let's go through each of these options, providing screenshots to demonstrate
what parts of a Streamlit app they affect where needed.
## primaryColor
`primaryColor` defines the accent color most often used throughout a Streamlit
app. A few examples of Streamlit widgets that use `primaryColor` include
`st.checkbox`, `st.slider`, and `st.text_input` (when focused).

Note: Any CSS color can be used as the value for primaryColor and the other color
options below. This means that theme colors can be specified in hex or with
browser-supported color names like "green", "yellow", and
"chartreuse". They can even be defined in the RGB and HSL formats!
## backgroundColor
Defines the background color used in the main content area of your app.
## secondaryBackgroundColor
This color is used where a second background color is needed for added
contrast. Most notably, it is the sidebar's background color. It is also used
as the background color for most interactive widgets.

## textColor
This option controls the text color for most of your Streamlit app.
## font
Selects the font used in your Streamlit app. Valid values are `"sans serif"`,
`"serif"`, and `"monospace"`. This option defaults to `"sans serif"` if unset
or invalid.
Note that code blocks are always rendered using the monospace font regardless of
the font selected here.
## base
An easy way to define custom themes that make small changes to one of the
preset Streamlit themes is to use the `base` option. Using `base`, the
Streamlit Light theme can be recreated as a custom theme by writing the
following:
```toml
[theme]
base="light"
```
The `base` option allows you to specify a preset Streamlit theme that your
custom theme inherits from. Any theme config options not defined in your theme
settings have their values set to those of the base theme. Valid values for
`base` are `"light"` and `"dark"`.
For example, the following theme config defines a custom theme nearly identical
to the Streamlit Dark theme, but with a new `primaryColor`.
```toml
[theme]
base="dark"
primaryColor="purple"
```
If `base` itself is omitted, it defaults to `"light"`, so you can define a
custom theme that changes the font of the Streamlit Light theme to serif with
the following config
```toml
[theme]
font="serif"
```
------------------------------------------------------------------------------------------------
CHAPTER 5: connections.md
------------------------------------------------------------------------------------------------
################################################
Section 5.1 - connecting-to-data.md
################################################
# Connecting to data
Most Streamlit apps need some kind of data or API access to be useful - either retrieving data to view or saving the results of some user action. This data or API is often part of some remote service, database, or other data source.
**Anything you can do with Python, including data connections, will generally work in Streamlit**. Streamlit's [tutorials] are a great starting place for many data sources. However:
- Connecting to data in a Python application is often tedious and annoying.
- There are specific considerations for connecting to data from streamlit apps, such as caching and secrets management.
**Streamlit provides [`st.connection()`] to more easily connect your Streamlit apps to data and APIs with just a few lines of code**. This page provides a basic example of using the feature and then focuses on advanced usage.
For a comprehensive overview of this feature, check out this video tutorial by Joshua Carroll, Streamlit's Product Manager for Developer Experience. You'll learn about the feature's utility in creating and managing data connections within your apps by using real-world examples.
<YouTube videoId="xQwDfW7UHMo" />
## Basic usage
For basic startup and usage examples, read up on the relevant data source tutorial]. Streamlit has built-in connections to SQL dialects and Snowflake. We also maintain installable connections for [Cloud File Storage and Google Sheets.
If you are just starting, the best way to learn is to pick a data source you can access and get a minimal example working from one of the pages above 👆. Here, we will provide an ultra-minimal usage example for using a SQLite database. From there, the rest of this page will focus on advanced usage.
### A simple starting point - using a local SQLite database
A local SQLite database could be useful for your app's semi-persistent data storage.
Note: Community Cloud apps do not guarantee the persistence of local file storage, so the platform may delete data stored using this technique at any time.
To see the example below running live, check out the interactive demo below:
<Cloud name="experimental-connection" path="SQL" height="600px" />
#### Step 1: Install prerequisite library - SQLAlchemy
All SQLConnections in Streamlit use SQLAlchemy. For most other SQL dialects, you also need to install the driver. But the SQLite driver ships with python3, so it isn't necessary.
```bash
pip install SQLAlchemy==1.4.0
```
#### Step 2: Set a database URL in your Streamlit secrets.toml file
Create a directory and file `.streamlit/secrets.toml` in the same directory your app will run from. Add the following to the file.
```toml
# .streamlit/secrets.toml
[connections.pets_db]
url = "sqlite:///pets.db"
```
#### Step 3: Use the connection in your app
The following app creates a connection to the database, uses it to create a table and insert some data, then queries the data back and displays it in a data frame.
```python
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
```
In this example, we didn't set a `ttl=` value on the call to [`conn.query()`], meaning Streamlit caches the result indefinitely as long as the app server runs.
Now, on to more advanced topics! 🚀
## Advanced topics
### Global secrets, managing multiple apps and multiple data stores
Streamlit [supports a global secrets file] specified in the user's home directory, such as `~/.streamlit/secrets.toml`. If you build or manage multiple apps, we recommend using a global credential or secret file for local development across apps. With this approach, you only need to set up and manage your credentials in one place, and connecting a new app to your existing data sources is effectively a one-liner. It also reduces the risk of accidentally checking in your credentials to git since they don't need to exist in the project repository.
For cases where you have multiple similar data sources that you connect to during local development (such as a local vs. staging database), you can define different connection sections in your secrets or credentials file for different environments and then decide which to use at runtime. `st.connection` supports this with the _`name=env:<MY_NAME_VARIABLE>`_ syntax.
E.g., say I have a local and a staging MySQL database and want to connect my app to either at different times. I could create a global secrets file like this:
```toml
# ~/.streamlit/secrets.toml
[connections.local]
url = "mysql://me:****@localhost:3306/local_db"
[connections.staging]
url = "mysql://jdoe:******@staging.acmecorp.com:3306/staging_db"
```
Then I can configure my app connection to take its name from a specified environment variable
```python
# streamlit_app.py
import streamlit as st
conn = st.connection("env:DB_CONN", "sql")
df = conn.query("select * from mytable")
# ...
```
Now I can specify whether to connect to local or staging at runtime by setting the `DB_CONN` environment variable.
```bash
# connect to local
DB_CONN=local streamlit run streamlit_app.py
# connect to staging
DB_CONN=staging streamlit run streamlit_app.py
```
### Advanced SQLConnection configuration
The SQLConnection] configuration uses SQLAlchemy `create_engine()` function. It will take a single URL argument or attempt to construct a URL from several parts (username, database, host, and so on) using [`SQLAlchemy.engine.URL.create()`.
Several popular SQLAlchemy dialects, such as Snowflake and Google BigQuery, can be configured using additional arguments to `create_engine()` besides the URL. These can be passed as `**kwargs` to the [st.connection] call directly or specified in an additional secrets section called `create_engine_kwargs`.
E.g. snowflake-sqlalchemy takes an additional `connect_args` argument as a dictionary for configuration that isn’t supported in the URL. These could be specified as follows:
```toml
# .streamlit/secrets.toml
[connections.snowflake]
url = "snowflake://<user_login_name>@<account_identifier>/"
[connections.snowflake.create_engine_kwargs.connect_args]
authenticator = "externalbrowser"
warehouse = "xxx"
role = "xxx"
```
```python
# streamlit_app.py
import streamlit as st
# url and connect_args from secrets.toml above are picked up and used here
conn = st.connection("snowflake", "sql")
# ...
```
Alternatively, this could be specified entirely in `**kwargs`.
```python
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
```
You can also provide both kwargs and secrets.toml values, and they will be merged (typically, kwargs take precedence).
### Connection considerations in frequently used or long-running apps
By default, connection objects are cached without expiration using [`st.cache_resource`]. In most cases this is desired. You can do `st.connection('myconn', type=MyConnection, ttl=<N>)` if you want the connection object to expire after some time.
Many connection types are expected to be long-running or completely stateless, so expiration is unnecessary. Suppose a connection becomes stale (such as a cached token expiring or a server-side connection being closed). In that case, every connection has a `reset()` method, which will invalidate the cached version and cause Streamlit to recreate the connection the next time it is retrieved
Convenience methods like `query()` and `read()` will typically cache results by default using [`st.cache_data`] without an expiration. When an app can run many different read operations with large results, it can cause high memory usage over time and results to become stale in a long-running app, the same as with any other usage of `st.cache_data`. For production use cases, we recommend setting an appropriate `ttl` on these read operations, such as `conn.read('path/to/file', ttl="1d")`. Refer to [Caching] for more information.
For apps that could get significant concurrent usage, ensure that you understand any thread safety implications of your connection, particularly when using a connection built by a third party. Connections built by Streamlit should provide thread-safe operations by default.
### Build your own connection
Building your own basic connection implementation using an existing driver or SDK is quite straightforward in most cases. However, you can add more complex functionality with further effort. This custom implementation can be a great way to extend support to a new data source and contribute to the Streamlit ecosystem.
Maintaining a tailored internal Connection implementation across many apps can be a powerful practice for organizations with frequently used access patterns and data sources.
<Cloud name="experimental-connection" path="Build_your_own" height="600px" />
The typical steps are:
1. Declare the Connection class, extending [`ExperimentalBaseConnection`] with the type parameter bound to the underlying connection object:
```python
from streamlit.connections import ExperimentalBaseConnection
import duckdb
class DuckDBConnection(ExperimentalBaseConnection[duckdb.DuckDBPyConnection])
```
2. Implement the `_connect` method that reads any kwargs, external config/credential locations, and Streamlit secrets to initialize the underlying connection:
```python
def _connect(self, **kwargs) -> duckdb.DuckDBPyConnection:
if 'database' in kwargs:
db = kwargs.pop('database')
else:
db = self._secrets['database']
return duckdb.connect(database=db, **kwargs)
```
3. Add useful helper methods that make sense for your connection (wrapping them in `st.cache_data` where caching is desired)
### Connection-building best practices
We recommend applying the following best practices to make your Connection consistent with the Connections built into Streamlit and the wider Streamlit ecosystem. These practices are especially important for Connections that you intend to distribute publicly.
1. **Extend existing drivers or SDKs, and default to semantics that makes sense for their existing users.**
You should rarely need to implement complex data access logic from scratch when building a Connection. Use existing popular Python drivers and clients whenever possible. Doing so makes your Connection easier to maintain, more secure, and enables users to get the latest features. E.g. SQLConnection] extends SQLAlchemy, [FileConnection extends fsspec, GsheetsConnection extends gspread, etc.
Consider using access patterns, method/argument naming, and return values that are consistent with the underlying package and familiar to existing users of that package.
2. **Intuitive, easy to use read methods.**
Much of the power of st.connection is providing intuitive, easy-to-use read methods that enable app developers to get started quickly. Most connections should expose at least one read method that is:
- Named with a simple verb, like `read()`, `query()`, or `get()`
- Wrapped by `st.cache_data` by default, with at least `ttl=` argument supported
- If the result is in a tabular format, it returns a pandas DataFrame
- Provides commonly used keyword arguments (such as paging or formatting) with sensible defaults - ideally, the common case requires only 1-2 arguments.
3. **Config, secrets, and precedence in `_connect` method.**
Every Connection should support commonly used connection parameters provided via Streamlit secrets and keyword arguments. The names should match the ones used when initializing or configuring the underlying package.
Additionally, where relevant, Connections should support data source specific configuration through existing standard environment variables or config / credential files. In many cases, the underlying package provides constructors or factory functions that already handle this easily.
When you can specify the same connection parameters in multiple places, we recommend using the following precedence order when possible (highest to lowest):
- Keyword arguments specified in the code
- Streamlit secrets
- data source specific configuration (if relevant)
4. **Handling thread safety and stale connections.**
Connections should provide thread-safe operations when practical (which should be most of the time) and clearly document any considerations around this. Most underlying drivers or SDKs should provide thread-safe objects or methods - use these when possible.
If the underlying driver or SDK has a risk of stateful connection objects becoming stale or invalid, consider building a low impact health check or reset/retry pattern into the access methods. The SQLConnection built into Streamlit has a good example of this pattern using tenacity and the built-in [Connection.reset()] method. An alternate approach is to encourage developers to set an appropriate TTL on the `st.connection()` call to ensure it periodically reinitializes the connection object.
################################################
Section 5.2 - secrets-management.md
################################################
# Secrets management
Storing unencrypted secrets in a git repository is a bad practice. For applications that require access to sensitive credentials, the recommended solution is to store those credentials outside the repository - such as using a credentials file not committed to the repository or passing them as environment variables.
Streamlit provides native file-based secrets management to easily store and securely access your secrets in your Streamlit app.
Note: Existing secrets management tools, such as dotenv files, AWS credentials files, Google Cloud Secret Manager, or Hashicorp Vault, will work fine in Streamlit. We just add native secrets management for times when it's useful.
## How to use secrets management
### Develop locally and set up secrets
Streamlit provides two ways to set up secrets locally using TOML format:
1. In a **global secrets file** at `~/.streamlit/secrets.toml` for macOS/Linux or `%userprofile%/.streamlit/secrets.toml` for Windows:
```toml
# Everything in this section will be available as an environment variable
db_username = "Jane"
db_password = "mypassword"
# You can also add other sections if you like.
# The contents of sections as shown below will not become environment variables,
# but they'll be easily accessible from within Streamlit anyway as we show
# later in this doc.
[my_other_secrets]
things_i_like = ["Streamlit", "Python"]
```
If you use the global secrets file, you don't have to duplicate secrets across several project-level files if multiple Streamlit apps share the same secrets.
2. In a **per-project secrets file** at `$CWD/.streamlit/secrets.toml`, where `$CWD` is the folder you're running Streamlit from. If both a global secrets file and a per-project secrets file exist, _secrets in the per-project file overwrite those defined in the global file_.
Note: Add this file to your `.gitignore` so you don't commit your secrets!
### Use secrets in your app
Access your secrets by querying the `st.secrets` dict, or as environment variables. For example, if you enter the secrets from the section above, the code below shows you how to access them within your Streamlit app.
```python
import streamlit as st
# Everything is accessible via the st.secrets dict:
st.write("DB username:", st.secrets["db_username"])
st.write("DB password:", st.secrets["db_password"])
# And the root-level secrets are also accessible as environment variables:
import os
st.write(
"Has environment variables been set:",
os.environ["db_username"] == st.secrets["db_username"],
)
```
Note: You can access `st.secrets` via attribute notation (e.g. `st.secrets.key`), in addition to key notation (e.g. `st.secrets["key"]`) — like [st.session_state].
You can even compactly use TOML sections to pass multiple secrets as a single attribute. Consider the following secrets:
```toml
[db_credentials]
username = "my_username"
password = "my_password"
```
Rather than passing each secret as attributes in a function, you can more compactly pass the section to achieve the same result. See the notional code below, which uses the secrets above:
```python
# Verbose version
my_db.connect(username=st.secrets.db_credentials.username, password=st.secrets.db_credentials.password)
# Far more compact version!
my_db.connect(**st.secrets.db_credentials)
```
### Error handling
Here are some common errors you might encounter when using secrets management.
- If a `.streamlit/secrets.toml` is created _while_ the app is running, the server needs to be restarted for changes to be reflected in the app.
- If you try accessing a secret, but no `secrets.toml` file exists, Streamlit will raise a `FileNotFoundError` exception:

- If you try accessing a secret that doesn't exist, Streamlit will raise a `KeyError` exception:
```python
import streamlit as st
st.write(st.secrets["nonexistent_key"])
```

### Use secrets on Streamlit Community Cloud
When you deploy your app to Streamlit Community Cloud, you can use the same secrets management workflow as you would locally. However, you'll need to also set up your secrets in the Community Cloud Secrets Management console. Learn how to do so via the Cloud-specific [Secrets management](/deploy/streamlit-community-cloud/deploy-your-app/secrets-management) documentation.
################################################
Section 5.3 - security-reminders.md
################################################
# Security reminders
## Protect your secrets
Never save usernames, passwords, or security keys directly in your code or commit them to your repository.
### Use environment variables
Avoid putting sensitve information in your code by using environment variables. Be sure to check out [`st.secrets`]. Research any platform you use to follow their security best practices. If you use Streamlit Community Cloud, [Secrets management](/deploy/streamlit-community-cloud/deploy-your-app/secrets-management) allows you save environment variables and store secrets outside of your code.
### Keep `.gitignore` updated
If you use any sensitive or private information during development, make sure that information is saved in separate files from your code. Ensure `.gitignore` is properly configured to prevent saving private information to your repository.
## Pickle warning
Streamlit's [`st.cache_data`] and [`st.session_state`] implicitly use the `pickle` module, which is known to be insecure. It is possible to construct malicious pickle data that will execute arbitrary code during unpickling. Never load data that could have come from an untrusted source in an unsafe mode or that could have been tampered with. **Only load data you trust**.
- When using `st.cache_data`, anything your function returns is pickled and stored, then unpickled on retrieval. Ensure your cached functions return trusted values. This warning also applies to [`st.cache`] (deprecated).
- When the `runner.enforceSerializableSessionState` [configuration option](<>) is set to `true`, ensure all data saved and retrieved from Session State is trusted.
------------------------------------------------------------------------------------------------
CHAPTER 6: custom-components.md
------------------------------------------------------------------------------------------------
################################################
Section 6.1 - components-api.md
################################################
# Intro to custom components
The first step in developing a Streamlit Component is deciding whether to create a static component (i.e. rendered once, controlled by Python) or to create a bi-directional component that can communicate from Python to JavaScript and back.
## Create a static component
If your goal in creating a Streamlit Component is solely to display HTML code or render a chart from a Python visualization library, Streamlit provides two methods that greatly simplify the process: `components.html()` and `components.iframe()`.
If you are unsure whether you need bi-directional communication, **start here first**!
### Render an HTML string
While [`st.text`], [`st.markdown`] and [`st.write`] make it easy to write text to a Streamlit app, sometimes you'd rather implement a custom piece of HTML. Similarly, while Streamlit natively supports [many charting libraries], you may want to implement a specific HTML/JavaScript template for a new charting library. [`components.html`] works by giving you the ability to embed an iframe inside of a Streamlit app that contains your desired output.
**Example**
```python
import streamlit as st
import streamlit.components.v1 as components
# bootstrap 4 collapse example
components.html(
"""
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
<div class="card">
<div class="card-header" id="headingOne">
<h5 class="mb-0">
<button class="btn btn-link" data-toggle="collapse" data-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
Collapsible Group Item #1
</button>
</h5>
<div class="card-body">
Collapsible Group Item #1 content
</div>
</div>
<div class="card-header" id="headingTwo">
<h5 class="mb-0">
<button class="btn btn-link collapsed" data-toggle="collapse" data-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
Collapsible Group Item #2
</button>
</h5>
<div class="card-body">
Collapsible Group Item #2 content
</div>
</div>
</div>
""",
height=600,
)
```
### Render an iframe URL
[`components.iframe`] is similar in features to `components.html`, with the difference being that `components.iframe` takes a URL as its input. This is used for situations where you want to include an entire page within a Streamlit app.
**Example**
```python
import streamlit as st
import streamlit.components.v1 as components
# embed streamlit docs in a streamlit app
components.iframe("https://example.com", height=500)
```
## Create a bi-directional component
A bi-directional Streamlit Component has two parts:
1. A **frontend**, which is built out of HTML and any other web tech you like (JavaScript, React, Vue, etc.), and gets rendered in Streamlit apps via an iframe tag.
2. A **Python API**, which Streamlit apps use to instantiate and talk to that frontend
To make the process of creating bi-directional Streamlit Components easier, we've created a React template and a TypeScript-only template in the Streamlit Component-template GitHub repo. We also provide some example Components in the same repo.
### Development Environment Setup
To build a Streamlit Component, you need the following installed in your development environment:
- Python 3.9 - Python 3.13
- Streamlit
- nodejs
- npm or yarn
Clone the component-template GitHub repo, then decide whether you want to use the React.js ("template") or plain TypeScript ("template-reactless") template.
1. Initialize and build the component template frontend from the terminal:
```bash
# React template
template/my_component/frontend
npm install    # Initialize the project and install npm dependencies
npm run start  # Start the Webpack dev server
# or
# TypeScript-only template
template-reactless/my_component/frontend
npm install    # Initialize the project and install npm dependencies
npm run start  # Start the Webpack dev server
```
2. _From a separate terminal_, run the Streamlit app (Python) that declares and uses the component:
```bash
# React template
cd template
. venv/bin/activate # or similar to activate the venv/conda environment where Streamlit is installed
pip install -e . # install template as editable package
streamlit run my_component/example.py # run the example
# or
# TypeScript-only template
cd template-reactless
. venv/bin/activate # or similar to activate the venv/conda environment where Streamlit is installed
pip install -e . # install template as editable package
streamlit run my_component/example.py # run the example
```
After running the steps above, you should see a Streamlit app in your browser that looks like this:

The example app from the template shows how bi-directional communication is implemented. The Streamlit Component displays a button (`Python → JavaScript`), and the end-user can click the button. Each time the button is clicked, the JavaScript front-end increments the counter value and passes it back to Python (`JavaScript → Python`), which is then displayed by Streamlit (`Python → JavaScript`).
### Frontend
Because each Streamlit Component is its own webpage that gets rendered into an `iframe`, you can use just about any web tech you'd like to create that web page. We provide two templates to get started with in the Streamlit Components-template GitHub repo; one of those templates uses React and the other does not.
Note: Even if you're not already familiar with React, you may still want to check out the React-based
template. It handles most of the boilerplate required to send and receive data from Streamlit, and
you can learn the bits of React you need as you go.
If you'd rather not use React, please read this section anyway! It explains the fundamentals of
Streamlit ↔ Component communication.
</Note>
#### React
The React-based template is in `template/my_component/frontend/src/MyComponent.tsx`.
- `MyComponent.render()` is called automatically when the component needs to be re-rendered (just like in any React app)
- Arguments passed from the Python script are available via the `this.props.args` dictionary:
```python
# Send arguments in Python:
result = my_component(greeting="Hello", name="Streamlit")
```
```javascript
// Receive arguments in frontend:
let greeting = this.props.args["greeting"]; // greeting = "Hello"
let name = this.props.args["name"]; // name = "Streamlit"
```
- Use `Streamlit.setComponentValue()` to return data from the component to the Python script:
```javascript
// Set value in frontend:
Streamlit.setComponentValue(3.14);
```
```python
# Access value in Python:
result = my_component(greeting="Hello", name="Streamlit")
st.write("result = ", result) # result = 3.14
```
When you call `Streamlit.setComponentValue(new_value)`, that new value is sent to Streamlit, which then _re-executes the Python script from top to bottom_. When the script is re-executed, the call to `my_component(...)` will return the new value.
From a _code flow_ perspective, it appears that you're transmitting data synchronously with the frontend: Python sends the arguments to JavaScript, and JavaScript returns a value to Python, all in a single function call! But in reality this is all happening _asynchronously_, and it's the re-execution of the Python script that achieves the sleight of hand.
- Use `Streamlit.setFrameHeight()` to control the height of your component. By default, the React template calls this automatically (see `StreamlitComponentBase.componentDidUpdate()`). You can override this behavior if you need more control.
- There's a tiny bit of magic in the last line of the file: `export default withStreamlitConnection(MyComponent)` - this does some handshaking with Streamlit, and sets up the mechanisms for bi-directional data communication.
#### TypeScript-only
The TypeScript-only template is in `template-reactless/my_component/frontend/src/MyComponent.tsx`.
This template has much more code than its React sibling, in that all the mechanics of handshaking, setting up event listeners, and updating the component's frame height are done manually. The React version of the template handles most of these details automatically.
- Towards the bottom of the source file, the template calls `Streamlit.setComponentReady()` to tell Streamlit it's ready to start receiving data. (You'll generally want to do this after creating and loading everything that the Component relies on.)
- It subscribes to `Streamlit.RENDER_EVENT` to be notified of when to redraw. (This event won't be fired until `setComponentReady` is called)
- Within its `onRender` event handler, it accesses the arguments passed in the Python script via `event.detail.args`
- It sends data back to the Python script in the same way that the React template does—clicking on the "Click Me!" button calls `Streamlit.setComponentValue()`
- It informs Streamlit when its height may have changed via `Streamlit.setFrameHeight()`
#### Working with Themes
<Note>
Custom component theme support requires streamlit-component-lib version 1.2.0 or higher.
Along with sending an `args` object to your component, Streamlit also sends
a `theme` object defining the active theme so that your component can adjust
its styling in a compatible way. This object is sent in the same message as
`args`, so it can be accessed via `this.props.theme` (when using the React
template) or `event.detail.theme` (when using the plain TypeScript template).
The `theme` object has the following shape:
```json
{
"base": "lightORdark",
"primaryColor": "someColor1",
"backgroundColor": "someColor2",
"secondaryBackgroundColor": "someColor3",
"textColor": "someColor4",
"font": "someFont"
}
```
The `base` option allows you to specify a preset Streamlit theme that your custom theme inherits from. Any theme config options not defined in your theme settings have their values set to those of the base theme. Valid values for `base` are `"light"` and `"dark"`.
Note that the theme object has fields with the same names and semantics as the
options in the "theme" section of the config options printed with the command
`streamlit config show`.
When using the React template, the following CSS variables are also set
automatically.
```css
--base
--primary-color
--background-color
--secondary-background-color
--text-color
--font
```
If you're not familiar with
CSS variables,
the TLDR version is that you can use them like this:
```css
.mySelector {
color: var(--text-color);
}
```
These variables match the fields defined in the `theme` object above, and
whether to use CSS variables or the theme object in your component is a matter
of personal preference.
#### Other frontend details
- Because you're hosting your component from a dev server (via `npm run start`), any changes you make should be automatically reflected in the Streamlit app when you save.
- If you want to add more packages to your component, run `npm add` to add them from within your component's `frontend/` directory.
```bash
npm add baseui
```
- To build a static version of your component, run `npm run export`. See [Prepare your Component](publish#prepare-your-component) for more information
### Python API
`components.declare_component()` is all that's required to create your Component's Python API:
```python
import streamlit.components.v1 as components
my_component = components.declare_component(
"my_component",
url="http://localhost:3001"
)
```
You can then use the returned `my_component` function to send and receive data with your frontend code:
```python
# Send data to the frontend using named arguments.
return_value = my_component(name="Blackbeard", ship="Queen Anne's Revenge")
# `my_component`'s return value is the data returned from the frontend.
st.write("Value = ", return_value)
```
While the above is all you need to define from the Python side to have a working Component, we recommend creating a "wrapper" function with named arguments and default values, input validation and so on. This will make it easier for end-users to understand what data values your function accepts and allows for defining helpful docstrings.
Please see this example from the Components-template for an example of creating a wrapper function.
### Data serialization
#### Python → Frontend
You send data from Python to the frontend by passing keyword args to your Component's invoke function (that is, the function returned from `declare_component`). You can send the following types of data from Python to the frontend:
- Any JSON-serializable data
- `numpy.array`
- `pandas.DataFrame`
Any JSON-serializable data gets serialized to a JSON string, and deserialized to its JavaScript equivalent. `numpy.array` and `pandas.DataFrame` get serialized using Apache Arrow and are deserialized as instances of `ArrowTable`, which is a custom type that wraps Arrow structures and provides a convenient API on top of them.
#### Frontend → Python
You send data from the frontend to Python via the `Streamlit.setComponentValue()` API (which is part of the template code). Unlike arg-passing from Python → frontend, **this API takes a single value**. If you want to return multiple values, you'll need to wrap them in an `Array` or `Object`.
Custom Components can send JSON-serializable data from the frontend to Python, as well as Apache Arrow `ArrowTable`s to represent dataframes.
################################################
Section 6.2 - create-component.md
################################################
# Create a Component
Note: If you are only interested in **using Streamlit Components**, then you can skip this section and
head over to the Streamlit Components Gallery to find and install
components created by the community!
Developers can write JavaScript and HTML "components" that can be rendered in Streamlit apps. Streamlit Components can receive data from, and also send data to, Streamlit Python scripts.
Streamlit Components let you expand the functionality provided in the base Streamlit package. Use Streamlit Components to create the needed functionality for your use-case, then wrap it up in a Python package and share with the broader Streamlit community!
**Types of Streamlit Components you could create include:**
- Custom versions of existing Streamlit elements and widgets, such as `st.slider` or `st.file_uploader`.
- Completely new Streamlit elements and widgets by wrapping existing React.js, Vue.js, or other JavaScript widget toolkits.
- Rendering Python objects having methods that output HTML, such as IPython `__repr_html__`.
- Convenience functions for commonly-used web features like GitHub gists and Pastebin.
## Part 1: Setup and Architecture
<YouTube videoId="BuD3gILJW-Q" />
## Part 2: Make a Slider Widget
<YouTube videoId="QjccJl_7Jco" />
################################################
Section 6.3 - limitations.md
################################################
# Limitations of custom components
## How do Streamlit Components differ from functionality provided in the base Streamlit package?
- Streamlit Components are wrapped up in an iframe, which gives you the ability to do whatever you want (within the iframe) using any web technology you like.
## What types of things aren't possible with Streamlit Components?
Because each Streamlit Component gets mounted into its own sandboxed iframe, this implies a few limitations on what is possible with Components:
- **Can't communicate with other Components**: Components can’t contain (or otherwise communicate with) other components, so Components cannot be used to build something like a grid layout.
- **Can't modify CSS**: A Component can’t modify the CSS that the rest of the Streamlit app uses, so you can't create something to put the app in dark mode, for example.
- **Can't add/remove elements**: A Component can’t add or remove other elements of a Streamlit app, so you couldn't make something to remove the app menu, for example.
## My Component seems to be blinking/stuttering...how do I fix that?
Currently, no automatic debouncing of Component updates is performed within Streamlit. The Component creator themselves can decide to rate-limit the updates they send back to Streamlit.
################################################
Section 6.4 - publish-component.md
################################################
# Publish a Component
## Publish to PyPI
Publishing your Streamlit Component to PyPI makes it easily accessible to Python users around the world. This step is completely optional, so if you won’t be releasing your component publicly, you can skip this section!
Note: For [static Streamlit Components], publishing a Python package to PyPI follows the same steps as the
core PyPI packaging instructions. A static Component likely contains only Python code, so once you have your
setup.py file correct and
generate your distribution files, you're ready to
upload to PyPI.
[Bi-directional Streamlit Components] at minimum include both Python and JavaScript code, and as such, need a bit more preparation before they can be published on PyPI. The remainder of this page focuses on the bi-directional Component preparation process.
### Prepare your Component
A bi-directional Streamlit Component varies slightly from a pure Python library in that it must contain pre-compiled frontend code. This is how base Streamlit works as well; when you `pip install streamlit`, you are getting a Python library where the HTML and frontend code contained within it have been compiled into static assets.
The component-template GitHub repo provides the folder structure necessary for PyPI publishing. But before you can publish, you'll need to do a bit of housekeeping:
1. Give your Component a name, if you haven't already
- Rename the `template/my_component/` folder to `template/<component name>/`
- Pass your component's name as the the first argument to `declare_component()`
2. Edit `MANIFEST.in`, change the path for recursive-include from `package/frontend/build *` to `<component name>/frontend/build *`
3. Edit `setup.py`, adding your component's name and other relevant info
4. Create a release build of your frontend code. This will add a new directory, `frontend/build/`, with your compiled frontend in it:
```bash
cd frontend
npm run build
```
5. Pass the build folder's path as the `path` parameter to `declare_component`. (If you're using the template Python file, you can set `_RELEASE = True` at the top of the file):
```python
import streamlit.components.v1 as components
# Change this:
# component = components.declare_component("my_component", url="http://localhost:3001")
# To this:
parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/build")
component = components.declare_component("new_component_name", path=build_dir)
```
### Build a Python wheel
Once you've changed the default `my_component` references, compiled the HTML and JavaScript code and set your new component name in `components.declare_component()`, you're ready to build a Python wheel:
1. Make sure you have the latest versions of setuptools, wheel, and twine
2. Create a wheel from the source code:
```bash
# Run this from your component's top-level directory; that is,
# the directory that contains `setup.py`
python setup.py sdist bdist_wheel
```
### Upload your wheel to PyPI
With your wheel created, the final step is to upload to PyPI. The instructions here highlight how to upload to Test PyPI, so that you can learn the mechanics of the process without worrying about messing anything up. Uploading to PyPI follows the same basic procedure.
1. Create an account on Test PyPI if you don't already have one
- Visit https://test.pypi.org/account/register/ and complete the steps
- Visit https://test.pypi.org/manage/account/#api-tokens and create a new API token. Don’t limit the token scope to a particular project, since you are creating a new project. Copy your token before closing the page, as you won’t be able to retrieve it again.
2. Upload your wheel to Test PyPI. `twine` will prompt you for a username and password. For the username, use **\_\_token\_\_**. For the password, use your token value from the previous step, including the `pypi-` prefix:
```bash
python -m twine upload --repository testpypi dist/*
```
3. Install your newly-uploaded package in a new Python project to make sure it works:
```bash
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-pkg-YOUR-USERNAME-HERE
```
If all goes well, you're ready to upload your library to PyPI by following the instructions at https://packaging.python.org/tutorials/packaging-projects/#next-steps.
Congratulations, you've created a publicly-available Streamlit Component!
## Promote your Component!
We'd love to help you share your Component with the Streamlit Community! To share it:
1. If you host your code on GitHub, add the tag `streamlit-component`, so that it's listed in the GitHub **streamlit-component** topic:

2. Post on the Streamlit Forum in Show the Community!. Use a post title similar to "New Component: `<your component name>`, a new way to do X".
3. Add your component to the Community Component Tracker.
4. Tweet us at @streamlit so that we can retweet your announcement for you.
Our Components Gallery is updated approximately every month. Follow the above recommendations to maximize the liklihood of your component landing in our Components Gallery. Community Components featured in our docs are hand-curated on a less-regular basis. Popular components with many stars and good documentation are more likely to be selected.
------------------------------------------------------------------------------------------------
CHAPTER 7: multipage-apps.md
------------------------------------------------------------------------------------------------
################################################
Section 7.1 - overview.md
################################################
# Overview of multipage apps
Streamlit provides two built-in mechanisms for creating multipage apps. The simplest method is to use a `pages/` directory. However, the preferred and more customizable method is to use `st.navigation`.
## `st.Page` and `st.navigation`
If you want maximum flexibility in defining your multipage app, we recommend using `st.Page` and `st.navigation`. With `st.Page` you can declare any Python file or `Callable` as a page in your app. Furthermore, you can define common elements for your pages in your entrypoint file (the file you pass to `streamlit run`). With these methods, your entrypoint file becomes like a picture frame shared by all your pages.
You must include `st.navigation` in your entrypoint file to configure your app's navigation menu. This is also how your entrypoint file serves as the router between your pages.
## `pages/` directory
If you're looking for a quick and simple solution, just place a `pages/` directory next to your entrypoint file. For every Python file in your `pages/` directory, Streamlit will create an additional page for your app. Streamlit determines the page labels and URLs from the file name and automatically populates a navigation menu at the top of your app's sidebar.
```
your_working_directory/
├── pages/
│   ├── a_page.py
│   └── another_page.py
└── your_homepage.py
```
Streamlit determines the page order in navigation from the filenames. You can use numerical prefixes in the filenames to adjust page order. For more information, see [How pages are sorted in the sidebar]. If you want to customize your navigation menu with this option, you can deactivate the default navigation through [configuration] (`client.showSidebarNavigation = false`). Then, you can use `st.page_link` to manually contruct a custom navigation menu. With `st.page_link`, you can change the page label and icon in your navigation menu, but you can't change the URLs of your pages.
## Page terminology
A page has four identifying pieces as follows:
- **Page source**: This is a Python file or callable function with the page's source code.
- **Page label**: This is how the page is identified within the navigation menu. See <i style={{ verticalAlign: "-.25em" }} class="material-icons-sharp">looks_one</i>.
- **Page title**: This is the content of the HTML `<title>` element and how the page is identified within a browser tab. See <i style={{ verticalAlign: "-.25em" }} class="material-icons-sharp">looks_two</i>.
- **Page URL pathname**: This is the relative path of the page from the root URL of the app. See <i style={{ verticalAlign: "-.25em" }} class="material-icons-sharp">looks_3</i>.
Additionly, a page can have two icons as follows:
- **Page favicon**: This is the icon next to your page title within a browser tab. See <i style={{ verticalAlign: "-.25em" }} class="material-icons-sharp">looks_4</i>.
- **Page icon**: This is the icon next to your page label in the navigation menu. See <i style={{ verticalAlign: "-.25em" }} class="material-icons-sharp">looks_5</i>.
Typically, the page icon and favicon are the same, but it's possible make them different.

## Automatic page labels and URLs
If you use `st.Page` without declaring the page title or URL pathname, Streamlit falls back on automatically determining the page label, title, and URL pathname in the same manner as when you use a `pages/` directory with the default navigation menu. This section describes this naming convention which is shared between the two approaches to multipage apps.
### Parts of filenames and callables
Filenames are composed of four different parts as follows (in order):
1. `number`: A non-negative integer.
2. `separator`: Any combination of underscore (`"_"`), dash (`"-"`), and space (`" "`).
3. `identifier`: Everything up to, but not including, `".py"`.
4. `".py"`
For callables, the function name is the `identifier`, including any leading or trailing underscores.
### How Streamlit converts filenames into labels and titles
Within the navigation menu, Streamlit displays page labels and titles as follows:
1. If your page has an `identifier`, Streamlit displays the `identifier`. Any underscores within the page's `identifier` are treated as spaces. Therefore, leading and trailing underscores are not shown. Sequential underscores appear as a single space.
2. Otherwise, if your page has a `number` but does not have an `identifier`, Streamlit displays the `number`, unmodified. Leading zeros are included, if present.
3. Otherwise, if your page only has a `separator` with no `number` and no `identifier`, Streamlit will not display the page in the sidebar navigation.
The following filenames and callables would all display as "Awesome page" in the sidebar navigation.
- `"Awesome page.py"`
- `"Awesome_page.py"`
- `"02Awesome_page.py"`
- `"--Awesome_page.py"`
- `"1_Awesome_page.py"`
- `"33 - Awesome page.py"`
- `Awesome_page()`
- `_Awesome_page()`
- `__Awesome_page__()`
### How Streamlit converts filenames into URL pathnames
Your app's homepage is associated to the root URL of app. For all other pages, their `identifier` or `number` becomes their URL pathname as follows:
- If your page has an `identifier` that came from a filename, Streamlit uses the `identifier` with one modification. Streamlit condenses each consecutive grouping of spaces (`" "`) and underscores (`"_"`) to a single underscore.
- Otherwise, if your page has an `identifier` that came from the name of a callable, Streamlit uses the `identifier` unmodified.
- Otherwise, if your page has a `number` but does not have an `identifier`, Streamlit uses the `number`. Leading zeros are included, if present.
For each filename in the list above, the URL pathname would be "Awesome_page" relative to the root URL of the app. For example, if your app was running on `localhost` port `8501`, the full URL would be `localhost:8501/awesome_page`. For the last two callables, however, the pathname would include the leading and trailing underscores to match the callable name exactly.
## Navigating between pages
The primary way users navigate between pages is through the navigation widget. Both methods for defining multipage apps include a default navigation menu that appears in the sidebar. When a user clicks this navigation widget, the app reruns and loads the selected page. Optionally, you can hide the default navigation UI and build your own with [`st.page_link`]. For more information, see [Build a custom navigation menu with `st.page_link`].
If you need to programmatically switch pages, use [`st.switch_page`].
Users can also navigate between pages using URLs as noted above. When multiple files have the same URL pathname, Streamlit picks the first one (based on the ordering in the navigation menu. Users can view a specific page by visiting the page's URL.
<Important>
Navigating between pages by URL creates a new browser session. In particular, clicking markdown links to other pages resets ``st.session_state``. In order to retain values in ``st.session_state``, handle page switching through Streamlit navigation commands and widgets, like ``st.navigation``, ``st.switch_page``, ``st.page_link``, and the built-in navigation menu.
</Important>
If a user tries to access a URL for a page that does not exist, they will see a modal like the one below, saying "Page not found."

################################################
Section 7.2 - page-and-navigation.md
################################################
# Define multipage apps with st.Page and st.navigation
# Define multipage apps with `st.Page` and `st.navigation`
`st.Page` and `st.navigation` are the preferred commands for defining multipage apps. With these commands, you have flexibility to organize your project files and customize your navigation menu. Simply initialize `StreamlitPage` objects with `st.Page`, then pass those `StreamlitPage` objects to `st.navigation` in your entrypoint file (i.e. the file you pass to `streamlit run`).
This page assumes you understand the [Page terminology] presented in the overview.
## App structure
When using `st.navigation`, your entrypoint file acts like a page router. Each page is a script executed from your entrypoint file. You can define a page from a Python file or function. If you include elements or widgets in your entrypoint file, they become common elements between your pages. In this case, you can think of your entrypoint file like a picture frame around each of your pages.
You can only call `st.navigation` once per app run and you must call it from your entrypoint file. When a user selects a page in navigation (or is routed through a command like `st.switch_page`), `st.navigation` returns the selected page. You must manually execute that page with the `.run()` method. The following example is a two-page app where each page is defined by a Python file.
**Directory structure:**
```
your-repository/
├── page_1.py
├── page_2.py
└── streamlit_app.py
```
**`streamlit_app.py`:**
```python
import streamlit as st
pg = st.navigation([st.Page("page_1.py"), st.Page("page_2.py")])
pg.run()
```
## Defining pages
`st.Page` lets you define a page. The first and only required argument defines your page source, which can be a Python file or function. When using Python files, your pages may be in a subdirectory (or superdirectory). The path to your page file must always be relative to the entrypoint file. Once you create your page objects, pass them to `st.navigation` to register them as pages in your app.
If you don't define your page title or URL pathname, Streamlit will infer them from the file or function name as described in the multipage apps [Overview]. However, `st.Page` lets you configure them manually. Within `st.Page`, Streamlit uses `title` to set the page label and title. Additionaly, Streamlit uses `icon` to set the page icon and favicon. If you want to have a different page title and label, or different page icon and favicon, you can use `st.set_page_config` to change the page title and/or favicon. Just call `st.set_page_config` after `st.navigation`, either in your entrypoint file or in your page source.
The following example uses `st.set_page_config` to set a page title and favicon consistently across pages. Each page will have its own label and icon in the navigation menu, but the browser tab will show a consistent title and favicon on all pages.
**Directory structure:**
```
your-repository/
├── create.py
├── delete.py
└── streamlit_app.py
```
**`streamlit_app.py`:**
```python
import streamlit as st
create_page = st.Page("create.py", title="Create entry", icon=":material/add_circle:")
delete_page = st.Page("delete.py", title="Delete entry", icon=":material/delete:")
pg = st.navigation([create_page, delete_page])
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()
```

## Customizing navigation
If you want to group your pages into sections, `st.navigation` lets you insert headers within your navigation. Alternatively, you can disable the default navigation widget and build a custom navigation menu with `st.page_link`.
Additionally, you can dynamically change which pages you pass to `st.navigation`. However, only the page returned by `st.navigation` accepts the `.run()` method. If a user enters a URL with a pathname, and that pathname is not associated to a page in `st.navigation` (on first run), Streamlit will throw a "Page not found" error and redirect them to the default page.
### Adding section headers
As long as you don't want to hide a valid, accessible page in the navigation menu, the simplest way to customize your navigation menu is to organize the pages within `st.navigation`. You can sort or group pages, as well as remove any pages you don't want the user to access. This is a convenient way to handle user permissions.
The following example creates two menu states. When a user starts a new session, they are not logged in. In this case, the only available page is the login page. If a user tries to access another page by URL, it will create a new session and Streamlit will not recognize the page. The user will be diverted to the login page. However, after a user logs in, they will see a navigation menu with three sections and be directed to the dashboard as the app's default page (i.e. homepage).
**Directory structure:**
```
your-repository/
├── reports
│   ├── alerts.py
│   ├── bugs.py
│   └── dashboard.py
├── tools
│   ├── history.py
│   └── search.py
└── streamlit_app.py
```
**`streamlit_app.py`:**
```python
import streamlit as st
if "logged_in" not in st.session_state:
st.session_state.logged_in = False
def login():
if st.button("Log in"):
st.session_state.logged_in = True
st.rerun()
def logout():
if st.button("Log out"):
st.session_state.logged_in = False
st.rerun()
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
dashboard = st.Page(
"reports/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True
)
bugs = st.Page("reports/bugs.py", title="Bug reports", icon=":material/bug_report:")
alerts = st.Page(
"reports/alerts.py", title="System alerts", icon=":material/notification_important:"
)
search = st.Page("tools/search.py", title="Search", icon=":material/search:")
history = st.Page("tools/history.py", title="History", icon=":material/history:")
if st.session_state.logged_in:
pg = st.navigation(
{
"Account": [logout_page],
"Reports": [dashboard, bugs, alerts],
"Tools": [search, history],
}
)
else:
pg = st.navigation([login_page])
pg.run()
```

### Dynamically changing the available pages
You can change what pages are available to a user by updating the list of pages in `st.navigation`. This is a convenient way to handle role-based or user-based access to certain pages. For more information, check out our tutorial, [Create a dynamic navigation menu].
### Building a custom navigation menu
If you want more control over your navigation menu, you can hide the default navigation and build your own. You can hide the default navigation by including `position="hidden"` in your `st.navigation` command. If you want a page to be available to a user without showing it in the navigation menu, you must use this method. A user can't be routed to a page if the page isn't included in `st.navigation`. This applies to navigation by URL as well as commands like `st.switch_page` and `st.page_link`.
################################################
Section 7.3 - page_directory.md
################################################
# Creating multipage apps using the `pages/` directory
The most customizable method for declaring multipage apps is using [Page and navigation]. However, Streamlit also provides a frictionless way to create multipage apps where pages are automatically recognized and shown in a navigation widget inside your app's sidebar. This method uses the `pages/` directory.
This page assumes you understand the [Page terminology] presented in the overview.
## App structure
When you use the `pages/` directory, Streamlit identifies pages in your multipage app by directory structure and filenames. Your entrypoint file (the file you pass to `streamlit run`), is your app's homepage. When you have a `pages/` directory next to your entrypoint file, Streamlit will identify each Python file within it as a page. The following example has three pages. `your_homepage.py` is the entrypoint file and homepage.
```
your_working_directory/
├── pages/
│   ├── a_page.py
│   └── another_page.py
└── your_homepage.py
```
Run your multipage app just like you would for a single-page app. Pass your entrypoint file to `streamlit run`.
```
streamlit run your_homepage.py
```
Only `.py` files in the `pages/` directory will be identified as pages. Streamlit ignores all other files in the `pages/` directory and its subdirectories. Streamlit also ignores Python files in subdirectories of `pages/`.
Note: If you call `st.navigation` in your app (in any session), Streamlit will switch to using the newer, Page-and-navigation multipage structure. In this case, the `pages/` directory will be ignored across all sessions. You will not be able to revert back to the `pages/` directory unless you restart you app.
### How pages are sorted in the sidebar
See the overview to understand how Streamlit assigns [Automatic page labels and URLs] based on the `number`, `separator`, `identifier`, and `".py"` extension that constitute a filename.
The entrypoint file is always displayed first. The remaining pages are sorted as follows:
- Files that have a `number` appear before files without a `number`.
- Files are sorted based on the `number` (if any), followed by the `label` (if any).
- When files are sorted, Streamlit treats the `number` as an actual number rather than a string. So `03` is the same as `3`.
This table shows examples of filenames and their corresponding labels, sorted by the order in which they appear in the sidebar.
**Examples**:
| **Filename**              | **Rendered label** |
| :------------------------ | :----------------- |
| `1 - first page.py`       | first page         |
| `12 monkeys.py`           | monkeys            |
| `123.py`                  | 123                |
| `123_hello_dear_world.py` | hello dear world   |
| `_12 monkeys.py`          | 12 monkeys         |
Note: Emojis can be used to make your page names more fun! For example, a file named `🏠_Home.py` will create a page titled "🏠 Home" in the sidebar. When adding emojis to filenames, it’s best practice to include a numbered prefix to make autocompletion in your terminal easier. Terminal-autocomplete can get confused by unicode (which is how emojis are represented).
## Notes and limitations
- Pages support run-on-save.
- When you update a page while your app is running, this causes a rerun for users currently viewing that exact page.
- When you update a page while your app is running, the app will not automatically rerun for users currently viewing a different page.
- While your app is running, adding or deleting a page updates the sidebar navigation immediately.
- [`st.set_page_config`] works at the page level.
- When you set `title` or `favicon` using `st.set_page_config`, this applies to the current page only.
- When you set `layout` using `st.set_page_config`, the setting will remain for the session until changed by another call to `st.set_page_config`. If you use `st.set_page_config` to set `layout`, it's recommended to call it on _all_ pages.
- Pages share the same Python modules globally:
```python
# page1.py
import foo
foo.hello = 123
# page2.py
import foo
st.write(foo.hello)  # If page1 already executed, this writes 123
```
- Pages share the same [st.session_state]:
```python
# page1.py
import streamlit as st
if "shared" not in st.session_state:
st.session_state["shared"] = True
# page2.py
import streamlit as st
st.write(st.session_state["shared"]) # If page1 already executed, this writes True
```
You now have a solid understanding of multipage apps. You've learned how to structure apps, define pages, and navigate between pages in the user interface. It's time to [create your first multipage app](/get-started/tutorials/create-a-multipage-app)! 🥳
################################################
Section 7.4 - widgets.md
################################################
# Working with widgets in multipage apps
When you create a widget in a Streamlit app, Streamlit generates a widget ID and uses it to make your widget stateful. As your app reruns with user interaction, Streamlit keeps track of the widget's value by associating its value to its ID. In particular, a widget's ID depends on the page where it's created. If you define an identical widget on two different pages, then the widget will reset to its default value when you switch pages.
This guide explains three strategies to deal with the behavior if you'd like to have a widget remain stateful across all pages. If don't want a widget to appear on all pages, but you do want it to remain stateful when you navigate away from its page (and then back), Options 2 and 3 can be used. For detailed information about these strategies, see [Understanding widget behavior].
## Option 1 (preferred): Execute your widget command in your entrypoint file
When you define your multipage app with `st.Page` and `st.navigation`, your entrypoint file becomes a frame of common elements around your pages. When you execute a widget command in your entrypoint file, Streamlit associates the widget to your entrypoint file instead of a particular page. Since your entrypoint file is executed in every app rerun, any widget in your entrypoint file will remain stateful as your users switch between pages.
This method does not work if you define your app with the `pages/` directory.
The following example includes a selectbox and slider in the sidebar that are rendered and stateful on all pages. The widgets each have an assigned key so you can access their values through Session State within a page.
**Directory structure:**
```
your-repository/
├── page_1.py
├── page_2.py
└── streamlit_app.py
```
**`streamlit_app.py`:**
```python
import streamlit as st
pg = st.navigation([st.Page("page_1.py"), st.Page("page_2.py")])
st.sidebar.selectbox("Group", ["A","B","C"], key="group")
st.sidebar.slider("Size", 1, 5, key="size")
pg.run()
```
## Option 2: Save your widget values into a dummy key in Session State
If you want to navigate away from a widget and return to it while keeping its value, or if you want to use the same widget on multiple pages, use a separate key in `st.session_state` to save the value independently from the widget. In this example, a temporary key is used with a widget. The temporary key uses an underscore prefix. Hence, `"_my_key"` is used as the widget key, but the data is copied to `"my_key"` to preserve it between pages.
```python
import streamlit as st
def store_value():
# Copy the value to the permanent key
st.session_state["my_key"] = st.session_state["_my_key"]
# Copy the saved value to the temporary key
st.session_state["_my_key"] = st.session_state["my_key"]
st.number_input("Number of filters", key="_my_key", on_change=store_value)
```
If this is functionalized to work with multiple widgets, it could look something like this:
```python
import streamlit as st
def store_value(key):
st.session_state[key] = st.session_state["_"+key]
def load_value(key):
st.session_state["_"+key] = st.session_state[key]
load_value("my_key")
st.number_input("Number of filters", key="_my_key", on_change=store_value, args=["my_key"])
```
## Option 3: Interrupt the widget clean-up process
When Streamlit gets to the end of an app run, it will delete the data for any widgets that were not rendered. This includes data for any widget not associated to the current page. However, if you re-save a key-value pair in an app run, Streamlit will not associate the key-value pair to any widget until you execute a widget command again with that key.
As a result, if you have the following code at the top of every page, any widget with the key `"my_key"` will retain its value wherever it's rendered (or not). Alternatively, if you are using `st.navigation` and `st.Page`, you can include this once in your entrypoint file before executing your page.
```python
if "my_key" in st.session_state:
st.session_state.my_key = st.session_state.my_key
```
