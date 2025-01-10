import streamlit as st
import datetime

# Static data for booked slots (replace this with your actual booked slots)
booked_slots_data = {
    "2025-01-08": ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"],  # Fully booked
    "2025-01-09": ["10:00", "13:00"],  # Partially booked
}

# Function to get booked slots for a specific date
def get_booked_slots(date):
    date_str = str(date)
    return booked_slots_data.get(date_str, [])

# Streamlit App
st.title("📅 Appointment Scheduling System")
st.write("Schedule an appointment by selecting an available slot.")

# Appointment Slot Selection
st.subheader("📆 Select Your Appointment Slot")
today = datetime.date.today()

# Disable previous dates
appointment_date = st.date_input("Choose a date", min_value=today)

if appointment_date:
    # Get booked slots for the selected date
    booked_slots = get_booked_slots(appointment_date)
    st.write(f"Booked slots for {appointment_date}: {', '.join(booked_slots) if booked_slots else 'None'}")

    # Define available times (9 AM to 5 PM)
    available_times = [f"{hour:02d}:00" for hour in range(9, 18)]
    available_slots = [time for time in available_times if time not in booked_slots]

    if not available_slots:  # Check if the entire day is booked
        st.warning(f"All slots are fully booked for {appointment_date}. Please choose another date.")
        appointment_time = None
    else:
        appointment_time = st.selectbox("Choose a time", available_slots)
else:
    appointment_time = None

# Save Appointment
if st.button("💾 Save Appointment"):
    if appointment_date and appointment_time:
        st.success(f"Appointment scheduled for {appointment_date} at {appointment_time}!")
    else:
        st.error("Please select a valid date and time.")

# View Booked Slots
if st.button("📋 View All Booked Slots"):
    st.write("### Current Booked Slots")
    for date, slots in booked_slots_data.items():
        st.write(f"**{date}:** {', '.join(slots) if slots else 'None'}")
