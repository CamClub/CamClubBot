
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update
)
from telegram.ext import (
    ApplicationBuilder,
    InlineQueryHandler,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from uuid import uuid4
import logging
import csv
import io
from datetime import datetime, timedelta
import random
import string
import json
import os

# === CONFIG ===
logging.basicConfig(level=logging.INFO)
ADMIN_ID = 7890437747
ORDINI_FILE = "ordini.json"

user_state = {}
orders = []
ordine_to_msgid = {}   # ordine_id: {"ragazza": (chat_id, msg_id), "admin": (chat_id, msg_id)}
order_id_counter = [1] # autoincrement solo per admin

# === RAGAZZE (mantiene dati come li hai forniti) ===
ragazze = {"Sarapinky": {
            "nome": "SaraPinky",
            "id_telegram": 7448228315,  # Metti l'ID reale
            "descrizione": "💎 La tua insospettabile vicina di casa.",
            "immagine": "https://i.postimg.cc/VvWmWdT2/Whats-App-Image-2025-07-24-at-15-17-33.jpg",
            "servizi": {
                "cam": [("🕒 3 minuti", 15), ("🕒 6 minuti", 25), ("🕒 10 minuti", 40), ("🕒 15 minuti", 55), ("🕒 20 minuti", 65),("🕒 30minuti", 90)],
                "sexchat": [("🕒 10 minuti", 30), ("🕒 15 minuti", 40), ("🕒 20 minuti", 50), ("🕒 45 minuti", 75), ("🕒 30 minuti", 70)],
                "video personalizzati": [("🎬 5 minuti ", 50), ("🎬 10 minuti", 90), ("🎬 15 minuti", 120)]
            },
            "extra": [("➕Scelta outfit", 5), ("➕Uso dildo", 5), ("➕Link Control al min",1)],
            "pagamenti": {
                "PayPal": "https://paypal.me/sarapinky",
                "Revolut": "https://revolut.me/sarapinky",
                "Satispay": "https://satispay.com/pagaragazza"
            }
        },
        "Miss_Pamy": {
            "nome": "Miss_Pamy",
            "id_telegram": 12345654, # Metti l'ID reale
            "descrizione": "💎 Sensuale e coinvolgente. Cam, chat e video esclusivi.",
            "immagine": "https://i.postimg.cc/ydCQPpZK/pamela.jpg",
            "servizi": {
                "cam": [("5 minuti", 15), ("10 minuti", 30), ("15 minuti", 45), ("20 minuti", 60), ("30 minuti", 75)],
                "sexchat": [("15 minuti", 35), ("30 minuti", 65), ("45 minuti", 90), ("60 minuti", 120), ("90 minuti", 160)],
                "video personalizzati": [("3 minuti", 25), ("5 minuti", 45), ("8 minuti", 70), ("10 minuti", 80), ("15 minuti", 110)]
            },
            "extra": [("Scelta outfit", 5), ("Uso plug", 10), ("Dirty talk", 6), ("Musica a scelta", 3), ("Piedi in primo piano", 6)],
            "pagamenti": {
                "PayPal": "https://paypal.me/hilarysgk",
                "Revolut": "https://revolut.me/hilary283",
                "Satispay": "https://satispay.com/hilary"
            }
        },
        "Hilary283": {
            "nome": "Hilary283",
            "id_telegram": 868210471, # Metti l'ID reale
            "descrizione": "💎 Sensuale e coinvolgente. Cam, chat e video esclusivi.",
            "immagine": "https://i.postimg.cc/SNWJgfHY/Whats-App-Image-2025-07-24-at-15-17-33-1.jpg",
            "servizi": {
                "cam": [("5 minuti", 15), ("10 minuti", 30), ("15 minuti", 45), ("20 minuti", 60), ("30 minuti", 75)],
                "sexchat": [("15 minuti", 35), ("30 minuti", 65), ("45 minuti", 90), ("60 minuti", 120), ("90 minuti", 160)],
                "video personalizzati": [("3 minuti", 25), ("5 minuti", 45), ("8 minuti", 70), ("10 minuti", 80), ("15 minuti", 110)]
            },
            "extra": [("Scelta outfit", 5), ("Uso plug", 10), ("Dirty talk", 6), ("Musica a scelta", 3), ("Piedi in primo piano", 6)],
            "pagamenti": {
                "PayPal": "https://paypal.me/hilarysgk",
                "Revolut": "https://revolut.me/hilary283",
                "Satispay": "https://satispay.com/hilary"
            }
        },
        "AltaClasse": {
            "nome": "AltaClasse",
            "id_telegram": 162776, # Metti l'ID reale
            "descrizione": "💎 Sensuale e coinvolgente. Cam, chat e video esclusivi.",
            "immagine": "https://i.postimg.cc/rFsJS2PW/camclub-altaclasse.jpg",
            "servizi": {
                "cam": [("5 minuti", 15), ("10 minuti", 30), ("15 minuti", 45), ("20 minuti", 60), ("30 minuti", 75)],
                "sexchat": [("15 minuti", 35), ("30 minuti", 65), ("45 minuti", 90), ("60 minuti", 120), ("90 minuti", 160)],
                "video personalizzati": [("3 minuti", 25), ("5 minuti", 45), ("8 minuti", 70), ("10 minuti", 80), ("15 minuti", 110)]
            },
            "extra": [("Scelta outfit", 5), ("Uso plug", 10), ("Dirty talk", 6), ("Musica a scelta", 3), ("Piedi in primo piano", 6)],
            "pagamenti": {
                "PayPal": "https://paypal.me/hilarysgk",
                "Revolut": "https://revolut.me/hilary283",
                "Satispay": "https://satispay.com/hilary"
            }
        },
        "DeaDiamante": {
            "nome": "DeaDiamante",
            "id_telegram": 162534937, # Metti l'ID reale
            "descrizione": "💎 Sensuale e coinvolgente. Cam, chat e video esclusivi.",
            "immagine": "https://i.postimg.cc/JnKNkp3P/camclub-deadiamante.jpg",
            "servizi": {
                "cam": [("5 minuti", 15), ("10 minuti", 30), ("15 minuti", 45), ("20 minuti", 60), ("30 minuti", 75)],
                "sexchat": [("15 minuti", 35), ("30 minuti", 65), ("45 minuti", 90), ("60 minuti", 120), ("90 minuti", 160)],
                "video personalizzati": [("3 minuti", 25), ("5 minuti", 45), ("8 minuti", 70), ("10 minuti", 80), ("15 minuti", 110)]
            },
            "extra": [("Scelta outfit", 5), ("Uso plug", 10), ("Dirty talk", 6), ("Musica a scelta", 3), ("Piedi in primo piano", 6)],
            "pagamenti": {
                "PayPal": "https://paypal.me/hilarysgk",
                "Revolut": "https://revolut.me/hilary283",
                "Satispay": "https://satispay.com/hilary"
            }
        },
        "SexyIlaria": {
            "nome": "SexyIlaria",
            "id_telegram": 1657856, # Metti l'ID reale
            "descrizione": "💎 Sensuale e coinvolgente. Cam, chat e video esclusivi.",
            "immagine": "https://i.postimg.cc/Qdkqpg39/sexyilaria.jpg",
            "servizi": {
                "cam": [("5 minuti", 15), ("10 minuti", 30), ("15 minuti", 45), ("20 minuti", 60), ("30 minuti", 75)],
                "sexchat": [("15 minuti", 35), ("30 minuti", 65), ("45 minuti", 90), ("60 minuti", 120), ("90 minuti", 160)],
                "video personalizzati": [("🎬 3 minuti", 25), ("🎬 5 minuti", 45), ("🎬 8 minuti", 70), ("🎬 10 minuti", 80), ("🎬 15 minuti", 110)]
            },
            "extra": [("Scelta outfit", 5), ("Uso plug", 10), ("Dirty talk", 6), ("Musica a scelta", 3), ("Piedi in primo piano", 6)],
            "pagamenti": {
                "PayPal": "https://paypal.me/hilarysgk",
                "Revolut": "https://revolut.me/hilary283",
                "Satispay": "https://satispay.com/hilary"
            }
        },
        "JennyDream": {
            "nome": "JennyDream",
            "id_telegram": 1625306376, # Metti l'ID reale (Confermato)
            "descrizione": "💎 Sono una giovane bellezza italiana, con due grandi occhi grigi che ti fotteranno il cervello.",
            "immagine": "https://i.postimg.cc/MKYc59nS/IMG-2590.jpg",
            "servizi": {
                "cam": [("5 minuti", 15), ("10 minuti", 30), ("15 minuti", 45), ("20 minuti", 60), ("30 minuti", 75)],
                "sexchat": [("15 minuti", 35), ("30 minuti", 65), ("45 minuti", 90), ("60 minuti", 120), ("90 minuti", 160)],
                "video personalizzati": [("🎬 3 minuti", 25), ("🎬 5 minuti", 45), ("🎬 8 minuti", 70), ("🎬 10 minuti", 80), ("🎬 15 minuti", 110)]
            },
            "extra": [("Scelta outfit", 5), ("Uso plug", 10), ("Dirty talk", 6), ("Musica a scelta", 3), ("Piedi in primo piano", 6)],
            "pagamenti": {
                "PayPal": "https://paypal.me/hilarysgk",
                "Revolut": "https://revolut.me/hilary283",
                "Satispay": "https://satispay.com/hilary"
            }
        },
        "Nicole98": {
            "nome": "Nicole98",
            "id_telegram": 5939504704, # Metti l'ID reale (Confermato)
            "descrizione": "💎 Sensuale e coinvolgente. Cam, chat e video esclusivi.",
            "immagine": "https://i.postimg.cc/hGNhvw59/IMG-2435.jpg",
            "servizi": {
                "cam": [("🕒 5 minuti", 20), ("🕒 10 minuti", 30), ("🕒 15 minuti", 50), ],
                "sexchat": [("🕒 10 minuti", 25), ("🕒 20 minuti", 50)],
                "video personalizzati": [("🎬 A partire da", 50), ("🎬 Gloryhole", 100), ("🎬 Gangbang", 250)],
            },
            "extra": [("➕Scelta outfit - completo", 10), ("➕Autoreggenti e tacchi", 5), ("➕Ahegao", 5), ("➕Footjob Dildo", 5), ("➕Strip tease", 5)],
            "pagamenti": {
                "PayPal": "https://paypal.me/nicolefnc",

            }
        },
        "Felix": {
            "nome": "Felix",
            "id_telegram": 161306376, # Metti l'ID reale
            "descrizione": "💎 Sensuale e coinvolgente. Cam, chat e video esclusivi.",
            "immagine": "https://i.postimg.cc/RFcCF0fB/Immagine.png",
            "servizi": {
                "cam": [("5 minuti", 15), ("10 minuti", 30), ("15 minuti", 45), ("20 minuti", 60), ("30 minuti", 75)],
                "sexchat": [("15 minuti", 35), ("30 minuti", 65), ("45 minuti", 90), ("60 minuti", 120), ("90 minuti", 160)],
                "video personalizzati": [("3 minuti", 25), ("5 minuti", 45), ("8 minuti", 70), ("10 minuti", 80), ("15 minuti", 110)]
            },
            "extra": [("Scelta outfit", 5), ("Uso plug", 10), ("Dirty talk", 6), ("Musica a scelta", 3), ("Piedi in primo piano", 6)],
            "pagamenti": {
                "PayPal": "https://paypal.me/hilarysgk",
                "Revolut": "https://revolut.me/hilary283",
                "Satispay": "https://satispay.com/hilary"
            }
        },
        "DeaEcstasy": {
            "nome": "DeaEcstasy",
            "id_telegram": 162536376, # Metti l'ID reale
            "descrizione": "💎 Sensuale e coinvolgente. Cam, chat e video esclusivi.",
            "immagine": "https://i.postimg.cc/vHPYDk1c/IMG-2513.jpg",
            "servizi": {
                "cam": [("5 minuti", 15), ("10 minuti", 30), ("15 minuti", 45), ("20 minuti", 60), ("30 minuti", 75)],
                "sexchat": [("15 minuti", 35), ("30 minuti", 65), ("45 minuti", 90), ("60 minuti", 120), ("90 minuti", 160)],
                "video personalizzati": [("3 minuti", 25), ("5 minuti", 45), ("8 minuti", 70), ("10 minuti", 80), ("15 minuti", 110)]
            },
            "extra": [("Scelta outfit", 5), ("Uso plug", 10), ("Dirty talk", 6), ("Musica a scelta", 3), ("Piedi in primo piano", 6)],
            "pagamenti": {
                "PayPal": "https://paypal.me/hilarysgk",
                "Revolut": "https://revolut.me/hilary283",
                "Satispay": "https://satispay.com/hilary"
            }
        },
        "Lili": {
            "nome": "Lili",
            "id_telegram": 162536776, # Metti l'ID reale
            "descrizione": "💎 Sensuale e coinvolgente. Cam, chat e video esclusivi.",
            "immagine": "https://i.postimg.cc/4yLDNC8G/IMG-2546.jpg",
            "servizi": {
                "cam": [("5 minuti", 15), ("10 minuti", 30), ("15 minuti", 45), ("20 minuti", 60), ("30 minuti", 75)],
                "sexchat": [("15 minuti", 35), ("30 minuti", 65), ("45 minuti", 90), ("60 minuti", 120), ("90 minuti", 160)],
                "video personalizzati": [("3 minuti", 25), ("5 minuti", 45), ("8 minuti", 70), ("10 minuti", 80), ("15 minuti", 110)]
            },
            "extra": [("Scelta outfit", 5), ("Uso plug", 10), ("Dirty talk", 6), ("Musica a scelta", 3), ("Piedi in primo piano", 6)],
            "pagamenti": {
                "PayPal": "https://paypal.me/hilarysgk",
                "Revolut": "https://revolut.me/hilary283",
                "Satispay": "https://satispay.com/hilary"
            }
        },
        "CoppiaBollente7": {
            "nome": "CoppiaBollente7",
            "id_telegram": 16253076, # Metti l'ID reale
            "descrizione": "💎 Sensuale e coinvolgente. Cam, chat e video esclusivi.",
            "immagine": "https://i.postimg.cc/wTJKYrhC/IMG-2581.jpg",
            "servizi": {
                "cam": [("5 minuti", 15), ("10 minuti", 30), ("15 minuti", 45), ("20 minuti", 60), ("30 minuti", 75)],
                "sexchat": [("15 minuti", 35), ("30 minuti", 65), ("45 minuti", 90), ("60 minuti", 120), ("90 minuti", 160)],
                "video personalizzati": [("3 minuti", 25), ("5 minuti", 45), ("8 minuti", 70), ("10 minuti", 80), ("15 minuti", 110)]
            },
            "extra": [("Scelta outfit", 5), ("Uso plug", 10), ("Dirty talk", 6), ("Musica a scelta", 3), ("Piedi in primo piano", 6)],
            "pagamenti": {
                "PayPal": "https://paypal.me/hilarysgk",
                "Revolut": "https://revolut.me/hilary283",
                "Satispay": "https://satispay.com/hilary"
            }
        },
        # Altre ragazze...
    

}

# === ORDINI PERSISTENTI ===

def genera_codice_ordine():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def salva_ordini():
    with open(ORDINI_FILE, "w") as f:
        json.dump({
            "orders": orders,
            "ordine_to_msgid": ordine_to_msgid,
            "order_id_counter": order_id_counter[0]
        }, f)

def carica_ordini():
    if not os.path.isfile(ORDINI_FILE):
        return
    with open(ORDINI_FILE, "r") as f:
        data = json.load(f)
        global orders, ordine_to_msgid
        orders.clear()
        orders.extend(data.get("orders", []))
        ordine_to_msgid.clear()
        ordine_to_msgid.update(data.get("ordine_to_msgid", {}))
        order_id_counter[0] = data.get("order_id_counter", 1)

carica_ordini()

# === RENDER FUNZIONI ===

def render_ordine_utente(ordine, stato_override=None):
    extras = ordine.get("extra_descr", "-")
    if isinstance(extras, list):
        extras = ", ".join([f"{n} (+{p}€)" for n, p in extras]) if extras else "-"
    stato_map = {
        "confermato": "✅ <b>PAGATO/CONFERMATO</b>",
        "non_confermato": "❌ <b>NON PAGATO/DA CONFERMARE</b>"
    }
    stato = stato_override or ordine.get("stato", "non_confermato")
    return (
        f"<b>Riepilogo Ordine <code>{ordine['ordine_codice']}</code></b>\n"
        f"───────────────\n"
        f"👩 Ragazza: <b>{ordine['ragazza_nome']}</b>\n"
        f"👤 Cliente: @{ordine.get('utente_username','Utente Telegram')} (ID: <code>{ordine.get('utente_id','')}</code>)\n"
        f"🛒 Servizio: <b>{ordine['servizio'].upper()}</b>\n"
        f"⏱️ Durata: <b>{ordine['durata']}</b>\n"
        f"💶 Prezzo base: <b>{ordine['prezzo']}€</b>\n"
        f"➕ Extra: <b>{extras}</b>\n"
        f"💳 Metodo: <b>{ordine['metodo']}</b>\n"
        f"💰 <b>TOTALE: {ordine['totale']}€</b>\n"
        f"───────────────\n"
        f"🗓️ Data: {ordine['data']}\n"
        f"📦 Stato: {stato_map.get(stato, stato)}"
    )

def render_ordine_admin(ordine, stato_override=None):
    extras = ordine.get("extra_descr", "-")
    if isinstance(extras, list):
        extras = ", ".join([f"{n} (+{p}€)" for n, p in extras]) if extras else "-"
    stato_map = {
        "confermato": "✅ <b>PAGATO/CONFERMATO</b>",
        "non_confermato": "❌ <b>NON PAGATO/DA CONFERMARE</b>"
    }
    stato = stato_override or ordine.get("stato", "non_confermato")
    return (
        f"<b>Riepilogo Ordine [#{ordine['ordine_id']}] <code>{ordine['ordine_codice']}</code></b>\n"
        f"───────────────\n"
        f"👩 Ragazza: <b>{ordine['ragazza_nome']}</b>\n"
        f"👤 Cliente: @{ordine.get('utente_username','Utente Telegram')} (ID: <code>{ordine.get('utente_id','')}</code>)\n"
        f"🛒 Servizio: <b>{ordine['servizio'].upper()}</b>\n"
        f"⏱️ Durata: <b>{ordine['durata']}</b>\n"
        f"💶 Prezzo base: <b>{ordine['prezzo']}€</b>\n"
        f"➕ Extra: <b>{extras}</b>\n"
        f"💳 Metodo: <b>{ordine['metodo']}</b>\n"
        f"💰 <b>TOTALE: {ordine['totale']}€</b>\n"
        f"───────────────\n"
        f"🗓️ Data: {ordine['data']}\n"
        f"📦 Stato: {stato_map.get(stato, stato)}"
    )

def calc_totale(prezzo, extra):
    totale = prezzo
    if extra:
        for e in extra:
            totale += e[1]
    return totale

# === HANDLERS BOT ===

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.lower()
    results = []
    for username, info in ragazze.items():
        if not query or query in username.lower() or query in info['nome'].lower():
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=info["nome"],
                    description=info["descrizione"],
                    thumbnail_url=info["immagine"],
                    input_message_content=InputTextMessageContent(
                        f"👩 {info['nome']}\n{info['descrizione']}\nPremi il tasto sotto per i servizi.",
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📂 Visualizza", callback_data=f"visualizza:{username}")]
                    ])
                )
            )
    await update.inline_query.answer(results, cache_time=3)

