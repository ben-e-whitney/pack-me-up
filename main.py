import pywapi
import sys

class Item:
    pass

class Clothing(Item):
    pass


if __name__ == "__main__":
    questions = ["zip code", "days", "nights",
                     "exercise (y/n)", "formal wear needed (y/n)"]

    trip = { q: input(q + "? ").lower() for q in questions }
    
    

