from pkg_resources import resource_filename
from py_md_doc import PyMdDoc, ClassInheritance
from py_md_doc.var_doc import VarDoc
from tdw.dev.config import Config
from tdw.dev.code_gen.cs_xml.util import recreate_directory


class PyDocGen:
    """
    Generate documentation for Python classes.
    """

    @staticmethod
    def generate() -> None:
        """
        Generate the documentation.
        """

        c = Config()
        output_directory = c.tdw_docs_path.joinpath("docs/python_api")
        recreate_directory(output_directory)
        # Add documentation for add-ons.
        add_ons_output_directory = output_directory.joinpath("add_ons")
        add_ons_input_directory = c.tdw_path.joinpath("Python/tdw/add_ons")
        add_ons_import_path = "tdw.add_ons"
        add_ons_import_prefix = f"from {add_ons_import_path}"
        ClassInheritance().get_from_directory(input_directory=add_ons_input_directory,
                                              output_directory=add_ons_output_directory,
                                              import_prefix=add_ons_import_prefix,
                                              import_path=add_ons_import_path,
                                              overrides={"Vr": "VR",
                                                         "v_r": "vr",
                                                         "Ui": "UI",
                                                         "u_i": "ui",
                                                         "VrayExporter": "VRayExporter",
                                                         "v_ray_exporter": "vray_exporter"},
                                              excludes=["avatar_body.py"])
        # Add documentation for UI widget add-ons.
        ui_widgets_output_directory = output_directory.joinpath("add_ons/ui_widgets")
        ui_widgets_input_directory = c.tdw_path.joinpath("Python/tdw/add_ons/ui_widgets")
        ui_widgets_import_path = "tdw.add_ons.ui_widgets"
        ui_widgets_import_prefix = f"from {ui_widgets_import_path}"
        ClassInheritance().get_from_directory(input_directory=ui_widgets_input_directory,
                                              output_directory=ui_widgets_output_directory,
                                              import_prefix=ui_widgets_import_prefix,
                                              import_path=ui_widgets_import_path)
        # Add documentation with metadata.
        add_ons_metadata_path = resource_filename(__name__, "add_on_metadata.json")
        md = PyMdDoc(input_directory=add_ons_input_directory,
                     files=[],
                     metadata_path=add_ons_metadata_path)
        for add_on, class_name in zip(["replicant", "wheelchair_replicant"],
                                      ["Replicant", "WheelchairReplicant"]):
            add_on_doc_path = add_ons_output_directory.joinpath(f"{add_on}.md")
            add_on_doc = add_on_doc_path.read_text(encoding="utf-8")
            add_on_doc = md.sort_by_metadata(class_name=class_name, doc=add_on_doc)
            add_on_doc_path.write_text(add_on_doc)
        # Add documentation for Wheelchair Replicants.
        wheelchair_replicant_input_directory = c.tdw_path.joinpath("Python/tdw/wheelchair_replicant")
        wheelchair_replicant_output_directory = output_directory.joinpath("wheelchair_replicant")
        md = PyMdDoc(input_directory=wheelchair_replicant_input_directory,
                     files=["wheel_values.py"])
        md.get_docs(output_directory=wheelchair_replicant_output_directory)
        # Add documentation for Wheelchair Replicant actions.
        wheelchair_replicant_actions_input_directory = wheelchair_replicant_input_directory.joinpath("actions")
        wheelchair_replicant_actions_output_directory = wheelchair_replicant_output_directory.joinpath("actions")
        wheelchair_replicant_actions_import_path = "tdw.wheelchair_replicant.actions"
        wheelchair_replicant_actions_import_prefix = f"from {wheelchair_replicant_actions_import_path}"
        ClassInheritance().get_from_directory(input_directory=wheelchair_replicant_input_directory.joinpath("actions"),
                                              output_directory=wheelchair_replicant_output_directory.joinpath("actions"),
                                              import_path=wheelchair_replicant_actions_import_path,
                                              import_prefix=f"from {wheelchair_replicant_actions_import_path}")
        md = PyMdDoc(input_directory=wheelchair_replicant_actions_input_directory,
                     files=["wheelchair_motion.py"])
        md.get_docs(output_directory=wheelchair_replicant_actions_output_directory,
                    import_prefix=wheelchair_replicant_actions_import_prefix)
        wheelchair_motion_path = wheelchair_replicant_actions_output_directory.joinpath("wheelchair_motion.md")
        wheelchair_motion_text = wheelchair_motion_path.read_text(encoding="utf-8")
        replicant_actions_directory = output_directory.joinpath("replicant/actions").resolve()
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/replicant/actions").resolve(),
                     files=["action.py"])
        md.get_docs(replicant_actions_directory)
        replicant_action_text = replicant_actions_directory.joinpath("action.md").read_text(encoding="utf-8")
        ci = ClassInheritance()
        wheelchair_motion_text = ci.get_from_text(child_text=wheelchair_motion_text,
                                                  parent_texts=[replicant_action_text])
        wheelchair_motion_path.write_text(wheelchair_motion_text)
        wheelchair_move_to_path = wheelchair_replicant_actions_output_directory.joinpath("move_to.md")
        wheelchair_move_to_path.write_text(ci.get_from_text(child_text=wheelchair_move_to_path.read_text(encoding="utf-8"),
                                                            parent_texts=[replicant_action_text]))

        # Fix Wheelchair Replicant action doc links.
        for f in wheelchair_replicant_actions_output_directory.iterdir():
            action_text = f.read_text(encoding="utf-8")
            for replicant_doc in ["arm.md", "collision_detection.md", "action_status.md", "replicant_static.md",
                                  "replicant_dynamic.md", "image_frequency.md"]:
                action_text = action_text.replace(f"(../{replicant_doc})", f"(../../replicant/{replicant_doc})")
            f.write_text(action_text)
        # Add documentation for asset bundle creators.
        ClassInheritance().get_from_directory(input_directory=c.tdw_path.joinpath("Python/tdw/asset_bundle_creator"),
                                              output_directory=output_directory.joinpath("asset_bundle_creator"),
                                              import_prefix="from tdw.asset_bundle_creator",
                                              import_path="tdw.asset_bundle_creator")

        # Add documentation for scene bounds.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/scene_data"),
                     files=["scene_bounds.py", "region_bounds.py", "interior_region.py", "room.py"])
        md.get_docs(output_directory=output_directory.joinpath("scene_data"))

        # Add documentation for object data.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/object_data"),
                     files=["transform.py", "rigidbody.py", "bound.py", "object_static.py",
                            "clatter_values.py", "physics_values.py"])
        md.get_docs(output_directory=output_directory.joinpath("object_data"),
                    import_prefix="from tdw.object_data")

        # Add documentation for collision data.
        ClassInheritance().get_from_directory(input_directory=c.tdw_path.joinpath("Python/tdw/collision_data"),
                                              output_directory=output_directory.joinpath("collision_data"),
                                              import_prefix="from tdw.collision_data",
                                              import_path="tdw.collision_data",
                                              excludes=["trigger_collision_event.py", "trigger_collider_shape.py"])
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/collision_data"),
                     files=["trigger_collision_event.py", "trigger_collider_shape.py"])
        md.get_docs(output_directory=output_directory.joinpath("collision_data"),
                    import_prefix="from tdw.collision_data")
        # Add documentation for robot data.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/robot_data"),
                     files=["drive.py", "joint_dynamic.py", "joint_static.py", "non_moving.py",
                            "robot_dynamic.py", "robot_static.py", "joint_type.py"])
        md.get_docs(output_directory=output_directory.joinpath("robot_data"),
                    import_prefix="from tdw.robot_data")

        # Add documentation for model tests.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/add_ons/model_verifier/model_tests"),
                     files=["model_test.py", "rotate_object_test.py", "missing_materials.py", "physics_quality.py",
                            "model_report.py"])
        md.get_docs(output_directory=output_directory.joinpath("model_tests"),
                    import_prefix="from tdw.add_ons.model_verifier.model_tests")

        # Add documentation for physics audio classes.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/physics_audio"),
                     files=["scrape_material.py", "scrape_model.py", "scrape_sub_object.py", "impact_material.py",
                            "clatter_object.py"])
        md.get_docs(output_directory=output_directory.joinpath("physics_audio"),
                    import_prefix="from tdw.physics_audio")

        # Add documentation for VR classes.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/vr_data"),
                     files=["oculus_touch_button.py", "rig_type.py", "finger_bone.py"])
        md.get_docs(output_directory=output_directory.joinpath("vr_data"),
                    import_prefix="from tdw.vr_data")

        # Add documentation for composite objects.
        composite_object_path = c.tdw_path.joinpath("Python/tdw/object_data/composite_object")
        md = PyMdDoc(input_directory=composite_object_path,
                     files=["composite_object_dynamic.py", "composite_object_static.py"])
        md.get_docs(output_directory=output_directory.joinpath("object_data/composite_object"),
                    import_prefix="from tdw.object_data.composite_object")
        # Add documentation for composite sub-objects.
        ClassInheritance().get_from_directory(input_directory=c.tdw_path.joinpath("Python/tdw/object_data/composite_object/sub_object"),
                                              output_directory=output_directory.joinpath("object_data/composite_object/sub_object"),
                                              import_prefix="from tdw.object_data.composite_object.sub_object",
                                              import_path="tdw.object_data.composite_object.sub_object")

        # Add documentation for container classes.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/container_data"),
                     files=["container_tag.py", "containment_event.py"])
        md.get_docs(output_directory=output_directory.joinpath("container_data"),
                    import_prefix="from tdw.container_data")
        ClassInheritance().get_from_directory(input_directory=c.tdw_path.joinpath("Python/tdw/container_data"),
                                              output_directory=output_directory.joinpath("container_data"),
                                              import_prefix="from tdw.container_data",
                                              import_path="tdw.container_data",
                                              excludes=["container_tag.py", "containment_event.py"])

        # Add documentation for abstract agent classes.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/agent_data"),
                     files=["agent_dynamic.py"])
        md.get_docs(output_directory=output_directory.joinpath("agent_data"),
                    import_prefix="from tdw.agent_data")
        agent_dynamic = output_directory.joinpath("agent_data/agent_dynamic.md").resolve().read_text(encoding="utf-8")

        # Add documentation for Replicant classes.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/replicant"),
                     files=["action_status.py", "arm.py", "collision_detection.py", "image_frequency.py",
                            "replicant_body_part.py", "replicant_dynamic.py", "replicant_static.py"])
        md.get_docs(output_directory=output_directory.joinpath("replicant"),
                    import_prefix="from tdw.replicant")
        # Class inheritance for ReplicantDynamic.
        replicant_dynamic_path = output_directory.joinpath("replicant/replicant_dynamic.md").resolve()
        replicant_dynamic = replicant_dynamic_path.read_text(encoding="utf-8")
        replicant_dynamic = ClassInheritance().get_from_text(child_text=replicant_dynamic,
                                                             parent_texts=[agent_dynamic])
        replicant_dynamic_path.write_text(replicant_dynamic)
        # Actions.
        ClassInheritance().get_from_directory(input_directory=c.tdw_path.joinpath("Python/tdw/replicant/actions"),
                                              output_directory=output_directory.joinpath("replicant/actions"),
                                              import_prefix="from tdw.replicant.actions",
                                              import_path="tdw.replicant.actions")
        wheelchair_reach_for_path = wheelchair_replicant_actions_output_directory.joinpath("reach_for.md")
        wheelchair_reach_for_path.write_text(ci.get_from_text(child_text=wheelchair_reach_for_path.read_text(encoding="utf-8"),
                                                              parent_texts=[replicant_actions_directory.joinpath("arm_motion.md").read_text(encoding="utf-8")]))
        # IK plans.
        ClassInheritance().get_from_directory(input_directory=c.tdw_path.joinpath("Python/tdw/replicant/ik_plans"),
                                              output_directory=output_directory.joinpath("replicant/ik_plans"),
                                              import_prefix="from tdw.replicant.ik_plans",
                                              import_path="tdw.replicant.ik_plans",
                                              excludes=["ik_plan_type.py"])
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/replicant/ik_plans"),
                     files=["ik_plan_type.py"])
        md.get_docs(output_directory=output_directory.joinpath("replicant/ik_plans"),
                    import_prefix="from tdw.replicant.ik_plans")

        # Add documentation for backend classes.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/backend"),
                     files=["update.py"])
        md.get_docs(output_directory=output_directory.joinpath("backend"),
                    import_prefix="from tdw.backend")

        # Add documentation for Obi data.
        ClassInheritance().get_from_directory(input_directory=c.tdw_path.joinpath("Python/tdw/obi_data/fluids"),
                                              output_directory=output_directory.joinpath("obi_data/fluids"),
                                              import_prefix="from tdw.obi_data.fluids",
                                              import_path="tdw.obi_data.fluids",
                                              excludes=["emitter_sampling_method.py", "fluid.py", "fluid_base.py",
                                                        "granular_fluid.py"])
        ClassInheritance().get_from_directory(input_directory=c.tdw_path.joinpath("Python/tdw/obi_data/fluids"),
                                              output_directory=output_directory.joinpath("obi_data/fluids"),
                                              import_prefix="from tdw.obi_data.fluids",
                                              import_path="tdw.obi_data.fluids",
                                              excludes=["emitter_sampling_method.py", "cube_emitter.py", "disk_emitter.py",
                                                        "edge_emitter.py", "emitter_shape.py", "sphere_emitter.py"])
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/obi_data"),
                     files=["obi_actor.py", "force_mode.py", "wind_source.py", "obi_backend.py"])
        md.get_docs(output_directory=output_directory.joinpath("obi_data"),
                    import_prefix="from tdw.obi_data")
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/obi_data/fluids"),
                     files=["emitter_sampling_method.py"])
        md.get_docs(output_directory=output_directory.joinpath("obi_data/fluids"),
                    import_prefix="from tdw.obi_data.fluids")
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/obi_data/collision_materials"),
                     files=["collision_material.py", "material_combine_mode.py"])
        md.get_docs(output_directory=output_directory.joinpath("obi_data/collision_materials"),
                    import_prefix="from tdw.obi_data.collision_materials")
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/obi_data/cloth"),
                     files=["cloth_material.py", "sheet_type.py", "tether_particle_group.py", "volume_type.py",
                            "tether_type.py"])
        md.get_docs(output_directory=output_directory.joinpath("obi_data/cloth"),
                    import_prefix="from tdw.obi_data.cloth")
        ClassInheritance().get_from_directory(input_directory=c.tdw_path.joinpath("Python/tdw/proc_gen/arrangements"),
                                              output_directory=output_directory.joinpath("proc_gen/arrangements"),
                                              import_prefix="from tdw.proc_gen.arrangements",
                                              import_path="tdw.proc_gen.arrangements")
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/proc_gen/arrangements/cabinetry"),
                     files=["cabinetry.py", "cabinetry_type.py"])
        md.get_docs(output_directory=output_directory.joinpath("proc_gen/arrangements/cabinetry"),
                    import_prefix="from tdw.proc_gen.arrangements.cabinetry")

        # Add documentation for LISDF data classes.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/lisdf_data"),
                     files=["lisdf_robot_metadata.py"])
        md.get_docs(output_directory=output_directory.joinpath("lisdf_data"),
                    import_prefix="from tdw.lisdf_data")

        # Add documentation for V-Ray data classes.
        ClassInheritance().get_from_directory(input_directory=c.tdw_path.joinpath("Python/tdw/vray_data"),
                                              output_directory=output_directory.joinpath("vray_data"),
                                              import_prefix="from tdw.vray_data",
                                              import_path="tdw.vray_data",
                                              overrides={"VrayMatrix": "VRayMatrix",
                                                         "v_ray_matrix": "vray_matrix"})
        # Add documentation for drone data classes.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/drone"),
                     files=["drone_dynamic.py"])
        md.get_docs(output_directory=output_directory.joinpath("drone"),
                    import_prefix="from tdw.drone")
        # Class inheritance for DroneDynamic.
        drone_dynamic_path = output_directory.joinpath("drone/drone_dynamic.md").resolve()
        drone_dynamic = drone_dynamic_path.read_text(encoding="utf-8")
        drone_dynamic = ClassInheritance().get_from_text(child_text=drone_dynamic,
                                                         parent_texts=[agent_dynamic])
        drone_dynamic_path.write_text(drone_dynamic)

        # Add documentation for vehicle data classes.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw/vehicle"),
                     files=["vehicle_dynamic.py"])
        md.get_docs(output_directory=output_directory.joinpath("vehicle"),
                    import_prefix="from tdw.vehicle")
        # Class inheritance for VehicleDynamic.
        vehicle_dynamic_path = output_directory.joinpath("vehicle/vehicle_dynamic.md").resolve()
        vehicle_dynamic = vehicle_dynamic_path.read_text(encoding="utf-8")
        vehicle_dynamic = ClassInheritance().get_from_text(child_text=vehicle_dynamic,
                                                           parent_texts=[agent_dynamic])
        vehicle_dynamic_path.write_text(vehicle_dynamic)

        # Add documentation for lerp data classes.
        ClassInheritance().get_from_directory(input_directory=c.tdw_path.joinpath("Python/tdw/lerp"),
                                              output_directory=output_directory.joinpath("lerp"),
                                              import_path="tdw.lerp",
                                              import_prefix="from tdw.lerp")

        # Add general documentation.
        md = PyMdDoc(input_directory=c.tdw_path.joinpath("Python/tdw").resolve(),
                     files=["audio_utils.py",
                            "controller.py",
                            "tdw_utils.py",
                            "quaternion_utils.py",
                            "remote_build_launcher.py",
                            "cardinal_direction.py",
                            "ordinal_direction.py",
                            "int_pair.py"])
        md.get_docs(output_directory=output_directory)
        vd = VarDoc()
        vd.get(src=c.tdw_path.joinpath("Python/tdw/type_aliases.py").resolve(),
               dst=output_directory.joinpath("type_aliases.md"))

        # Add dev documentation.
        dev_path_py = c.tdw_path.joinpath("Python/tdw/dev").resolve()
        dev_path_md = output_directory.joinpath("dev")
        md = PyMdDoc(input_directory=dev_path_py,
                     files=["affordance_points_creator.py",
                            "asset_bundles.py",
                            "config.py",
                            "dockerizer.py",
                            "pypi_uploader.py"])
        md.get_docs(output_directory=dev_path_md)
        vd = VarDoc()
        vd.get(src=dev_path_py.joinpath("versions.py"),
               dst=dev_path_md.joinpath("versions.md.md"))
        dev_path_py = dev_path_py.joinpath("code_gen")
        dev_path_md = dev_path_md.joinpath("code_gen")
        md = PyMdDoc(input_directory=dev_path_py,
                     files=["commands_code_gen.py",
                            "cached_objects.py",
                            "fb_doc_gen.py",
                            "py_doc_gen.py"])
        md.get_docs(output_directory=dev_path_md)
        dev_path_py = dev_path_py.joinpath("cs_xml")
        dev_path_md = dev_path_md.joinpath("cs_xml")
        md = PyMdDoc(input_directory=dev_path_py,
                     files=["assembly.py",
                            "enum_member.py",
                            "field.py",
                            "py_field.py",
                            "method.py",
                            "namespace.py",
                            "parameter.py"])
        md.get_docs(output_directory=dev_path_md)
        ci = ClassInheritance()
        ci.get_from_directory(input_directory=dev_path_py,
                              output_directory=dev_path_md,
                              import_path="tdw.dev.code_gen.cs_xml",
                              import_prefix="from tdw.code_gen.dev.cs_xml",
                              includes=["member.py", "enum_type.py", "struct.py", "klass.py"])
        dev_path_py = dev_path_py.joinpath("field_doc_gen")
        dev_path_md = dev_path_md.joinpath("field_doc_gen")
        ci.get_from_directory(input_directory=dev_path_py,
                              output_directory=dev_path_md,
                              import_path="tdw.dev.code_gen.cs_xml.field_doc_gen",
                              import_prefix="from tdw.dev.code_gen.cs_xml.field_doc_gen")

        # Get the table of contents.
        toc = PyMdDoc.get_dir_toc(directory=output_directory,
                                  class_name_overrides={"Pypi": "PyPi",
                                                        "TdwUtils": "TDWUtils",
                                                        "Vr": "VR",
                                                        "Ui": "UI"},
                                  import_prefix="tdw",
                                  link_prefix=".")
        # Adjust the README table of contents.
        readme_path = output_directory.joinpath("python_api.md")
        readme_path.write_text("# `tdw` module API\n\n" + toc)


if __name__ == "__main__":
    PyDocGen.generate()