async def visualizza_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        username = query.data.split(":")[1]
        info = ragazze[username]
    except Exception:
        await query.edit_message_text("❌ Ragazza non trovata.")
        return
    tastiera = [
        [InlineKeyboardButton("📸 CAM", callback_data=f"servizio:{username}:cam")],
        [InlineKeyboardButton("💬 SEXCHAT", callback_data=f"servizio:{username}:sexchat")],
        [InlineKeyboardButton("🎥 VIDEO", callback_data=f"servizio:{username}:video personalizzati")],
        [InlineKeyboardButton("🔙 Torna al menù", callback_data=f"visualizza:{username}")]
    ]
    await query.edit_message_text(
        f"👩 {info['nome']}\n{info['descrizione']}\n\nScegli un servizio:",
        reply_markup=InlineKeyboardMarkup(tastiera)
    )

async def servizio_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        _, username, servizio = query.data.split(":")
        info = ragazze[username]
        opzioni = info["servizi"][servizio]
    except Exception:
        await query.edit_message_text("❌ Servizio non disponibile.")
        return
    tastiera = [
        [InlineKeyboardButton(f"{durata} – {prezzo}€", callback_data=f"acquista:{username}:{servizio}:{durata}:{prezzo}")]
        for durata, prezzo in opzioni
    ]
    tastiera.append([InlineKeyboardButton("🔙 Torna al menù", callback_data=f"visualizza:{username}")])
    await query.edit_message_text(
        f"💎 {info['nome']}\nServizio: {servizio.upper()}\nScegli durata e prezzo:",
        reply_markup=InlineKeyboardMarkup(tastiera)
    )

