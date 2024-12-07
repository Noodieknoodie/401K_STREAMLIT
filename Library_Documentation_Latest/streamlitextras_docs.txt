# @ Streamlit-extras is a Python library that extends the traditional Streamlit module by adding enhanced features and custom components to create more sophisticated web applications. It provides over 20 functional and visual additions that make Streamlit apps more interactive and visually appealing

# To use any specific feature, you simply need to import it from the appropriate streamlit_extras module. The imports follow this pattern: from streamlit_extras.[component_name] import [function_name]


(1) ### https://arnaudmiribel.github.io/streamlit-extras/extras/add_vertical_space/ ###
Summary
Add n lines of vertical space to your Streamlit app in one command
Examples
example
defexample():add_n_lines=st.slider("Add n vertical lines below this",1,20,5)add_vertical_space(add_n_lines)st.write("Here is text after the nth line!")

(2) ### https://arnaudmiribel.github.io/streamlit-extras/extras/altex/ ###
Summary
A simple wrapper on top of Altair to make Streamlit charts in an express API. If you're lazy and/or familiar with Altair, this is  probably a good fit! Inspired by plost and plotly-express.
Examples
example_line
@cache_datadefexample_line():stocks=get_stocks_data()line_chart(data=stocks.query("symbol == 'GOOG'"),x="date",y="price",title="A beautiful simple line chart",)
example_multi_line
@cache_datadefexample_multi_line():stocks=get_stocks_data()line_chart(data=stocks,x="date",y="price",color="symbol",title="A beautiful multi line chart",)
example_bar
@cache_datadefexample_bar():stocks=get_stocks_data()bar_chart(data=stocks.query("symbol == 'GOOG'"),x="date",y="price",title="A beautiful bar chart",)
example_hist
@cache_datadefexample_hist():stocks=get_stocks_data()hist_chart(data=stocks.assign(price=stocks.price.round(0)),x="price",title="A beautiful histogram",)
example_scatter
@cache_datadefexample_scatter():weather=get_weather_data()scatter_chart(data=weather,x=alt.X("wind:Q",title="Custom X title"),y=alt.Y("temp_min:Q",title="Custom Y title"),title="A beautiful scatter chart",)
example_sparkline
@cache_datadefexample_sparkline():stocks=get_stocks_data()sparkline_chart(data=stocks.query("symbol == 'GOOG'"),x="date",y="price",title="A beautiful sparkline chart",rolling=7,height=150,)
example_minisparklines
@cache_datadefexample_minisparklines():stocks=get_stocks_data()left,middle,right=st.columns(3)withleft:data=stocks.query("symbol == 'GOOG'")st.metric("GOOG",int(data["price"].mean()))sparkline_chart(data=data,x="date",y="price:Q",height=80,autoscale_y=True,)withmiddle:data=stocks.query("symbol == 'MSFT'")st.metric("MSFT",int(data["price"].mean()))sparkline_chart(data=data,x="date",y="price:Q",height=80,autoscale_y=True,)withright:data=stocks.query("symbol == 'AAPL'")st.metric("AAPL",int(data["price"].mean()))sparkline_chart(data=data,x="date",y="price:Q",height=80,autoscale_y=True,)
example_sparkbar
@cache_datadefexample_sparkbar():stocks=get_stocks_data()sparkbar_chart(data=stocks.query("symbol == 'GOOG'"),x="date",y="price",title="A beautiful sparkbar chart",height=150,)
example_sparkarea
@cache_datadefexample_sparkarea():random_data=get_random_data()df=pd.melt(random_data,id_vars="index",value_vars=list("abcdefg"),)sparkarea_chart(data=df,x="index",y="value",color=alt.Color("variable",legend=None),title="A beautiful (also probably useless) sparkarea chart",opacity=alt.value(0.6),height=200,)
example_hist_time
@cache_datadefexample_hist_time():weather=get_weather_data()hist_chart(data=weather,x="week(date):T",y="day(date):T",color=alt.Color("median(temp_max):Q",legend=None,),title="A beautiful time hist chart",)
example_bar_sorted
@cache_datadefexample_bar_sorted():weather=get_weather_data()bar_chart(data=weather.sort_values(by="temp_max",ascending=False).head(25),x=alt.X("date",sort="-y"),y=alt.Y("temp_max:Q"),title="A beautiful sorted-by-value bar chart",)
example_bar_normalized
@cache_datadefexample_bar_normalized():barley=get_barley_data()bar_chart(data=barley,x=alt.X("variety:N",title="Variety"),y=alt.Y("sum(yield):Q",stack="normalize"),color="site:N",title="A beautiful normalized stacked bar chart",)
example_bar_grouped
@cache_datadefexample_bar_grouped():barley=get_barley_data()bar_chart(data=barley,x="year:O",y="sum(yield):Q",color="year:N",column="site:N",title="A beautiful grouped bar charts",width=90,use_container_width=False,)
example_bar_horizontal
@cache_datadefexample_bar_horizontal():weather=get_weather_data()bar_chart(data=weather.head(15),x="temp_max:Q",y=alt.Y("date:O",title="Temperature"),title="A beautiful horizontal bar chart",)
example_bar_log
@cache_datadefexample_bar_log():weather=get_weather_data()bar_chart(data=weather,x=alt.X("temp_max:Q",title="Temperature"),y=alt.Y("count()",title="Count of records",scale=alt.Scale(type="symlog"),),title="A beautiful histogram... with log scale",)
example_scatter_opacity
@cache_datadefexample_scatter_opacity():weather=get_weather_data()scatter_chart(data=weather,x=alt.X("wind:Q",title="Custom X title"),y=alt.Y("temp_min:Q",title="Custom Y title"),title="A beautiful scatter chart with custom opacity",opacity=0.2,)
example_bar_normalized_custom
@cache_datadefexample_bar_normalized_custom():barley=get_barley_data()bar_chart(data=barley,x=alt.X("variety",title="Variety"),y="sum(yield)",color=alt.Color("site",scale=alt.Scale(scheme="lighttealblue"),legend=None),title="A beautiful stacked bar chart (without legend, custom colors)",)

