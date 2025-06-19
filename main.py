from fastapi import FastAPI, Query
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
import pytz
import uvicorn

app = FastAPI()

@app.get("/getFlightStatus")
def get_flight_status(
    pnr: str = Query(..., min_length=6, max_length=6, pattern="^[A-Z0-9]{6}$"),
    lastName: str = Query(..., min_length=2)
):
    local_tz = pytz.timezone("America/Chicago")
    now = datetime.now(local_tz)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://www.aa.com/reservation/viewReservationsAccess.do", timeout=30000)
            page.fill("input[name='lastName']", lastName)
            page.fill("input[name='recordLocator']", pnr)
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)

            # Optional: expand all flight segments
            expand_buttons = page.query_selector_all("button[aria-expanded='false']")
            for btn in expand_buttons:
                try:
                    btn.click()
                    page.wait_for_timeout(500)
                except:
                    continue

            # Extract passenger name
            passenger_name = page.query_selector("div[data-qa='passenger-card'] h4")
            passenger = passenger_name.inner_text().strip() if passenger_name else "Unknown"

            # Extract flight blocks
            flight_cards = page.query_selector_all("div[data-qa='flight-detail-card']")
            flights = []

            for card in flight_cards:
                try:
                    flight_number = card.query_selector("img + span")
                    flight_code = flight_number.inner_text().strip() if flight_number else "Unknown"

                    depart_code = card.query_selector("div[data-qa='flight-depart'] strong")
                    arrive_code = card.query_selector("div[data-qa='flight-arrive'] strong")

                    depart_time = card.query_selector("div[data-qa='flight-depart'] span")
                    arrive_time = card.query_selector("div[data-qa='flight-arrive'] span")

                    seat = card.query_selector("div:has-text('Seats') + div span")
                    gate = card.query_selector("div:has-text('Gate') + div")
                    terminal = card.query_selector("div:has-text('Terminal') + div")
                    aircraft = card.query_selector("div:has-text('Aircraft') + div")
                    meal = card.query_selector("div:has-text('Meal') + div")

                    flights.append({
                        "flight": flight_code,
                        "from": depart_code.inner_text().strip() if depart_code else None,
                        "to": arrive_code.inner_text().strip() if arrive_code else None,
                        "departureTime": depart_time.inner_text().strip() if depart_time else None,
                        "arrivalTime": arrive_time.inner_text().strip() if arrive_time else None,
                        "terminal": terminal.inner_text().strip() if terminal else None,
                        "gate": gate.inner_text().strip() if gate else None,
                        "seat": seat.inner_text().strip() if seat else None,
                        "aircraft": aircraft.inner_text().strip() if aircraft else None,
                        "meal": meal.inner_text().strip() if meal else None
                    })
                except Exception as e:
                    continue

            browser.close()

            return {
                "passenger": passenger,
                "flights": flights,
                "timestamp": now.isoformat()
            }

        except PlaywrightTimeoutError:
            browser.close()
            return {"error": "Timed out loading the AA reservations page"}
        except Exception as e:
            browser.close()
            return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
