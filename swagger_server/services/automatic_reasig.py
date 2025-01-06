#1.- seleccionar vendedores tienen ese programa
#2.- seleccionar el vendedor con el menor numero de prospecciones asignadas
#3.- devolver ese id del vendedor

#hay que generar un aleatorio

import random
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from swagger_server.models import SalesAdvisor, Prospection, AcademicProgram
import os
import logging

# Configuración de la base de datos
pass_sam = os.getenv('DB_PASSWORD')
engine = create_engine(f'mysql+pymysql://root:{pass_sam}@localhost:3306/espae_prospections')
Session = sessionmaker(bind=engine)

def get_sales_advisor_with_least_prospections(program_id):
    session = Session
    try:
        # 1. Seleccionar los vendedores que tienen el programa dado
        sales_advisors = session.query(SalesAdvisor).join(SalesAdvisor.programs).filter(AcademicProgram.id == program_id).all()

        if not sales_advisors:
            return None

        # 2. Seleccionar el vendedor con el menor número de prospecciones asignadas en total de todos los programas
        sales_advisor_prospections = {}
        for advisor in sales_advisors:
            prospection_count = session.query(func.count(Prospection.id)).filter(Prospection.sales_advisor_id == advisor.id).scalar()
            sales_advisor_prospections[advisor.id] = prospection_count

        # Obtener el menor número de prospecciones
        min_prospections = min(sales_advisor_prospections.values())

        # 3. Devolver el ID del vendedor que tenga menos prospecciones
        # En caso de empate, seleccionar aleatoriamente entre los vendedores con el mismo número de prospecciones
        candidates = [advisor_id for advisor_id, count in sales_advisor_prospections.items() if count == min_prospections]
        selected_advisor_id = random.choice(candidates)

        return selected_advisor_id
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        session.close()