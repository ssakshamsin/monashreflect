<br />
<p align="center">
  <a href="https://github.com/ssakshamsin/monashreflect">
    <img src="app/static/images/favicon.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">MonashReflect</h3>

  <p align="center">
    A practice site to learn scraping and full-stack web design !
    <br />
  </p>
</p>

## Project Details

The website is currently running at "[MonashReflect](https://www.monashreflect.com/)" for a limited time, until 3 months after original release. We were inspired by a Reddit post on the Monash subreddit, and built this entire website from scratch in 4 days. :D

The data processing can be found at "https://github.com/ssakshamsin/monash-units-scraper"

# Getting Started

To get a local copy up and running follow these steps.

## Instructions

1. You must have SQLite installed, if you are on Windows you can install it from [here](https://www.sqlite.org/download.html)"
2. Open a command prompt in the root directory:
  3. pip install -r requirements.txt
  4. venv\Scripts\activate
  5. flask db init
  6. flask db migrate -m "i"
  7. flask db upgrade
  8. python seed_database.py
  9. flask run
   You should have a local version of the website running on http://127.0.0.1:5000/ !

# Future Plans

We don't have any plans for this project, if you wanna discuss anything just contact us!
