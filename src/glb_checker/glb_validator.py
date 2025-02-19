import trimesh
import logging
import numpy as np
from pathlib import Path


class GLBMeshValidator:
    MAX_FACES = 64000
    SEVERITY_THRESHOLD = 0.7
    OFFSET_SCALE_FACTOR = 5e-5

    def __init__(self, mesh_path):
        self.mesh_path = mesh_path
        self.errors = []

    def load_mesh(self):
        """
        Loads a mesh from the specified path.

        Checks for the following issues:

        - Multiple objects in a scene (e.g., a GLTF file with more than one mesh)
        - Invalid mesh type

        Returns the loaded mesh if no issues are found.
        Returns None if any issues are found.
        """
        try:
            mesh = trimesh.load(self.mesh_path)

            # Check for multiple objects in a scene (e.g., a GLTF file with more than one mesh)
            if isinstance(mesh, trimesh.Scene):
                # If the scene contains more than one object, report it
                if len(mesh.geometry) > 1:
                    self.errors.append(
                        f"Scene contains multiple objects: {len(mesh.geometry)} objects found."
                    )
                    return None
                # If it contains only one object, proceed with the first mesh
                return self._extract_first_mesh_from_scene(mesh)

            if isinstance(mesh, trimesh.path.path.Path3D):
                return self._convert_path3d_to_mesh(mesh)

            if not isinstance(mesh, trimesh.Trimesh):
                self.errors.append(f"Invalid mesh type: {type(mesh)}")
                return None

            return mesh
        except Exception as e:
            self.errors.append(f"Error loading mesh: {str(e)}")
            return None

    def _extract_first_mesh_from_scene(self, scene):
        meshes = list(scene.geometry.values())
        if meshes:
            return meshes[0]
        else:
            self.errors.append("Scene contains no meshes.")
            return None

    def _convert_path3d_to_mesh(self, path_obj):
        self.errors.append("Detected Path3D object.")
        converted_mesh = path_obj.to_mesh()
        if converted_mesh:
            self.errors.append("Converted Path3D to Trimesh.")
            return converted_mesh
        else:
            self.errors.append("Failed to convert Path3D to mesh.")
            return path_obj

    def validate(self):
        """
        Validates a mesh object against a set of criteria.

        Returns:
            tuple: A tuple containing two elements:
                - success (bool): True if the mesh is valid, False otherwise.
                - error_messages (list): A list of error messages if the mesh is invalid.
        """
        mesh = self.load_mesh()
        if not mesh:
            return False, self.errors

        checks = [
            self.check_face_count(mesh),
            self.check_empty_mesh(mesh),
            self.check_degenerate_faces(mesh),
            self.detect_severe_self_intersections(mesh),
            # self.check_edge_lengths(mesh),
            # self.check_aspect_ratio(mesh),
            self.check_normals_consistency(mesh),
        ]
        return all(checks), self.errors

    def check_face_count(self, mesh):
        if len(mesh.faces) > self.MAX_FACES:
            self.errors.append(f"Too many faces ({len(mesh.faces)}).")
            return False
        return True

    def check_empty_mesh(self, mesh):
        if len(mesh.faces) == 0:
            self.errors.append("Mesh has no faces.")
            return False
        return True

    def check_degenerate_faces(self, mesh):
        areas = mesh.area_faces
        if np.any(areas < 1e-10):
            self.errors.append("Mesh has degenerate faces.")
            return False
        return True

    def detect_severe_self_intersections(self, mesh):
        """
        Checks for severe self-intersections in a mesh.

        This function offsets each face by a small amount and checks for collisions with the rest of the mesh. If the number of colliding faces exceeds a certain threshold, the mesh is considered to have severe self-intersections.

        Args:
            mesh (trimesh.Trimesh): The mesh to check for self-intersections.

        Returns:
            bool: True if the mesh has no severe self-intersections, False otherwise.
        """
        try:
            bvh = trimesh.collision.CollisionManager()
            bvh.add_object("mesh", mesh)
            severe_intersections = []

            for i, face in enumerate(mesh.faces):
                face_vertices = np.array(mesh.vertices[face])
                if face_vertices.shape != (3, 3):
                    self.errors.append(
                        f"Skipping face {i} due to incorrect shape: {face_vertices.shape}"
                    )
                    continue

                offset = (
                    np.mean(face_vertices, axis=0, keepdims=True)
                    * self.OFFSET_SCALE_FACTOR
                )
                perturbed_face = face_vertices + offset

                try:
                    collisions = bvh.in_collision_single(
                        trimesh.Trimesh(vertices=perturbed_face, faces=[[0, 1, 2]])
                    )
                    if collisions:
                        severe_intersections.append(i)
                except Exception as e:
                    self.errors.append(f"Error processing face {i}: {e}")
                    continue

            if len(severe_intersections) / len(mesh.faces) > self.SEVERITY_THRESHOLD:
                self.errors.append(
                    f"Severe self-intersections detected: {len(severe_intersections)} faces."
                )
                return False

            return True
        except Exception as e:
            self.errors.append(f"Error detecting self-intersections: {e}")
            return False

    def check_edge_lengths(self, mesh):
        """
        Checks that the edge lengths in the mesh are within a reasonable range.

        Args:
            mesh (trimesh.Trimesh): The mesh to check.

        Returns:
            bool: True if the mesh has edge lengths within a reasonable range, False otherwise.
        """
        edges = mesh.edges_unique_length
        min_length, max_length = np.min(edges), np.max(edges)

        if min_length < 1e-6:
            self.errors.append("Mesh has extremely short edges.")
            return False
        if max_length > 10:
            self.errors.append("Mesh has extremely long edges.")
            return False
        return True

    def check_aspect_ratio(self, mesh):
        """
        Checks that the aspect ratio of the mesh's faces is reasonable.

        A high aspect ratio indicates that a face is thin or stretched, which
        can be problematic for some downstream applications. This check
        ensures that the aspect ratio of all faces is above a certain threshold.

        Args:
            mesh (trimesh.Trimesh): The mesh to check.

        Returns:
            bool: True if the mesh has reasonable aspect ratios, False otherwise.
        """
        aspect_ratios = mesh.area_faces / (mesh.edges_unique_length.max() ** 2)
        if np.any(aspect_ratios < 1e-3):
            self.errors.append(
                "Mesh contains faces with high aspect ratios (thin or stretched)."
            )
            return False
        return True

    def check_normals_consistency(self, mesh):
        """
        Checks that the mesh's face normals are consistently oriented.

        Args:
            mesh (trimesh.Trimesh): The mesh to check.

        Returns:
            bool: True if the mesh has consistently oriented face normals, False otherwise.
        """
        if not mesh.is_winding_consistent:
            self.errors.append("Mesh has inconsistent face normal orientations.")
            return False
        return True
