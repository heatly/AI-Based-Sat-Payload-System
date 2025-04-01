import tkinter as tk
from tkinter import ttk, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import numpy as np
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq  # Placeholder; adjust for xAI’s Grok API

# Location of the JSON file
JSON_FILE_PATH = "sensor_data.json"

# Placeholder Grok API credentials (replace with actual values from xAI)
GROK_API_KEY = "xai-1LesDvLzzKkQoW4mbF1p60psiPndxJWAjTtAVBzLgSmwGKZoiq85wAaeseDAjVaqJbCyCa9rAgpGpZuL"  # Replace with your real API key
GROK_MODEL = "grok"  # Replace with actual Grok model name if specified by xAI

class GrokChatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("Grok 3 Chatbot - Multi-Sensor Analysis")
        self.root.geometry("800x600")

        # Load data from JSON file
        self.data = self.load_sensor_data()

        # Initialize Grok LLM with LangChain (with fallback if API fails)
        try:
            self.llm = ChatGroq(
                api_key=GROK_API_KEY,
                model=GROK_MODEL,
                temperature=0.7,
            )
            self.llm_available = True
        except Exception as e:
            self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
            self.chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
            self.chat_display.insert(tk.END, f"Warning: Could not connect to Grok API ({str(e)}). Using fallback mode.\n")
            self.llm_available = False

        # Chat display (moved here to ensure it’s defined if LLM fails)
        if not hasattr(self, 'chat_display'):
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
        self.chat_display.insert(tk.END, "Grok 3: Hello! I'm Grok 3, powered by xAI. I can analyze temperature, humidity, air quality, and light intensity data from the JSON file (2025-03-20 and 2025-04-01). Ask me about climate, crops, air, light, or request graphs!\n\n")

    def process_input(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        self.chat_display.insert(tk.END, f"You: {user_input}\n")
        self.input_field.delete(0, tk.END)

        response = self.process_query(user_input)
        self.chat_display.insert(tk.END, f"Grok 3: {response}\n\n")
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

        # LLM-based responses
        if self.llm_available:
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"You are Grok 3, an AI assistant by xAI. Use this sensor data (2025-03-20 and 2025-04-01): Temperature={avg_temp or 'N/A'}°C, Humidity={avg_humidity or 'N/A'}%, Air Quality (PM2.5)={avg_air_quality:.1f} µg/m³, Light Intensity={avg_light_intensity:.1f} lux. Handle missing data gracefully and provide detailed responses."),
                ("human", "{query}")
            ])
            chain = prompt | self.llm
            try:
                if "climatic" in query or "climate" in query or "condition" in query:
                    return chain.invoke({"query": f"Describe the climatic conditions for temperature {avg_temp or 'N/A'}°C, humidity {avg_humidity or 'N/A'}%, air quality {avg_air_quality:.1f} µg/m³, and light intensity {avg_light_intensity:.1f} lux."}).content
                elif "crop" in query or "growth" in query or "grow" in query:
                    return chain.invoke({"query": f"What crops can grow well with temperature {avg_temp or 'N/A'}°C, humidity {avg_humidity or 'N/A'}%, air quality {avg_air_quality:.1f} µg/m³, and light intensity {avg_light_intensity:.1f} lux? Include suitability details."}).content
                elif "recommend" in query or "remmodate" in query:
                    return chain.invoke({"query": f"Provide recommendations for managing a farm with temperature {avg_temp or 'N/A'}°C, humidity {avg_humidity or 'N/A'}%, air quality {avg_air_quality:.1f} µg/m³, and light intensity {avg_light_intensity:.1f} lux."}).content
                elif "air" in query and "quality" in query:
                    return chain.invoke({"query": f"Analyze air quality with PM2.5 at {avg_air_quality:.1f} µg/m³. Is it safe? What does it mean?"}).content
                elif "light" in query or "ldr" in query or "bright" in query:
                    return chain.invoke({"query": f"Analyze light intensity at {avg_light_intensity:.1f} lux. Is it suitable for plants? What does it mean?"}).content
                else:
                    return chain.invoke({"query": query}).content
            except Exception as e:
                return f"Error: Could not process with Grok API ({str(e)}). Using fallback:\n{self.fallback_response(query, avg_temp, avg_humidity, avg_air_quality, avg_light_intensity)}"
        else:
            return self.fallback_response(query, avg_temp, avg_humidity, avg_air_quality, avg_light_intensity)

    def fallback_response(self, query, avg_temp, avg_humidity, avg_air_quality, avg_light_intensity):
        query = query.lower()
        if "climatic" in query or "climate" in query or "condition" in query:
            return (f"Based on the sensor data (2025-03-20 and 2025-04-01):\n"
                    f"- Temperature: {avg_temp:.1f}°C\n"
                    f"- Humidity: {avg_humidity:.1f}%\n"
                    f"- Air Quality (PM2.5): {avg_air_quality:.1f} µg/m³\n"
                    f"- Light Intensity: {avg_light_intensity:.1f} lux\n"
                    f"This suggests a warm, moderately humid environment with variable air quality and bright light.")
        elif "crop" in query or "growth" in query or "grow" in query:
            return (f"Crop suitability (Temp: {avg_temp:.1f}°C, Humidity: {avg_humidity:.1f}%, Air: {avg_air_quality:.1f} µg/m³, Light: {avg_light_intensity:.1f} lux):\n"
                    f"- **Rice**: Needs 25-35°C, 70-80% humidity, good air (<50 µg/m³), 1000-2000 lux. Possible with irrigation and cleaner air.\n"
                    f"- **Maize**: 25-33°C, 50-75% humidity, tolerates moderate air, 1000-2000 lux. Suitable.\n"
                    f"- **Cassava**: 25-35°C, 60-80% humidity, moderate air OK, 800-1500 lux. Excellent.\n"
                    f"- **Mango**: 24-35°C, 50-70% humidity, prefers cleaner air, 1000-2000 lux. Suitable if air improves.")
        elif "recommend" in query or "remmodate" in query:
            return (f"Recommendations (Temp: {avg_temp:.1f}°C, Humidity: {avg_humidity:.1f}%, Air: {avg_air_quality:.1f} µg/m³, Light: {avg_light_intensity:.1f} lux):\n"
                    f"- Use shade nets for heat.\n"
                    f"- Irrigate if humidity drops below 60%.\n"
                    f"- Improve air quality if >50 µg/m³ (ventilation/filters).\n"
                    f"- Light is sufficient; adjust for shade-loving plants.")
        elif "air" in query and "quality" in query:
            safety = "safe" if avg_air_quality <= 50 else "potentially unhealthy"
            return f"Air quality (PM2.5) is {avg_air_quality:.1f} µg/m³. This is {safety}. Levels above 50 µg/m³ may affect sensitive crops or health."
        elif "light" in query or "ldr" in query or "bright" in query:
            suitability = "suitable for most plants" if 500 <= avg_light_intensity <= 2000 else "may need adjustment"
            return f"Light intensity is {avg_light_intensity:.1f} lux. This is {suitability}. Most crops need 500-2000 lux."
        else:
            return "I can help with graphs, stats, climate, crops, air quality, light, or recommendations. What would you like?"

    def plot_single(self, times, values, ylabel, title):
        self.clear_graph()
        fig, ax = plt.subplots(figsize=(6, 4))
        # Replace None with NaN for plotting
        plot_values = [v if v is not None else np.nan for v in values]
        ax.plot(times, plot_values, 'g-' if "Humidity" in ylabel else 'r-' if "Air" in ylabel else 'y-' if "Light" in ylabel else 'b-', label=ylabel)
        ax.set_title(title)
        ax.set_xlabel("Time")
        ax.set_ylabel(ylabel)
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return f"{title} graph generated!"

    def plot_both(self, times, vals1, vals2, ylabel1, ylabel2):
        self.clear_graph()
        fig, ax1 = plt.subplots(figsize=(6, 4))
        plot_vals1 = [v if v is not None else np.nan for v in vals1]
        plot_vals2 = [v if v is not None else np.nan for v in vals2]
        ax1.plot(times, plot_vals1, 'b-', label=ylabel1)
        ax1.set_xlabel("Time")
        ax1.set_ylabel(ylabel1, color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        ax2 = ax1.twinx()
        ax2.plot(times, plot_vals2, 'g-', label=ylabel2)
        ax2.set_ylabel(ylabel2, color='g')
        ax2.tick_params(axis='y', labelcolor='g')
        ax1.set_title(f"{ylabel1} and {ylabel2} Over Time")
        plt.xticks(rotation=45)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return f"{ylabel1} and {ylabel2} graph generated!"

    def clear_graph(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GrokChatbot(root)
    root.mainloop()
