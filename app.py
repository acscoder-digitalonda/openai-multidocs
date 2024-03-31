 
from openai import OpenAI
 
import streamlit as st
from gdocs import gdocs
 

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  
model_name = "gpt-4-turbo-preview"
def send_llm(prompt,data):
    system_prompting = "You are a helpful assistant."
    if len(data):
        system_prompting += "Based on these "+str(len(data))+" documents provided below, please complete the task requested by the user:" 
        c = 0
        for title,chunk in data:
            c += 1
            system_prompting += "\n\n"
            system_prompting += "Document #"+str(c)+" :"+title
            system_prompting += "\n\n"
            system_prompting += "\n\n".join(chunk)
            system_prompting += "--------------------------------------------------"
            system_prompting += "\n\n"
  
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompting },
            {"role": "user", "content": prompt},
        ],
        model=model_name,
    )
    return chat_completion.choices[0].message

def get_gdoc(url):
    creds = gdocs.gdoc_creds()
    document_id = gdocs.extract_document_id(url)
    chunks = gdocs.read_gdoc_content(creds,document_id)
    title = gdocs.read_gdoc_title(creds,document_id)
    return document_id,title,chunks

 
with st.sidebar:
  doc_url = st.text_input("Enter your Gooogle Docs url:")
  submit_button = st.button("Add Document")
  st.subheader("Select Your Docs")

  if not "all_docs" in st.session_state:
        st.session_state.all_docs = {}
  all_docs = st.session_state.all_docs

  if submit_button:
    document_id,title,chunks = get_gdoc(doc_url)
    all_docs[document_id] = (title,chunks)
    st.session_state.all_docs = all_docs 
     
    
  doc_options = st.multiselect(
    'Select Your Docs',
    all_docs.keys(),
    format_func = lambda x: all_docs[x][0] if x in all_docs else x,
    )
     
your_prompt = st.text_area("Enter your Prompt:")  
submit_llm = st.button("Send")
if submit_llm:
    data = []
    for doc in doc_options:
        data.append(all_docs[doc])
    
    response = send_llm(your_prompt,data)
    st.write(response.content)