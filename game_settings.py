from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class GameSettings:
    """Class to handle all game settings and configurations."""
    personality: str = "Unhinged"  # Default personality
    audience_type: str = "Academic"  # Default audience type
    difficulty: str = "normal"     # For future difficulty settings
    max_turns: int = 10           # For future turn limit implementation
    scoring_enabled: bool = True   # For future scoring system toggle
    support_shift_cap: int = 10    # Maximum percentage that support can shift per turn
    custom_settings: Dict[str, Any] = field(default_factory=dict)  # For any additional settings

    @classmethod
    def default(cls) -> 'GameSettings':
        """Create a GameSettings instance with default values."""
        return cls()

    @classmethod
    def from_dict(cls, settings_dict: dict) -> 'GameSettings':
        """Create a GameSettings instance from a dictionary."""
        # Filter out None values and unknown attributes
        valid_settings = {k: v for k, v in settings_dict.items() 
                         if v is not None and hasattr(cls, k)}
        
        # Store any additional settings in custom_settings
        custom_settings = {k: v for k, v in settings_dict.items() 
                          if not hasattr(cls, k)}
        
        return cls(**valid_settings, custom_settings=custom_settings)

    def to_dict(self) -> dict:
        """Convert settings to dictionary format."""
        return {
            'personality': self.personality,
            'audience_type': self.audience_type,
            'difficulty': self.difficulty,
            'max_turns': self.max_turns,
            'scoring_enabled': self.scoring_enabled,
            'support_shift_cap': self.support_shift_cap,
            'custom_settings': self.custom_settings
        }

    def update(self, **kwargs) -> None:
        """Update settings with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.custom_settings[key] = value
