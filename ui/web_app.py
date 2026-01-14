import streamlit as st
import pandas as pd
import sys
import os

# Añadir root al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, init_db
from database.models import ReservationStatus, Platform
from services.reservation_service import ReservationService
from services.notification_service import NotificationService

def get_db():
    if 'db' not in st.session_state:
        init_db()
        st.session_state.db = SessionLocal()
    return st.session_state.db

def main():
    db = get_db()
    st.title("📱 ReservaMaster")
    
    tab1, tab2 = st.tabs(["📝 Pendientes", "✅ Confirmadas"])
    
    with tab1:
        pending = ReservationService.get_pending_reservations(db)
        for res in pending:
            st.write(f"**{res.customer_name}** - {res.platform.value}")
            if st.button("Aceptar", key=f"acc_{res.id}"):
                ReservationService.update_reservation_status(db, res.id, ReservationStatus.CONFIRMED)
                st.rerun()

    with tab2:
        confirmed = ReservationService.get_confirmed_reservations(db)
        if confirmed:
            data = [{"Cliente": r.customer_name, "Plataforma": r.platform.value} for r in confirmed]
            st.dataframe(pd.DataFrame(data))

if __name__ == "__main__":
    main()
