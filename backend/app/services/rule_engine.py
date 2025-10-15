"""
Rule engine for evaluating detection rules.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
from shapely.geometry import Point, Polygon

from app.models.db_models import Rule, RuleType

logger = logging.getLogger(__name__)


class RuleEngine:
    """Engine for evaluating detection rules."""
    
    def __init__(self):
        self.state = {}  # Track state for stateful rules (e.g., dwell time)
    
    def evaluate_rule(self, rule: Rule, detection: Dict[str, Any]) -> bool:
        """Evaluate a single rule against a detection."""
        try:
            if rule.rule_type == RuleType.ZONE_ENTRY:
                return self._evaluate_zone_entry(rule, detection)
            elif rule.rule_type == RuleType.ZONE_EXIT:
                return self._evaluate_zone_exit(rule, detection)
            elif rule.rule_type == RuleType.DWELL_TIME:
                return self._evaluate_dwell_time(rule, detection)
            elif rule.rule_type == RuleType.OBJECT_COUNT:
                return self._evaluate_object_count(rule, detection)
            elif rule.rule_type == RuleType.LINE_CROSSING:
                return self._evaluate_line_crossing(rule, detection)
            else:
                logger.warning(f"Unknown rule type: {rule.rule_type}")
                return False
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.id}: {e}")
            return False
    
    def _evaluate_zone_entry(self, rule: Rule, detection: Dict[str, Any]) -> bool:
        """Evaluate zone entry rule."""
        config = rule.config
        
        # Check object type
        if "object_types" in config:
            if detection.get("class") not in config["object_types"]:
                return False
        
        # Check confidence threshold
        if "threshold" in config:
            if detection.get("confidence", 0) < config["threshold"]:
                return False
        
        # Check zone geometry
        if "zone" in config:
            bbox = detection.get("bbox", [])
            if len(bbox) == 4:
                # Calculate center point of bounding box
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2
                point = Point(center_x, center_y)
                
                # Create polygon from zone coordinates
                zone_coords = config["zone"]
                if len(zone_coords) >= 3:
                    polygon = Polygon(zone_coords)
                    return polygon.contains(point)
        
        return True
    
    def _evaluate_zone_exit(self, rule: Rule, detection: Dict[str, Any]) -> bool:
        """Evaluate zone exit rule."""
        # Similar to zone entry but check if object was in zone and now is out
        # Requires state tracking
        track_id = detection.get("track_id")
        if not track_id:
            return False
        
        config = rule.config
        state_key = f"{rule.id}:{track_id}"
        
        # Check if object is currently in zone
        in_zone = self._evaluate_zone_entry(rule, detection)
        
        # Check previous state
        was_in_zone = self.state.get(state_key, {}).get("in_zone", False)
        
        # Update state
        self.state[state_key] = {
            "in_zone": in_zone,
            "timestamp": datetime.utcnow()
        }
        
        # Trigger if was in zone and now is out
        return was_in_zone and not in_zone
    
    def _evaluate_dwell_time(self, rule: Rule, detection: Dict[str, Any]) -> bool:
        """Evaluate dwell time rule."""
        track_id = detection.get("track_id")
        if not track_id:
            return False
        
        config = rule.config
        dwell_threshold = config.get("dwell_time_seconds", 10)
        
        state_key = f"{rule.id}:{track_id}"
        
        # Check if object is in zone
        in_zone = self._evaluate_zone_entry(rule, detection)
        
        if in_zone:
            if state_key not in self.state:
                # First time seeing this object in zone
                self.state[state_key] = {
                    "entry_time": datetime.utcnow(),
                    "in_zone": True
                }
                return False
            else:
                # Calculate dwell time
                entry_time = self.state[state_key].get("entry_time")
                if entry_time:
                    dwell_seconds = (datetime.utcnow() - entry_time).total_seconds()
                    return dwell_seconds >= dwell_threshold
        else:
            # Object left zone, reset state
            if state_key in self.state:
                del self.state[state_key]
        
        return False
    
    def _evaluate_object_count(self, rule: Rule, detection: Dict[str, Any]) -> bool:
        """Evaluate object count rule."""
        # This requires tracking multiple objects simultaneously
        # Implementation would need batch processing of all detections
        config = rule.config
        count_threshold = config.get("count_threshold", 5)
        
        # Placeholder - would need actual count from batch
        return False
    
    def _evaluate_line_crossing(self, rule: Rule, detection: Dict[str, Any]) -> bool:
        """Evaluate line crossing rule."""
        track_id = detection.get("track_id")
        if not track_id:
            return False
        
        config = rule.config
        line = config.get("line")  # [[x1, y1], [x2, y2]]
        
        if not line or len(line) != 2:
            return False
        
        # Get current position
        bbox = detection.get("bbox", [])
        if len(bbox) != 4:
            return False
        
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        
        state_key = f"{rule.id}:{track_id}"
        
        # Check previous position
        if state_key in self.state:
            prev_x = self.state[state_key].get("x")
            prev_y = self.state[state_key].get("y")
            
            if prev_x is not None and prev_y is not None:
                # Check if line was crossed
                # Simplified check - in production would use proper line intersection
                crossed = self._check_line_crossing(
                    (prev_x, prev_y), (center_x, center_y), line
                )
                
                # Update state
                self.state[state_key] = {"x": center_x, "y": center_y}
                
                return crossed
        
        # Store initial position
        self.state[state_key] = {"x": center_x, "y": center_y}
        return False
    
    def _check_line_crossing(
        self,
        prev_point: tuple,
        curr_point: tuple,
        line: List[List[float]]
    ) -> bool:
        """Check if movement crossed a line."""
        # Simplified implementation
        # In production, use proper line segment intersection algorithm
        return False
    
    def cleanup_state(self, max_age_seconds: int = 300):
        """Clean up old state entries."""
        now = datetime.utcnow()
        to_delete = []
        
        for key, value in self.state.items():
            timestamp = value.get("timestamp")
            if timestamp and (now - timestamp).total_seconds() > max_age_seconds:
                to_delete.append(key)
        
        for key in to_delete:
            del self.state[key]
        
        if to_delete:
            logger.info(f"Cleaned up {len(to_delete)} state entries")
