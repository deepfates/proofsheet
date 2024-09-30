from fasthtml.common import Div, P, Figure, Small 
from sqlite_minutils.db import NotFoundError 

from proofsheet.utils import calculate_range

def proof_grid(p):
    try:
        grid_cells = []
        grid_size = p.grid_size
        
        # Calculate x and y values
        x_values = calculate_range(p.x_range_start, p.x_range_end, p.grid_size, p.x_param)
        y_values = calculate_range(p.y_range_start, p.y_range_end, p.grid_size, p.y_param)

        for i in range(grid_size):  # y-axis (rows)
            row = []
            for j in range(grid_size):  # x-axis (columns)
                image_id = f"{i}_{j}"
                cell_id = f"proof-{p.id}-img-{image_id}"

                cell_content = Div(
                    "Loading...",
                    cls="placeholder",
                    id=f"content-{cell_id}",
                    hx_get=f"/proofs/{p.id}/image/{image_id}",
                    hx_trigger="load",
                    hx_swap="outerHTML",
                )
                caption = Div( 
                    f"{x_values[i]:.1f}, {y_values[j]:.1f}",
                    cls="caption"
                )

                cell = Figure(
                    cell_content,
                    caption,
                    id=cell_id,
                    cls="cell",
                )
                row.append(cell)
            grid_cells.append(Div(*row, cls="grid-row"))

        grid = Div(*grid_cells, cls="proof-grid", style=f"--grid-size: {grid_size};")

        return Div(
            Div(
                P(f"{p.prompt} /{p.seed}"),
                Small(f"{p.x_param}, {p.y_param}"),
                cls="generation-prompt"
            ),
            grid,
            cls="proof-card",
        )
    except NotFoundError:
        return Div(P("proof not found."), cls="error")
