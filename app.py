import os
from openai import OpenAI
 
import streamlit as st
from gdocs import gdocs
 

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
model_name = "gpt-4-turbo-preview"
def send_llm(prompt,data):
    prompting = ""
    if len(data):
        prompting += "Based on these documents provided below, please complete the task requested by the user:" 
    
        for title,chunk in data:
            prompting += "\n\n"
            prompting += "Document title :"+title
            prompting += "\n\n"
            prompting += "\n\n".join(chunk)
            prompting += "--------------------------------------------------"
            prompting += "\n\n"
 
    prompting += "USER task:"
    prompting += prompt
     
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompting},
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