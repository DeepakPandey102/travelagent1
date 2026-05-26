# travelagent1
ITS DEMO FOR NOW





STUDENT ID :20250891                         DEEPAK PANDEY                                        JANGAN UNIVERSITY 


LETS GO THROUGH THE BACKEND::::::::



What Happens When Generate Is Clicked
0. Save User Inputs to Session State
All the form values (origin, destination, dates, budget, hotel tier, cabin class, travel theme, activities, notes) are saved into Streamlit's session_state. The image caches are also cleared so fresh photos load for the new destination.

Step 1 — ✈️ Live Flight Search
pythonfetch_flights_live(src, dst, dep_date, ret_date)
Calls the SerpAPI Google Flights engine with your origin, destination, departure date, and return date. It returns up to 4 "best" flights and 2 "other" flights, which get saved to session_state.best_flights. These are later displayed as flight cards below the form.

Step 2 — 🔍 Destination Research (AI Agent)
A Gemini 2.5 Flash AI agent (Research Agent) is created with SerpAPI as its tool. It searches the web for:

Top attractions in the destination city
Admission prices for those attractions
Tailored to your listed activities and special notes

The result (structured markdown) is saved to session_state.research_text.

Step 3 — 🏨 Hotels & Dining (AI Agent)
A second Gemini 2.5 Flash agent (Hotel Agent) searches for:

Hotels matching your selected star rating and budget tier
Restaurant recommendations in the destination city
All prices shown in your chosen currency

Saved to session_state.hotel_text.

Step 4 — 🗺️ Full Itinerary Builder (AI Agent)
A third Gemini agent (Planner Agent) takes the research + hotel output and synthesizes them into a complete travel plan. It is explicitly instructed to produce:

A cost summary table (flights, lodging, transit, food, activities, grand total) capped at your max budget
A day-by-day schedule with individual cost tags per activity
Tailored to your travel theme (solo/couple/family/group) and cabin class

Saved to session_state.itinerary_text.

Step 5 — 🌤️ Live Weather
Calls wttr.in (a free public weather API) for the destination city. Extracts:

Current temperature, description, feels-like, humidity
A 3-day forecast (high/low/description for each day)

Saved to session_state.weather_text.

After All Steps Complete

session_state.plan_ready is set to True
A success message is shown: "✅ Plan generated! Navigate to Itinerary and Weather tabs."
Streamlit reruns (st.rerun()) so the page refreshes and the flight cards appear right below the form


What You See on Other Tabs After Generation
TabWhat's Shown✈️ Plan TripLive flight cards (airline, route, price, duration, stops)🗺️ ItineraryBudget summary + day-by-day plan with costs from the Planner Agent🌤️ WeatherTemperature, humidity, conditions, packing tips, 3-day forecast🌅 DiscoverDestination photos, airport images, and POI photos from Unsplash (loaded lazily when you visit the tab)
