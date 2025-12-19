"""
Collision Detection Client (Python 2.7 for H3D)
Communicates with collision_server.py via JSON files
Handles 9 DOF: 6 C-arm + 3 Table
"""

from H3DInterface import *
import json
import os
import time

# Global state
collision_material = None
xray_border_material = None
status_circle_material = None
status_text_material = None
status_text_node = None
last_pose = {
    'lao_rao': None, 'cran_caud': None, 'wigwag': None,
    'lateral': None, 'vertical': None, 'horizontal': None,
    'zoom': None
}
last_result = {'collision': False, 'collision_points': {'total': 0}}
check_throttle_time = 0
THROTTLE_INTERVAL = 0.2

def initialize():
    """Initialize material and slider references from main.x3d"""
    global collision_material, xray_border_material
    global status_circle_material, status_text_material, status_text_node
    
    refs_count = len(references.getValue())
    if refs_count >= 6:
        if refs_count >= 11:
            collision_material = references.getValue()[10]
            if refs_count >= 12:
                xray_border_material = references.getValue()[11]
            if refs_count >= 13:
                status_circle_material = references.getValue()[12]
            if refs_count >= 14:
                status_text_material = references.getValue()[13]
            if refs_count >= 15:
                status_text_node = references.getValue()[14]
        print("[Collision Client] Initialized with 6 C-arm + 3 Table DOF + Zoom")
        print("[Collision Client] Ensure collision_server.py is running")
    else:
        print("[Collision Client ERROR] Need at least 6 refs, got " + str(refs_count))

def update_visual_feedback(has_collision, point_count):
    """Update visual indicators to red (collision) or green (safe)"""
    global collision_material, xray_border_material
    global status_circle_material, status_text_material, status_text_node
    
    if has_collision:
        diffuse, emissive = RGB(1, 0, 0), RGB(0.3, 0, 0)
        circle_emissive = RGB(0.5, 0, 0)
        text_color = RGB(0.8, 0, 0)
        status_msg = "Collision Detected"
    else:
        diffuse, emissive = RGB(0, 1, 0), RGB(0, 0.3, 0)
        circle_emissive = RGB(0, 0.5, 0)
        text_color = RGB(0, 0.6, 0)
        status_msg = "No Collision"
    
    if collision_material is not None:
        collision_material.diffuseColor.setValue(diffuse)
        collision_material.emissiveColor.setValue(emissive)
    if xray_border_material is not None:
        xray_border_material.diffuseColor.setValue(diffuse)
        xray_border_material.emissiveColor.setValue(emissive)
    if status_circle_material is not None:
        status_circle_material.diffuseColor.setValue(diffuse)
        status_circle_material.emissiveColor.setValue(circle_emissive)
    if status_text_material is not None:
        status_text_material.diffuseColor.setValue(text_color)
    if status_text_node is not None:
        status_text_node.string.setValue([status_msg])

def check_collision(lao_rao, cran_caud, wigwag=0, lateral=0, vertical=0, horizontal=0,
                    table_vertical=0, table_longitudinal=0, table_transverse=0, zoom=1.0):
    """Check collision by writing pose to JSON and reading result"""
    pose_file = 'collision_pose.json'
    result_file = 'collision_result.json'
    
    try:
        pose_data = {
            'lao_rao': float(lao_rao),
            'cran_caud': float(cran_caud),
            'wigwag': float(wigwag),
            'lateral': float(lateral) / 100.0,
            'vertical': float(vertical) / 100.0,
            'horizontal': float(horizontal) / 100.0,
            'table_vertical': float(table_vertical) / 100.0,
            'table_longitudinal': float(table_longitudinal) / 100.0,
            'table_transverse': float(table_transverse) / 100.0,
            'zoom': float(zoom),
            'timestamp': time.time()
        }
        
        with open(pose_file, 'w') as f:
            json.dump(pose_data, f)
        
        max_wait = 0.5
        wait_interval = 0.05
        waited = 0
        result_mod_time = os.path.getmtime(result_file) if os.path.exists(result_file) else 0
        
        while waited < max_wait:
            time.sleep(wait_interval)
            waited += wait_interval
            
            if os.path.exists(result_file):
                new_mod_time = os.path.getmtime(result_file)
                if new_mod_time > result_mod_time:
                    break
        
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                return json.load(f)
        else:
            return {'collision': False, 'error': 'Server not responding', 
                   'collision_points': {'total': 0}}
    
    except Exception as e:
        print("[Collision Client ERROR] " + str(e))
        return {'collision': False, 'error': str(e), 
               'collision_points': {'total': 0}}

