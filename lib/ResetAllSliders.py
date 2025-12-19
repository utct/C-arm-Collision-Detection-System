"""
Reset All Sliders Script (Python 2.7 compatible)
Resets all C-arm and table sliders to their default values
"""

from H3DInterface import *

def reset_all_sliders():
    """Reset all sliders to their default values"""
    # Get references directly each time (more reliable)
    # refs[0] = ResetButton (TouchButton)
    # refs[1] = Rotation1Slider (Orbital/LAO-RAO)
    # refs[2] = Rotation2Slider (Tilt/CRAN-CAUD)
    # refs[3] = Rotation3Slider (Wigwag)
    # refs[4] = Translation1Slider (Lateral)
    # refs[5] = Translation2Slider (Horizontal)
    # refs[6] = Translation3Slider (Vertical)
    # refs[7] = TableVerticalSlider
    # refs[8] = TableLongitudinalSlider
    # refs[9] = TableTransverseSlider
    # refs[10] = ZoomSlider (default = 1.0)
    
    refs = references.getValue()
    
    if len(refs) < 2:
        print("[Reset All] No sliders to reset")
        return
    
    print("[Reset All] Resetting all {0} sliders...".format(len(refs) - 1))
    
    # Reset all sliders (skip refs[0] which is the button)
    for i in range(1, len(refs)):
        try:
            slider = refs[i]
            # Zoom slider (last one) resets to 1.0, others to 0.0
            if i == 10:  # Zoom slider
                slider.value.setValue(1.0)
                print("[Reset All] Zoom slider -> 1.0")
            else:
                slider.value.setValue(0.0)
        except Exception as e:
            print("[Reset All] Error resetting slider {0}: {1}".format(i, str(e)))
    
    print("[Reset All] Done!")

# Event handler for button press
class ResetButtonHandler(AutoUpdate(SFBool)):
    """Handles reset button press"""
    def update(self, event):
        is_pressed = event.getValue()
        if is_pressed:
            reset_all_sliders()
        return is_pressed

# Create input field for button route
resetButton = ResetButtonHandler()

print("[Reset All] Script loaded")
