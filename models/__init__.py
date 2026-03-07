# Import all models here so they can be imported from 'models'
from .games import Game
from .gamemove import GameMove
from .registration import Registration  # if you have a registration model
from .survey import SurveyQuestion
from .response import Response

# Optional: define __all__ to be explicit
__all__ = ["Game", "GameMove", "Registration", "SurveyQuestion", "Response"]
