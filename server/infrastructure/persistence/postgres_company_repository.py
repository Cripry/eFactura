import psycopg2
from domain.company.repository import CompanyRepository
from domain.company.company import Company
from config import Config


class PostgresCompanyRepository(CompanyRepository):
    def __init__(self):
        self.connection = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
        )

    def save(self, company: Company):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO companies (id, name, auth_token, created_at)
                VALUES (%s, %s, %s, %s)
            """,
                (company.id, company.name, company.auth_token, company.created_at),
            )
        self.connection.commit()

    def find_by_token(self, token: str) -> Company:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, auth_token, created_at
                FROM companies
                WHERE auth_token = %s
            """,
                (token,),
            )
            result = cursor.fetchone()
            if result:
                return Company(id=result[0], name=result[1], auth_token=result[2])
            return None

    def update(self, company: Company):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE companies
                SET auth_token = %s
                WHERE id = %s
            """,
                (company.auth_token, company.id),
            )
        self.connection.commit()
