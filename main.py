from fastapi import FastAPI, Query
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import pytz
import uvicorn

app = FastAPI()

@app.get("/getFlightStatus")
def get_flight_status(
    pnr: str = Query(..., min_length=6, max_length=6, pattern="^[A-Z]{6}$"),
    lastName: str = Query(..., min_length=2)
):
    local_tz = pytz.timezone("America/Chicago")
    now = datetime.now(local_tz)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://www.aa.com/reservation/viewReservationsAccess.do")
        page.fill("input[name='lastName']", lastName)
        page.fill("input[name='recordLocator']", pnr)
        page.click("button[type='submit']")
        page.wait_for_timeout(5000)

        # Placeholder response
        upcoming = [{
            "flight": "AA123",
            "from": "DFW",
            "to": "LAX",
            "scheduled": "2025-06-20T14:45:00",
            "updatedTime": "2025-06-20T15:10:00",
            "gate": "C12",
            "status": "Delayed",
            "boardingTime": "2025-06-20T14:25:00"
        }]

        missed = [{
            "flight": "AA789",
            "from": "JFK",
            "to": "DFW",
            "scheduled": "2025-06-19T11:15:00",
            "updatedTime": "2025-06-19T11:15:00",
            "gate": "B3",
            "status": "Departed",
            "boardingTime": "2025-06-19T10:45:00"
        }]

        browser.close()

        missed_filtered = [f for f in missed if datetime.fromisoformat(f["scheduled"]).astimezone(local_tz) < now]
        upcoming_filtered = [f for f in upcoming if datetime.fromisoformat(f["scheduled"]).astimezone(local_tz) >= now]

        return {
            "missedFlights": missed_filtered,
            "upcomingFlights": upcoming_filtered
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
