"""
This module contains the functions to cancel the bookings
"""

import json
import os
from time import sleep

import requests
from dotenv import load_dotenv

load_dotenv()


def get_bookings_to_cancel(debug: bool = True) -> list[dict]:
    """
    Get the bookings to cancel
    """
    bookings_to_cancel = []
    bookings = []

    if debug:
        with open('dump_bookings.json', encoding='utf-8') as f:
            data = json.load(f)
            bookings = data['bookings']
    else:
        api_key = os.getenv('CAL_API_KEY')
        response = requests.get(
            f'https://api.cal.com/v1/bookings?apiKey={api_key}',
            timeout=10)
        bookings = response.json()['bookings']

    for booking in bookings:
        if booking['status'] == 'ACCEPTED' and booking['eventTypeId'] == 974519:
            bookings_to_cancel.append(booking)

    return bookings_to_cancel


def cancel_bookings(bookings_to_cancel: list[dict]) -> None:
    """
    Cancel the bookings
    """
    cancellation_reason = '''
Bien-aimé(e),

Nous rendons grâce à Dieu pour votre engagement dans cette dynamique d'intercession en faveur de notre territoire qui assurément déclenchera une cascade de grâces, de faveur dans nos vies.

Le programme initialement prévu le 19 août est reporté à la semaine d'après : lundi 26 août 2024. Suite à quelques difficultés rencontrées dans l'organisation et la mise en place opérationnelle de ce programme, notre équipe a tout mis en oeuvre pour résoudre les dysfonctionnements. Par conséquent, un nouveau lien d'inscription a été crée, ce qui annule les inscriptions précédentes.

Nous vous demandons pardon pour la gêne occasionnée et nous vous invitons à vous réinscrire via le lien suivant : https://cal.com/iccaura/100-jours-de-prieres-non-stop

Ensemble nous allons enfanter les desseins de Dieu dans notre région.

Nous vous remercions pour compréhension 

Abondantes bénédictions

Pour le staff pastoral ICC AuRA
L'équipe de coordination
'''
    for booking in bookings_to_cancel:
        booking_id = booking['id']
        api_key = os.getenv('CAL_API_KEY')
        response = requests.delete(
            f'https://api.cal.com/v1/bookings/{booking_id}/cancel?apiKey={
                api_key}&cancellationReason={cancellation_reason}',
            timeout=10)
        print(response.json())
        sleep(3)


def main():
    """
    Cancel the bookings
    """
    bookings_to_cancel = get_bookings_to_cancel(debug=False)
    cancel_bookings(bookings_to_cancel)


if __name__ == '__main__':
    main()
