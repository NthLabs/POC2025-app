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

def log_prompt_perf(userInput, logFile, callback, timeInvoke):
    id =          st.context.headers["Sec-Websocket-Key"]
    timestamp =   datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    tokPrompt =   callback.prompt_tokens
    tokComplete = callback.completion_tokens
    tokTotal =    callback.total_tokens
    tokPerSec =   tokComplete / timeInvoke

    with open(logFile, "a") as promptLog:
        promptLog.write(f"{timestamp},{id},{tokPrompt},{tokComplete},{tokTotal},{timeInvoke:.1f},{tokPerSec:.1f},{userInput}\n")