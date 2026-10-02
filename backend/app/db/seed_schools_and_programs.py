import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.db.database import SessionLocal
import app.models
from app.models.school import School
from app.models.program import Program
from sqlalchemy import text

SEED_DATA = [
    {
        "school": {
            "name": "The ICT University",
            "location": "Messassi, Yaounde, Centre Region, Cameroon",
            "description": "Premier US-accredited private university in Central Africa delivering cutting-edge, ICT-driven education, innovation, and global entrepreneurship training.",
            "website_url": "https://ictuniversity.edu.cm",
            "logo_url": "https://ictuniversity.edu.cm/wp-content/uploads/2021/04/ict-logo.png",
            "contact_email": "admissions@ictuniversity.edu.cm",
            "application_deadline": "October 31, 2026",
            "rolling_admission": True,
        },
        "programs": [
            {
                "field_of_study": "Software Engineering",
                "degree_type": "Bachelor",
                "tuition_fee": "730,000 FCFA / year",
                "duration": "3 years",
                "language_of_instruction": "English",
                "delivery_mode": "On-Campus",
                "admission_requirements": "GCE Advanced Level (minimum 2 papers with C in Math/Computer Science) or Baccalaureat C/D/TI.",
                "required_documents": "GCE/Bacc transcript, National ID card copy, 2 passport photos, Birth Certificate.",
                "application_deadline": "October 31, 2026",
                "class_size": 60,
                "description": "Comprehensive software engineering curriculum covering full-stack web, mobile architectures, algorithms, cloud systems, and agile dev practices.",
            },
            {
                "field_of_study": "Cybersecurity & Digital Forensics",
                "degree_type": "Bachelor",
                "tuition_fee": "780,000 FCFA / year",
                "duration": "3 years",
                "language_of_instruction": "English",
                "delivery_mode": "On-Campus",
                "admission_requirements": "GCE Advanced Level with 2 passes in science subjects or Baccalaureat C/D/TI/E.",
                "required_documents": "Academic transcripts, Proof of English proficiency, Copy of CNI/Passport, Recommendation letter.",
                "application_deadline": "October 31, 2026",
                "class_size": 45,
                "description": "Advanced defensive security, network penetration testing, cryptography, incident response, digital evidence collection, and cloud security.",
            },
            {
                "field_of_study": "Information Systems & Big Data Analytics",
                "degree_type": "Master",
                "tuition_fee": "1,100,000 FCFA / year",
                "duration": "2 years",
                "language_of_instruction": "English",
                "delivery_mode": "Hybrid",
                "admission_requirements": "Bachelor degree in Computer Science, Software Engineering, Mathematics, or related STEM discipline (min GPA 2.8/4.0).",
                "required_documents": "Certified degree certificate, official transcripts, CV/Resume, Statement of Purpose, 2 academic references.",
                "application_deadline": "November 15, 2026",
                "class_size": 35,
                "description": "Postgraduate training focusing on big data pipelines, distributed systems, machine learning engineering, enterprise BI architectures, and cloud analytics.",
            },
        ],
    },
    {
        "school": {
            "name": "National Advanced School of Engineering (Polytech Yaounde)",
            "location": "Melan, Yaounde, Centre Region, Cameroon",
            "description": "Cameroon's premier public grande ecole d'ingenieurs affiliated with University of Yaounde I, training elite engineers and innovators since 1971.",
            "website_url": "https://polytechnique.cm",
            "logo_url": "https://polytechnique.cm/wp-content/themes/enspy/images/logo.png",
            "contact_email": "contact@polytechnique.cm",
            "application_deadline": "July 15, 2026",
            "rolling_admission": False,
        },
        "programs": [
            {
                "field_of_study": "Computer Engineering & Artificial Intelligence",
                "degree_type": "Engineering Diploma (Master Equiv.)",
                "tuition_fee": "50,000 FCFA / year (State tuition)",
                "duration": "5 years",
                "language_of_instruction": "Bilingual (French / English)",
                "delivery_mode": "On-Campus",
                "admission_requirements": "Competitive entrance examination (Concours National) open to Bac C/D/TI/E or GCE A-Level Sciences (Math & Physics).",
                "required_documents": "Certified copy of Birth Certificate, Baccalaureat/GCE A-Level slip, Medical certificate of fitness, Concours receipt.",
                "application_deadline": "July 15, 2026",
                "class_size": 75,
                "description": "Elite 5-year engineering cycle encompassing computer architecture, deep learning, embedded robotics, distributed computing, and software systems.",
            },
            {
                "field_of_study": "Telecommunications & Network Engineering",
                "degree_type": "Engineering Diploma (Master Equiv.)",
                "tuition_fee": "50,000 FCFA / year (State tuition)",
                "duration": "5 years",
                "language_of_instruction": "Bilingual (French / English)",
                "delivery_mode": "On-Campus",
                "admission_requirements": "Competitive national entrance exam (Concours ENSPY) in Mathematics and Physics.",
                "required_documents": "Concours file, certified transcripts, National ID copy, Birth certificate, 4 passport photos.",
                "application_deadline": "July 15, 2026",
                "class_size": 60,
                "description": "In-depth education covering 5G/6G mobile networks, fiber optics, RF systems, satellite communications, network protocols, and cyber-defense.",
            },
            {
                "field_of_study": "Civil & Environmental Engineering",
                "degree_type": "Engineering Diploma (Master Equiv.)",
                "tuition_fee": "50,000 FCFA / year (State tuition)",
                "duration": "5 years",
                "language_of_instruction": "Bilingual (French / English)",
                "delivery_mode": "On-Campus",
                "admission_requirements": "National competitive entrance examination (Concours) for Bac C, D, E, F4 or GCE A-Level with Math and Physics.",
                "required_documents": "Concours application receipt, certified academic diplomas, medical certificate, birth certificate.",
                "application_deadline": "July 15, 2026",
                "class_size": 80,
                "description": "Structural design, geotechnics, bridge and road construction, hydraulics, smart infrastructure, and sustainable environmental engineering.",
            },
        ],
    },
    {
        "school": {
            "name": "IUSTY (Institut Universitaire et Strategique de l'Estuaire)",
            "location": "Soa / Nsam, Yaounde, Centre Region, Cameroon",
            "description": "Fast-growing university institute offering vocational degrees, professional bachelors, and masters focused on immediate industry employment.",
            "website_url": "https://iusty.com",
            "logo_url": "https://iusty.com/assets/img/logo.png",
            "contact_email": "info@iusty.com",
            "application_deadline": "October 25, 2026",
            "rolling_admission": True,
        },
        "programs": [
            {
                "field_of_study": "Software Engineering & Database Administration",
                "degree_type": "Licence Professionnelle",
                "tuition_fee": "450,000 FCFA / year",
                "duration": "3 years (or 1 yr top-up after BTS/HND)",
                "language_of_instruction": "Bilingual (French / English)",
                "delivery_mode": "On-Campus",
                "admission_requirements": "Baccalaureat (all series) or GCE A-Level (min 2 papers), or HND/BTS for direct 3rd year entry.",
                "required_documents": "Copy of National ID card, birth certificate, certified copies of high school diplomas, 2 passport photos.",
                "application_deadline": "October 25, 2026",
                "class_size": 50,
                "description": "Practical, market-oriented degree covering backend APIs, relational & NoSQL databases, mobile applications, and cloud devops.",
            },
            {
                "field_of_study": "Accounting, Audit & Financial Control",
                "degree_type": "Licence Professionnelle",
                "tuition_fee": "420,000 FCFA / year",
                "duration": "3 years",
                "language_of_instruction": "French",
                "delivery_mode": "On-Campus",
                "admission_requirements": "Baccalaureat G2/B/C/D or GCE A-Level with passes in Economics or Accounting.",
                "required_documents": "Certified high school diploma, birth certificate, transcript of records, 2 passport size photos.",
                "application_deadline": "October 25, 2026",
                "class_size": 70,
                "description": "Comprehensive OHADA accounting standards, corporate taxation, statutory auditing, management control, and financial reporting.",
            },
            {
                "field_of_study": "Logistics & Transport Management",
                "degree_type": "HND (Higher National Diploma)",
                "tuition_fee": "380,000 FCFA / year",
                "duration": "2 years",
                "language_of_instruction": "Bilingual (French / English)",
                "delivery_mode": "On-Campus",
                "admission_requirements": "Baccalaureat (any series) or GCE A-Level (minimum 2 papers).",
                "required_documents": "High school diploma copy, birth certificate, application form, 2 passport photos.",
                "application_deadline": "October 25, 2026",
                "class_size": 60,
                "description": "Supply chain optimization, freight forwarding, customs clearance, warehouse management, and international trade operations.",
            },
        ],
    },
    {
        "school": {
            "name": "Messassi Institute of Science and Technology (MIST)",
            "location": "Dispensaire Messassi, Yaounde, Centre Region, Cameroon",
            "description": "Specialized polytechnic institute known for rigorous hands-on technical training, biomedical technologies, engineering, and digital entrepreneurship.",
            "website_url": "https://mist.cm",
            "logo_url": "https://mist.cm/assets/images/mist-logo.png",
            "contact_email": "admissions@mist.cm",
            "application_deadline": "November 05, 2026",
            "rolling_admission": True,
        },
        "programs": [
            {
                "field_of_study": "Biomedical Engineering & Hospital Equipment Maintenance",
                "degree_type": "Bachelor of Technology",
                "tuition_fee": "650,000 FCFA / year",
                "duration": "3 years",
                "language_of_instruction": "English",
                "delivery_mode": "On-Campus",
                "admission_requirements": "GCE Advanced Level in Sciences (Physics, Biology, Chemistry, or Math) or Bac C/D/F5.",
                "required_documents": "Certified GCE/Bac transcripts, copy of Birth Certificate, National ID, Medical fitness certificate.",
                "application_deadline": "November 05, 2026",
                "class_size": 40,
                "description": "Specialized technical program bridging healthcare and engineering: maintenance of diagnostic imaging, patient monitors, and hospital robotics.",
            },
            {
                "field_of_study": "Electrical Power Systems & Renewable Energy",
                "degree_type": "Bachelor of Technology",
                "tuition_fee": "580,000 FCFA / year",
                "duration": "3 years",
                "language_of_instruction": "Bilingual (French / English)",
                "delivery_mode": "On-Campus",
                "admission_requirements": "GCE A-Level Sciences (Math & Physics) or Bac C, E, F3.",
                "required_documents": "Certified high school credentials, Birth Certificate, National ID card copy, 2 passport photos.",
                "application_deadline": "November 05, 2026",
                "class_size": 50,
                "description": "Solar PV design, mini-grid electrification, industrial electrical installations, high-voltage networks, and energy efficiency systems.",
            },
            {
                "field_of_study": "Computer Systems & Network Security",
                "degree_type": "HND (Higher National Diploma)",
                "tuition_fee": "480,000 FCFA / year",
                "duration": "2 years",
                "language_of_instruction": "English",
                "delivery_mode": "On-Campus",
                "admission_requirements": "GCE Advanced Level (min 2 papers) or Baccalaureat C/D/TI.",
                "required_documents": "Certified copies of GCE/Bac, Birth certificate, 2 photos, National ID card.",
                "application_deadline": "November 05, 2026",
                "class_size": 45,
                "description": "Practical 2-year state HND covering Linux administration, Cisco routing and switching, firewall configuration, and client-server networks.",
            },
        ],
    },
]

def seed_database():
    db = SessionLocal()
    try:
        print("Clearing existing schools and programs in Neon database...")
        db.execute(text("DELETE FROM programs;"))
        db.execute(text("DELETE FROM schools;"))
        db.commit()

        total_schools = 0
        total_programs = 0

        for item in SEED_DATA:
            school_data = item["school"]
            school = School(**school_data)
            db.add(school)
            db.flush()
            total_schools += 1

            for prog_data in item["programs"]:
                program = Program(school_id=school.id, **prog_data)
                db.add(program)
                total_programs += 1

        db.commit()
        print("Successfully seeded Neon PostgreSQL database!")
        print(f"  - Schools added: {total_schools}")
        print(f"  - Programs added: {total_programs}")
    except Exception as e:
        db.rollback()
        print(f"Error while seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
