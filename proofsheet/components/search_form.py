from fasthtml.common import Form, Input, Select, Option, Group, Button
from proofsheet.utils import valid_params

def search_form():
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
        hx_post="/create_proof",
        hx_swap="afterbegin",  # Prepends the new proof
        hx_target="#proofs-container",  # Target the container where proofs are displayed
        hx_trigger="submit",
    )

    return add_form
