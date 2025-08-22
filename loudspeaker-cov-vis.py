# -*- coding: utf-8 -*-
"""
Created on Fri Aug 22 14:11:21 2025

@author: maxbu
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


#2d space
x = np.linspace(-10, 10, 200)
y = np.linspace(0, 20, 200)
X, Y = np.meshgrid(x, y)

speaker_pos = np.array([0, 0])

#init params
initial_angle_deg = 90.0
initial_rotation_deg = 0.0  


def calculate_spl_map(X, Y, coverage_angle_deg, rotation_deg):
    
    vectors = np.stack([X - speaker_pos[0], Y - speaker_pos[1]], axis=-1)
    
    #distance from speaker at each point
    distance = np.linalg.norm(vectors, axis=-1) + 1e-6
    
    #ISL: SPL drops by 6 dB for doubling of distance
    spl = 100 - 20 * np.log10(distance)
    
    #speakers direcitonal angle
    speaker_aim_rad = np.deg2rad(rotation_deg - 90)
    angle_from_center = np.arctan2(vectors[..., 1], vectors[..., 0]) - speaker_aim_rad
    angle_from_center = (angle_from_center + np.pi) % (2 * np.pi) - np.pi # Wrap to -pi, pi
    
    #attenuate SPL outside of coverage
    half_coverage_rad = np.deg2rad(coverage_angle_deg / 2)
    #full SPL inside the angle, very low SPL outside
    spl[np.abs(angle_from_center) > half_coverage_rad] = 50 
    
    return spl

fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(left=0.1, bottom=0.25)

#display inital SPL in heatmap
spl_map = calculate_spl_map(X, Y, initial_angle_deg, initial_rotation_deg)
cax = ax.imshow(spl_map, extent=[-10, 10, 0, 20], origin='lower', cmap='inferno', vmin=70, vmax=105)

ax.set_title('Loudspeaker Coverage & SPL Drop-off')
ax.set_xlabel('Width (m)')
ax.set_ylabel('Distance (m)')
ax.plot(speaker_pos[0], speaker_pos[1], 'wo', markersize=8, label='Speaker') # Mark speaker
ax.legend()
fig.colorbar(cax, label='SPL (dB)')


#sliders
ax_coverage = plt.axes([0.15, 0.1, 0.65, 0.03])
ax_rotation = plt.axes([0.15, 0.05, 0.65, 0.03])

coverage_slider = Slider(ax=ax_coverage, label='Coverage (°)', valmin=30, valmax=120, valinit=initial_angle_deg)
rotation_slider = Slider(ax=ax_rotation, label='Rotation (°)', valmin=-90, valmax=90, valinit=initial_rotation_deg)



def update(val):
    #call when slider moved
    current_coverage = coverage_slider.val
    current_rotation = rotation_slider.val
    
    #recalc new SPL
    new_spl_map = calculate_spl_map(X, Y, current_coverage, current_rotation)
    
    #update heatmap
    cax.set_data(new_spl_map)
    
    #redraw figure
    fig.canvas.draw_idle()

coverage_slider.on_changed(update)
rotation_slider.on_changed(update)

plt.show()