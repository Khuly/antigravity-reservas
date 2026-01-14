"""
Servicio de gestión de reservas.
Maneja la lógica de negocio para crear, actualizar y consultar reservas.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models import PendingReservation, ReservationStatus, Platform
from utils.logger import app_logger


class ReservationService:
    """
    Servicio para gestión de reservas.
    """
    
    @staticmethod
    def create_reservation(
        db: Session,
        platform: Platform,
        customer_id: str,
        customer_name: Optional[str] = None,
        reservation_date: Optional[datetime] = None,
        reservation_time: Optional[str] = None,
        party_size: Optional[int] = None,
        notes: Optional[str] = None
    ) -> PendingReservation:
        """
        Crea una nueva reserva en estado PENDING.
        """
        reservation = PendingReservation(
            platform=platform,
            customer_id=customer_id,
            customer_name=customer_name,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            party_size=party_size,
            notes=notes,
            status=ReservationStatus.PENDING
        )
        
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        
        app_logger.info(
            f"Reserva creada: ID={reservation.id}, "
            f"platform={platform}, customer={customer_name}"
        )
        
        return reservation
    
    @staticmethod
    def update_reservation_status(
        db: Session,
        reservation_id: int,
        new_status: ReservationStatus
    ) -> Optional[PendingReservation]:
        """
        Actualiza el estado de una reserva.
        """
        reservation = db.query(PendingReservation).filter(
            PendingReservation.id == reservation_id
        ).first()
        
        if not reservation:
            app_logger.warning(f"Reserva no encontrada: ID={reservation_id}")
            return None
        
        old_status = reservation.status
        reservation.status = new_status
        reservation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(reservation)
        
        app_logger.info(
            f"Reserva actualizada: ID={reservation_id}, "
            f"{old_status} -> {new_status}"
        )
        
        return reservation
    
    @staticmethod
    def get_pending_reservations(db: Session) -> List[PendingReservation]:
        return db.query(PendingReservation).filter(
            PendingReservation.status == ReservationStatus.PENDING
        ).order_by(PendingReservation.created_at.desc()).all()
    
    @staticmethod
    def get_confirmed_reservations(db: Session) -> List[PendingReservation]:
        return db.query(PendingReservation).filter(
            PendingReservation.status == ReservationStatus.CONFIRMED
        ).order_by(PendingReservation.updated_at.desc()).all()
    
    @staticmethod
    def get_all_reservations(db: Session) -> List[PendingReservation]:
        return db.query(PendingReservation).order_by(
            PendingReservation.created_at.desc()
        ).all()
