import base64
from io import BytesIO
import os
from PIL import Image
import torch
from OmniParser.utils import (
    check_ocr_box,
    get_yolo_model,
    get_caption_model_processor,
    get_som_labeled_img
)

def test_image_parsing(
    image_path: str,
    box_threshold: float = 0.05,
    iou_threshold: float = 0.1,
    use_paddleocr: bool = True,
    imgsz: int = 640,
    output_dir: str = "caption_test_results"
):
    """
    Process an image with OmniParser to get bounding boxes, captions, and annotated visualization.
    
    Args:
        image_path: Path to input image
        box_threshold: Confidence threshold for box detection
        iou_threshold: IOU threshold for box overlap
        use_paddleocr: Whether to use PaddleOCR instead of EasyOCR
        imgsz: Size for icon detection
        output_dir: Directory to save results
    """
    print(f"Processing image: {image_path}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load image and get size ratio for box drawing
    image = Image.open(image_path)
    box_overlay_ratio = image.size[0] / 3200
    
    # Configure box drawing parameters
    draw_bbox_config = {
        'text_scale': 0.8 * box_overlay_ratio,
        'text_thickness': max(int(2 * box_overlay_ratio), 1),
        'text_padding': max(int(3 * box_overlay_ratio), 1),
        'thickness': max(int(3 * box_overlay_ratio), 1),
    }
    
    # Initialize models
    print("Loading models...")
    yolo_model = get_yolo_model(model_path='OmniParser/weights/icon_detect/best.pt')
    caption_model_processor = get_caption_model_processor(
        model_name="florence2",
        model_name_or_path="OmniParser/weights/icon_caption_florence"
    )
    
    # Get OCR results
    print("Running OCR detection...")
    ocr_results, _ = check_ocr_box(
        image_path,
        display_img=False,
        output_bb_format='xyxy',
        goal_filtering=None,
        easyocr_args={'paragraph': False, 'text_threshold': 0.9},
        use_paddleocr=use_paddleocr
    )
    text, ocr_bbox = ocr_results
    
    # Process image with OmniParser
    print("Running element detection and captioning...")
    dino_labeled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
        image_path,
        yolo_model,
        BOX_TRESHOLD=box_threshold,
        output_coord_in_ratio=True,
        ocr_bbox=ocr_bbox,
        draw_bbox_config=draw_bbox_config,
        caption_model_processor=caption_model_processor,
        ocr_text=text,
        iou_threshold=iou_threshold,
        imgsz=imgsz,
        use_local_semantics=True  # Enable captioning
    )
    
    # Save results
    print("\nResults:")
    
    # Save annotated image
    annotated_image = Image.open(BytesIO(base64.b64decode(dino_labeled_img)))  # Decode base64 image
    annotated_output_path = os.path.join(output_dir, "annotated_image.png")
    annotated_image.save(annotated_output_path)
    print(f"Saved annotated image to: {annotated_output_path}")
    
    # Print and save element information
    elements_output_path = os.path.join(output_dir, "element_info.txt")
    with open(elements_output_path, 'w') as f:
        # First print OCR text boxes
        for idx, (text_content, bbox) in enumerate(zip(text, ocr_bbox)):
            element_info = f"Element {idx} (Text):\n"
            element_info += f"  Content: {text_content}\n"
            element_info += f"  Bounding Box (xyxy): {bbox}\n"
            print(element_info)
            f.write(element_info + "\n")
       
        # Then print detected UI elements
        start_idx = len(text)
        for idx, (label, coords) in enumerate(label_coordinates.items(), start=start_idx):
            if idx < len(parsed_content_list):
                content = parsed_content_list[idx].split(': ')[1]
                if content.strip():  # Filter out empty UI elements
                    element_info = f"Element {idx} (UI):\n"
                    element_info += f"  Caption: {content}\n"
                    element_info += f"  Coordinates (xywh): {coords}\n"
                    print(element_info)
                    f.write(element_info + "\n")
                    
    print(f"Saved element information to: {elements_output_path}")
    
    return {
        'annotated_image': annotated_output_path,
        'elements_file': elements_output_path,
        'text_elements': list(zip(text, ocr_bbox)),
        'ui_elements': list(zip(label_coordinates.items(), parsed_content_list[len(text):]))
    }

if __name__ == "__main__":
    # Example usage
    test_images = [
        "results/20241119_13_37_49/taskArXiv--7/screenshot_raw1.png",
    ]
    
    for image_path in test_images:
        try:
            print(f"\nProcessing {image_path}")
            print("=" * 80)
            results = test_image_parsing(image_path)
            print(f"Successfully processed {image_path}")
            print("-" * 80)
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
