import argparse
import asyncio
import random
import uuid
from datetime import datetime, timezone

from faker import Faker
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.auth.models.user import UserORM
from src.infrastructure.auth.services.hasher import Hasher
from src.infrastructure.budget.models.budget import BudgetORM
from src.infrastructure.budget.models.category import CategoryORM
from src.infrastructure.workspace.models.workspace import WorkspaceMemberORM, WorkspaceORM
from src.infrastructure.database import Base
from src.domain.workspace.value_objects import WorkspaceRole

# Configuration
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/wiselab"
# Use Spanish locale for Faker
fake = Faker('es_ES')

async def seed_default_categories(session: AsyncSession):
    """Seed default categories in Spanish."""
    print("Seeding default categories in Spanish...")
    categories = [
        ("Vivienda", "Alquiler, hipoteca, servicios del hogar"),
        ("Transporte", "Combustible, transporte público, mantenimiento de vehículos"),
        ("Alimentación", "Supermercado, restaurantes, snacks"),
        ("Servicios", "Electricidad, agua, internet, telefonía"),
        ("Salud y Bienestar", "Gimnasio, seguros, gastos médicos"),
        ("Compras", "Ropa, electrónica, artículos para el hogar"),
        ("Entretenimiento", "Cine, juegos, eventos sociales"),
        ("Educación", "Cursos, libros, colegiaturas"),
        ("Viajes", "Vuelos, hoteles, vacaciones"),
        ("Inversiones", "Acciones, criptomonedas, ahorros"),
        ("Otros", "Gastos varios no categorizados"),
    ]
    
    for name, desc in categories:
        stmt = select(CategoryORM).where(CategoryORM.name == name, CategoryORM.is_default == True)
        result = await session.execute(stmt)
        if not result.scalar_one_or_none():
            cat = CategoryORM(
                id=uuid.uuid4(),
                name=name,
                description=desc,
                is_default=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            session.add(cat)
    
    await session.commit()

async def seed(reset: bool = False):
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        if reset:
            print("Resetting database (truncating tables)...")
            await session.execute(text("TRUNCATE users, workspaces, categories, budgets, workspace_members CASCADE"))
            await session.commit()
        
        await seed_default_categories(session)
        
        # 1. Create 5 Users
        print("Creating 5 users...")
        users = []
        for i in range(5):
            email = f"usuario{i+1}@example.com"
            # Check if user exists
            stmt = select(UserORM).where(UserORM.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                user = UserORM(
                    id=uuid.uuid4(),
                    email=email,
                    password_hash=Hasher.get_password_hash("password123"),
                    full_name=fake.name(),
                    is_active=True
                )
                session.add(user)
                users.append(user)
            else:
                users.append(user)
        
        await session.commit()
        for u in users:
            await session.refresh(u)

        # 2. Get Default Categories
        print("Fetching default categories...")
        stmt = select(CategoryORM).where(CategoryORM.is_default == True)
        result = await session.execute(stmt)
        default_categories = result.scalars().all()
        if not default_categories:
            print("Warning: No default categories found even after seeding attempt.")
            return

        # 3. Create 10 Workspaces
        print("Creating 10 workspaces...")
        workspace_templates = [
            ("Finanzas Familiares", "Gestión integral de ingresos, gastos y ahorros del hogar.", "Hogar"),
            ("Consultoría Pro S.L.", "Control presupuestario y seguimiento de facturación corporativa.", "Empresa"),
            ("Ahorro para Vivienda", "Fondo dedicado para la entrada de la primera residencia.", "Inversión"),
            ("Gastos del Viaje Japón", "Presupuesto detallado para transporte, alojamiento y ocio en Asia.", "Viajes"),
            ("Cartera de Inversión", "Seguimiento de dividendos, acciones y mercado cripto.", "Inversión"),
            ("Educación Continua", "Fondo para cursos técnicos, certificaciones y libros.", "Educación"),
            ("Presupuesto Personal", "Control diario de gastos hormiga y flujo de caja personal.", "Personal"),
            ("Startup Ecommerce", "Operaciones financieras, marketing y logística del negocio.", "Empresa"),
            ("Mantenimiento del Hogar", "Fondo para reparaciones, mejoras y servicios domésticos.", "Hogar"),
            ("Fondo de Emergencia", "Reserva de seguridad para imprevistos y tranquilidad financiera.", "Personal"),
        ]
        
        workspaces = []
        for name, desc, cat in workspace_templates:
            owner = random.choice(users)
            workspace = WorkspaceORM(
                id=uuid.uuid4(),
                name=name,
                description=desc,
                category=cat,
                owner_id=owner.id,
                is_active=True
            )
            session.add(workspace)
            workspaces.append(workspace)
            
            # Add owner as workspace member
            member = WorkspaceMemberORM(
                id=uuid.uuid4(),
                workspace_id=workspace.id,
                user_id=owner.id,
                role=WorkspaceRole.OWNER.value,
                joined_at=datetime.now(timezone.utc)
            )
            session.add(member)

        await session.commit()
        for w in workspaces:
            await session.refresh(w)

        # 4. Create 20 Memberships (Admin or Member)
        print("Creating 20 additional memberships...")
        roles = [WorkspaceRole.ADMIN.value, WorkspaceRole.EDITOR.value, WorkspaceRole.VIEWER.value]
        memberships_created = 0
        max_attempts = 100
        attempts = 0
        while memberships_created < 20 and attempts < max_attempts:
            attempts += 1
            workspace = random.choice(workspaces)
            user = random.choice(users)
            
            # Check if already a member
            stmt = select(WorkspaceMemberORM).where(
                WorkspaceMemberORM.workspace_id == workspace.id,
                WorkspaceMemberORM.user_id == user.id
            )
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                member = WorkspaceMemberORM(
                    id=uuid.uuid4(),
                    workspace_id=workspace.id,
                    user_id=user.id,
                    role=random.choice(roles),
                    joined_at=datetime.now(timezone.utc)
                )
                session.add(member)
                memberships_created += 1

        # 5. Create 10 Budgets
        print("Creating 10 budgets...")
        budgets_created = 0
        now = datetime.now(timezone.utc)
        attempts = 0
        while budgets_created < 10 and attempts < max_attempts:
            attempts += 1
            workspace = random.choice(workspaces)
            category = random.choice(default_categories)
            month = now.month
            year = now.year
            
            # Check for duplicates (UniqueConstraint uq_budget_workspace_category_period)
            stmt = select(BudgetORM).where(
                BudgetORM.workspace_id == workspace.id,
                BudgetORM.category_id == category.id,
                BudgetORM.month == month,
                BudgetORM.year == year
            )
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                budget = BudgetORM(
                    id=uuid.uuid4(),
                    workspace_id=workspace.id,
                    owner_id=workspace.owner_id,
                    category_id=category.id,
                    limit_amount=float(random.randint(500, 5000)),
                    month=month,
                    year=year
                )
                session.add(budget)
                budgets_created += 1

        await session.commit()
        print("Seeding completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database with fake data.")
    parser.add_argument("--reset", action="store_true", help="Truncate tables before seeding.")
    args = parser.parse_args()
    
    asyncio.run(seed(reset=args.reset))
