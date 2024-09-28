import os
import uuid
import uvicorn
from fasthtml.common import Link, Input, Select, Option, Button, Group, Label, Div, Img, P, H1, H2, Main, Form, Titled, FileResponse, FastHTML, serve

from sqlite_minutils.db import NotFoundError
from db import initialize_database
from proofsheet.generate import generate_proofsheet
from utils import valid_params
from components.proofsheet_grid import proofsheet_grid

# Initialize the FastHTML app
app = FastHTML()

# Our FastHTML app
app = FastHTML(hdrs=(
    Link(rel="stylesheet", href="/static/styles.css", type="text/css"),
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
    inp_prompt = Input(
        name="prompt",
        placeholder="Enter a prompt",
        value="A beautiful landscape",
        required=True,
    )
    inp_grid_size = Input(
        name="grid_size", type="number", min="1", max="10", value="3", required=True
    )
    inp_seed = Input(
        name="seed", type="number", value="42", required=True
    )
    inp_x_param = Select(
        *[Option(param) for param in valid_params], name="x_param", required=True
    )
    inp_x_range_start = Input(
        name="x_range_start",
        type="number",
        step="any",
        placeholder="X Range Start",
        value="1",
        required=True,
    )
    inp_x_range_end = Input(
        name="x_range_end",
        type="number",
        step="any",
        placeholder="X Range End",
        value="50",
        required=True,
    )
    inp_y_param = Select(
        *[Option(param) for param in valid_params], name="y_param", required=True
    )
    inp_y_range_start = Input(
        name="y_range_start",
        type="number",
        step="any",
        placeholder="Y Range Start",
        value="0.1",
        required=True,
    )
    inp_y_range_end = Input(
        name="y_range_end",
        type="number",
        step="any",
        placeholder="Y Range End",
        value="10.0",
        required=True,
    )

    add_form = Form(
        Group(inp_prompt, inp_grid_size, inp_seed),
        Group(inp_x_param, Group(inp_x_range_start, inp_x_range_end)),
        Group(inp_y_param, Group(inp_y_range_start, inp_y_range_end)),
        Button("Generate"),
        hx_post="/create_proofsheet",
        hx_swap="afterbegin",  # Prepends the new proofsheet
        hx_target="#proofs-container",  # Target the container where proofs are displayed
        hx_trigger="submit",
    )

    # Get all proofs
    print("proofs", proofs)
    try:
        valid_proofs = proofs(limit=10)
    except NotFoundError:
        valid_proofs = []

    # Generate proofs HTML
    if valid_proofs:
        proofs_grid = Div(
            *reversed([proofsheet_grid(p) for p in valid_proofs]),
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
            add_form,
            proofs_grid,
            cls="container",
        ),
    )
@app.post("/create_proofsheet")
def create_proofsheet(
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
    # Create a unique folder for the proofsheet
    folder = os.path.join("data", "proofs", str(uuid.uuid4()))
    os.makedirs(folder, exist_ok=True)

    # Insert the new proofsheet into the database
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
    

    # Start generating the proofsheet images
    generate_proofsheet(proof_data)

    # Render the new proofshet grid to be appended
    new_proofsheet_html = proofsheet_grid(p)

    # Return the new proofshet HTML to be appended
    return new_proofsheet_html

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
            "Still generating...",
            cls="placeholder",
            id=f"proof-{proof_id}-img-{image_id}",
            hx_get=f"/proofs/{proof_id}/image/{image_id}",
            hx_trigger="every 2s",
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
