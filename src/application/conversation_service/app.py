import sys
from pathlib import Path

sys.path.append((Path.cwd() / "src").as_posix())

import asyncio
import config as cfg
from utils.s3_utils import S3Utils
import gradio as gr
from application.rag_service.build_index import build_index
from application.rag_service.rag_pipeline import rag_pipe

s3_utils = S3Utils(
    bucket_name=cfg.app.s3.bucket_name, region_name=cfg.app.s3.region_name
)


def create_interface():
    """Create the Gradio interface for the application."""

    with gr.Blocks(title="AWS Documentation Search") as interface:
        gr.Markdown("# AWS Documentation Search")

        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask a question about your documents...",
                    lines=2,
                )
                query_button = gr.Button("Ask")
                response_output = gr.Textbox(
                    label="Response", interactive=False, lines=10
                )
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("# Source Documents ")

                # Dropdown to select a file, choices will be set dynamically
                file_dropdown = gr.Dropdown(
                    choices=[], label="Select a source document", interactive=True
                )

                # Markdown component to display the content of the selected file as rendered markdown inside a box
                file_content_output = gr.Markdown(label="Document Content")

                # Function to load and return the content of the selected file as markdown
                def show_file_content(selected_file):
                    if selected_file:
                        try:
                            # s3_key = f"{cfg.app.s3.folder}/{selected_file}"
                            # return s3_utils.get_file_content(s3_key=s3_key)
                            return s3_utils.mock_get_file_content(selected_file)
                        except Exception as e:
                            return f"Error loading file: {str(e)}"
                    return ""

                file_dropdown.change(
                    show_file_content,
                    inputs=[file_dropdown],
                    outputs=[file_content_output],
                )

        def query_documents(query):
            try:
                result = asyncio.run(rag_pipe.predict(query))
                response = result["response"]
                source_documents = list(result.get("source_documents", []))
                # Update the file_dropdown choices with the new source documents
                file_dropdown.choices = source_documents
                return response, source_documents
            except Exception as e:
                return f"Error processing query: {str(e)}", []

        # Add a hidden output for source documents to update the dropdown choices
        source_docs_output = gr.State([])

        def update_source_docs(source_documents):
            file_dropdown.choices = source_documents
            return gr.update(choices=source_documents)

        query_button.click(
            query_documents,
            inputs=[query_input],
            outputs=[response_output, source_docs_output],
        )

        source_docs_output.change(
            update_source_docs, inputs=[source_docs_output], outputs=[file_dropdown]
        )

    return interface


def main():
    """Main function to launch the Gradio interface."""
    build_index(
        model_provider=cfg.app.model.provider,
        model_name=cfg.app.model.name,
        model_type=cfg.app.model.type,
        vector_db=cfg.app.vector_db.name,
    )
    iface = create_interface()
    iface.launch()


if __name__ == "__main__":
    main()
