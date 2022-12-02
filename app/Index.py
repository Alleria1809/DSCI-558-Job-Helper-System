import streamlit as st
import pandas as pd
import PyPDF2
import os
from PIL import Image
import spacy
import re
import string
from nltk.corpus import stopwords
from wordcloud import WordCloud
from wordcloud import WordCloud, STOPWORDS
from neo4j import GraphDatabase

# import KG

st.set_page_config(
    page_title="Job Index",
    page_icon="👋",
    layout="wide"
)

st.write("# 👨‍💼 👩‍💼Welcome to KG Job Helper System!")

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

@st.cache
def data_loader(dataset):
    # '''Returns the whole csv file with all the attributes'''
    data_df = pd.read_csv(dataset)
    return data_df


def write_result(record):
    # '''write each search result with a structure'''
    detail_col1, detail_col2 = st.columns([4, 2])
    with detail_col1:  # write the details for the job
        st.write('###### Job Title')
        st.markdown("""[{}]({})""".format(record['job_title'], record['url']))
        st.markdown("""###### Company:  [{}]({})""".format(record['company_name'], record['website']))
        if record['salary']:
            st.write("salary: {}".format(record['salary'].strip('$')))
        if record['work_type']:
            st.write("work type: {}".format(record['work_type']))
    with detail_col2:  # set the logo for the company
        company_logo = record['logo_url']  # will need to be changed into company_logo_urls
        if company_logo != "Unknown":
            st.image(company_logo, caption=record['company_name'], use_column_width='auto')

    # use tabs to show the detailed results, allow the user to chose and see
    tab1, tab2 = st.tabs(["Job details", "Company details"])
    with tab1:
        # with st.expander('Click to see job description details'):
        # st.write(record['job_details'])
        st.markdown('**State/Area**: \t \t {}'.format(record['state']))
        st.markdown('**City**: \t \t {}'.format(record['city']))
        st.write("**Salary**: {}".format(record['salary'].strip('$')))
        st.write("**Work Type**: {}".format(record['work_type']))
        st.write("**Source**: {}".format(record['source']))

    with tab2:
        st.markdown('**Company name**: \t \t {}'.format(record['company_name']))
        st.markdown('**State/Area**: \t \t {} '.format(record['company_state']))
        st.markdown('**City**: \t \t {}'.format(record['company_city']))
        st.markdown('**Size**: \t \t {}'.format(record['size']))
        st.markdown('**Industry**: \t \t {}'.format(record['industry']))
        st.markdown('**Founded Year**: \t \t {}'.format(record['founded']))
        st.markdown('**Revenue**: \t \t {}'.format(record['revenue']))
        st.markdown('**Company Type**: \t \t {}'.format(record['type']))


# add elements in the side bar
# Using "with" notation
# put the image and multi-page selection here
with st.sidebar:
    col1, col2, col3 = st.columns([1, 6, 1])

    with col1:
        st.write("")

    with col2:
        image = Image.open(r'./static/jobs.jpg')
        st.image(image, caption='Job Helper System', use_column_width='auto')

    with col3:
        st.write("")

st.subheader("Search Your Ideal Job!")

# this is for the database
dataset = './job_positions_full2.csv'
data_df = data_loader(dataset)
data_df = data_df.fillna('')

company_data = './company_full2.csv'
company_df = data_loader(company_data)
company_df = company_df.fillna('')

# this is for the select box of the job_category and set the default first job catgory as Data Scientist
# """You need to query all the job category and put them into the job_set, and put Data Scientist at the begining of the set"""
first_job = ['Data Scientist']
job_set_default = ['All']
# kg query
conn = Neo4jConnection(uri="bolt://localhost:7687", user="558proj", pwd="558proj")
query_string = '''
MATCH (job:job_node)-[:belong_to]->(job_category:category_node)
RETURN job_category.name
'''
job_set = []
lst = conn.query(query_string, db='neo4j')
for job in lst:
   job_set.append(job[0])

#job_set = set(data_df['category'].tolist())
job_set = set(job_set)
job_set.remove('Data Scientist')
if '' in job_set:
    job_set.remove('')
# job_set_list returns a full **list** of job categories(including 'All') and Data Scientist is the first shown job category
job_set_list = first_job + list(job_set) + job_set_default

