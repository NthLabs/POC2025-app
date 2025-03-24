# pip install -qU langchain_community pypdf
from langchain_community.document_loaders import PyPDFLoader
import os


# My Variables
myDocs = "./data/pdftest"

if not os.path.isdir(myDocs):
    os.makedirs(myDocs)


for pdf in os.listdir(myDocs):
    loader=PyPDFLoader(f"{myDocs}/{pdf}")
    docs = loader.load()
    print(pdf)
    for page in range(len(docs)):
        print(f"{page + 1} - {len(docs[page].page_content.split())} words")


