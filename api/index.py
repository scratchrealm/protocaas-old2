from fastapi import FastAPI
from .routers.processor.router import router as processor_router
from .routers.compute_resource.router import router as compute_resource_router
from .routers.client.router import router as client_router
from .routers.gui.router import router as gui_router


app = FastAPI()

# requests from a processing job
app.include_router(processor_router, prefix="/api/processor")

# requests from a compute resource
app.include_router(compute_resource_router, prefix="/api/compute_resource")

# requests from a client (usually Python)
app.include_router(client_router, prefix="/api/client")

# requests from the GUI
app.include_router(gui_router, prefix="/api/gui")