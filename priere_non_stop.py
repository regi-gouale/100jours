"""
This module contains the functions to get the bookings data from the Cal API
"""

import json
import os

import pandas as pd
import requests

from dotenv import load_dotenv

load_dotenv()


def get_bookings_data(debug: bool = True) -> list[dict]:
    """
    Get the bookings data from the Cal API
    """
    filtered_bookings = []
    all_bookings = []
    api_key = os.getenv("CAL_API_KEY")
    event_type_id = os.getenv("EVENT_TYPE_ID")
    if not api_key or not event_type_id:
        raise ValueError("API key or event type ID not set")

    if debug:
        with open("dump_bookings.json", encoding="utf-8") as f:
            data = json.load(f)
            all_bookings = data["bookings"]
    else:
        response = requests.get(
            f"https://api.cal.com/v1/bookings?apiKey={api_key}", timeout=10
        )
        all_bookings = response.json()["bookings"]

    for booking in all_bookings:

        if booking["status"] != "CANCELLED":
            filtered_bookings.append(booking)

    return filtered_bookings


def format_data_from_api(bookings: list[dict]) -> list[dict]:
    """
    Format the data
    """
    formatted_bookings = []
    for booking in bookings:
        for attendee in booking["attendees"]:
            formatted_booking = {
                "Creneau": booking["startTime"],
                "Fin": booking["endTime"],
                "Fuseau Horaire": attendee["timeZone"],
                "Nom Prenom": attendee["name"].strip().replace("  ", " "),
                "Email": attendee["email"],
            }
            formatted_bookings.append(formatted_booking)

    return formatted_bookings


def convert_to_dataframe(data: list[dict]) -> pd.DataFrame:
    """
    Convert the data to a pandas DataFrame
    """
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    df["Creneau"] = pd.to_datetime(df["Creneau"])
    df["Fin"] = pd.to_datetime(df["Fin"])
    df["Creneau"] = df["Creneau"].dt.tz_convert("Europe/Paris")
    df["Fin"] = df["Fin"].dt.tz_convert("Europe/Paris")
    df["Occupe"] = True

    return df


def create_csv_json_files(dataframe: pd.DataFrame, debug: bool = True) -> None:
    """
    Create a CSV file from the DataFrame
    """
    if not debug:
        dataframe.to_csv("~/apps/100jours/bookings.csv", index=False, sep=";")
        dataframe.to_json("~/apps/100jours/bookings.json", orient="records")
    else:
        dataframe.to_csv("~/apps/100jours/debug_bookings.csv", index=False, sep=";")
        dataframe.to_json("~/apps/100jours/debug_bookings.json", orient="records")


def merge_slots_and_bookings(
    slots: pd.DataFrame, bookings: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge the slots and bookings DataFrames
    """

    dataframe = pd.merge(slots, bookings, on="Creneau", how="left")
    dataframe["Occupe"] = dataframe.apply(
        lambda x: (
            x["Occupe_x"] or x["Occupe_y"]
            if pd.notna(x["Occupe_x"]) and pd.notna(x["Occupe_y"])
            else x["Occupe_x"] if pd.notna(x["Occupe_x"]) else x["Occupe_y"]
        ),
        axis=1,
    )
    dataframe.drop(columns=["Occupe_x", "Occupe_y"], inplace=True)
    return dataframe


def get_slots_from_cal_to_dataframe(debug: bool = True) -> pd.DataFrame:
    """
    Get all the slots from the Cal API
    """
    data = None
    date_range = pd.date_range(
        start="2024-08-26",
        end="2024-09-23",
        freq="90min",
        tz="Europe/Paris",
        inclusive="left",
    )
    date_range = date_range.to_frame(index=False, name="Creneau")
    date_range["Occupe"] = False

    if debug:
        with open("dump_available_slots.json", encoding="utf-8") as f:
            data = json.load(f)

    else:
        api_key = os.getenv("CAL_API_KEY")
        start_time = "2024-08-19T00:00:00Z"
        end_time = "2024-12-04T23:59:59Z"
        time_zone = "Europe/Paris"
        event_type_id = os.getenv("EVENT_TYPE_ID")
        response = requests.get(
            "https://api.cal.com/v1/slots?apiKey={api_key}&startTime={start_time}&endTime={end_time}&timeZone={time_zone}&eventTypeId={event_type_id}".format(
                api_key=api_key,
                start_time=start_time,
                end_time=end_time,
                time_zone=time_zone,
                event_type_id=event_type_id,
            ),
            timeout=10,
        )
        data = response.json()

    slots = data["slots"]
    formatted_slots = []

    for _date in slots:
        for slot in slots[_date]:
            occupyed = False
            try:
                if slot["attendees"] > 0:
                    occupyed = True
            except KeyError:
                pass
            formatted_slots.append({"Creneau": slot["time"], "Occupe": occupyed})

    formatted_slots = pd.DataFrame(formatted_slots, columns=["Creneau", "Occupe"])

    formatted_slots["Creneau"] = pd.to_datetime(formatted_slots["Creneau"], utc=True)
    formatted_slots["Creneau"] = formatted_slots["Creneau"].dt.tz_convert(
        "Europe/Paris"
    )

    formatted_slots = pd.merge(date_range, formatted_slots, on="Creneau", how="left")
    formatted_slots["Occupe"] = formatted_slots.apply(
        lambda x: x["Occupe_x"] if pd.notna(x["Occupe_x"]) else x["Occupe_y"], axis=1
    )
    formatted_slots.drop(columns=["Occupe_x", "Occupe_y"], inplace=True)

    return formatted_slots


def main():
    """
    Main function
    """
    bookings = get_bookings_data(debug=False)
    print(f"Number of booked slots: {len(bookings)}")
    formatted_bookings = format_data_from_api(bookings)
    print(f"Number of persons: {len(formatted_bookings)}")
    dt_bookings = convert_to_dataframe(formatted_bookings)
    slots = get_slots_from_cal_to_dataframe(debug=False)
    print(f"Number of slots: {len(slots)}")
    merged = merge_slots_and_bookings(slots, dt_bookings)

    create_csv_json_files(merged, debug=False)


if __name__ == "__main__":
    main()