(3) ### https://arnaudmiribel.github.io/streamlit-extras/extras/app_logo/ ###
Summary
Add a logo on top of the navigation bar of a multipage app
Examples
example
defexample():ifst.checkbox("Use url",value=True):add_logo("http://placekitten.com/120/120")else:add_logo("gallery/kitty.jpeg",height=300)st.write("👈 Check out the cat in the nav-bar!")

(4) ### https://arnaudmiribel.github.io/streamlit-extras/extras/badges/ ###
Summary
Create custom badges (e.g. PyPI, Streamlit Cloud, GitHub, Twitter, Buy Me a Coffee)
Examples
example_pypi
defexample_pypi():badge(type="pypi",name="plost")badge(type="pypi",name="streamlit")
example_streamlit
defexample_streamlit():badge(type="streamlit",url="https://plost.streamlitapp.com")
example_github
defexample_github():badge(type="github",name="streamlit/streamlit")
example_twitter
defexample_twitter():badge(type="twitter",name="streamlit")
example_buymeacoffee
defexample_buymeacoffee():badge(type="buymeacoffee",name="andfanilo")

(5) ### https://arnaudmiribel.github.io/streamlit-extras/extras/bottom_container/ ###
Summary
A multi-element container that sticks to the bottom of the app.
Examples
example
defexample():st.write("This is the main container")withbottom():st.write("This is the bottom container")st.text_input("This is a text input in the bottom container")

(6) ### https://arnaudmiribel.github.io/streamlit-extras/extras/button_selector/ ###
Summary
A button selector that can be used to select an item from a list of options.
Examples
example
defexample():month_list=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec",]selected_index=button_selector(month_list,index=0,spec=4,key="button_selector_example_month_selector",label="Month Selector",)st.write(f"Selected month:{month_list[selected_index]}")

