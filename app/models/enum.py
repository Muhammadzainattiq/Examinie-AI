from enum import Enum


class Role(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"

class SocialInteractionStyle(str, Enum):
    INTROVERT = "introvert"
    EXTROVERT = "extrovert"
    AMBIVERT = "ambivert"

class DecisionMakingApproach(str, Enum):
    THINKER = "thinker"
    FEELER = "feeler"

class MotivationToStudy(str, Enum):
    GRADES = "grades"
    KNOWLEDGE = "knowledge"
    PERSONAL_GROWTH = "personal growth"
    CURIOSITY = "curiosity"
    PEER_COMPETITION = "peer competition"

class ExamQuestionHandling(str, Enum):
    SKIP_AND_RETURN = "skip and return"
    ATTEMPT_IMMEDIATELY = "attempt immediately"
    PROCESS_OF_ELIMINATION = "process of elimination"
    EDUCATED_GUESS = "educated guess"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, Enum):
    MCQ = "MCQs"
    SHORT_QUESTION = "Short Questions"
    LONG_QUESTION = "Long Questions/Essay Questions"
    CODING_PROBLEM = "Coding Problems"
    CASE_STUDY = "Case Studies"
    TRUE_FALSE = "True/False"
    FILL_IN_THE_BLANK = "Fill in the Blanks"
    YOUTUBE_VIDEO = "Youtube video"

class CurrentLevelOfEducation(Enum):
    KINDERGARTEN = "Kindergarten"
    PRIMARY_SCHOOL = "Primary School"
    MIDDLE_SCHOOL = "Middle School"
    HIGH_SCHOOL = "High School"
    UNDERGRADUATE = "Undergraduate"
    POSTGRADUATE = "Postgraduate"
    DOCTORATE = "Doctorate"
    OTHER = "Other"


class LatestGrade(Enum):
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"
    C_MINUS = "C-"
    D_PLUS = "D+"
    D = "D"
    D_MINUS = "D-"
    F = "F"
    INCOMPLETE = "I"  # Incomplete grade
    PASS = "P"        # Pass grade
    FAIL = "F"        # Fail grade
    OTHER = "Other"   # For any other grading system

class CareerPath(str, Enum):
    ENGINEERING = "Engineering"
    MEDICINE = "Medicine"
    LAW = "Law"
    ART = "Art"
    BUSINESS = "Business"
    TECHNOLOGY = "Technology"
    SCIENCE = "Science"
    EDUCATION = "Education"
    FINANCE = "Finance"
    HOSPITALITY = "Hospitality"
    HEALTHCARE = "Healthcare"
    ENVIRONMENTAL_SCIENCE = "Environmental Science"
    MEDIA_AND_COMMUNICATIONS = "Media and Communications"
    PSYCHOLOGY = "Psychology"
    SOCIAL_WORK = "Social Work"
    ENTREPRENEURSHIP = "Entrepreneurship"
    SPORTS = "Sports"
    GOVERNMENT_AND_POLITICS = "Government and Politics"
    OTHER = "Other"

class FavoriteSubject(Enum):
    MATHEMATICS = "Mathematics"
    SCIENCE = "Science"
    ENGLISH = "English"
    HISTORY = "History"
    GEOGRAPHY = "Geography"
    ART = "Art"
    MUSIC = "Music"
    COMPUTER_SCIENCE = "Computer Science"
    PHYSICAL_EDUCATION = "Physical Education"
    LANGUAGE = "Language"
    OTHER = "Other"


class FileType(str, Enum):
    FREE_TEXT = "Free Text"
    TOPIC = "Topic"
    PDF = "PDF"
    DOCX = "DOCX"
    XLSX = "XLSX"
    PPTX = "PPTX"
    IMAGE = "Image"
    Youtube_Video = "Youtube_Video"
    ARTICLE = "Article"
    EXAM = "Exam"