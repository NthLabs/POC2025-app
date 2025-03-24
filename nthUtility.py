import streamlit as st
import os
from datetime import datetime


def file_structure(myDocs):
    if not os.path.isdir(myDocs):
        os.makedirs(myDocs)
    if not os.path.isdir("catalog"):
        os.makedirs("catalog")
    if not os.path.isdir("logs"):
        os.mkdir("logs")


def log_prompt(userInput, logFile):
    id = st.context.headers["Sec-Websocket-Key"]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    with open(logFile, "a") as promptLog:
        promptLog.write(f"{timestamp},{id},{userInput}\n")