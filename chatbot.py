import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Location of the JSON file
JSON_FILE_PATH = "sensor_data.json"

# Placeholder Gemini API credentials (replace with actual values from Gemini)
GEMINI_API_KEY = "AIzaSyDQtpJCrcaMu0vgcrWU0RDtVFrntw8L1OE"  # Replace with your real Gemini API key
GEMINI_API_URL = "https://api.gemini.com/v1/ask"  # Placeholder URL, replace with the correct endpoint

class GeminiChatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini 3 Chatbot - Multi-Sensor Analysis")
        self.root.geometry("800x600")

        # Load data from JSON file
        self.data = self.load_sensor_data()

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Input field
        self.input_field = ttk.Entry(root, width=60)
        self.input_field.grid(row=1, column=0, padx=10, pady=10)
        self.input_field.bind("<Return>", self.process_input)

        # Send button
        self.send_button = ttk.Button(root, text="Send", command=self.process_input)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        # Graph frame
        self.graph_frame = ttk.Frame(root)
        self.graph_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10)

        self.display_initial_message()

    def load_sensor_data(self):
        try:
            with open(JSON_FILE_PATH, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            self.chat_display.insert(tk.END, f"Error: Could not find file at {JSON_FILE_PATH}\n")
            return {}
        except json.JSONDecodeError:
            self.chat_display.insert(tk.END, "Error: Invalid JSON format in sensor data file\n")
            return {}

    def display_initial_message(self):
        self.chat_display.insert(tk.END, "Gemini 3: Hello! I'm Gemini 3, powered by xAI. I can analyze temperature, humidity, air quality, and light intensity data from the JSON file (2025-03-20 and 2025-04-01). Ask me about climate, crops, air, light, or request graphs!\n\n")

    def process_input(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        self.chat_display.insert(tk.END, f"You: {user_input}\n")
        self.input_field.delete(0, tk.END)

        response = self.process_query(user_input)
        self.chat_display.insert(tk.END, f"Gemini 3: {response}\n\n")
        self.chat_display.see(tk.END)

    def process_query(self, query):
        if not self.data or "_default" not in self.data or "1" not in self.data["_default"]:
            return "Error: No valid sensor data loaded from the file."

        # Combine data from both dates
        all_data = {}
        for date in ["2025-03-20", "2025-04-01"]:
            if date in self.data["_default"]["1"]:
                all_data.update(self.data["_default"]["1"][date])

        times = list(all_data.keys())
        temps = [all_data[t].get("temperature") for t in times]
        humidities = [all_data[t].get("humidity") for t in times]
        air_qualities = [all_data[t].get("air_quality", 50) for t in times]  # Default 50 µg/m³ if missing
        light_intensities = [all_data[t].get("light_intensity", 1000) for t in times]  # Default 1000 lux if missing

        # Filter out None values for averaging
        valid_temps = [t for t in temps if t is not None]
        valid_humidities = [h for h in humidities if h is not None]
        valid_air_qualities = [a for a in air_qualities if a is not None]
        valid_light_intensities = [l for l in light_intensities if l is not None]

        avg_temp = np.mean(valid_temps) if valid_temps else None
        avg_humidity = np.mean(valid_humidities) if valid_humidities else None
        avg_air_quality = np.mean(valid_air_qualities) if valid_air_qualities else 50
        avg_light_intensity = np.mean(valid_light_intensities) if valid_light_intensities else 1000

        query = query.lower()

        # Graph requests
        if "graph" in query or "plot" in query:
            if "temperature" in query and "humidity" in query:
                return self.plot_both(times, temps, humidities, "Temperature (°C)", "Humidity (%)")
            elif "temperature" in query or ("graph" in query and "temp" in query):
                return self.plot_single(times, temps, "Temperature (°C)", "Temperature Over Time")
            elif "humidity" in query:
                return self.plot_single(times, humidities, "Humidity (%)", "Humidity Over Time")
            elif "air" in query and "quality" in query:
                return self.plot_single(times, air_qualities, "Air Quality (µg/m³)", "Air Quality Over Time")
            elif "light" in query or "ldr" in query:
                return self.plot_single(times, light_intensities, "Light Intensity (lux)", "Light Intensity Over Time")
            else:
                return "Please specify what to graph (temperature, humidity, air quality, light intensity)"

        # Statistical queries
        if "average" in query:
            if "temperature" in query:
                return f"The average temperature is {avg_temp:.1f}°C" if avg_temp else "No valid temperature data"
            elif "humidity" in query:
                return f"The average humidity is {avg_humidity:.1f}%" if avg_humidity else "No valid humidity data"
            elif "air" in query and "quality" in query:
                return f"The average air quality (PM2.5) is {avg_air_quality:.1f} µg/m³"
            elif "light" in query or "ldr" in query:
                return f"The average light intensity is {avg_light_intensity:.1f} lux"

        # Call Gemini API for LLM-based queries
        response = self.call_gemini_api(query, avg_temp, avg_humidity, avg_air_quality, avg_light_intensity)
        return response

    def call_gemini_api(self, query, avg_temp, avg_humidity, avg_air_quality, avg_light_intensity):
        payload = {
            "query": query,
            "temperature": avg_temp or "N/A",
            "humidity": avg_humidity or "N/A",
            "air_quality": avg_air_quality or "N/A",
            "light_intensity": avg_light_intensity or "N/A"
        }

        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}"
        }

        try:
            response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
            response_data = response.json()
            return response_data.get("response", "Sorry, I couldn't get a meaningful response from Gemini.")
        except Exception as e:
            return f"Error: {str(e)}. Please try again."

    def plot_single(self, times, values, ylabel, title):
        fig, ax = plt.subplots()
        ax.plot(times, values, label=ylabel, color='tab:blue')
        ax.set_xlabel('Time')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.get_tk_widget().pack()
        canvas.draw()

        return "Graph displayed!"

    def plot_both(self, times, temps, humidities, temp_ylabel, humidity_ylabel):
        fig, ax1 = plt.subplots()

        ax1.set_xlabel('Time')
        ax1.set_ylabel(temp_ylabel, color='tab:blue')
        ax1.plot(times, temps, color='tab:blue', label="Temperature")
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        ax2 = ax1.twinx()
        ax2.set_ylabel(humidity_ylabel, color='tab:green')
        ax2.plot(times, humidities, color='tab:green', label="Humidity")
        ax2.tick_params(axis='y', labelcolor='tab:green')

        fig.tight_layout()
        fig.legend(loc='upper right')

        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.get_tk_widget().pack()
        canvas.draw()

        return "Graph displayed!"

# Create Tkinter window
root = tk.Tk()
chatbot = GeminiChatbot(root)
root.mainloop()
