import streamlit as st
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain

st.set_page_config(
    page_title="Refine Text",)
st.image("images/NthLabs.png", width=200)
st.divider()


llm = ChatNVIDIA(
    base_url="http://10.106.14.20:8021/v1",
    api_key="FAKE",
    model="meta/llama-3.1-8b-instruct",
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
                                'Please provide three alternate examples of the the following text',
                                height = 150)
    userInput = st.text_area('Enter text:', 
                        placeholder = 'Type or paste your text here',
                        height = 200)
    submitted = st.form_submit_button('Submit')
    if submitted:
        with st.spinner('Calculating the response...'):
            generate_response(userInput)


