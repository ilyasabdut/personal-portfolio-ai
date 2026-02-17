import uvicorn
import sys

if __name__ == "__main__":
    try:
        uvicorn.run(
            "src.entrypoints.main_app:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="debug"
        )
    except Exception as e:
        print(f"Failed to start server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        print("Server stopped.")
        sys.exit(0)
