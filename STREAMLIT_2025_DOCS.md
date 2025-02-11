# Streamlit Documentation (Tailored for Data-Driven Applications)

This document provides a focused guide to Streamlit features relevant for building data-driven, interactive applications. It emphasizes best practices, efficient data handling, and user interface design.

## I. Core Concepts

### 1. Caching

Efficiently manage data loading and computations to prevent redundant operations.

*   **`st.cache_data` (For Data)**

    *   **Purpose:** Cache functions that return data (DataFrames, NumPy arrays, API responses, database query results, etc.).
    *   **Behavior:**
        *   Stores serialized (pickled) copies of return values. Prevents unintended mutations.
        *   Returns a *copy* of the cached object, ensuring data integrity across sessions and reruns.
        *   Hashes input parameters and function code to detect changes.
        *   Use `st.cache_data.clear()` to clear the cache.
        * Has static element replay.
    *   **Best Practices:**
        *   Use for *all* data loading and transformation functions.
        *   Set `ttl` (time-to-live) for data that may become stale (e.g., API data, database queries).
        *   Set `max_entries` to limit cache size and prevent memory issues.
        *   Use `experimental_allow_widgets=True` *only* when a widget's value *directly* affects the cached data. Be extremely mindful of potential memory issues.
        *   Use `hash_funcs` for custom hashing of unhashable input parameters:
            ```python
            @st.cache_data(hash_funcs={MyClass: lambda obj: hash(obj.some_attribute)})
            def my_func(obj: MyClass): ...
            ```
        *   Use `show_spinner` to disable or customize the loading spinner.
    * **Example:**
    ```python
        @st.cache_data(ttl=3600, max_entries=100)  # Cache for 1 hour, max 100 entries
        def load_data(url):
            return pd.read_csv(url)
    ```

*   **`st.cache_resource` (For Global Resources)**

    *   **Purpose:** Cache global resources like database connections, ML models, or other expensive-to-create objects.
    *   **Behavior:**
        *   Stores the *actual* object instance (singleton).  Returns the *same* object to all users and sessions.
        *   Does *not* create copies.  Mutations affect the cached object directly.
        *   Hashes input parameters and function code.
    *   **Best Practices:**
        *   Use for resources that should be shared globally and are expensive to create.
        *   Ensure the cached object is thread-safe if concurrent access is possible.
        *   Use `ttl` to periodically refresh the resource (e.g., reconnect to a database).
        * Use `show_spinner` to disable or customize the loading spinner.
        * Has static element replay.
        *   Use `hash_funcs` as needed, similar to `st.cache_data`.

    * **Example:**

    ```python
    @st.cache_resource(ttl=86400)  # Reconnect every 24 hours
    def get_db_connection():
        return connect_to_database(...)
    ```

### 2. Session State (`st.session_state`)

Manage user-specific data and interactions across reruns.

*   **Purpose:** Store variables that need to persist between reruns within a single user session (e.g., filter selections, form input, page navigation state).
*   **API:** Dictionary-like access (`st.session_state['key']`) and attribute access (`st.session_state.key`).
*   **Best Practices:**
    *   **Initialization:**  Always initialize variables:
        ```python
        if 'my_variable' not in st.session_state:
            st.session_state.my_variable = initial_value
        ```
    *   **Callbacks:** Use `on_change` (most widgets) or `on_click` (buttons) to update session state when widgets change.  Define the callback function *before* the widget:
        ```python
        def my_callback():
            st.session_state.my_variable = st.session_state.my_widget_key

        st.selectbox("Select an option", options, key="my_widget_key", on_change=my_callback)
        ```
    *   **Forms:** Widgets inside `st.form` *do not* trigger immediate updates.  Use `st.form_submit_button` with an `on_click` callback to process form data. Access form inputs via `st.session_state`.
    *   **Order of Execution:** Callbacks execute *before* the main script reruns.
*   **Limitations:**
    *   Do *not* modify a widget's value in session state *after* the widget has been created.
    *   Do *not* directly set the state of button-like widgets (`st.button`, `st.download_button`). Use callbacks.
    *  use `st.session_state.clear()` to clear the state.
### 3. Forms (`st.form`)

Batch user input to prevent reruns on every individual widget change within the form.

*   **Purpose:**  Group related input widgets.  Only submit data when a `st.form_submit_button` is clicked.
*   **Usage:**
    ```python
    with st.form(key='my_form'):
        # ... input widgets ...
        submit_button = st.form_submit_button("Submit", on_click=my_submit_callback)
    ```
* form inputs values are accessed through st.session_state.
*   **Best Practices:**
    *   Always use a `key`.
    *   Place all related input widgets *inside* the `with st.form():` block.
    *   Use `st.form_submit_button` with an `on_click` callback to handle form submission.
*   **Limitations:**
    *   Only `st.form_submit_button` can have a callback *within* a form.
    *   Cannot nest forms.

