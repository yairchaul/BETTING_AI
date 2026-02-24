from google.cloud import vision
from google.oauth2 import service_account
import streamlit as st


def get_vision_client():

    creds_dict = dict(st.secrets["google_credentials"])

    # 🔥 FIX CRÍTICO
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict
    )

    client = vision.ImageAnnotatorClient(credentials=credentials)

    return client