async def acquisto_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        _, username, servizio, durata, prezzo = query.data.split(":")
        prezzo = int(prezzo)
        stato = user_state.get(query.from_user.id, {})
        stato.update({"username": username, "servizio": servizio, "durata": durata, "prezzo": prezzo, "extra": []})
        user_state[query.from_user.id] = stato
    except Exception:
        await query.edit_message_text("❌ Errore nei dati di acquisto.")
        return
    tastiera = [
        [InlineKeyboardButton("➕ Aggiungi extra", callback_data=f"extra:{username}:{servizio}")],
        [InlineKeyboardButton("💳 Vai al pagamento", callback_data=f"pagamenti:{username}")]
    ]
    tastiera.append([InlineKeyboardButton("🔙 Torna al menù", callback_data=f"visualizza:{username}")])
    await query.edit_message_text(
        f"✅ Hai scelto: {servizio.upper()} – {durata} – {prezzo}€\nVuoi aggiungere extra?",
        reply_markup=InlineKeyboardMarkup(tastiera)
    )

async def extra_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    if len(parts) == 3:
        _, username, servizio = parts
    elif len(parts) == 4:
        _, username, servizio, _ = parts
    else:
        await query.edit_message_text("❌ Errore parametri extra.")
        return
    try:
        info = ragazze[username]
        extra_list = info.get("extra", [])
        stato = user_state.get(query.from_user.id, {})
        if "extra" not in stato:
            stato["extra"] = []
        selected_idx = stato.get("extra", [])
    except Exception as e:
        await query.edit_message_text(f"❌ Errore nel caricamento extra.\n{e}")
        return
    tastiera = []
    for idx, (nome, prezzo) in enumerate(extra_list):
        selected = "✅ " if idx in selected_idx else ""
        tastiera.append([InlineKeyboardButton(
            f"{selected}{nome} +{prezzo}€",
            callback_data=f"toggleextra:{username}:{servizio}:{idx}"
        )])
    tastiera.append([InlineKeyboardButton("✅ Conferma extra", callback_data=f"pagamenti:{username}")])
    tastiera.append([InlineKeyboardButton("🔙 Torna al menù", callback_data=f"visualizza:{username}")])
    if selected_idx:
        extra_strings = [f"• {extra_list[i][0]} +{extra_list[i][1]}€" for i in selected_idx]
        extrasel = "\n\nExtra selezionati:\n" + "\n".join(extra_strings)
    else:
        extrasel = ""
    await query.edit_message_text(
        f"➕ Seleziona gli extra da aggiungere (puoi selezionarne più di uno):{extrasel}",
        reply_markup=InlineKeyboardMarkup(tastiera)
    )

