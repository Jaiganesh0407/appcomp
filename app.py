import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import smtplib
from email.message import EmailMessage

# Load secrets from .streamlit/secrets.toml
openai.api_key = st.secrets["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"]
EMAIL_ADDRESS = st.secrets["jaiganeshmandha8@gmail.com"]
EMAIL_PASSWORD = st.secrets["Jaiganesh@2004"]
TO_EMAIL = "jaiganeshmanda@gmail.com"

st.title("🕵️ Competitor Website Monitor & Email Reporter")

urls = {
    "ScienceSoft": "https://www.sciencesoft.com/",
    "BairesDev": "https://www.bairesdev.com/",
    "ELEKS": "https://eleks.com/",
    "Vention": "https://vention.com/",
    "Radixweb": "https://radixweb.com/"
}

summaries = {}

def fetch_and_summarize(name, url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)[:3000]  # Limit size
        prompt = f"Summarize this homepage content for key business offerings or updates:\n{text}"
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = completion.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return f"❌ Failed to fetch {name}: {e}"

st.subheader("Website Summaries")

for name, url in urls.items():
    with st.spinner(f"Fetching {name}..."):
        summary = fetch_and_summarize(name, url)
        summaries[name] = summary
        st.markdown(f"### {name}")
        st.write(summary)

def send_email(summary_dict):
    msg = EmailMessage()
    msg["Subject"] = "🧾 Daily Competitor Summary Report"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    body = "\n\n".join([f"{name}:\n{content}" for name, content in summary_dict.items()])
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email sending failed: {e}")
        return False

if st.button("📧 Email This Report"):
    if send_email(summaries):
        st.success("Email sent successfully!")