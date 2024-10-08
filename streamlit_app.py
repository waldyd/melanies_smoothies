# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

def clear_session():
    st.session_state["text"] = ""
    #st.session_state["multiselect"] = ""


# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your Smoothie!
    """
)

#user_input = st.text_area("Name on Smoothie: ")   #, "")
name_on_order = st.text_input("Name on Smoothie: ", "", key="text")
st.write("The name on your smoothie will be: ", name_on_order)


#option = st.selectbox(
#    "What is your favorite fruit?",
#    ("Banana", "Strawberries", "Peaches"),
#)

#st.write("Your favorite fruit is:", option)

# session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))#.collect()
#st.dataframe(data=my_dataframe, use_container_width=True)

#options = my_dataframe['FRUIT_NAME'].tolist()
#options = [row['FRUIT_NAME'] for row in my_dataframe]
#st.write(options[0])
#default = [options[0]] if options else None
#st.write(default)

pd_df = my_dataframe.to_pandas()
#st.dataframe(data=pd_df, use_container_width=True)
#st.stop()

# Create a multiselect widget
ingredients_list = st.multiselect('Choose up to 5 ingredients:'
                                  , my_dataframe
                                  , max_selections=5
                                  , key="multiselect")
#ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe, key="multiselect", default=[my_dataframe.first()]) # ['FRUIT_NAME'].unique())
#ingredients_list = st.multiselect('Choose up to 5 ingredients:', options, key="multiselect", default=default) # ['FRUIT_NAME'].unique())

# Display the selected values
if ingredients_list:
    #st.write('You selected:', ingredients_list)
    #st.text(ingredients_list)

    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader('{} Nutririon Information'.format(fruit_chosen))

        #st.write("https://fruityvice.com/api/fruit/{}".format(fruit_chosen))
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/{}".format(search_on), verify=False)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    #st.write(my_insert_stmt)
    #st.stop()
    
    time_to_insert = st.button('Submit Order')
    #time_to_insert = st.button('Submit Order', on_click=clear_session)
    #if ingredients_string:
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        
        st.success('Your Smoothie is ordered, {}!'.format(name_on_order), icon="✅")