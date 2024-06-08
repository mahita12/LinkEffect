import os
import pandas as pd
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
from pyngrok import ngrok
import threading

load_dotenv()
# Set up AzureOpenAI client
client = AzureOpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),  # assuming your key is saved under 'OPENAI_API_KEY'
    azure_endpoint=os.getenv('OPEN_AI_ENDPOINT'),  # your Azure OpenAI endpoint
    api_version="2023-07-01-preview"  # updated API version
)
deployment_id = os.getenv('OPEN_AI_DEPLOYMENT_NAME')

def generate_message_content(recipient_name, recipient_position, recipient_company, sender_name, sender_position, desired_job, message_purpose):
    prompt = (
        f"Write a professional message to {recipient_name}, who is a {recipient_position} at {recipient_company}. "
        f"The message is from {sender_name}, who is currently a {sender_position} and is interested in the {desired_job} position at {recipient_company}. "
        f"The purpose of the message is: {message_purpose}. Please ensure the message is polite and professional."
    )

    completion = client.chat.completions.create(
        model=deployment_id,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    return completion.choices[0].message.content

def search_data(df, column, value):
    """Search the DataFrame based on user input and return the results."""
    if column not in df.columns:
        return None
    results = df[df[column].astype(str).str.contains(value, case=False, na=False)]
    return results

st.title("LinkedIn Connections Data Explorer & Message Generator")

st.subheader("By using this service, users consent to the upload and display of their data in accordance with our privacy policy.")

st.subheader("""To download your LinkedIn connections data and display it using Python, follow these steps:

Step 1: Download Your LinkedIn Connections Data
Log in to LinkedIn:

Go to LinkedIn and log in to your account.
Access the Data Privacy Section:

Click on your profile icon at the top of LinkedIn and select Settings & Privacy.
Navigate to the Data privacy section.
Request a Download of Your Data:

Under the How LinkedIn uses your data section, click on Get a copy of your data.
Select the Connections option to download your connections data.
Click on Request archive. LinkedIn will prepare your data and send you an email when it is ready for download.
Download the Data:

Follow the link in the email from LinkedIn to download your connections data. The file will typically be in CSV format.""")

    # CSV File Upload Section
st.subheader("Upload your CSV file")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")


if uploaded_file is not None:
    try:
        # Try reading with default comma delimiter
        try:
            df = pd.read_csv(uploaded_file)
        except pd.errors.ParserError:
            # Fallback to reading with a semicolon delimiter
            uploaded_file.seek(0)  # Reset file pointer to beginning
            df = pd.read_csv(uploaded_file,delimiter=',', skiprows=2)

        st.write("File uploaded successfully!")
        st.write(df)
    except Exception as e:
        st.error(f"Error uploading file: {e}")

# Data Search Section
    st.subheader("Search your Data")
    search_column = st.text_input("Enter the column name to search")
    search_value = st.text_input(f"Enter the value to search in column '{search_column}'")

    if st.button("Search"):
        if search_column and search_value:
            results = search_data(df, search_column, search_value)
            if results is not None and not results.empty:
                st.write(f"Search Results for '{search_value}' in '{search_column}':")
                st.write(results)
            else:
                st.warning("No matching data found.")
        else:
            st.warning("Please enter both column name and search value")

    

    # Message Generation Section
    st.subheader("Generate a Professional Message")
    recipient_name = st.text_input("Recipient's Name")
    recipient_position = st.text_input("Recipient's Job Position")
    recipient_company = st.text_input("Recipient's Company")
    sender_name = st.text_input("Your Name")
    sender_position = st.text_input("Your Current Job Position")
    desired_job = st.text_input("Job Position You Are Interested In")
    message_purpose = st.text_area("Purpose of the Message")

    if st.button("Generate Message"):
        if recipient_name and recipient_position and recipient_company and sender_name and sender_position and desired_job and message_purpose:
            message_content = generate_message_content(
                recipient_name, recipient_position, recipient_company,
                sender_name, sender_position, desired_job, message_purpose
            )

            st.subheader("Generated Message Content")
            st.write(message_content)
        else:
            st.warning("Please fill in all the fields")