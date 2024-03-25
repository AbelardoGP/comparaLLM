import cohere
import openai
import streamlit as st
import threading
import queue

# Streamlit Interface for API Keys
st.title("AI by Tecmilenio. Cohere vs OpenAI")
st.write("Esta APP despliega las respuestas de Cohere y de OpenAI a tu pregunta, y despues le pide a OpenAI que combine las 2 respuestas")
# Function to combine responses
def combine_responses(cohere_answer, openai_answer):
    combined_query = f"Combine these answers for a better response:\nCohere: {cohere_answer}\nOpenAI: {openai_answer}"
    client = openai.OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(model='gpt-4-1106-preview', messages=[{"role": "user", "content": combined_query}])
    return response.choices[0].message.content


cohere_api_key = st.text_input('Enter your Cohere API Key:', type='password')
openai_api_key = st.text_input('Enter your OpenAI API Key:', type='password')

# Check if API keys are provided
if cohere_api_key and openai_api_key:
    # Initialize your OpenAI and Cohere clients
    co = cohere.Client(cohere_api_key)
    openai.api_key = openai_api_key

    # Function to get response from Cohere
    def get_cohere_response(qstn, response_queue):
        response = co.generate(model='command', prompt="contesta en español la siguiente pregunta:" +qstn)
        bot_answer = response.generations[0].text
        bot_answer = bot_answer.replace("\n\n--", "").replace("\n--", "").strip()
        response_queue.put(('Cohere', bot_answer))

    # Function to get response from OpenAI
    def get_openai_response(qstn, response_queue):
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(model='gpt-4-1106-preview', messages=[{"role": "user", "content": qstn}])
        bot_answer = response.choices[0].message.content
        bot_answer = bot_answer.replace("\n\n--", "").replace("\n--", "").strip()
        response_queue.put(('OpenAI', bot_answer))

    # Combine responses using OpenAI
    def combine_responses(cohere_answer, openai_answer):
        combined_query = f"Combine these answers for a better response:\nCohere: {cohere_answer}\nOpenAI: {openai_answer}"
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(model='gpt-4-1106-preview', messages=[{"role": "user", "content": combined_query}])
        return response.choices[0].message.content



# Get user question
qstn_input = st.text_input("Escribe tu pregunta")

if st.button("Enviar"):
    if qstn_input:
        my_bar = st.progress(0)
        response_queue = queue.Queue()

        # Start threads for parallel processing
        threading.Thread(target=get_cohere_response, args=(qstn_input, response_queue)).start()
        threading.Thread(target=get_openai_response, args=(qstn_input, response_queue)).start()

        # Wait for both responses
        responses = {}
        for _ in range(2):
            source, response = response_queue.get()
            responses[source] = response
            my_bar.progress(len(responses) / 2)

        # Display individual responses in columns
        col1, col2 = st.columns(2)
        with col1:
            st.write("Cohere's Response:", responses['Cohere'])
        with col2:
            st.write("OpenAI's Response:", responses['OpenAI'])

        # Combine responses
        combined_answer = combine_responses(responses['Cohere'], responses['OpenAI'])
        st.write("Combined Response:", combined_answer)

        my_bar.progress(1)
    else:
        st.error("Please enter a question.")
