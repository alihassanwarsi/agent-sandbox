from app.db.database import Base, engine
from app.db.models import ApprovalRequestORM

Base.metadata.create_all(engine)
print("Tables created.")