async def toggleextra_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        _, username, servizio, idx = query.data.split(":")
        idx = int(idx)
        stato = user_state.get(query.from_user.id, {})
        extra_corrente = stato.get("extra", [])
        if idx in extra_corrente:
            extra_corrente.remove(idx)
        else:
            extra_corrente.append(idx)
        stato["extra"] = extra_corrente
        user_state[query.from_user.id] = stato
    except Exception as e:
        await query.edit_message_text(f"❌ Errore toggle extra: {e}")
        return
    await extra_callback(update, context)

async def pagamenti_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    stato = user_state.get(query.from_user.id, {})
    username = stato.get("username")
    info = ragazze[username]
    pagamenti = info.get("pagamenti", {})
    tastiera = [
        [InlineKeyboardButton(
            metodo,
            callback_data=f"pagalink:{username}:{metodo}"
        )] for metodo in pagamenti if pagamenti[metodo]
    ]
    tastiera.append([InlineKeyboardButton("🔙 Torna al menù", callback_data=f"visualizza:{username}")])
    await query.edit_message_text(
        "Scegli il metodo di pagamento:",
        reply_markup=InlineKeyboardMarkup(tastiera)
    )

async def pagalink_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        _, username, metodo = query.data.split(":")
        stato = user_state.get(query.from_user.id, {})
        info = ragazze[username]
        pagamenti = info["pagamenti"]
        link_pagamento = pagamenti[metodo]
        servizio = stato.get("servizio", "")
        durata = stato.get("durata", "")
        prezzo = stato.get("prezzo", 0)
        extra_idx = stato.get("extra", [])
        extra = [info["extra"][i] for i in extra_idx]
        extra_descr = [info["extra"][i] for i in extra_idx]
        totale = calc_totale(prezzo, extra)
        utente = update.effective_user.username or ""
        utente_id = update.effective_user.id
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ordine_id = order_id_counter[0]
        order_id_counter[0] += 1
        ordine_codice = genera_codice_ordine()
        ordine = {
            "ordine_id": ordine_id,      # solo admin
            "ordine_codice": ordine_codice, # tutti
            "ragazza": username,
            "ragazza_nome": info["nome"],
            "ragazza_id_telegram": info.get("id_telegram", None),
            "utente": utente or str(utente_id),
            "utente_username": utente,
            "utente_id": utente_id,
            "servizio": servizio,
            "durata": durata,
            "prezzo": prezzo,
            "extra_descr": extra_descr,
            "metodo": metodo,
            "totale": totale,
            "stato": "non_confermato",
            "data": data
        }
        orders.append(ordine)
        ordine_to_msgid[ordine_id] = {}
        salva_ordini()
    except Exception as e:
        await query.edit_message_text(f"❌ Errore nel riepilogo finale. {e}")
        return

    testo_cliente = render_ordine_utente(ordine)
    pay_button = InlineKeyboardButton(
        f"💸 Paga ora con {metodo}", url=link_pagamento
    )
    await query.edit_message_text(
        testo_cliente + "\n\n<b>➡️ Premi il bottone qui sotto per pagare!</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [pay_button]
        ])
    )

    # Notifica ragazza (con bottoni conferma/nonconferma)
    ragazza_id = info.get("id_telegram")
    testo_ragazza = render_ordine_utente(ordine)
    if ragazza_id:
        try:
            msg_r = await context.bot.send_photo(
                chat_id=ragazza_id,
                photo=info["immagine"],
                caption=testo_ragazza,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ PAGATO", callback_data=f"setstatus:{ordine_id}:confermato"),
                        InlineKeyboardButton("❌ NON PAGATO", callback_data=f"setstatus:{ordine_id}:non_confermato")
                    ]
                ])
            )
            ordine_to_msgid[ordine_id]["ragazza"] = (ragazza_id, msg_r.message_id)
            salva_ordini()
        except Exception:
            pass

    # Notifica admin (con bottoni)
    testo_admin = render_ordine_admin(ordine)
    msg_a = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=testo_admin,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ PAGATO", callback_data=f"setstatus:{ordine_id}:confermato"),
                InlineKeyboardButton("❌ NON PAGATO", callback_data=f"setstatus:{ordine_id}:non_confermato")
            ]
        ])
    )
    ordine_to_msgid[ordine_id]["admin"] = (ADMIN_ID, msg_a.message_id)
    salva_ordini()

