# Import Base from base_class to ensure all models share the same metadata
from app.db.base_class import Base
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.school import School
from app.models.program import Program
from app.models.application import Application
from app.models.favorite import Favorite
from app.models.document import Document
from app.models.application_submission import ApplicationSubmission
