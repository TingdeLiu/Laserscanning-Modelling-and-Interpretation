# Functions to support the laserscanning exercise in classification.
#
# (c) 07 DEC 2021  Claus Brenner
import numpy as np
import plyfile

# Helper to generate PLY file.
# xyz is assumed to contain channels: X, Y, Z, reflectance, rel_height
# shaped as (channels, rows, columns).
# feature_list is a list of tuples (feature_name, feature_array),
# one tuple for each feature channel. feature_array must have shape
# (rows, columns).
def write_ply_file(xyz, feature_list = [],
                   ply_filename = "output.ply",
                   write_row_col = False):
    
    # First get validity mask. A point is invalid if it is (0,0,0).
    valid = np.logical_or(np.logical_or(
        xyz[0] != 0.0, xyz[1] != 0.0), xyz[2] != 0.0)
    valid_count = np.sum(valid)

    # Generate and fill array for binary ply write.
    dtype = np.dtype([("x", "<f4"), ("y", "<f4"), ("z", "<f4"),
                      ("reflectance", "<f4"), ("rel_height", "<f4")] +\
                     ([("strip_row", "<f4"), ("strip_column", "<f4")] if\
                      write_row_col else []) +\
                     [ (name, "<f4") for name, _ in feature_list ])
    # Allocate data.
    data = np.empty((valid_count,), dtype=dtype)
    # Add basic data from xyz.
    data["x"] = xyz[0][valid]
    data["y"] = xyz[1][valid] 
    data["z"] = xyz[2][valid]
    data["reflectance"] = xyz[3][valid]
    data["rel_height"] = xyz[4][valid]
    # Add row and column, if requested.
    if write_row_col:
        cm, rm = np.meshgrid(np.arange(xyz.shape[2]),
                             np.arange(xyz.shape[1]))
        data["strip_row"] = rm[valid]
        data["strip_column"] = cm[valid]
    # Add additional features from feature list.
    for name, values in feature_list:
        data[name] = values[valid]

    # Write PLY.
    with open(ply_filename, "w") as ply:
        print("ply\n"
              "format binary_little_endian 1.0\n"
              "comment Written by support_functions.py\n"
              "comment coordinate_system is local\n"
              "element vertex %d\n"
              "property float x\n"
              "property float y\n"
              "property float z\n"
              "property float reflectance\n"
              "property float rel_height\n" % valid_count, file=ply)
        if write_row_col:
            print("property float strip_row\nproperty float strip_column",
                  file=ply)
        for name, _ in feature_list:
            print("property float %s" % name, file=ply)
        print("end_header", file=ply)
        data.tofile(ply)
        

# Readback labels from a ply file.
def read_back_labels_from_ply_file(ply_filename,
    scanstrip_row_name = "scalar_strip_row",
    scanstrip_column_name = "scalar_strip_column",
    scanstrip_label_name = "scalar_label"):

    # Get PLY contents.
    data = plyfile.PlyData.read(ply_filename)
    vertices = data["vertex"]

    # Return arrays: row, column, label.
    return vertices[scanstrip_row_name].astype(np.uint16),\
           vertices[scanstrip_column_name].astype(np.uint32),\
           vertices[scanstrip_label_name].astype(np.int32)
    

if __name__ == "__main__":

    # Example conversion.
    npy_path = "./original_as_npy/"
    one_scanstrip_name = "210903_123403_Scanner_1"

    # Get data.
    xyz = np.load(npy_path + one_scanstrip_name + ".npy")

    # Write to PLY.
    write_ply_file(xyz, feature_list = [("label", np.zeros_like(xyz[0]))],
                   ply_filename = one_scanstrip_name + ".ply")