(7) ### https://arnaudmiribel.github.io/streamlit-extras/extras/buy_me_a_coffee/ ###
Summary
Adds a floating button which links to your Buy Me a Coffee page
Examples
example
defexample():button(username="fake-username",floating=False,width=221)

(8) ### https://arnaudmiribel.github.io/streamlit-extras/extras/camera_input_live/ ###
Summary
A camera input that updates a variable number of seconds
Docstring
Visit thePyPI pagefor more information.
Examples
example
defexample():st.write("# See a new image every second")controls=st.checkbox("Show controls")image=camera_input_live(show_controls=controls)ifimageisnotNone:st.image(image)

(9) ### https://arnaudmiribel.github.io/streamlit-extras/extras/capture/ ###
Summary
Capture utility extensions for the standard streamlit library
Examples
example_stdout
defexample_stdout():output=st.empty()withstdout(output.code,terminator=""):print("This is some captured stdout")print("How about that, Isn't it great?")ifst.button("Click to print more"):print("You added another line!")
example_stderr
defexample_stderr():output=st.empty()withstderr(output.code,terminator=""):print("This is some captured stderr",file=sys.stderr)print("For this example, though, there aren't any problems...yet",file=sys.stderr)ifst.button("Throw an error!"):print("ERROR: Task failed successfully",file=sys.stderr)print("Psst....stdout isn't captured here")
example_logcapture
defexample_logcapture():logger=logging.getLogger("examplelogger")logger.setLevel("DEBUG")withlogcapture(st.empty().code,from_logger=logger):logger.error("Roses are red")logger.info("Violets are blue")logger.warning("This warning is yellow")logger.debug("Your code is broke, too")

(10) ### https://arnaudmiribel.github.io/streamlit-extras/extras/card/ ###
Summary
Streamlit Component, for a UI card
Docstring
Visit thePyPI pagefor more information.
Examples
example
defexample():card(title="Hello World!",text="Some description",image="http://placekitten.com/300/250",url="https://www.google.com",)

(11) ### https://arnaudmiribel.github.io/streamlit-extras/extras/chart_annotations/ ###
Summary
Add annotations to specific timestamps in your time series in Altair!
Examples
example
defexample()->None:data:pd.DataFrame=get_data()chart:alt.TopLevelMixin=get_chart(data=data)chart+=get_annotations_chart(annotations=[("Mar 01, 2008","Pretty good day for GOOG"),("Dec 01, 2007","Something's going wrong for GOOG & AAPL"),("Nov 01, 2008","Market starts again thanks to..."),("Dec 01, 2009","Small crash for GOOG after..."),],)st.altair_chart(chart,use_container_width=True)# type: ignore

(12) ### https://arnaudmiribel.github.io/streamlit-extras/extras/chart_container/ ###
Summary
Embed your chart in a nice tabs container to let viewers explore and export its underlying data.
Examples
example_one
defexample_one():chart_data=_get_random_data()withchart_container(chart_data):st.write("Here's a cool chart")st.area_chart(chart_data)
example_two
defexample_two():chart_data=_get_random_data()withchart_container(chart_data):st.write("I can use a subset of the data for my chart... ""but still give all the necessary context in ""`chart_container`!")st.area_chart(chart_data[["a","b"]])

(13) ### https://arnaudmiribel.github.io/streamlit-extras/extras/colored_header/ ###
Summary
This function makes headers much prettier in Streamlit.Note that this now accessible in native Streamlit in st.header
           with parameterdivider!
Examples
example
defexample():colored_header(label="My New Pretty Colored Header",description="This is a description",color_name="violet-70",)

