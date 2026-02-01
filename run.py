#!/usr/bin/env python
"""
Simple launcher script for the AI Dual-Use Risk Assessor
"""
import uvicorn


def main():
    print("=" * 50)
    print("AI Dual-Use Risk Assessor")
    print("=" * 50)
    print("\nStarting server at http://localhost:8000")
    print("Press Ctrl+C to stop\n")

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
