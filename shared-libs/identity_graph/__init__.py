"""
Identity Graph - Shared Library

Provides graph-based identity resolution, entity linking, and relationship
mapping across the TuringMachines platform.
"""

from typing import Dict, Any, List, Set
import logging

logger = logging.getLogger(__name__)


class IdentityGraph:
    """
    Graph-based identity resolution and relationship mapping.
    
    Maintains a knowledge graph of identities, their relationships,
    and associated risk signals for fraud and AML detection.
    """
    
    def __init__(self):
        """Initialize identity graph."""
        self.logger = logging.getLogger(f"{__name__}.IdentityGraph")
        self.entities = {}
        self.relationships = {}
    
    def add_entity(self, entity_id: str, entity_type: str,
                   attributes: Dict[str, Any]) -> None:
        """
        Add an entity to the graph.
        
        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity (user, device, account, etc.)
            attributes: Entity attributes and metadata
        """
        self.entities[entity_id] = {
            "type": entity_type,
            "attributes": attributes,
            "relationships": []
        }
        self.logger.debug(f"Added entity: {entity_id} ({entity_type})")
    
    def add_relationship(self, source_id: str, target_id: str,
                        relationship_type: str, weight: float = 1.0) -> None:
        """
        Add a relationship between entities.
        
        Args:
            source_id: Source entity identifier
            target_id: Target entity identifier
            relationship_type: Type of relationship
            weight: Relationship strength (0.0-1.0)
        """
        if source_id not in self.relationships:
            self.relationships[source_id] = []
        
        self.relationships[source_id].append({
            "target": target_id,
            "type": relationship_type,
            "weight": weight
        })
        
        self.logger.debug(
            f"Added relationship: {source_id} --{relationship_type}--> {target_id}"
        )
    
    def find_connected_entities(self, entity_id: str, max_depth: int = 2) -> Set[str]:
        """
        Find all entities connected to a given entity.
        
        Args:
            entity_id: Starting entity identifier
            max_depth: Maximum relationship depth to traverse
            
        Returns:
            Set of connected entity identifiers
        """
        connected = set()
        visited = set()
        queue = [(entity_id, 0)]
        
        while queue:
            current_id, depth = queue.pop(0)
            
            if current_id in visited or depth > max_depth:
                continue
            
            visited.add(current_id)
            connected.add(current_id)
            
            # Add neighbors to queue
            if current_id in self.relationships:
                for rel in self.relationships[current_id]:
                    if rel["target"] not in visited:
                        queue.append((rel["target"], depth + 1))
        
        return connected
    
    def get_entity_risk_score(self, entity_id: str) -> float:
        """
        Calculate risk score based on entity and connected entities.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Risk score (0.0-1.0)
        """
        if entity_id not in self.entities:
            return 0.0
        
        # Base risk from entity attributes
        entity = self.entities[entity_id]
        base_risk = entity.get("attributes", {}).get("risk_score", 0.0)
        
        # Propagate risk from connected entities
        connected = self.find_connected_entities(entity_id, max_depth=1)
        connected_risk = 0.0
        
        for connected_id in connected:
            if connected_id != entity_id:
                connected_entity = self.entities.get(connected_id, {})
                connected_risk += connected_entity.get("attributes", {}).get("risk_score", 0.0)
        
        if connected:
            avg_connected_risk = connected_risk / len(connected)
            return min(1.0, (base_risk + avg_connected_risk) / 2)
        
        return base_risk


__all__ = ["IdentityGraph"]
