"""Android entry point used by Buildozer."""

__version__ = "0.1.0"

from myra.mobile_app import MyraMobileApp


if __name__ == "__main__":
    MyraMobileApp().run()
