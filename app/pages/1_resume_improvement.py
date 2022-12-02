import streamlit as st
import pandas as pd
import PyPDF2
import os
from PIL import Image
import spacy
import re
import string
from nltk.corpus import stopwords
# from wordcloud import WordCloud
from wordcloud import WordCloud, STOPWORDS
from nltk.tokenize import word_tokenize
import random
from annotated_text import annotated_text, annotation
import plotly.graph_objects as go
import functools
import rltk
import copy
# import KG

st.set_page_config(
    page_title="Improve Your Resume",
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
def resume_text_extraction(file):
    "Extract the pdf data from the file"
    file_o = open(file,'rb') # open the file
    file_reader = PyPDF2.PdfFileReader(file_o) # read the file
    count_page = file_reader.getNumPages() # get the number of pages in the file
    count = 0
    text = []
    while count<count_page:
        page_obj = file_reader.getPage(count)
        count += 1
        content = page_obj.extractText()
        text.append(content)
    file_o.close()
    return ''.join(text)

@st.cache
def text_preprocessing(text):
    # Clean the numbers, punctuations, urls, whitespace
    puncs = string.punctuation
    text = re.sub(r'http\S+\s*', ' ', text)  # remove URLs
    text = re.sub(r'#\S+', ' ', text)  # remove #
    text = re.sub(r'@\S+', ' ', text)  # remove @
    text = re.sub('[%s]' % re.escape(puncs), ' ', text)  # remove punctuations
    text = re.sub(r'[^\x00-\x7f]',r' ', text) 
    text = re.sub('[0-9]+', ' ', text)  # remove numbers
    text = re.sub(r'\s+', ' ', text)  # remove extra whitespace
    return text

@st.cache
def resume_qualification_extraction(text):
    skills_education = ''.join(text.lower().split('education')[1:])
    text_tokens = word_tokenize(skills_education)
    tokens_without_sw = [word for word in text_tokens if word not in stopwords.words()]
    skills_education = (" ").join(tokens_without_sw)
    return skills_education

@st.cache
def info_extraction(text):
    nlp = spacy.load(r'./model_best/content/model-best')
    for doc in nlp.pipe(text, disable=["tagger", "parser"]):
        return ([(ent.text, ent.label_) for ent in doc.ents])

def create_wc(skill_text):
    cloud = WordCloud(background_color=(215,211,198), max_words=300, collocations=False, width=800, height=500, stopwords=STOPWORDS).generate(skill_text)
    cloud.to_file("./static/WordCloud.png")
    return 1

@st.cache
def transform_res(res):
    skills = []
    diploma = []
    major = []
    experience = []
    for (data, label) in res:
        if label=='SKILLS':
            skills.append(data)
        elif label=='DIPLOMA':
            diploma.append(data)
        elif label=='DIPLOMA_MAJOR':
            major.append(data)
        else:
            experience.append(data)
    skill_text = ' '.join(skills)
    # cloud = WordCloud(background_color=(215,211,198), max_words=300, collocations=False, width=800, height=500, stopwords=STOPWORDS).generate(skill_text)
    # # wc_path = os.path.join(save_folder,'./static/WordCloud.png')
    # cloud.to_file(wc_path)
    return skills,diploma,major,experience,skill_text

@st.cache
def data_loader(dataset):
    data_df = pd.read_csv(dataset)
    data_df = data_df.fillna('')
    return data_df

# @st.cache
def complete_skills(ideal_job_df,my_skills):
    skills_req = ideal_job_df['skills'].tolist()
    total_skills_req = []
    matched_skills = []
    skills_text = ''
    for skills in skills_req:
    	skills_token = skills.split(';')
    	for token in skills_token:
    		if token not in stopwords.words():
        		total_skills_req.append(token)
    # print(total_skills_req)
    # print(my_skills)
    # st.write(my_skills)
    total_skills_req = set(total_skills_req) # make a set of the total skills required with no duplication
    skills_improve_set = copy.deepcopy(total_skills_req)
    for skill in total_skills_req:
        # if skill not in my_skills:
        #     skills_improve.append(skill)
        for my_skill in my_skills:
            # res, lev_dist = lev_distance(skill, my_skill)
            if jw_similarity(skill,my_skill,0.8):
                # st.write(skill,my_skill)
                matched_skills.append((my_skill,skill))
                if skill in skills_improve_set:
                    skills_improve_set.remove(skill)
                # skills_improve.append(skill)
            # else:
                # skills_text += skill
                # skills_text += ';'
            # if nw_similarity(skill,my_skill,0.5):
            #     st.write(skill,my_skill)
            # if skill and my_skill:
                # res, lev_dist = lev_distance(skill, my_skill)
                # if not nw_similarity(skill,my_skill,0.7):
                    # skills_improve.append(skill)
    # skills_improve = list(set(skills_improve)) # remove duplication
    # skills_improve = skills_text.split(';')
    skills_improve = list(skills_improve_set)
    matched_skills = list(set(matched_skills))
    # st.write(skills_improve)
    return skills_improve, matched_skills


@st.cache
def create_job_list(data_df):

	data_df['job_title'] = data_df['job_title'].fillna('')
	data_df['skills'] = data_df['skills'].fillna('')
	job_category = data_df[data_df['job_title']!=''].groupby(['job_title'], as_index=False).agg({'skills':';'.join})

	jobs = []
	job_title_list = job_category['job_title'].tolist()
	job_skill_list = job_category['skills'].tolist()

	for i in range(len(job_title_list)):
		total_skills_req = []
		skills_token = job_skill_list[i].split(';')

		# # remove stopwords, very slow
		# total_skills_req = [word for word in skills_token if word not in stopwords.words()]
		if skills_token!=['']:
			job = {'job_title':job_title_list[i],'skills':skills_token}
			jobs.append(job)
	return jobs


# @st.cache
def job_matcher(my_skills, jobs):
    matched = []
    for job in jobs:
        nskills_job = len(job['skills'])
        count = 0
        for my_skill in my_skills:
            if my_skill in job['skills']:
                count += 1
            # for skill in job['skills']:
            #     if skill and my_skill:
            #         # res, lev_dist = lev_distance(skill, my_skill)
            #         if nw_similarity(skill,my_skill,0.8):
            #             count += 1
        if count:
            matched.append({'job_title':job['job_title'],
                # kind of laplace smooting
                'percentage': (count)/(nskills_job),
                'job_skill':job['skills'],
                'my_skill':my_skills
                }) 
    return matched

# levenshtein distance
# attention: should be an inverse because this is the distance
def lev_distance(s1, s2):
    lev_dist = rltk.levenshtein_distance(s1, s2)
    if lev_dist > min(len(s1), len(s2)) /1.5:
        return False, lev_dist
    return True, lev_dist

# needleman-wunch similarity
def nw_similarity(s1,s2,threshold):
# s1 = r1.title
  # s2 = r2.title
    nw_sim = rltk.needleman_wunsch_similarity(s1,s2)
    if nw_sim>=threshold:
        return True
  # print(nw_sim)
    return False

# jaro winkler similarity
def jw_similarity(s1,s2,threshold):
# s1 = r1.title
  # s2 = r2.title
    jw_sim = rltk.jaro_winkler_similarity(s1,s2)
    if jw_sim>=threshold:
        return True
  # print(nw_sim)
    return False

# add elements in the side bar
# Using "with" notation
with st.sidebar:
    col1, col2, col3 = st.columns([1,6,1])

    with col1:
      st.write("")

    with col2:
      image = Image.open(r'./static/jobs.jpg')
      st.image(image, caption='Job Helper System',use_column_width='auto')

    with col3:
      st.write("")
    

# receive a resume file at a time
# uploaded_file = st.file_uploader(label = "Please select your resume.", type=['pdf'], accept_multiple_files=False)

col4, col5, col6 = st.columns([6, 1, 1])

# dataset = './job_positions_full2.csv'
# data_df = data_loader(dataset)
# data_df = data_df.fillna('')

query_string = '''MATCH (c:category_node) <-[:belong_to]-(n:job_node)-[:need_skill]-> (s:skill_node)
RETURN n.id, n.title, s.name, c.name'''
lst = conn.query(query_string, db='neo4j')

job_id = []
skills = []
job_titles = []
for row in lst:
    job_id.append(row[0])
    skills.append(row[2])
    job_titles.append(row[1])
data_df = pd.DataFrame({'id':job_id,'skills':skills,'job_title':job_titles})
data_df = data_df.groupby(['id'])['skills'].apply(';'.join).reset_index()

# job_set_default = ['All']
job_set = set(data_df['category'].tolist())
# job_set = set(data_df['job_title'].tolist())
first_job = ['Data Scientist']
if '' in job_set:
	job_set.remove('')
job_set.remove('Data Scientist')
job_set_list = first_job + list(job_set)

with col4:
    st.markdown(
        """#### Here is the page for your future! 💪"""
    )
    Name = st.text_input("Name : ")
    Email = st.text_input("Email ID : ")
        # ideal_job = st.text_input("Ideal Job : ")
    ideal_job_option = st.selectbox(
                'Please select your ideal job category:',
                job_set_list)
   
    job_title_set = set(data_df[data_df['category']==ideal_job_option]['job_title'].tolist())

    ideal_job_title_option = st.selectbox(
                'Please select your ideal job:',
                job_title_set)

    # st.write('###### Job')
    # st.markdown("""[{}]({})""".format(record['company_name'],record['company_url']))

    st.write('You selected:', ideal_job_option, 'and the track:', ideal_job_title_option)
    with st.form(key="Form :", clear_on_submit = True):
        File = st.file_uploader(label = "Please select your resume.", type=["pdf"], accept_multiple_files=False)
        Submit = st.form_submit_button(label='Analyze')
        

    st.subheader("Details : ")
    st.metric(label = "Name :", value = Name)
    st.metric(label = "Email ID :", value = Email)

    if Submit :
        st.markdown("**The resume is sucessfully Uploaded.**")
        # Save uploaded file to current directory
        save_folder = os.getcwd()
        save_path = os.path.join(save_folder, File.name)
        with open(save_path, mode='wb') as w:
            w.write(File.getvalue())

        if os.path.exists(save_path):
            # file_path = save_path
            # print(save_path)
            st.success(f'File {File.name} is successfully saved!')
            st.write('')

            # analyze_button = st.button('Analyze your resume!')

            # with st.form(key="Ideal Job Form :", clear_on_submit = True):
            #     ideal_job = st.text_input("Ideal Job : ")
                # Analysis = st.form_submit_button(label='Analysis')
                
            # if Analysis:
            with st.spinner("Generating analysis..."):
                text = resume_text_extraction(save_path)
                text = text_preprocessing(text)
                    # st.write(text)
                    # print(text)

                skills_education = resume_qualification_extraction(text)
                res = info_extraction([skills_education])
                # st.write('res',res)
                # print(res)

                    
                my_skills,diploma,major,experience,skill_text = transform_res(res)

                st.subheader('%s \'s skills:' %Name)
                # st.write('123',skill_text)
                # st.write(skill_text)
                    
                create_wc(skill_text)
                wc_path = os.path.join(save_folder,'./static/WordCloud.png')

                skill_cloud = Image.open(wc_path)
                st.image(skill_cloud, caption='Your skills set',use_column_width='auto')

                st.subheader('Your diploma:')
                
                for d in diploma:
                        # st.write(d)
                        # st.metric(label="diploma", value=d)
                    st.write('#### 🎯 {}'.format(d))          


                if ideal_job_option == 'All':
                	ideal_job_df = data_df
                else:
                	ideal_job_df = data_df[data_df['job_title']==ideal_job_title_option]
                	# ideal_job_df = data_df[data_df['job_title'].str.contains(ideal_job, na=False, case=False)]

                skills_improve,matched_skills = complete_skills(ideal_job_df,my_skills)
                # st.write(ideal_job_df['SKILLS'].tolist())
                # st.write(my_skills)

                # st.snow()
                with st.container():
                    colors = ["#8ef", "#faa", "#afa", "#fea",'#6E85B7',"#B2C8DF",'#C4D7E0','#F8F9D7',\
                    '#FBFACD','#DEBACE','#BA94D1','#7F669D']
                    
                    with st.expander('Click to see the matched skills(your skill, matched skills in the job)'):
                        # st.markdown(matched_skills)
                        for (resume_skill,jd_skill) in matched_skills:
                            chosen_color = random.sample(colors, 1)
                            matched_skill = (resume_skill,jd_skill,chosen_color)
                            annotated_text(matched_skill)
                    

                with st.container():
                    st.subheader('You need to improve:')

                    skills_tuples = []
                    colors = ["#8ef", "#faa", "#afa", "#fea",'#6E85B7',"#B2C8DF",'#C4D7E0','#F8F9D7',\
                    '#FBFACD','#DEBACE','#BA94D1','#7F669D']
                    
                    for skill in skills_improve:
                        chosen_color = random.sample(colors, 1)
                        # st.write(skill)
                        skills_tuples.append((skill,'',chosen_color))
                    # with st.echo():
                    # skills_text = '\t'.join(skills_improve)
                    annotated_text(*skills_tuples)



                    jobs = create_job_list(data_df)
                    # print(my_skills)
                    matched_jobs = job_matcher(my_skills, jobs)
                    matched_jobs = sorted(matched_jobs, key=lambda x:x['percentage'], reverse=True)



                with st.container():
                    if len(matched_jobs)>=9:
                        number_jobs = 9 # default 9 jobs
                    elif len(matched_jobs)>=3:
                        number_jobs = 3
                    # number_jobs = st.text_input('Enter the number of Recommended Jobs:')
                    # if number_jobs:
                    # number_jobs = int(number_jobs)

                    st.write('')
                    st.write('')
                    st.write('#### {} Recommended jobs for you:'.format(number_jobs))

                    matched_res = {}
                    matched_jobs_list = []
                    matched_percentage_list = []

                    for i in range(number_jobs):
                        matched_jobs_list.append(matched_jobs[i]['job_title'])
                        matched_percentage_list.append(matched_jobs[i]['percentage'])
                    	# st.write(f"##### cv matching with {matched_jobs[i]['job_title']}")
                    	# st.write(f"{matched_jobs[i]['percentage']}")
                    matched_res['job_title'] = matched_jobs_list
                    matched_res['percentage'] = matched_percentage_list
                    chart = functools.partial(st.plotly_chart, use_container_width=True)

                    labels = matched_jobs_list
                    values = matched_percentage_list

                    # Use `hole` to create a donut-like pie chart
                    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                    fig.update_layout(
                    title={'text': "Recommended jobs for you"})
                    chart(fig)









               