## II. Layout and Containers

Organize and structure your app's UI.

*   **`st.container()`:**
    *   **Purpose:** Group related UI elements logically.  Improves visual organization and enables targeted updates.
    *   **Best Practice:** Use extensively for a clean, structured layout.
*   **`st.columns()`:**
    *   **Purpose:** Create horizontal layouts.
    *   **Best Practice:** *Always* use inside containers (`st.container`, `st.sidebar`, etc.).  Favor symmetrical column splits (e.g., `[2, 2, 2]`, `[3, 3]`).
*   **`st.expander()`:**
    *   **Purpose:** Hide/show content.  Useful for less frequently accessed information or details.
*   **`st.tabs()`:**
    *   **Purpose:** Organize content into separate tabbed views.
*   **`st.sidebar`:**
    *   **Purpose:**  Create a sidebar for navigation, filters, settings, or less prominent content.
    *   **Usage:** `st.sidebar.widget()` or `with st.sidebar:`
* **Context Managers:**
    * Use `with` to increase readability.

## III. Displaying Data

Show data in various formats, with interactivity.

*   **`st.dataframe()`:**
    *   **Purpose:** Display interactive tables (sorting, filtering).
    *   **Best Practice:** Use for tabular data where user interaction (sorting, filtering) is desired.
    *   **Column Configuration API:**  Customize column display and behavior (data types, formatting, editing).
*   **`st.data_editor()`:**
    *  Edit tables.
*   **`st.table()`:**
    *   **Purpose:** Display static tables (non-editable).
*   **`st.metric()`:**
    *   **Purpose:** Display key metrics prominently.
    *   **Best Practice:** Use for highlighting important values.
*  **`st.code`**:
    * Display code.
* **`st.divider`**:
    * Insert a divider.

## IV. User Input Widgets

Collect input from users through various interactive elements.

*   **Common Widgets:**
    *   `st.selectbox`: Dropdown selection.
    *   `st.date_input`: Date selection.
    *   `st.number_input`: Numeric input.
    *   `st.text_input`: Single-line text input.
    *  `st.toggle`: Toggle input.
    *   `st.checkbox`: Boolean input.
    *   `st.radio`: Radio button selection.
    *   `label_visibility`: Control label visibility.
*   **Best Practices:**
    *   Use `key` parameter to uniquely identify widgets, especially when using them dynamically.
    *   Use `on_change` (or `on_click` for buttons) callbacks to respond to user interaction.
    *   Within forms, use `st.form_submit_button` and access values through `st.session_state`.

## V. Status & Feedback

Provide feedback to users about the app's state and actions.

*   **`st.error()`:** Display error messages.
*   **`st.warning()`:** Display warning messages.
*   **`st.success()`:** Display success messages.
*   **`st.info()`:** Display informational messages.
*   **`st.toast()`:** Display brief, non-intrusive notifications.
*   **`st.spinner()`:**  Show a loading spinner while a block of code is executing:
    ```python
    with st.spinner("Loading data..."):
        data = load_data()
    ```
* **`st.status`**: Show status.
*  **`st.help`**: shows docstrings

## VI. Multipage Apps
* Use `st.Page` and `st.navigation` for flexibility.
    ```python
    import streamlit as st
    pg = st.navigation([st.Page("page_1.py"), st.Page("page_2.py")])
    pg.run()
    ```
* Use `pages/` directory for a quick solution.
* Use `st.switch_page` to change pages.

## VII. Advanced Concepts

* **`st.fragment`:**
  * Run sections independently.
  * Use `run_every` to automatically rerun.
  * Can draw to main body.
  * Cannot render widgets outside of main body.

*   **Custom Components:**  Extend Streamlit's functionality with custom HTML, CSS, and JavaScript.

*   **Error Handling:** Use `try...except` blocks to gracefully handle potential errors (e.g., database connection issues).

*   **Data Validation:** Perform client-side validation within forms to provide immediate feedback to users and prevent unnecessary processing.

* **Timezone Handling**
  * Streamlit shows datetime objects exactly as they are, be sure to consider that.
  * Convert to a specific timezone before displaying, if necessary.

## VIII. Deprecated Features (Avoid)

*   `st.experimental_memo` (use `st.cache_data`)
*   `st.experimental_singleton` (use `st.cache_resource`)
*   `st.experimental_rerun` (use `st.rerun`)
* `st.experimental_data_editor` (use `st.data_editor`)
*   `st.experimental_get_query_params` and `st.experimental_set_query_params` (use `st.query_params`)
*   `st.cache` (use `st.cache_data` or `st.cache_resource`)

This document provides a comprehensive yet concise guide to building effective Streamlit applications, tailored for data-centric use cases. It emphasizes best practices and efficient techniques, serving as a reliable foundation for your Streamlit projects.