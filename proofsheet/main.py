import os
import uuid
import uvicorn
from fasthtml.common import Link, Input, Select, Option, Button, Group, Label, Div, Img, P, H1, H2, Main, Form, Titled, FileResponse, FastHTML, serve

from sqlite_minutils.db import NotFoundError
from db import initialize_database
from proofsheet.generate import generate_proof
from proofsheet.utils import valid_params
from proofsheet.components.proof_grid import proof_grid
from proofsheet.components.search_form import search_form

# Initialize the FastHTML app
app = FastHTML()

# Our FastHTML app
app = FastHTML(hdrs=(
    Link(rel='stylesheet', href='https://unpkg.com/latex.css/style.min.css', type='text/css'),
    Link(rel='stylesheet', href='/static/styles.css', type='text/css'),
    ),
)

# Initialize the database
db = initialize_database()
proofs = db.t.proofs
Proof = proofs.dataclass()

# Register routes
@app.get("/")
def home():
    # Get all proofs
    # print("proofs", proofs)
    try:
        valid_proofs = proofs()
    except NotFoundError:
        valid_proofs = []

    # print("valid_proofs length", len(valid_proofs))

    # Generate proofs HTML
    if valid_proofs:
        proofs_grid = Div(
            *reversed([proof_grid(p) for p in valid_proofs]),
            id="proofs-container",
            cls="proofs-grid-container",
        )
    else:
        proofs_grid = Div(
            P("No proofs found."),
            id="proofs-container",
            cls="proofs-grid-container",
        )

    return Titled(
        "Proofs",
        Main(
            search_form(),
            proofs_grid,
            cls="container",
        ),
    )
@app.post("/create_proof")
def create_proof(
    prompt: str,
    grid_size: int,
    seed: int,
    x_param: str,
    x_range_start: float,
    x_range_end: float,
    y_param: str,
    y_range_start: float,
    y_range_end: float,
):
    # Validate parameter names
    if x_param not in valid_params or y_param not in valid_params:
        return Div(P("Invalid parameters selected for axes."), cls="error-messages")

    # Validate range values
    errors = []
    if x_range_start >= x_range_end:
        errors.append("X Range Start must be less than X Range End.")
    if y_range_start >= y_range_end:
        errors.append("Y Range Start must be less than Y Range End.")
    if grid_size < 1 or grid_size > 10:
        errors.append("Grid Size must be between 1 and 10.")

    if errors:
        return Div(*[P(error) for error in errors], cls="error-messages")
    # Create a unique folder for the proof
    folder = os.path.join("data", "proofs", str(uuid.uuid4()))
    os.makedirs(folder, exist_ok=True)

    # Insert the new proof into the database
    proof_data = {
        "id": uuid.uuid4(),
        "prompt": prompt,
        "seed": seed,
        "folder": folder,
        "grid_size": grid_size,
        "x_param": x_param,
        "x_range_start": x_range_start,
        "x_range_end": x_range_end,
        "y_param": y_param,
        "y_range_start": y_range_start,
        "y_range_end": y_range_end,
    }
    p = proofs.insert(proof_data)
    

    # Start generating the proof images
    generate_proof(proof_data)

    # Render the new proofshet grid to be appended
    new_proof_html = proof_grid(p)

    # Return the new proofshet HTML to be appended
    return new_proof_html

@app.get("/proofs/{proof_id}/image/{image_id}")
def update_proof_image(proof_id: str, image_id: str):
    p = proofs[proof_id]
    image_path = os.path.join(p.folder, f"{image_id}.png")
    
    if os.path.exists(image_path):
        return Img(
            src=f"/data/{p.folder}/{image_id}.png",
            alt=f"Image {image_id}",
            cls="proof-image",
        )
    else:
        return Div(
            "",
            cls="placeholder",
            id=f"proof-{proof_id}-img-{image_id}",
            hx_get=f"/proofs/{proof_id}/image/{image_id}",
            hx_trigger="every 300ms",
            hx_swap="outerHTML",
        )

@app.get("/static/{fname}.{ext}")
def static_files(fname: str, ext: str):
    return FileResponse(f"static/{fname}.{ext}")

@app.get("/data/{path:path}")
def data_files(path: str):
    return FileResponse(f"{path}")

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
