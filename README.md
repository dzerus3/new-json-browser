# new-json-browser
## The project is still a WIP

A browser for common JSON info

## What is this?
This program has been created as an offline alternative for the [Cataclysm DDA item browser](https://cdda-trunk.chezzo.com/). Although the item browser is great, there are a few reasons why it might not be for you.

- You do not have access to the internet for extended periods of time
- You do not want to start up a browser just for this
- You prefer a text only interface for one reason or another
- You want information about something that is not an item (i.e. mutations)
- You want to see edits that are not part of the official release
- You want save the information for later use
- The item browser is handing out server errors instead of information
- And so on

Ideally, this project aims to replicate all the features currently in the item browser but offline and in Python.

## What currently works?
- Basic user interface
- Basic info on items, mutations, bionics, martial arts, monsters, and vehicle parts
- Translation system to turn JSON variables into human-readable strings

## What features are planned?
- Advanced info on martial arts bonuses
- Item crafting and deconstruction info
- Hotkeys

## What might be planned?
- Clickable links (I don't know how I'll implement that yet)
- Favorite items (Don't really know how this would work either)
- Better UI (I personally don't have a problem)

## Why the rewrite?
This project is a rewrite of the original Cataclysm JSON Browser, which I wrote about 9 months ago. The truth is, at that time I had little experience with code, and the last program I wrote at that point was finished more than a year ago. Most of the code was beyond salvage. I didn't really bother with writing things like classes, the program was built from the ground up with a command line interface in mind, and the method for choosing which JSON to load was convoluted and broken. I have learned quite a bit since then, and although this is not perfect, I believe I have remedied the critical problems.