# """ ideal_job_option is the selected job category"""
ideal_job_option = st.selectbox(
    'Please select your ideal job:',
    job_set_list)
st.write('You selected:', ideal_job_option)
#if ideal_job_option == 'All':
#    ideal_job_df = data_df
#else:
#    ideal_job_df = data_df[data_df['category'] == ideal_job_option]


# this part is for selecting state, city and work type
# query results should include:
# job_category, state, city, work_type, job_title, job_url,
# company_name, company_url, company_logo, salary, job_details
# company attributes such as industry, founded year, ...
filter_col1, filter_col2, filter_col3 = st.columns([3, 3, 3])

with filter_col1:
    # this defines a list of states with CA as the first default state and including 'All'
    # """ query: select all the states based on the selected job category: ideal_job_option"""
    # """ get a list of states"""
    first_state = ['CA']
    state_set_default = ['All']

    #kg query
    if ideal_job_option == "All":
        query_string = '''
            MATCH (job:job_node)-[:belong_to]->(job_category:category_node)
            with collect(job) as jobs
            MATCH (job:job_node)-[:located_in]->(job_location:location_node) <-[:subClassOf]-(job_state:state_node)
            where job in jobs
            RETURN job.title, job_state.name'''
    else:
        query_string = '''
            MATCH (job:job_node)-[:belong_to]->(job_category:category_node{name:'%s'})
            with collect(job) as jobs
            MATCH (job:job_node)-[:located_in]->(job_location:location_node) <-[:subClassOf]-(job_state:state_node)
            where job in jobs
            RETURN job.title, job_state.name'''%(ideal_job_option)
    state_set = []
    lst = conn.query(query_string, db='neo4j')
    for job in lst:
        state_set.append(job[1])


    #state_set = set(ideal_job_df['state'].tolist())
    state_set = set(state_set)
    state_set.remove('CA')

    state_set_list = first_state + list(state_set) + state_set_default
    state_option = st.selectbox(
        'Please select your ideal state/area:',
        state_set_list)
#if state_option == 'All':
#    selected_df = ideal_job_df
#else:
#    selected_df = ideal_job_df[ideal_job_df['state'] == state_option]

with filter_col2:
    first_city = ['All']
    #city_set_default = ['All']

    # kg query
    if ideal_job_option == "All":
        i = ""
    else:
        i = "{name:'%s'}" % ideal_job_option
    if state_option == "All":
        j = ""
    else:
        j = "{name:'%s'}" % state_option
    query_string = '''
        MATCH (job:job_node)-[:belong_to]->(job_category:category_node%s)
        with collect(job) as jobs

        MATCH (job:job_node)-[:located_in]->(job_location:location_node) <- [:subClassOf]-(job_state:state_node%s)
        where job in jobs
        with collect(job) as jobs

        MATCH (job:job_node)-[:located_in]->(job_location:location_node) <-[:subClassOf]-(job_city:city_node)
        where job in jobs
        RETURN job.title, job_city.name''' % (i, j)

    city_set = []
    lst = conn.query(query_string, db='neo4j')
    for job in lst:
        city_set.append(job[1])

    #city_set = set(selected_df['city'].tolist())
    city_set = set(city_set)
    #city_set.remove('Los Angeles')

    city_set_list = first_city + list(city_set)
    city_option = st.selectbox(
        'Please select your ideal city:',
        city_set_list)

#if city_option == 'All':
#    selected_df = selected_df
#else:
#    selected_df = selected_df[selected_df['city'] == city_option]
with filter_col3:
    type_set_default = ['All']

    # kg query
    if ideal_job_option == "All":
        i = ""
    else:
        i = "{name:'%s'}" % ideal_job_option
    if state_option == "All":
        j = ""
    else:
        j = "{name:'%s'}" % state_option
    if city_option == "All":
        k = ""
    else:
        k = "{name:'%s'}" % city_option
    query_string = '''
        MATCH (job:job_node)-[:belong_to]->(job_category:category_node%s)
        with collect(job) as jobs

        MATCH (job:job_node)-[:located_in]->(job_location:location_node) <- [:subClassOf]-(job_state:state_node%s)
        where job in jobs
        with collect(job) as jobs

        MATCH (job:job_node)-[:located_in]->(job_location:location_node) <- [:subClassOf]-(job_city:city_node%s)
        where job in jobs
        RETURN job.work_type''' % (i, j, k)

    type_set = []
    lst = conn.query(query_string, db='neo4j')
    for job in lst:
        type_set.append(job[0])

    #type_set = set(selected_df['work_type'].tolist())
    type_set = set(type_set)

    type_set_list = type_set_default + list(type_set)
    type_option = st.selectbox(
        'Please select your ideal work type:',
        type_set_list)

