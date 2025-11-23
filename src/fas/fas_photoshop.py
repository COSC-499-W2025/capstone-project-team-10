from typing import Dict, Any
from psd_tools import PSDImage

def extract_photoshop_data(file_path: str) -> Dict[str, Any]:
    """
    Extract key metadata and file insights from a Photoshop (.psd) file.
    Works with psd-tools >= 2.0.
    """
    try:
        psd: PSDImage = PSDImage.open(file_path)
    except FileNotFoundError:
        return {"error": f"File not found: {file_path}"}
    except ValueError as e:
        return {"error": f"Unsupported PSD color mode: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to open PSD: {str(e)}"}

    metadata: Dict[str, Any] = {
        "width": getattr(psd, "width", None),
        "height": getattr(psd, "height", None),
        "number_of_layers": len(psd),
        "color_mode": getattr(psd, "color_mode", "Unknown"),
        "bit_depth": getattr(psd, "bits_per_channel", None),
    }

    # ICC profile and compression
    metadata["icc_profile"] = getattr(psd, "color_profile", None)
    metadata["compression"] = getattr(psd, "compression", None)

    # Layers
    layers = {}
    for layer in psd:
        layers[layer.name] = {
            "visible": getattr(layer, "visible", None),
            "opacity": getattr(layer, "opacity", None),
            "blend_mode": getattr(layer, "blend_mode", None),
            "bbox": getattr(layer, "bbox", None),
            "has_mask": getattr(layer, "has_mask", lambda: False)(),
        }
    metadata["layers"] = layers

    # Image resources
    image_resources = getattr(psd, "image_resources", {})
    metadata["resolution_info"] = str(image_resources.get("ResolutionInfo", None))
    metadata["xmp_metadata"] = str(image_resources.get("XMPMetadata", None))
    metadata["thumbnail"] = "Available" if "Thumbnail" in image_resources else "None"

    return metadata
