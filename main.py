import pywapi

weather = None

def main():
    global weather
    questions = ["zip code", "days", "nights",
                     "exercise (y/n)", "formal wear needed (y/n)"]

    trip = { q: input(q + "? ").lower() for q in questions }
    weather = pywapi.get_weather_from_weather_com(trip["zip code"], units="")

if __name__ == "__main__":
    main()

