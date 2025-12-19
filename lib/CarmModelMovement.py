from H3DInterface import *



#
# moves C Arm 3D model according to sliders
#
# Changes transformations of the C Arm model according to the
# sliders. Slider values are routed in, transformations are changed
# via reference.
# Return value is irrelevant but is needed as this is AutoUpdate
#
# @route0 value of rotational slider1
# @route1 value of rotational slider2
# @route2 value of rotational slider3
# @route3 value of translation slider1
# @route4 value of translation slider2
# @route5 value of translation slider3
# @return true if successful
#
rotation1 = SFFloat()
rotation2 = SFFloat()
rotation3 = SFFloat()
translation1 = SFFloat()
translation2 = SFFloat()
translation3 = SFFloat()



class modelMovements(AutoUpdate(TypedField(SFBool,
                                           (SFFloat, SFFloat, SFFloat,
                                            SFFloat, SFFloat, SFFloat)))):
    def update(self, event):
        try:
            routes_in = self.getRoutesIn()
            rot1 = routes_in[0].getValue()
            rot2 = routes_in[1].getValue()
            rot3 = routes_in[2].getValue()
            trans1 = routes_in[3].getValue()
            trans2 = routes_in[4].getValue()
            trans3 = routes_in[5].getValue()


            carmRot1 = references.getValue()[0]
            carmRot2 = references.getValue()[1]
            carmRot3 = references.getValue()[2]  # cArmYaw (TCarmEverythingButBase)
            carmtrans = references.getValue()[3]  # cArmGlobalTransform
            poleTransform = references.getValue()[4] if len(references.getValue()) > 4 else None  # TTelescopingPole
            poleCylinder = references.getValue()[5] if len(references.getValue()) > 5 else None   # TelescopingPoleCylinder


            carmRot1.getField("rotation").setValue(
                Rotation(0, 0, 1, (rot1 * 3.14159265) / 180)
            )
            carmRot2.getField("rotation").setValue(
                Rotation(0, 0, 1, (rot2 * 3.14159265) / 180)
            )
            carmRot3.getField("rotation").setValue(
                Rotation(0, 1, 0, (rot3 * 3.14159265) / 180)
            )


            # Apply strict limits to keep C-arm base within X-ray view
            limited_trans1 = max(-5, min(5, trans1))   # Lateral: -5 to 5cm
            limited_trans2 = max(-5, min(5, trans2))   # Horizontal: -5 to 5cm
            limited_trans3 = max(0, min(46, trans3))   # Vertical: 0 to 46cm


            # Apply lateral and horizontal translations to global transform
            # Keep base on ground (Y=0), only apply X and Z movements
            carmtrans.getField("translation").setValue(
                Vec3f(-limited_trans1 / 100.0, 0.0, -limited_trans2 / 100.0)
            )


            # Move only the C-shape up/down with vertical translation
            carmRot3.getField("translation").setValue(
                Vec3f(0.0, limited_trans3 / 100.0, 0.0)
            )

            # Update telescoping pole - now attached to horizontal arm, just needs to stretch down
            if poleTransform and poleCylinder:
                pole_height = limited_trans3 / 100.0  # Convert cm to meters
                
                # The horizontal arm is rotated, so we need to position the pole along its local axis
                # The arm's rotation is "0.707107 0.000000 -0.707106 3.141593"
                # This means the pole needs to extend in the arm's local coordinate system
                # Try positive Y to extend downward in world space
                pole_center_y = (pole_height + 0.1) / 2.0
                
                # Position pole in horizontal arm's local coordinate system
                poleTransform.getField("translation").setValue(
                    Vec3f(0, pole_center_y, 0)
                )
                
                # Set cylinder height to match the vertical movement plus overlap with base
                poleCylinder.getField("height").setValue(
                    max(0.01, pole_height + 0.1)  # Add 10cm overlap
                )

        except IndexError:
            pass


        return True



modelMovements = modelMovements()


rotation1.route(modelMovements)
rotation2.route(modelMovements)
rotation3.route(modelMovements)
translation1.route(modelMovements)
translation2.route(modelMovements)
translation3.route(modelMovements)