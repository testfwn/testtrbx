from aiohttp import web
import os

routes = web.RouteTableDef()


# Route to check the service status
@routes.get("/", allow_head=True)
async def root_route_handler(_):
    response = {"status": "running v3"}
    return web.json_response(response)


# Route to display the log data
@routes.get("/logs", allow_head=True)
async def get_logs_handler(_):
    try:
        with open("log.txt", "r", encoding="utf-8") as file:
            log_data = file.read()
        return web.Response(text=log_data, content_type="text/plain")
    except FileNotFoundError:
        return web.Response(text="Log file not found.", status=404)
    except Exception as e:
        return web.Response(text=f"Error reading log file: {e}", status=500)


# Route to truncate the log data
@routes.get("/delete-logs")
async def truncate_logs_handler(_):
    try:
        open("log.txt", "w").close()  # Truncate the log file
        return web.json_response(
            {"status": "success", "message": "Log file truncated successfully."}
        )
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


# Application setup
async def web_server():
    app = web.Application()
    app.add_routes(routes)
    return app
