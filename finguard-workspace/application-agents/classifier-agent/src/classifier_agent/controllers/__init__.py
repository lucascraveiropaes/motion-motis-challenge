"""Route handlers grouped by resource."""

from classifier_agent.controllers.agent_controller import router as agent_router
from classifier_agent.controllers.classify_controller import router as classify_router

__all__ = ["agent_router", "classify_router"]
