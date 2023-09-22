from fastapi import FastAPI
from .processor_api.router import router as processor_router
from .compute_resource_api.router import router as compute_resource_router
from .client_api.router import router as client_router
from .gui_api.router import router as gui_router


app = FastAPI()

# requests from a processing job
app.include_router(processor_router)

# requests from a compute resource
app.include_router(compute_resource_router)

# requests from a client (usually Python)
app.include_router(client_router)

# requests from the GUI
app.include_router(gui_router)