(14) ### https://arnaudmiribel.github.io/streamlit-extras/extras/concurrency_limiter/ ###
Summary
This decorator limit function execution concurrency with max_concurrency param.
Examples
example
defexample():@concurrency_limiter(max_concurrency=1)defheavy_computation():st.write("Heavy computation")progress_text="Operation in progress. Please wait."my_bar=st.progress(0,text=progress_text)forpercent_completeinrange(100):time.sleep(0.15)my_bar.progress(percent_complete+1,text=progress_text)st.write("END OF Heavy computation")return42my_button=st.button("Run heavy computation")ifmy_button:heavy_computation()

(15) ### https://arnaudmiribel.github.io/streamlit-extras/extras/customize_running/ ###
Summary
Customize the running widget
Examples
example
defexample():click=st.button("Observe where the 🏃‍♂️ running widget is now!")ifclick:center_running()time.sleep(2)

(16) ### https://arnaudmiribel.github.io/streamlit-extras/extras/dataframe_explorer/ ###
Summary
Let your viewers explore dataframes themselves! Learn more about it on thisblog post
Examples
example_one
defexample_one():dataframe=generate_fake_dataframe(size=500,cols="dfc",col_names=("date","income","person"),seed=1)filtered_df=dataframe_explorer(dataframe,case=False)st.dataframe(filtered_df,use_container_width=True)

(17) ### https://arnaudmiribel.github.io/streamlit-extras/extras/echo_expander/ ###
Summary
Execute code, and show the code that was executed, but in an expander.
Examples
example1
defexample1():withecho_expander():importstreamlitasstst.markdown("""This component is a combination of `st.echo` and `st.expander`.The code inside the `with echo_expander()` block will be executed,and the code can be shown/hidden behind an expander""")
example2
defexample2():withecho_expander(code_location="below",label="Simple Dataframe example"):importpandasaspdimportstreamlitasstdf=pd.DataFrame([[1,2,3,4,5],[11,12,13,14,15]],columns=("A","B","C","D","E"),)st.dataframe(df)

(18) ### https://arnaudmiribel.github.io/streamlit-extras/extras/embed_code/ ###
Summary
Embed code from various platforms (Gists, snippets...)
Docstring
Visit thePyPI pagefor more information.
Examples
example_github
defexample_github():github_gist("https://gist.github.com/randyzwitch/be8c5e9fb5b8e7b046afebcac12e5087/",width=700,height=400,)
example_gitlab
defexample_gitlab():gitlab_snippet("https://gitlab.com/snippets/1995463",width=700,height=200,)

(19) ### https://arnaudmiribel.github.io/streamlit-extras/extras/faker/ ###
Summary
Fake Streamlit commands at the speed of light! Great for prototyping apps.
Docstring
Visit thePyPI pagefor more information.
Examples
example
defexample():fake=get_streamlit_faker(seed=42)fake.markdown()fake.info(icon="💡",body="You can also pass explicit parameters!")fake.selectbox()fake.slider()fake.metric()fake.altair_chart()

(20) ### https://arnaudmiribel.github.io/streamlit-extras/extras/function_explorer/ ###
Summary
Give a UI to any Python function! Very alpha though
Examples
example
defexample():deffoo(age:int,name:str,image_url:str="http://placekitten.com/120/120"):st.write(f"Hey! My name is{name}and I'm{age}years old")st.write("Here's a picture")st.image(image_url)function_explorer(foo)

(21) ### https://arnaudmiribel.github.io/streamlit-extras/extras/grid/ ###
Summary
A multi-element container that places elements on a specified grid layout.
Examples
example
defexample():random_df=pd.DataFrame(np.random.randn(20,3),columns=["a","b","c"])my_grid=grid(2,[2,4,1],1,4,vertical_align="bottom")# Row 1:my_grid.dataframe(random_df,use_container_width=True)my_grid.line_chart(random_df,use_container_width=True)# Row 2:my_grid.selectbox("Select Country",["Germany","Italy","Japan","USA"])my_grid.text_input("Your name")my_grid.button("Send",use_container_width=True)# Row 3:my_grid.text_area("Your message",height=40)# Row 4:my_grid.button("Example 1",use_container_width=True)my_grid.button("Example 2",use_container_width=True)my_grid.button("Example 3",use_container_width=True)my_grid.button("Example 4",use_container_width=True)# Row 5 (uses the spec from row 1):withmy_grid.expander("Show Filters",expanded=True):st.slider("Filter by Age",0,100,50)st.slider("Filter by Height",0.0,2.0,1.0)st.slider("Filter by Weight",0.0,100.0,50.0)my_grid.dataframe(random_df,use_container_width=True)