async def setstatus_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        _, order_id, new_status = query.data.split(":")
        order_id = int(order_id)
        ordine = next((o for o in orders if o["ordine_id"] == order_id), None)
        if not ordine:
            await query.edit_message_text("❌ Ordine non trovato.")
            return
        if ordine["stato"] == new_status:
            await query.answer("Lo stato è già aggiornato.", show_alert=True)
            return
        ordine["stato"] = new_status
        salva_ordini()
        msg_ids = ordine_to_msgid.get(order_id, {})
        testo_ragazza = render_ordine_utente(ordine, stato_override=new_status)
        testo_admin = render_ordine_admin(ordine, stato_override=new_status)
        # Modifica messaggio della ragazza
        if msg_ids.get("ragazza", (None, None))[0]:
            try:
                await context.bot.edit_message_caption(
                    chat_id=msg_ids["ragazza"][0],
                    message_id=msg_ids["ragazza"][1],
                    caption=testo_ragazza,
                    parse_mode="HTML",
                    reply_markup=None
                )
            except Exception as err:
                if "Message is not modified" not in str(err):
                    raise
        # Modifica messaggio dell'admin
        if msg_ids.get("admin", (None, None))[0]:
            try:
                await context.bot.edit_message_text(
                    chat_id=msg_ids["admin"][0],
                    message_id=msg_ids["admin"][1],
                    text=testo_admin,
                    parse_mode="HTML",
                    reply_markup=None
                )
            except Exception as err:
                if "Message is not modified" not in str(err):
                    raise
        # Modifica callback stesso utente
        try:
            if query.from_user.id == ordine['ragazza_id_telegram']:
                await query.edit_message_caption(
                    caption=testo_ragazza,
                    parse_mode="HTML"
                )
            elif query.from_user.id == ADMIN_ID:
                await query.edit_message_text(
                    testo_admin,
                    parse_mode="HTML"
                )
        except Exception as err:
            if "Message is not modified" not in str(err):
                raise
    except Exception as e:
        await query.edit_message_text(f"❌ Errore aggiornamento stato. {e}")