st.write('You selected: state: {}, city: {}, work type: {}'.format(state_option, city_option, type_option))

# if type_option == 'All':
#     selected_df = selected_df
# else:
#     selected_df = selected_df[selected_df['work_type'] == type_option]
# st.dataframe(selected_df)

# kg query
if ideal_job_option == "All":
    i = ""
else:
    i = "{name:'%s'}" % ideal_job_option
if state_option == "All":
    j = ""
else:
    j = "{name:'%s'}" % state_option
if city_option == "All":
    k = ""
else:
    k = "{name:'%s'}" % city_option
if type_option == "All":
    l = ""
else:
    l = "{work_type:'%s'}" % type_option
query_string = '''
MATCH (job:job_node)-[:belong_to]->(job_category:category_node%s)
with collect(job) as jobs

MATCH (job:job_node)-[:located_in]->(job_location:location_node) <- [:subClassOf]-(job_state:state_node%s)
where job in jobs
with collect(job) as jobs

MATCH (job:job_node)-[:located_in]->(job_location:location_node) <- [:subClassOf]-(job_city:city_node%s)
where job in jobs
with collect(job) as jobs

MATCH (job:job_node%s)<-[:company_of]-(company:company_node)-[:founded_year]->(founded:year_node)
where job in jobs
RETURN job.name, job.title, job.url, job.salary, job.work_type, job.source, company.name, company.website, company.size, company.industry, company.revenue, company.type, company.logo, founded.name
'''%(i, j, k, l)

header = ['id', 'job_title','url','salary','work_type','source','company_name','website','size','industry','revenue','type','logo_url','founded']
info_set = []
lst = conn.query(query_string, db='neo4j')
for job in lst:
    lst1 = []
    for i in job:
        lst1.append(i)
    info_set.append(lst1)
selected_df = pd.DataFrame(lst, columns=header)
job_state = []
job_city = []
company_state = []
company_city = []
for i in range(len(selected_df)):
    record = selected_df.iloc[i,:]
    job_id = record['id']
    query_string = '''
    MATCH (job:job_node{name:'%s'})-[:located_in]->(location:location_node)<-[:subClassOf]-(state:state_node)
    MATCH (job:job_node{name:'%s'})-[:located_in]->(location:location_node)<-[:subClassOf]-(city:city_node)
    MATCH (job:job_node{name:'%s'})<-[:company_of]-(company:company_node)-[:located_in]->(company_location:location_node)<-[:subClassOf]-(company_city:city_node)
    MATCH (job:job_node{name:'%s'})<-[:company_of]-(company:company_node)-[:located_in]->(company_location:location_node)<-[:subClassOf]-(company_state:state_node)
    RETURN state.name, city.name, company_state.name, company_city.name''' % (job_id, job_id, job_id, job_id)
    lst = conn.query(query_string, db='neo4j')
    job_state.append(lst[0][0])
    job_city.append(lst[0][1])
    company_state.append(lst[0][2])
    company_city.append(lst[0][3])

selected_df['state'] = job_state
selected_df['city'] = job_city
selected_df['company_state'] = company_state
selected_df['company_city'] = company_city

st.subheader('Your Job Search Result: ')
total_records = len(selected_df)
st.write('#### {} jobs found!'.format(total_records))

number_sub_cols = len(selected_df) // 2
res_col1, res_space1, res_col2 = st.columns([3, 1, 3])

count = 1
for i in range(len(selected_df)):
    record = selected_df.iloc[i, :]
    #company_record = company_df[company_df['company_name'] == record['company']]
    write_result(record)
    st.markdown("***")
    count += 1







