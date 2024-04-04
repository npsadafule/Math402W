import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file
df = pd.read_excel("Appointments.xlsx")

# Ensure "ApptBookedDate" is a datetime type
df['ApptBookedDate'] = pd.to_datetime(df['ApptBookedDate'])

# Extract year from "ApptBookedDate"
df['Year'] = df['ApptBookedDate'].dt.year

# Group by "ApptTypeDesc" and "Year", then count appointments
appointment_counts = df.groupby(['ApptTypeDesc', 'Year']).size().reset_index(name='Counts')

# Find the total counts for each "ApptTypeDesc" across all years and get the top 20
total_counts = appointment_counts.groupby(['ApptTypeDesc'])['Counts'].sum().nlargest(20)

# Select only the records that match the top 20 "ApptTypeDesc"
top_appointment_counts = appointment_counts[appointment_counts['ApptTypeDesc'].isin(total_counts.index)]

# Now pivot the table so we get one column per year and one row per "ApptTypeDesc"
pivot_table = top_appointment_counts.pivot_table(index='ApptTypeDesc', columns='Year', values='Counts', aggfunc='sum', fill_value=0)

# Sort the pivot table rows by the total counts in descending order
pivot_table = pivot_table.loc[total_counts.index]

# Plot
plt.figure(figsize=(14, 10))
pivot_table.plot(kind='bar', figsize=(14, 10))
plt.title('Top 20 Appointment Types by Total Number of Appointments and Year (Descending Order)')
plt.xlabel('Appointment Type')
plt.ylabel('Number of Appointments')
plt.xticks(rotation=45)
plt.legend(title='Year', bbox_to_anchor=(1.01, 1), loc='upper left')
plt.tight_layout()

# Show the plot
plt.show()