# === DASHBOARD & EXPORT ===

PERIODO, FINE_PERIODO, INIZIO_PERIODO = range(3)

async def dashboard_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # lista ragazze in ordine alfabetico
    bottoni = sorted([
        [InlineKeyboardButton(ragazze[k]['nome'], callback_data=f"dashgirl:{k}")]
        for k in ragazze
    ], key=lambda x: x[0].text)
    await update.message.reply_text(
        "👩‍💻 Scegli la ragazza per il riepilogo:",
        reply_markup=InlineKeyboardMarkup(bottoni)
    )
    return PERIODO

async def dashboard_periodo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    username = query.data.split(":")[1]
    context.user_data["dashboard_girl"] = username
    now = datetime.now()
    tastiera = [
        [InlineKeyboardButton("Ultimo giorno", callback_data="period:last_day")],
        [InlineKeyboardButton("Ultima settimana", callback_data="period:last_week")],
        [InlineKeyboardButton("Ultimo mese", callback_data="period:last_month")],
        [InlineKeyboardButton("Scegli un periodo", callback_data="period:custom")],
    ]
    await query.edit_message_text(
        f"Seleziona il periodo per la ragazza <b>{ragazze[username]['nome']}</b>:",
        reply_markup=InlineKeyboardMarkup(tastiera),
        parse_mode="HTML"
    )
    return FINE_PERIODO