(22) ### https://arnaudmiribel.github.io/streamlit-extras/extras/image_coordinates/ ###
Summary
Allows you to add an image to your app, and get the coordinates of where the user last
clicked on the image.
Docstring
Visit thePyPI pagefor more information.
Examples
example
defexample():"# Click on the image"last_coordinates=streamlit_image_coordinates("https://placekitten.com/200/300")st.write(last_coordinates)

(23) ### https://arnaudmiribel.github.io/streamlit-extras/extras/image_in_tables/ ###
Summary
Transform URLs into images in your dataframes
Examples
example
defexample(df:pd.DataFrame):st.caption("Input dataframe (notice 'Flag' column is full of URLs)")st.write(df)df_html=table_with_images(df=df,url_columns=("Flag",))st.caption("Ouput")st.markdown(df_html,unsafe_allow_html=True)

(24) ### https://arnaudmiribel.github.io/streamlit-extras/extras/image_selector/ ###
Summary
Allows users to select an area within an image, using a lasso or a bounding
box.
Examples
example
defexample():response=requests.get("https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500")image=Image.open(BytesIO(response.content))selection_type=st.radio("Selection type",["lasso","box"],index=0,horizontal=True)selection=image_selector(image=image,selection_type=selection_type)ifselection:st.json(selection,expanded=False)show_selection(image,selection)

(25) ### https://arnaudmiribel.github.io/streamlit-extras/extras/jupyterlite/ ###
Summary
Add a Jupyterlite sandbox to your Streamlit app in one command
Examples
example
defexample():jupyterlite(1500,1600)

(26) ### https://arnaudmiribel.github.io/streamlit-extras/extras/keyboard_text/ ###
Summary
Create a keyboard styled text
Examples
example_default
defexample_default():load_key_css()key("⌘+K")
example_inline
defexample_inline():load_key_css()st.write(f"Also works inline! Example:{key('⌘+K',write=False)}",unsafe_allow_html=True,)

(27) ### https://arnaudmiribel.github.io/streamlit-extras/extras/keyboard_url/ ###
Summary
Create bindings so that hitting a key on your keyboard opens an URL in a new tab!
Examples
example
defexample():# Main functionkeyboard_to_url(key="S",url="https://www.github.com/streamlit/streamlit")load_key_css()st.write(f"""Now hit{key("S",False)}on your keyboard...!""",unsafe_allow_html=True,)

(28) ### https://arnaudmiribel.github.io/streamlit-extras/extras/let_it_rain/ ###
Summary
Use this to create more animations like st.balloons() and st.snow()
Examples
example
defexample():rain(emoji="🎈",font_size=54,falling_speed=5,animation_length="infinite",)

(29) ### https://arnaudmiribel.github.io/streamlit-extras/extras/mandatory_date_range/ ###
Summary
Just like st.date_input, but enforces that it always and only returns a start and
end date, even if the user has only selected one of the dates. Until the user
selects both dates, the app will not run.
Examples
example
defexample():st.write("""This is an example of a date range picker that *always* returns a start andend date, even if the user has only selected one of the dates. Until theuser selects both dates, the app will not run.""")result=date_range_picker("Select a date range")st.write("Result:",result)

(30) ### https://arnaudmiribel.github.io/streamlit-extras/extras/markdownlit/ ###
Summary
markdownlit adds a set of lit Markdown commands for your Streamlit apps!Note you can now use colored text in markdown with native Streamlit, check
    outthe docs!
