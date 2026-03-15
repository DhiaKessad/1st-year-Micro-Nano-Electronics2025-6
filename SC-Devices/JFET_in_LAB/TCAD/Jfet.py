import devsim

device_name = "J113"
region_name = "bulk"
mesh_name   = "jfet_mesh"

devsim.create_2d_mesh(mesh=mesh_name)
devsim.add_2d_mesh_line(mesh=mesh_name, dir="x", pos=0.0, ps=0.5e-5)
devsim.add_2d_mesh_line(mesh=mesh_name, dir="x", pos=5.0e-4, ps=0.5e-5)
devsim.add_2d_mesh_line(mesh=mesh_name, dir="y", pos=0.0, ps=0.1e-5)
devsim.add_2d_mesh_line(mesh=mesh_name, dir="y", pos=1.0e-4, ps=0.1e-5)

devsim.add_2d_region(mesh=mesh_name, region=region_name, material="Silicon")
devsim.add_2d_contact(mesh=mesh_name, region=region_name, name="source", material="Metal", xl=0.0, xh=0.0, yl=0.0, yh=1.0e-4)
devsim.add_2d_contact(mesh=mesh_name, region=region_name, name="drain", material="Metal", xl=5.0e-4, xh=5.0e-4, yl=0.0, yh=1.0e-4)
devsim.add_2d_contact(mesh=mesh_name, region=region_name, name="gate", material="Metal", xl=1.5e-4, xh=3.5e-4, yl=1.0e-4, yh=1.0e-4)
devsim.finalize_mesh(mesh=mesh_name)
devsim.create_device(mesh=mesh_name, device=device_name)

devsim.node_solution(device=device_name, region=region_name, name="NetDoping")
devsim.node_solution(device=device_name, region=region_name, name="Potential")

x_nodes = devsim.get_node_model_values(device=device_name, region=region_name, name="x")
y_nodes = devsim.get_node_model_values(device=device_name, region=region_name, name="y")

doping_values = []
potential_values = [0.0] * len(x_nodes)

eps = 1e-8
for x, y in zip(x_nodes, y_nodes):
    if ((1.5e-4 - eps) <= x <= (3.5e-4 + eps)) and (y >= (0.8e-4 - eps)):
        doping_values.append(-1.0e18)
    else:
        doping_values.append(1.61e16)

devsim.set_node_values(device=device_name, region=region_name, name="NetDoping", values=doping_values)
devsim.set_node_values(device=device_name, region=region_name, name="Potential", values=potential_values)

devsim.write_devices(file="j113_physics.vtk", type="vtk")

print("SUCCESS: J113 array length:", len(doping_values))
print("MIN NetDoping:", min(doping_values))
print("MAX NetDoping:", max(doping_values))
