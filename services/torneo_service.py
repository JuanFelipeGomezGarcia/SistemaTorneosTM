"""Servicio de lógica de negocio para torneos"""
from database.db_operations import DatabaseOperations

class TorneoService:
    def __init__(self):
        self.db = DatabaseOperations()
    
    def crear_torneo(self, nombre, fecha):
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del torneo es obligatorio")
        return self.db.crear_torneo(nombre.strip(), fecha)
    
    def obtener_torneos(self):
        return self.db.obtener_torneos()
    
    def obtener_torneo(self, torneo_id):
        torneos = self.db.obtener_torneos()
        return next((t for t in torneos if t['id'] == torneo_id), None)
    
    def actualizar_estado(self, torneo_id, estado):
        return self.db.actualizar_estado_torneo(torneo_id, estado)
    
    def puede_finalizar(self, torneo_id):
        categorias = self.db.obtener_categorias(torneo_id)
        return all(cat.get('ganador') for cat in categorias)
