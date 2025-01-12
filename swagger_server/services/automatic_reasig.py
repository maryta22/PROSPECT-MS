#1.- seleccionar vendedores tienen ese programa
#2.- seleccionar el vendedor con el menor numero de prospecciones asignadas
#3.- devolver ese id del vendedor

#hay que generar un aleatorio

import random
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine, func
import logging
from dotenv import load_dotenv
import os

from swagger_server.database_models.models import (
    AcademicProgram,
    SalesAdvisor,
    Prospection,
    ProgramSellers,
    ProspectionSalesAdvisor
)

load_dotenv()

class AutomaticReasig:
    def __init__(self):
        db_password = os.getenv('DB_PASSWORD')
        self.engine = create_engine(f'mysql+pymysql://root:{db_password}@localhost:3306/espae_prospections')
        self.Session = sessionmaker(bind=self.engine)

    def get_sales_advisor_with_least_prospections(self, program_id):
        session = self.Session()
        try:
            # 1. Seleccionar los vendedores que tienen el programa dado
            if not program_id:
                print("No program_id provided.")
                return None
            sales_advisors = session.query(SalesAdvisor).join(
                ProgramSellers, ProgramSellers.id_sales_advisor == SalesAdvisor.id
            ).filter(
                ProgramSellers.id_academic_program == program_id,
                ProgramSellers.state == 1,  # Solo relaciones activas
                SalesAdvisor.state == 1  # Solo asesores activos
            ).all()
            print("Program_id: ",program_id)
            if not sales_advisors:
                print(f"No sales advisors found for program_id {program_id}.")
                return None

            # 2. Contar las prospecciones asignadas a cada vendedor
            sales_advisor_prospections = {}
            for advisor in sales_advisors:
                prospection_count = session.query(func.count(ProspectionSalesAdvisor.id)).filter(
                    ProspectionSalesAdvisor.id_sales_advisor == advisor.id,
                    ProspectionSalesAdvisor.state == 1  # Solo prospecciones activas
                ).scalar()
                sales_advisor_prospections[advisor.id] = prospection_count

            # Obtener el menor número de prospecciones
            min_prospections = min(sales_advisor_prospections.values())

            # 3. Seleccionar aleatoriamente entre los vendedores con el menor número de prospecciones
            candidates = [advisor_id for advisor_id, count in sales_advisor_prospections.items() if count == min_prospections]
            selected_advisor_id = random.choice(candidates)

            logging.info(f"Selected Sales Advisor ID: {selected_advisor_id}")
            print("candidatos: ",candidates)
            return selected_advisor_id
        except Exception as e:
            logging.error(f"Error in get_sales_advisor_with_least_prospections: {e}")
            return None
        finally:
            session.close()
