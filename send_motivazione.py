"""
Bot Telegram Motivazionale — Versione GRATUITA
Legge le frasi da un Google Doc pubblico e invia quella del giorno
in un topic specifico di un gruppo Telegram privato.
"""

import os
import re
import requests
from datetime import date

TELEGRAM_BOT_TOKEN   = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL_ID  = os.environ["TELEGRAM_CHANNEL_ID"]
TELEGRAM_TOPIC_ID    = os.environ["TELEGRAM_TOPIC_ID"]
GOOGLE_DRIVE_FILE_ID = os.environ["GOOGLE_DRIVE_FILE_ID"]
START_DAY = int(os.environ.get("START_DAY", "155"))


def scarica_testo() -> str:
    url = f"https://docs.google.com/document/d/{GOOGLE_DRIVE_FILE_ID}/export?format=txt"
    risposta = requests.get(url, timeout=15)
    risposta.raise_for_status()
    return risposta.text


def estrai_frasi(testo: str) -> dict:
    frasi = {}
    pattern = re.compile(r'[Gg]iorno\s+(\d+)\s*[:.\-]\s*(.+?)(?=\n[Gg]iorno\s+\d+|\Z)', re.DOTALL)
    for match in pattern.finditer(testo):
        numero    = int(match.group(1))
        contenuto = match.group(2).strip()
        if contenuto:
            frasi[numero] = contenuto
    if not frasi:
        raise ValueError(f"Nessuna frase trovata. Prime 300 char:\n{testo[:300]}")
    return frasi


def frase_del_giorno(frasi: dict) -> tuple:
    giorno_anno = date.today().timetuple().tm_yday
    chiavi      = sorted(frasi.keys())
    totale      = len(chiavi)
    offset      = (giorno_anno - START_DAY) % totale
    numero      = chiavi[offset]
    return numero, frasi[numero]


def invia_su_telegram(testo: str) -> None:
    url     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id":           TELEGRAM_CHANNEL_ID,
        "message_thread_id": int(TELEGRAM_TOPIC_ID),
        "text":              testo,
        # Nessun parse_mode — testo plain, nessun problema con caratteri speciali
    }
    risposta = requests.post(url, json=payload, timeout=15)
    if not risposta.ok:
        print(f"Errore Telegram: {risposta.text}")
    risposta.raise_for_status()
    print("Messaggio inviato con successo!")


if __name__ == "__main__":
    print("Scarico il documento da Google Drive...")
    testo = scarica_testo()
    frasi = estrai_frasi(testo)
    print(f"Trovate {len(frasi)} frasi.")

    numero, contenuto = frase_del_giorno(frasi)
    print(f"Invio Giorno {numero}: {contenuto[:60]}...")

    invia_su_telegram(contenuto)