def check_collision_throttled():
    """Check collision with throttling to avoid overwhelming the server"""
    global last_pose, last_result, check_throttle_time
    
    current_time = time.time()
    if current_time - check_throttle_time < THROTTLE_INTERVAL:
        return
    check_throttle_time = current_time
    
    refs = references.getValue()
    if len(refs) < 6:
        return
    
    lao_rao = refs[0].value.getValue()
    cran_caud = refs[1].value.getValue()
    wigwag = refs[2].value.getValue()
    lateral = refs[3].value.getValue()
    horizontal = refs[4].value.getValue()
    vertical = refs[5].value.getValue()
    
    table_vertical = refs[6].value.getValue() if len(refs) >= 7 else 0.0
    table_longitudinal = refs[7].value.getValue() if len(refs) >= 8 else 0.0
    table_transverse = refs[8].value.getValue() if len(refs) >= 9 else 0.0
    zoom = refs[9].value.getValue() if len(refs) >= 10 else 1.0
    
    if last_pose['lao_rao'] is not None:
        changes = [
            abs(lao_rao - last_pose['lao_rao']),
            abs(cran_caud - last_pose['cran_caud']),
            abs(wigwag - last_pose['wigwag']),
            abs(lateral - last_pose['lateral']),
            abs(horizontal - last_pose['horizontal']),
            abs(vertical - last_pose['vertical']),
            abs(table_vertical - last_pose.get('table_vertical', 0)),
            abs(table_longitudinal - last_pose.get('table_longitudinal', 0)),
            abs(table_transverse - last_pose.get('table_transverse', 0)),
            abs(zoom - last_pose.get('zoom', 1.0)) * 100
        ]
        if all(c < 0.5 for c in changes[:-1]) and changes[-1] < 1:
            return
    
    last_pose.update({
        'lao_rao': lao_rao, 'cran_caud': cran_caud, 'wigwag': wigwag,
        'lateral': lateral, 'horizontal': horizontal, 'vertical': vertical,
        'table_vertical': table_vertical, 'table_longitudinal': table_longitudinal,
        'table_transverse': table_transverse, 'zoom': zoom
    })
    
    result = check_collision(lao_rao, cran_caud, wigwag, lateral, vertical, horizontal,
                            table_vertical, table_longitudinal, table_transverse, zoom)
    last_result = result
    
    has_collision = result.get('collision', False)
    point_count = result.get('collision_points', {}).get('total', 0)
    update_visual_feedback(has_collision, point_count)
    
    if has_collision:
        print("*** COLLISION DETECTED *** {0} points".format(point_count))
    else:
        print("SAFE - No collision")

class CollisionEventHandler(AutoUpdate(SFFloat)):
    """Triggers collision check when slider value changes"""
    def update(self, event):
        check_collision_throttled()
        return event.getValue()

# Create handlers for all DOF
rotation1 = CollisionEventHandler()
rotation2 = CollisionEventHandler()
rotation3 = CollisionEventHandler()
translation1 = CollisionEventHandler()
translation2 = CollisionEventHandler()
translation3 = CollisionEventHandler()
tableVertical = CollisionEventHandler()
tableLongitudinal = CollisionEventHandler()
tableTransverse = CollisionEventHandler()
zoom = CollisionEventHandler()

initialize()
