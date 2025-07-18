import pytest
from src.application.conversation_service import create_interface


def test_create_ui():
    """
    Tests that the Gradio UI is created without errors.
    """
    try:
        ui = create_interface()
        assert ui is not None
    except Exception as e:
        pytest.fail(f"UI creation failed with an exception: {e}")