async def dashboard_fine_periodo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    now = datetime.now()
    periodo = query.data.split(":")[1]
    context.user_data["period_type"] = periodo

    if periodo == "last_day":
        inizio = now - timedelta(days=1)
        fine = now
    elif periodo == "last_week":
        inizio = now - timedelta(days=7)
        fine = now
    elif periodo == "last_month":
        inizio = now - timedelta(days=30)
        fine = now
    elif periodo == "custom":
        context.user_data["awaiting_start_date"] = True
        await query.edit_message_text(
            "📅 Inserisci la data di INIZIO nel formato <b>GG/MM/AAAA</b> (es: 01/07/2025):",
            parse_mode="HTML"
        )
        return INIZIO_PERIODO

    context.user_data["period_inizio"] = inizio.strftime("%Y-%m-%d %H:%M:%S")
    context.user_data["period_fine"] = fine.strftime("%Y-%m-%d %H:%M:%S")
    await dashboard_show(update, context)
    return ConversationHandler.END

async def dashboard_inizio_periodo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_start_date" not in context.user_data:
        return ConversationHandler.END
    try:
        txt = update.message.text.strip()
        inizio = datetime.strptime(txt, "%d/%m/%Y")
        context.user_data["custom_inizio"] = inizio
        context.user_data.pop("awaiting_start_date")
        context.user_data["awaiting_end_date"] = True
        await update.message.reply_text(
            "📅 Ora inserisci la data di FINE nel formato <b>GG/MM/AAAA</b> (es: 15/07/2025):",
            parse_mode="HTML"
        )
        return FINE_PERIODO
    except Exception:
        await update.message.reply_text(
            "❌ Data non valida. Riprova (es: 01/07/2025)"
        )
        return INIZIO_PERIODO

