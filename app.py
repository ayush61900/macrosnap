import streamlit as st
import requests

from google import genai
from google.genai import types

from prompts import (
    SUMMARY_REQUEST_PROMPT,
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
)


# CONFIGURATION


MODEL_NAME = "gemini-3.5-flash"

st.set_page_config(
    page_title="MacroSnap",
    page_icon="🥗",
    layout="centered"
)

# API KEYS / SECRETS


GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

TELEGRAM_BOT_TOKEN = st.secrets.get(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = st.secrets.get(
    "TELEGRAM_CHAT_ID"
)


# CHECK SECRETS


if not GEMINI_API_KEY:

    st.error(
        "❌ GEMINI_API_KEY is missing. "
        "Add it to .streamlit/secrets.toml."
    )

    st.stop()


if not TELEGRAM_BOT_TOKEN:

    st.error(
        "❌ TELEGRAM_BOT_TOKEN is missing. "
        "Add it to .streamlit/secrets.toml."
    )

    st.stop()


if not TELEGRAM_CHAT_ID:

    st.error(
        "❌ TELEGRAM_CHAT_ID is missing. "
        "Add it to .streamlit/secrets.toml."
    )

    st.stop()



# SESSION STATE


if "has_meal_data" not in st.session_state:

    st.session_state.has_meal_data = False

# GEMINI CLIENT


@st.cache_resource
def get_gemini_client():

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


gemini_client = get_gemini_client()

# MESSAGE FUNCTIONS


def render_message(message):

    with st.chat_message(message["role"]):

        if message["kind"] == "text":

            st.write(
                message["content"]
            )

        elif message["kind"] == "image":

            st.image(
                message["content"]
            )


def add_message(
    role,
    kind,
    content
):

    st.session_state.messages.append(
        {
            "role": role,
            "kind": kind,
            "content": content
        }
    )

    render_message(
        st.session_state.messages[-1]
    )

# GEMINI


def ask_gemini(parts):

    try:

        response = (
            st.session_state.chat.send_message(
                parts
            )
        )

        return response.text

    except Exception as error:

        return (
            "Sorry, something went wrong while "
            f"analyzing your meal:\n\n{error}"
        )

# TELEGRAM

def clean_telegram_text(text):

    if not text:

        return (
            "No nutrition summary available."
        )

    # Remove unnecessary whitespace
    text = " ".join(
        text.split()
    )

    # Telegram message limit
    if len(text) > 4000:

        text = (
            text[:4000]
            + "..."
        )

    return text


def send_telegram(
    user_name,
    summary
):

    message = (
        "🥗 MacroSnap Daily Summary\n\n"
        f"Hello {user_name}!\n\n"
        f"{clean_telegram_text(summary)}"
    )

    url = (
        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    try:

        response = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            },
            timeout=15
        )

        result = response.json()

        if result.get("ok"):

            return (
                True,
                "Message sent successfully"
            )

        return (
            False,
            result.get(
                "description",
                "Telegram API error"
            )
        )

    except requests.exceptions.Timeout:

        return (
            False,
            "Telegram request timed out."
        )

    except requests.exceptions.RequestException as error:

        return (
            False,
            f"Network error: {error}"
        )

    except Exception as error:

        return (
            False,
            str(error)
        )

# STEP 1: ONBOARDING


if "onboarded" not in st.session_state:

    st.title(
        "🥗 MacroSnap"
    )

    st.caption(
        "Snap it. Track it. "
        "Send your nutrition results to Telegram."
    )

    with st.form(
        "onboarding_form"
    ):

        name = st.text_input(
            "Your name",
            placeholder="Enter your name"
        )

        st.info(
            "Your nutrition summary will be "
            "sent to your connected Telegram account."
        )

        submitted = st.form_submit_button(
            "Let's go 🚀"
        )

        if submitted:

            if not name.strip():

                st.warning(
                    "Please enter your name."
                )

            else:

                # Save user's name
                st.session_state.name = (
                    name.strip()
                )

                # Create Gemini chat
                st.session_state.chat = (
                    gemini_client.chats.create(
                        model=MODEL_NAME,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT
                        )
                    )
                )

                # Initialize messages
                st.session_state.messages = []

                # Reset meal state
                st.session_state.has_meal_data = False

                # Mark onboarding complete
                st.session_state.onboarded = True

                st.rerun()

    st.stop()



# STEP 2: CHAT INTERFACE


header_col, button_col = st.columns(
    [5, 2],
    vertical_alignment="center"
)
# HEADER


with header_col:

    st.title(
        "🥗 MacroSnap"
    )

# SEND TO TELEGRAM BUTTON


with button_col:

    if st.button(
        "📤 Send to Telegram",
        disabled=not st.session_state.has_meal_data,
        use_container_width=True
    ):

        with st.spinner(
            "Summarizing your day... 🧮"
        ):

            summary = ask_gemini(
                [
                    SUMMARY_REQUEST_PROMPT
                ]
            )

        success, info = send_telegram(
            st.session_state.name,
            summary
        )

        if success:

            st.success(
                "Sent! Check your Telegram 📲"
            )

        else:

            st.error(
                f"Couldn't send message: {info}"
            )

# USER INFORMATION


st.caption(
    f"Logged in as {st.session_state.name} "
    "• Nutrition updates go to Telegram 📲"
)

# DISPLAY CHAT HISTORY


if not st.session_state.messages:

    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        )
    )

else:

    for message in st.session_state.messages:

        render_message(
            message
        )


# CHAT INPUT


user_input = st.chat_input(
    "Ask a question, or attach a photo of your meal",
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png"
    ]
)

# PROCESS USER INPUT

if user_input:

    st.session_state.has_meal_data = True

    photo = (
        user_input.files[0]
        if user_input.files
        else None
    )

    text = user_input.text

    parts = []

    # IMAGE
  

    if photo is not None:

        photo_bytes = (
            photo.getvalue()
        )

        # Display uploaded image
        add_message(
            "user",
            "image",
            photo_bytes
        )

        # Send image to Gemini
        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type
            )
        )


    # TEXT
 
    if text:

        add_message(
            "user",
            "text",
            text
        )

        parts.append(
            text
        )

    # IMAGE WITHOUT TEXT

    elif photo is not None:

        parts.append(
            """
            Analyze this meal carefully.

            Identify the food items and estimate:

            1. Calories
            2. Protein
            3. Carbohydrates
            4. Fat

            Give the result in a simple,
            clear and easy-to-understand format.
            """
        )


    # GEMINI RESPONSE


    with st.spinner(
        "Crunching the numbers... 🧮"
    ):

        answer = ask_gemini(
            parts
        )

    # DISPLAY GEMINI RESPONSE
   

    add_message(
        "assistant",
        "text",
        answer
    )

    # REFRESH PAGE
   

    st.rerun()