
import streamlit as st
from datetime import date, datetime
from backend import generate_email

# Page configuration
st.set_page_config(
    page_title="AI Email Generator",
    page_icon="📧",
    layout="centered"
)

st.title("📧 AI Email Generator")
st.write("Generate professional emails using AI.")

# Initialize email history
if "email_history" not in st.session_state:
    st.session_state.email_history = []

# Email tone
tone = st.selectbox(
    "Select Email Tone",
    ["Formal", "Friendly", "Professional"]
)

# Email purpose
purpose = st.text_area(
    "Enter Email Purpose",
    placeholder="Example: Request leave for two days"
)

# Recipient
recipient = st.selectbox(
    "Select Recipient",
    ["Manager", "Client", "Student"]
)

recipient_name = st.text_input(
    "Enter Recipient Name",
    placeholder="Example: Seetha"
)

sender_name = st.text_input(
    "Enter Your Name",
    placeholder="Example: Shiyam"
)

# Detect email category
purpose_lower = purpose.lower()

leave_keywords = [
    "leave",
    "vacation",
    "sick leave",
    "annual leave",
    "time off"
]

production_keywords = [
    "production",
    "deployment",
    "go live",
    "go-live",
    "release",
    "postpone",
    "postponement"
]

is_leave_request = any(
    word in purpose_lower for word in leave_keywords
)

is_production_email = any(
    word in purpose_lower for word in production_keywords
)

# Leave date fields
start_date = None
end_date = None

if is_leave_request:

    st.subheader("📅 Leave Details (Optional)")

    include_start_date = st.checkbox(
        "Provide Leave Start Date"
    )

    if include_start_date:
        start_date = st.date_input(
            "Leave Start Date",
            value=date.today()
        )

    include_end_date = st.checkbox(
        "Provide Leave End Date"
    )

    if include_end_date:
        end_date = st.date_input(
            "Leave End Date",
            value=date.today()
        )

# Production date and time fields
production_start_datetime = None

if is_production_email:

    st.subheader("🚀 Proposed Production Schedule")

    st.write(
        "Enter when production is expected to start "
        "after the postponement."
    )

    include_production_date = st.checkbox(
        "Choose a different production start date"
    )

    if include_production_date:
        production_date = st.date_input(
            "Proposed Production Start Date",
            value=date.today()
        )
    else:
        # If no date is selected, use today's date
        production_date = date.today()

    # Time field always appears
    production_time = st.time_input(
        "Proposed Production Start Time",
        value=datetime.now().time().replace(second=0, microsecond=0)
    )

    production_start_datetime = (
        f"{production_date.strftime('%d %B %Y')} "
        f"at {production_time.strftime('%I:%M %p')}"
    )

    st.info(
        f"Proposed production schedule: "
        f"{production_start_datetime}"
    )

# Generate email
if st.button("Generate Email", type="primary"):

    if not purpose.strip():
        st.warning("Please enter the email purpose.")

    elif not recipient_name.strip():
        st.warning("Please enter the recipient's name.")

    elif not sender_name.strip():
        st.warning("Please enter your name.")

    elif start_date and end_date and end_date < start_date:
        st.error("Leave end date cannot be earlier than start date.")

    else:

        try:

            with st.spinner("Generating your email..."):

                output = generate_email(
                    purpose=purpose,
                    tone=tone,
                    recipient=recipient,
                    recipient_name=recipient_name.strip().title(),
                    sender_name=sender_name.strip(),
                    start_date=start_date,
                    end_date=end_date,
                    production_start_datetime=production_start_datetime
                )

            email_record = {
                "subject": output["subject"],
                "body": output["body"],
                "created_at": datetime.now().strftime(
                    "%d-%m-%Y %I:%M %p"
                )
            }

            # Latest email appears first
            st.session_state.email_history.insert(
                0,
                email_record
            )

            st.success("Email generated successfully!")

        except Exception as e:
            st.error(f"Something went wrong: {e}")


# Latest generated email
if st.session_state.email_history:

    st.divider()

    st.subheader("📧 Latest Generated Email")

    latest_email = st.session_state.email_history[0]

    st.write("**Subject:**", latest_email["subject"])

    st.write("**Body:**")

    st.text(latest_email["body"])

    email_text = (
        f"Subject: {latest_email['subject']}\n\n"
        f"Body:\n{latest_email['body']}"
    )

    st.download_button(
        "⬇️ Download Latest Email",
        data=email_text,
        file_name="latest_email.txt",
        mime="text/plain"
    )


# Email History
if st.session_state.email_history:

    st.divider()

    st.subheader("📚 Email History")

    st.write(
        f"Total emails generated: "
        f"{len(st.session_state.email_history)}"
    )

    selected_index = st.selectbox(
        "Select an email to view",
        options=range(len(st.session_state.email_history)),
        format_func=lambda i: (
            f"{i + 1}. "
            f"{st.session_state.email_history[i]['subject']} "
            f"({st.session_state.email_history[i]['created_at']})"
        )
    )

    selected_email = st.session_state.email_history[selected_index]

    with st.expander("View Selected Email"):

        st.write("**Subject:**", selected_email["subject"])

        st.text(selected_email["body"])
