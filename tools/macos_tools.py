import subprocess
import json

def open_application(app_name: str) -> str:
    """
    Opens a specific application on macOS.
    
    Args:
        app_name: The name of the application to open (e.g., 'Safari', 'Spotify', 'Calendar').
        
    Returns:
        A status message indicating whether the application was successfully opened.
    """
    try:
        # Using "open -a" to launch the app by name
        result = subprocess.run(
            ["open", "-a", app_name],
            capture_output=True,
            text=True,
            check=True
        )
        return json.dumps({
            "status": "success",
            "message": f"Successfully requested macOS to open '{app_name}'."
        })
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or f"Application '{app_name}' not found."
        return json.dumps({
            "status": "error",
            "message": f"Failed to open '{app_name}': {error_msg}"
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        })
