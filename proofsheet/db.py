from fasthtml.common import database

# Initialize the database globally
db = None

def initialize_database():
    global db
    if db is None:
        # Database setup
        db = database('data/proofs.db')
        if 'proofs' not in db.t:
            db.t.proofs.create(
                prompt=str,
                id=str,
                folder=str,
                pk='id',
                grid_size=int,
                x_param=str,
                x_range_start=float,
                x_range_end=float,
                y_param=str,
                y_range_start=float,
                y_range_end=float,
                seed=int
            )
        db.t.proofs.dataclass()
    return db
