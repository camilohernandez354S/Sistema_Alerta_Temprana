"""
Modelos para blockchain
"""
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib
from typing import Optional

class Block(BaseModel):
    """Modelo para un bloque en la cadena"""
    index: int = Field(..., description="Índice del bloque")
    timestamp: str = Field(..., description="Timestamp de creación")
    data: dict = Field(..., description="Datos del sensor")
    previous_hash: Optional[str] = Field(None, description="Hash del bloque anterior")
    hash: str = Field(..., description="Hash del bloque")
    
    @classmethod
    def create_genesis_block(cls):
        """Crear el bloque génesis"""
        genesis_data = {
            "nivel_agua": 0,
            "estado": "genesis",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return cls(
            index=0,
            timestamp=genesis_data["timestamp"],
            data=genesis_data,
            previous_hash="0",
            hash=cls.calculate_hash(0, genesis_data["timestamp"], genesis_data, "0")
        )
    
    @staticmethod
    def calculate_hash(index: int, timestamp: str, data: dict, previous_hash: str) -> str:
        """Calcular el hash del bloque"""
        block_string = f"{index}{timestamp}{str(data)}{previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    """Implementación básica de blockchain para asegurar datos de sensor"""
    def __init__(self):
        self.chain = [Block.create_genesis_block()]
        
    def add_block(self, data: dict) -> Block:
        """Agregar un nuevo bloque a la cadena"""
        last_block = self.chain[-1]
        new_block = Block(
            index=last_block.index + 1,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data=data,
            previous_hash=last_block.hash,
            hash=Block.calculate_hash(
                last_block.index + 1,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data,
                last_block.hash
            )
        )
        self.chain.append(new_block)
        return new_block
    
    def validate_chain(self) -> bool:
        """Validar la integridad de la cadena"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current.hash != Block.calculate_hash(
                current.index,
                current.timestamp,
                current.data,
                current.previous_hash
            ):
                return False
            
            if current.previous_hash != previous.hash:
                return False
        
        return True