Docstring
Visit thePyPI pagefor more information.
Examples
example_link_and_colors
defexample_link_and_colors():mdlit("""Tired from [default links](https://extras.streamlit.app)?Me too! Discover Markdownlit's `@()` operator. Just insert a link and itwill figure a nice icon and label for you!Example: @(https://extras.streamlit.app)... better, right? You canalso @(🍐)(manually set the label if you want)(https://extras.streamlit.app)btw, and play with a [red]beautiful[/red] [blue]set[/blue] [orange]of[/orange][violet]colors[/violet]. Another perk is those beautiful arrows -> <-""")
example_collapsible_content
defexample_collapsible_content():mdlit(textwrap.dedent("""??? Bonus@(🎁)(A very insightful tutorial)(https://www.youtube.com/watch?v=dQw4w9WgXcQ)"""))

(31) ### https://arnaudmiribel.github.io/streamlit-extras/extras/mention/ ###
Summary
Create nice links with icons, like Notion mentions!
Examples
example_1
defexample_1():mention(label="An awesome Streamlit App",icon="streamlit",# Some icons are available... like Streamlit!url="https://extras.streamlitapp.com",)
example_2
defexample_2():mention(label="streamlit-extras",icon="🪢",# You can also just use an emojiurl="https://github.com/arnaudmiribel/streamlit-extras",)
example_3
defexample_3():mention(label="example-app-cv-model",icon="github",# GitHub is also featured!url="https://github.com/streamlit/example-app-cv-model",)
example_4
defexample_4():mention(label="That page somewhere in Notion",icon="notion",# Notion is also featured!url="https://notion.so",)
example_5
defexample_5():inline_mention=mention(label="streamlit",icon="twitter",# Twitter is also featured!url="https://www.twitter.com/streamlit",write=False,)st.write(f"Here's how to use the mention inline:{inline_mention}. Cool"" right?",unsafe_allow_html=True,)

(32) ### https://arnaudmiribel.github.io/streamlit-extras/extras/metric_cards/ ###
Summary
Restyle metrics as cards
Examples
example
defexample():col1,col2,col3=st.columns(3)col1.metric(label="Gain",value=5000,delta=1000)col2.metric(label="Loss",value=5000,delta=-1000)col3.metric(label="No Change",value=5000,delta=0)style_metric_cards()

(33) ### https://arnaudmiribel.github.io/streamlit-extras/extras/no_default_selectbox/ ###
Summary
Just like st.selectbox, but with no default value -- returns None if nothing is selected.
Examples
example
defexample():st.write("""This is an example of a selectbox that returns None unless the user hasexplicitly selected one of the options.The selectbox below has no default value, so it will return None until theuser selects an option.""")result=selectbox("Select an option",["A","B","C"])st.write("Result:",result)result=selectbox("Select an option with different label",["A","B","C"],no_selection_label="<None>",)st.write("Result:",result)

(34) ### https://arnaudmiribel.github.io/streamlit-extras/extras/prometheus/ ###
Summary
Expose Prometheus metrics (https://prometheus.io) from your Streamlit app.
Examples
example
defexample():importstreamlitasstfromprometheus_clientimportCounter@st.cache_resourcedefget_metric():registry=streamlit_registry()returnCounter(name="my_counter",documentation="A cool counter",labelnames=("app_name",),registry=registry,# important!!)SLIDER_COUNT=get_metric()app_name=st.text_input("App name","prometheus_app")latest=st.slider("Latest value",0,20,3)ifst.button("Submit"):SLIDER_COUNT.labels(app_name).inc(latest)st.write("""View a fuller example that uses the (safer) import metrics method at:https://github.com/arnaudmiribel/streamlit-extras/tree/main/src/streamlit_extras/prometheus/example""")st.write("""### Example output at `{host:port}/_stcore/metrics````# TYPE my_counter counter# HELP my_counter A cool countermy_counter_total{app_name="prometheus_app"} 14.0my_counter_created{app_name="prometheus_app"} 1.7042185907557938e+09```""")

(35) ### https://arnaudmiribel.github.io/streamlit-extras/extras/row/ ###
Summary
A multi-element horizontal container that places elements in a row.
Examples
example
defexample():random_df=pd.DataFrame(np.random.randn(20,3),columns=["a","b","c"])row1=row(2,vertical_align="center")row1.dataframe(random_df,use_container_width=True)row1.line_chart(random_df,use_container_width=True)row2=row([2,4,1],vertical_align="bottom")row2.selectbox("Select Country",["Germany","Italy","Japan","USA"])row2.text_input("Your name")row2.button("Send",use_container_width=True)

(36) ### https://arnaudmiribel.github.io/streamlit-extras/extras/sandbox/ ###
Summary
Execute untrusted Streamlit code in a sandboxed environment.
Examples
example
defexample():defembedded_app():importnumpyasnpimportpandasaspdimportplotly.expressaspximportstreamlitasst@st.cache_datadefget_data():dates=pd.date_range(start="01-01-2020",end="01-01-2023")data=np.random.randn(len(dates),1).cumsum(axis=0)returnpd.DataFrame(data,index=dates,columns=["Value"])data=get_data()value=st.slider("Select a range of values",int(data.min()),int(data.max()),(int(data.min()),int(data.max())),)filtered_data=data[(data["Value"]>=value[0])&(data["Value"]<=value[1])]st.plotly_chart(px.line(filtered_data,y="Value"))sandbox(embedded_app)

(37) ### https://arnaudmiribel.github.io/streamlit-extras/extras/st_keyup/ ###
Summary
A text input that updates with every key press
Docstring
Visit thePyPI pagefor more information.
Examples
example
defexample():st.write("## Notice how the output doesn't update until you hit enter")out=st.text_input("Normal text input")st.write(out)st.write("## Notice how the output updates with every key you press")out2=st_keyup("Keyup input")st.write(out2)
example_with_debounce
defexample_with_debounce():st.write("## Notice how the output doesn't update until 500ms has passed")out=st_keyup("Keyup with debounce",debounce=500)st.write(out)

(38) ### https://arnaudmiribel.github.io/streamlit-extras/extras/stateful_button/ ###
Summary
Button that keeps track of its state, so that it works as a toggle button
Examples
example
defexample():ifbutton("Button 1",key="button1"):ifbutton("Button 2",key="button2"):ifbutton("Button 3",key="button3"):st.write("All 3 buttons are pressed")

(39) ### https://arnaudmiribel.github.io/streamlit-extras/extras/stateful_chat/ ###
Summary
A chat container that automatically keeps track of the chat history.
Examples
example
defexample():withchat(key="my_chat"):ifprompt:=st.chat_input():add_message("user",prompt,avatar="🧑‍💻")defstream_echo():forwordinprompt.split():yieldword+" "time.sleep(0.15)add_message("assistant","Echo: ",stream_echo,avatar="🦜")

(40) ### https://arnaudmiribel.github.io/streamlit-extras/extras/stodo/ ###
Summary
Simple Python function to create to-do items in Streamlit!
Examples
example
defexample():to_do([(st.write,"☕ Take my coffee")],"coffee",)to_do([(st.write,"🥞 Have a nice breakfast")],"pancakes",)to_do([(st.write,":train: Go to work!")],"work",)

(41) ### https://arnaudmiribel.github.io/streamlit-extras/extras/stoggle/ ###
Summary
Toggle button just like in Notion!
Examples
example
defexample():stoggle("Click me!","""🥷 Surprise! Here's some additional content""",)

(42) ### https://arnaudmiribel.github.io/streamlit-extras/extras/streaming_write/ ###
Summary
Drop-in replacement forst.writewith streaming support.
Examples
example
defexample():defstream_example():forwordin_LOREM_IPSUM.split():yieldword+" "time.sleep(0.1)# Also supports any other object supported by `st.write`yieldpd.DataFrame(np.random.randn(5,10),columns=["a","b","c","d","e","f","g","h","i","j"],)forwordin_LOREM_IPSUM.split():yieldword+" "time.sleep(0.05)ifst.button("Stream data"):write(stream_example)

(43) ### https://arnaudmiribel.github.io/streamlit-extras/extras/stylable_container/ ###
Summary
A container that allows to style its child elements using CSS.
Examples
example
defexample():withstylable_container(key="green_button",css_styles="""button {background-color: green;color: white;border-radius: 20px;}""",):st.button("Green button")st.button("Normal button")withstylable_container(key="container_with_border",css_styles="""{border: 1px solid rgba(49, 51, 63, 0.2);border-radius: 0.5rem;padding: calc(1em - 1px)}""",):st.markdown("This is a container with a border.")

(44) ### https://arnaudmiribel.github.io/streamlit-extras/extras/switch_page_button/ ###
Summary
Function to switch page programmatically in a MPA
Examples
example
defexample():want_to_contribute=st.button("I want to contribute!")ifwant_to_contribute:switch_page("Contribute")

(45) ### https://arnaudmiribel.github.io/streamlit-extras/extras/tags/ ###
Summary
Display tags like github issues!
Examples
example
defexample():tagger_component("Here is a feature request",["p2","🚩triaged","backlog"])tagger_component("Here are colored tags",["turtle","rabbit","lion"],color_name=["blue","orange","lightblue"],)tagger_component("Annotate the feature",["hallucination"],color_name=["blue"],)

(46) ### https://arnaudmiribel.github.io/streamlit-extras/extras/theme/ ###
Summary
A component that returns the active theme of the Streamlit app.
Docstring
Visit thePyPI pagefor more information.
Examples
example_1
defexample_1():importstreamlitasstfromstreamlit_themeimportst_themetheme=st_theme()st.write(theme)
example_2
defexample_2():importstreamlitasstfromstreamlit_themeimportst_themeadjust=st.toggle("Make the CSS adjustment")st.write("Input:")st.code(f"""st.write("Lorem ipsum")st_theme(adjust={adjust})st.write("Lorem ipsum")""")st.write("Output:")st.write("Lorem ipsum")st_theme(adjust=adjust)st.write("Lorem ipsum")

(47) ### https://arnaudmiribel.github.io/streamlit-extras/extras/toggle_switch/ ###
Summary
On/Off Toggle Switch with color customizations.Note
    that this is now available as a native Streamlit command st.toggle.
    Check out thedocs!
Docstring
Visit thePyPI pagefor more information.
Examples
example
defexample():st.write("## Toggle Switch")st_toggle_switch(label="Enable Setting?",key="switch_1",default_value=False,label_after=False,inactive_color="#D3D3D3",# optionalactive_color="#11567f",# optionaltrack_color="#29B5E8",# optional)

(48) ### https://arnaudmiribel.github.io/streamlit-extras/extras/vertical_slider/ ###
Summary
Continuous Vertical Slider with color customizations
Docstring
Visit thePyPI pagefor more information.
Examples
example
defexample():st.write("## Vertical Slider")vertical_slider(key="slider",default_value=25,step=1,min_value=0,max_value=100,track_color="gray",# optionalthumb_color="blue",# optionalslider_color="red",# optional)

(49) ### https://arnaudmiribel.github.io/streamlit-extras/extras/word_importances/ ###
Summary
Highlight words based on their importances. Inspired from captum library.
Examples
example
defexample():text=("Streamlit Extras is a library to help you discover, learn, share and"" use Streamlit bits of code!")html=format_word_importances(words=text.split(),importances=(0.1,0.2,0,-1,0.1,0,0,0.2,0.3,0.8,0.9,0.6,0.3,0.1,0,0,0),# fmt: skip)st.write(html,unsafe_allow_html=True)
