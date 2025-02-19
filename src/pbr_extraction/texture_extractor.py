from pygltflib import GLTF2


def extract_pbr_textures(glb_file):
    """
    Extracts PBR material data from a GLB file.

    Args:
        glb_file: The path to the GLB file.

    Returns:
        A list of dictionaries containing the PBR material data for each material in the GLB file.
        Each dictionary has the following key-value pairs:
            - base_color_texture: The texture index of the base color texture.
            - metallic_roughness_texture: The texture index of the metallic roughness texture.
            - roughness_factor: The roughness factor value.
            - metallic_factor: The metallic factor value.
            - normal_texture: The texture index of the normal map texture.
    """
    gltf = GLTF2.load(glb_file)

    materials_info = []

    for material in gltf.materials:
        material_data = {}

        # PBR Metallic Roughness
        if hasattr(material.pbrMetallicRoughness, "baseColorTexture"):
            base_color_texture = material.pbrMetallicRoughness.baseColorTexture
            material_data["base_color_texture"] = (
                gltf.textures[base_color_texture.index].source
                if base_color_texture
                else "No Texture"
            )

        if hasattr(material.pbrMetallicRoughness, "metallicRoughnessTexture"):
            metallic_roughness_texture = material.pbrMetallicRoughness.metallicRoughnessTexture
            material_data["metallic_roughness_texture"] = (
                gltf.textures[metallic_roughness_texture.index].source
                if metallic_roughness_texture
                else "No Texture"
            )

        # Roughness & Metallic Values
        if hasattr(material.pbrMetallicRoughness, "roughnessFactor"):
            material_data["roughness_factor"] = material.pbrMetallicRoughness.roughnessFactor

        if hasattr(material.pbrMetallicRoughness, "metallicFactor"):
            material_data["metallic_factor"] = material.pbrMetallicRoughness.metallicFactor

        # Normal map
        if hasattr(material, "normalTexture"):
            normal_texture = material.normalTexture
            material_data["normal_texture"] = (
                gltf.textures[normal_texture.index].source
                if normal_texture
                else "No Texture"
            )

        materials_info.append(material_data)

    return materials_info
