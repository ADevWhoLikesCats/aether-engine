#!/usr/bin/env python3
"""inspect_glb.py - parse a .glb file and print its node hierarchy."""
import json
import struct
import sys

def read_glb(path):
    with open(path, "rb") as f:
        magic, version, length = struct.unpack("<III", f.read(12))
        if magic != 0x46546C67:  # 'glTF'
            sys.exit("Not a valid GLB file")
        
        # Read first chunk (JSON)
        chunk_len, chunk_type = struct.unpack("<II", f.read(8))
        if chunk_type != 0x4E4F534A:  # 'JSON'
            sys.exit("First chunk is not JSON")
        
        json_bytes = f.read(chunk_len)
        data = json.loads(json_bytes.decode("utf-8"))
        return data

def print_tree(data):
    nodes = data.get("nodes", [])
    meshes = data.get("meshes", [])
    scenes = data.get("scenes", [])
    
    print(f"Total nodes: {len(nodes)}")
    print(f"Total meshes: {len(meshes)}")
    print(f"Total scenes: {len(scenes)}")
    print()

    # Build parent map
    parent_map = {}
    for i, node in enumerate(nodes):
        for child in node.get("children", []):
            parent_map[child] = i
            
    def walk(idx, depth=0):
        node = nodes[idx]
        name = node.get("name", f"<node_{idx}>")
        mesh_idx = node.get("mesh")
        
        prefix = "  " * depth
        info = ""
        if mesh_idx is not None:
            mesh = meshes[mesh_idx]
            prim_count = len(mesh.get("primitives", []))
            info = f" [mesh {mesh_idx}, {prim_count} prims]"
        
        # Check for translation
        t = node.get("translation")
        t_str = ""
        if t:
            t_str = f" t=({t[0]:.2f}, {t[1]:.2f}, {t[2]:.2f})"
            
        print(f"{prefix}[{idx}] {name}{info}{t_str}")
        
        for child in node.get("children", []):
            walk(child, depth + 1)
            
    # Walk from scene roots
    if scenes:
        for root in scenes[0].get("nodes", []):
            walk(root)
    else:
        # Fallback: walk from all nodes that have no parents
        roots = [i for i in range(len(nodes)) if i not in parent_map]
        for root in roots:
            walk(root)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 inspect_glb.py <file.glb>")
    
    data = read_glb(sys.argv[1])
    print_tree(data)
