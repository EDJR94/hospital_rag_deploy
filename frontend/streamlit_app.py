import streamlit as st
import os
import requests

CHATBOT_URL = "http://backend:8000/hospital_agent"

with st.sidebar:

    st.header("Example Questions")
    st.markdown("- Which hospitals are in the hospital system?")
    st.markdown(
        "- At which hospitals are patients complaining about billing and "
        "insurance issues?"
    )
    st.markdown(
        "- What are patients saying about the nursing staff at "
        "Castaneda-Hardy?"
    )
    st.markdown(
        "- List every review for visits treated by physician 270. Don't leave any out."
    )
    st.markdown(
        "- What's the blood type of the oldest patient?"
    )

    st.markdown(
        "- Which was the last consult?"
    )
    
    st.markdown(
        "- What are the main causes of bad reviews?"
    )

    st.markdown(
        "- Give me information about any insurance payer"
    )

    st.markdown(
        "- Which hospital has the best and worst reviews?"
    )
    


st.title("Hospital System Chatbot")
st.info(
    "Ask me questions about patients, visits, insurance payers, hospitals, "
    "physicians and reviews!"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "output" in message.keys():
            st.markdown(message["output"])

        if "explanation" in message.keys():
            with st.status("How was this generated", state="complete"):
                st.info(message["explanation"])

if prompt := st.chat_input("What do you want to know?"):
    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({"role": "user", "output": prompt})

    data = {"text": prompt}

    with st.spinner("Searching for an answer..."):
        response = requests.post(CHATBOT_URL, json=data)

        if response.status_code == 200:
            output_text = response.json()["output"]
            explanation = response.json()["intermediate_steps"]

        else:
            output_text = """An error occurred while processing your message.
            Please try again or rephrase your message."""
            explanation = output_text

    st.chat_message("assistant").markdown(output_text)
    st.status("How was this generated", state="complete").info(explanation)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "output": output_text,
            "explanation": explanation,
        }
    )