from .start import register_start_handler
from .study import register_study_handler
from .career import register_career_handler
from .campus import register_campus_handler
from .social import register_social_handler
from .assignment_solver import register_assignment_solver_handler

def register_handlers(bot):
    register_start_handler(bot)
    register_assignment_solver_handler(bot)  # Register this before study handler
    register_study_handler(bot)
    register_career_handler(bot)
    register_campus_handler(bot)
    register_social_handler(bot)