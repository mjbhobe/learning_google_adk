from buffet_bot.common.a2a_server import create_app
from .task_manager import run

# -----------------------------------------------------------------------------
# this line is the star of our show!! Let's unpack it from the inside out:
#
#    type("Agent", (), {"execute": run})
#
# This is Python's dynamic class creation using the built-in type() function. 
# Its three arguments are:
# This is Python's dynamic class creation using the built-in type() function. 
# Its three arguments are:
#   - "Agent" - The name of the new class
#   - () - No base classes (inherits from object)
#   - dict	{"execute": run}	The class body — a single method called execute,
#       pointing to the run function
# It's effectively equivalent to writing this class by hand:
#
# class Agent:
#     execute = run   # run is the async function from task_manager
#
# Why do this? 
#
#   create_app()
# expects an agent object with an execute method (look at a2a_server.py)
#   await agent.execute(payload)). 
# Rather than formally defining a full class just to satisfy that interface, 
# a quick anonymous class is created on the fly using type()
# -----------------------------------------------------------------------------

app = create_app(agent=type("Agent", (), {"execute": run}))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
