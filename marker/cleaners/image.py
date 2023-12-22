import fitz as pymupdf
import magic
from azure.storage.blob import BlobServiceClient, ContentSettings

from marker.bbox import correct_rotation
from marker.schema import Span, Line, Block
from marker.settings import settings


def upload_to_azure_blob(image: bytes, blob_name: str):
    # Create a blob service client
    blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(settings.AZURE_STORAGE_CONTAINER_NAME)

    # Upload the image
    content_settings = ContentSettings(content_type=magic.from_buffer(image, mime=True))
    blob_client = container_client.upload_blob(name=blob_name, data=image, content_settings=content_settings)

    return blob_client.url


def get_image_block(doc_path_name: str, page: pymupdf.Page, pnum: int, block: dict, block_idx: int):
    if block["type"] != 1:
        raise ValueError("Block is not an image block")

    image_id = f"image_{pnum}_{block_idx}"
    image_blob_name = f"{doc_path_name}/{image_id}.{block['ext']}"
    image_url = upload_to_azure_blob(block["image"], image_blob_name)

    bbox = correct_rotation(block["bbox"], page)
    span_obj = Span(
        text=f"![alt image text]({image_url})",
        bbox=bbox,
        span_id=image_id,
        font="Arial",
        color=0,
    )
    line_obj = Line(
        spans=[span_obj],
        bbox=bbox
    )
    block_obj = Block(
        lines=[line_obj],
        bbox=bbox,
        pnum=pnum
    )
    return block_obj

