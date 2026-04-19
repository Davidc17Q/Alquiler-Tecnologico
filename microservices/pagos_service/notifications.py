from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def send_payment_confirmation_email(
    to: str,
    usuario_nombre: str,
    equipo_nombre: str,
    fecha_inicio: str,
    fecha_fin: str,
    monto: str,
) -> None:
    subject = "Confirmación de pago de alquiler - TechRent"
    body = (
        f"Hola {usuario_nombre},\n\n"
        f"Tu pago por el alquiler del equipo '{equipo_nombre}' "
        f"ha sido confirmado.\n"
        f"Fechas: {fecha_inicio} al {fecha_fin}\n"
        f"Monto pagado: {monto}\n\n"
        "Gracias por utilizar TechRent."
    )
    user = os.getenv("EMAIL_HOST_USER", "").strip()
    password = os.getenv("EMAIL_HOST_PASSWORD", "").strip()
    host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    port = int(os.getenv("EMAIL_PORT", "587"))
    from_email = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@techrent.local")

    if not user or not password:
        print(f"[TechRent][NOTIFICACIÓN] To={to} | Subject={subject}\n{body}\n")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to
    msg.set_content(body)

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)
