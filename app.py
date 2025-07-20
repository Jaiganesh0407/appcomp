import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import smtplib
from email.message import EmailMessage

# Access secrets from .streamlit/secrets.toml
openai.api_key = st.secrets["openai_key"]
EMAIL_ADDRESS = st.secrets["email"]
EMAIL_PASSWORD = st.secrets["email_password"]
TO_EMAIL = "jaiganeshmanda@gmail.com"

st.set_page_config(page_title="Competitor Monitor", page_icon="🕵️")
st.title("🕵️ Competitor Website Monitor & Email Reporter")

# List of websites to track
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
        text = soup.get_text(separator=" ", strip=True)[:3000]
        prompt = f"Summarize this homepage content for key business offerings or updates:\n{text}"
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = completion.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return f"❌ Failed to fetch {name}: {e}"

st.subheader("📄 Website Summaries")

# Fetch summaries
for name, url in urls.items():
    with st.spinner(f"Fetching and summarizing {name}..."):
        summary = fetch_and_summarize(name, url)
        summaries[name] = summary
        st.markdown(f"### 🔹 {name}")
        st.write(summary)

# Email sending function
def send_email(summary_dict):
    msg = EmailMessage()
    msg["Subject"] = "🧾 Daily Competitor Summary Report"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    body = "\n\n".join([f"{name}:\n{summary}" for name, summary in summary_dict.items()])
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email sending failed: {e}")
        return False

# Email trigger button
if st.button("📧 Email This Report"):
    if send_email(summaries):
        st.success("✅ Email sent successfully!")
