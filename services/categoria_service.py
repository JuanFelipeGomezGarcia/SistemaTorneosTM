"""Servicio de lógica de negocio para categorías"""
from database.db_operations import DatabaseOperations

class CategoriaService:
    def __init__(self):
        self.db = DatabaseOperations()
    
    def crear_categoria(self, torneo_id, nombre, personas_por_cuadro, participantes):
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la categoría es obligatorio")
        
        participantes = [p.strip() for p in participantes if p.strip()]
        
        if len(participantes) < personas_por_cuadro:
            raise ValueError(f"Necesitas al menos {personas_por_cuadro} participantes")
        
        cantidad_cuadros = (len(participantes) + personas_por_cuadro - 1) // personas_por_cuadro
        
        categoria_id = self.db.crear_categoria(torneo_id, nombre.strip(), cantidad_cuadros, personas_por_cuadro)
        
        if categoria_id:
            for p in participantes:
                self.db.agregar_participante(categoria_id, p)
        
        return categoria_id
    
    def obtener_categorias(self, torneo_id):
        return self.db.obtener_categorias(torneo_id)
    
    def obtener_participantes(self, categoria_id):
        return self.db.obtener_participantes(categoria_id)