async def dashboard_fine_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_end_date" not in context.user_data or "custom_inizio" not in context.user_data:
        return ConversationHandler.END
    try:
        txt = update.message.text.strip()
        fine = datetime.strptime(txt, "%d/%m/%Y")
        inizio = context.user_data["custom_inizio"]
        if fine < inizio:
            await update.message.reply_text("❌ La data di fine deve essere successiva a quella di inizio.")
            return FINE_PERIODO
        context.user_data["period_inizio"] = inizio.strftime("%Y-%m-%d %H:%M:%S")
        context.user_data["period_fine"] = fine.strftime("%Y-%m-%d %H:%M:%S")
        context.user_data.pop("awaiting_end_date")
        await dashboard_show(update, context)
        return ConversationHandler.END
    except Exception:
        await update.message.reply_text(
            "❌ Data non valida. Riprova (es: 15/07/2025)"
        )
        return FINE_PERIODO

async def dashboard_show(update, context):
    username = context.user_data["dashboard_girl"]
    nome = ragazze[username]['nome']
    try:
        inizio = datetime.strptime(context.user_data["period_inizio"], "%Y-%m-%d %H:%M:%S")
        fine = datetime.strptime(context.user_data["period_fine"], "%Y-%m-%d %H:%M:%S")
    except Exception:
        await update.message.reply_text("❌ Errore periodo date.")
        return
    filtered = [o for o in orders if o['ragazza'] == username and inizio <= datetime.strptime(o['data'], "%Y-%m-%d %H:%M:%S") <= fine]
    confermati = [o for o in filtered if o['stato'] == "confermato"]
    nonconf = [o for o in filtered if o['stato'] != "confermato"]
    tot_conf = sum(o['totale'] for o in confermati)
    tot_non = sum(o['totale'] for o in nonconf)
    msg = (
        f"<b>Statistiche di {nome}</b>\n"
        f"Periodo: <code>{inizio.strftime('%d/%m/%Y')}</code> - <code>{fine.strftime('%d/%m/%Y')}</code>\n"
        f"───────────────\n"
        f"• Ordini CONFERMATI: <b>{len(confermati)}</b>\n"
        f"• Ordini NON CONFERMATI: <b>{len(nonconf)}</b>\n"
        f"• Totale CONFERMATO: <b>{tot_conf}€</b>\n"
        f"• Totale NON confermato: <b>{tot_non}€</b>\n"
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(msg, parse_mode="HTML")
    else:
        await update.message.reply_text(msg, parse_mode="HTML")

async def esporta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    f = io.StringIO()
    writer = csv.writer(f)
    writer.writerow([
        "ID Ordine (ADMIN)", "Codice Ordine", "Ragazza", "Cliente", "ID Cliente", "Servizio", "Durata", "Prezzo Base",
        "Extra", "Metodo", "Totale", "Stato", "Data"
    ])
    for o in orders:
        writer.writerow([
            o['ordine_id'],
            o['ordine_codice'],
            o['ragazza_nome'],
            o['utente_username'],
            o['utente_id'],
            o['servizio'],
            o['durata'],
            o['prezzo'],
            "; ".join([f"{n} (+{p}€)" for n, p in o.get('extra_descr', [])]) if o.get('extra_descr') else "",
            o['metodo'],
            o['totale'],
            o['stato'],
            o['data']
        ])
    f.seek(0)
    await update.message.reply_document(
        document=io.BytesIO(f.read().encode()),
        filename="ordini.csv",
        caption="📦 Export ordini in CSV"
    )

def main():
    app = ApplicationBuilder().token("7634974075:AAGAG-ZYtg8VHoBNcBDEDXvv8j-XBk_0eeY").build()
    # Inline/Callback
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CallbackQueryHandler(visualizza_callback, pattern="^visualizza:"))
    app.add_handler(CallbackQueryHandler(servizio_callback, pattern="^servizio:"))
    app.add_handler(CallbackQueryHandler(acquisto_callback, pattern="^acquista:"))
    app.add_handler(CallbackQueryHandler(extra_callback, pattern="^extra:"))
    app.add_handler(CallbackQueryHandler(toggleextra_callback, pattern="^toggleextra:"))
    app.add_handler(CallbackQueryHandler(pagamenti_callback, pattern="^pagamenti:"))
    app.add_handler(CallbackQueryHandler(pagalink_callback, pattern="^pagalink:"))
    app.add_handler(CallbackQueryHandler(setstatus_callback, pattern="^setstatus:"))
    # Dashboard con ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("dashboard", dashboard_start)],
        states={
            PERIODO: [CallbackQueryHandler(dashboard_periodo, pattern="^dashgirl:")],
            FINE_PERIODO: [
                CallbackQueryHandler(dashboard_fine_periodo, pattern="^period:"),
                MessageHandler(filters.TEXT & (~filters.COMMAND), dashboard_fine_custom)
            ],
            INIZIO_PERIODO: [MessageHandler(filters.TEXT & (~filters.COMMAND), dashboard_inizio_periodo)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)
    # Export
    app.add_handler(CommandHandler("esporta", esporta_handler))
    print("Bot in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()
