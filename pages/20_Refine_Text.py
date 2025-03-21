import streamlit as st
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from poc_env import *

st.set_page_config(
    page_title="Refine Text",)
st.image("images/NthLabs.png", width=200)
st.divider()


llm = ChatNVIDIA(
    base_url=f"http://{llm1Addr}/v1",
    api_key="FAKE",
    model=llm1Model,
    temperature=0.9)

def no_rag(userInput):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{systemPrompt}{context}"),
        ("user", "{userInput}"),
    ])
    stuffDocumentsChain = create_stuff_documents_chain(llm,prompt)

    response = stuffDocumentsChain.invoke({
        "systemPrompt": systemPrompt,
        "userInput": userInput,
        "context": "",
        })
    return response

def generate_response(userInput):
    response = no_rag(userInput)
    st.markdown(response)

with st.form('my_form'):
    systemPrompt = st.text_area('System Prompt:',
                                'Please provide three alternate examples of the following text',
                                height = 150)
    userInput = st.text_area('Enter text:', 
                        placeholder = 'Type or paste your text here',
                        height = 200)
    submitted = st.form_submit_button('Submit')
    if submitted:
        with st.spinner('Calculating the response...'):
            generate_response(userInput)


