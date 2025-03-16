import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.lines import Line2D

# Set page configuration
st.set_page_config(page_title="Cab Route Visualizer", layout="wide")

st.title("Cab Management System: Interactive Route Visualizer")
st.write("Explore different scenarios for picking up a second customer while maintaining first customer priority")

# Define the scenarios
scenarios = {
    "Case 1.1: B on direct route, dropoff after A": 1.1,
    "Case 1.2: B requires detour, dropoff after A": 1.2,
    "Case 2.1: B and Db on direct route before A's dropoff": 2.1,
    "Case 2.2: B and Db require detours before A's dropoff": 2.2,
    "Case 3: B's pickup after A's dropoff": 3.0
}

# Create sidebar for controls
st.sidebar.header("Scenario Selection")
selected_scenario = st.sidebar.selectbox(
    "Choose a scenario:",
    list(scenarios.keys())
)

scenario_code = scenarios[selected_scenario]

# Time control sliders
st.sidebar.header("Time Parameters")
original_time = st.sidebar.slider("Original journey time (minutes)", 10, 60, 20)

# Additional parameters based on scenario
detour_size = 0
detour1_size = 0
detour2_size = 0

if scenario_code == 1.2:
    detour_size = st.sidebar.slider("Detour size (% of direct route)", 5, 50, 20)
elif scenario_code == 2.2:
    detour1_size = st.sidebar.slider("Pickup detour size (%)", 5, 30, 15)
    detour2_size = st.sidebar.slider("Dropoff detour size (%)", 5, 30, 15)

# Function to calculate time overhead based on scenario
def calculate_time_overhead(scenario, orig_time):
    if scenario == 1.1:
        # Minimal overhead, just pickup time
        return orig_time * 1.05
    elif scenario == 1.2:
        # Depends on detour size
        return orig_time * (1 + detour_size/100)
    elif scenario == 2.1:
        # Two stops but no detours
        return orig_time * 1.1
    elif scenario == 2.2:
        # Multiple detours
        return orig_time * (1 + (detour1_size + detour2_size)/100)
    elif scenario == 3.0:
        # No impact on A
        return orig_time
    return orig_time

# Calculate the new time
new_time = calculate_time_overhead(scenario_code, original_time)

# Display time metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Original Time (T₀)", f"{original_time} min")
with col2:
    st.metric("New Time (T₁)", f"{new_time:.1f} min")
with col3:
    overhead_percent = ((new_time / original_time) - 1) * 100
    st.metric("Time Overhead", f"{overhead_percent:.1f}%", f"{overhead_percent:.1f}%")

# Check if time constraint is met
max_allowed_time = original_time * 1.5
constraint_met = new_time <= max_allowed_time

if constraint_met:
    st.success(f"✓ Time constraint met! T₁ ({new_time:.1f} min) ≤ 1.5 × T₀ ({max_allowed_time:.1f} min)")
else:
    st.error(f"✗ Time constraint violated! T₁ ({new_time:.1f} min) > 1.5 × T₀ ({max_allowed_time:.1f} min)")

# Create the route visualization
st.header("Route Visualization")

def plot_scenario(scenario, fig, ax):
    # Setup plot basics
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(selected_scenario, fontsize=14)
    
    # Base points for all scenarios
    a_pickup = (1, 3)  # Point A (customer 1 pickup)
    a_dropoff = (9, 3)  # Point Da (customer 1 dropoff)
    
    # Plot A and Da
    ax.plot(a_pickup[0], a_pickup[1], 'o', markersize=12, color='#4CAF50')
    ax.text(a_pickup[0], a_pickup[1]-0.4, 'A', fontsize=12, ha='center')
    
    ax.plot(a_dropoff[0], a_dropoff[1], 's', markersize=12, color='#F44336')
    ax.text(a_dropoff[0], a_dropoff[1]-0.4, 'Da', fontsize=12, ha='center')
    
    # Draw different scenarios
    if scenario == 1.1:
        # B on direct route, dropoff after A
        b_pickup = (5, 3)
        b_dropoff = (9.5, 3)
        
        ax.plot(b_pickup[0], b_pickup[1], 'o', markersize=12, color='#4CAF50')
        ax.text(b_pickup[0], b_pickup[1]-0.4, 'B', fontsize=12, ha='center')
        
        ax.plot(b_dropoff[0], b_dropoff[1], 's', markersize=12, color='#F44336')
        ax.text(b_dropoff[0], b_dropoff[1]-0.4, 'Db', fontsize=12, ha='center')
        
        # Direct route
        ax.plot([a_pickup[0], b_pickup[0]], [a_pickup[1], b_pickup[1]], 'k-', linewidth=2.5)
        ax.plot([b_pickup[0], a_dropoff[0]], [b_pickup[1], a_dropoff[1]], 'k-', linewidth=2.5)
        ax.plot([a_dropoff[0], b_dropoff[0]], [a_dropoff[1], b_dropoff[1]], 'k-', linewidth=2.5)
        
    elif scenario == 1.2:
        # B requires detour, dropoff after A
        b_pickup = (4, 5)
        b_dropoff = (9.5, 3)
        
        ax.plot(b_pickup[0], b_pickup[1], 'o', markersize=12, color='#4CAF50')
        ax.text(b_pickup[0], b_pickup[1]+0.3, 'B', fontsize=12, ha='center')
        
        ax.plot(b_dropoff[0], b_dropoff[1], 's', markersize=12, color='#F44336')
        ax.text(b_dropoff[0], b_dropoff[1]-0.4, 'Db', fontsize=12, ha='center')
        
        # Direct route between A and Da (shown faded)
        ax.plot([a_pickup[0], a_dropoff[0]], [a_pickup[1], a_dropoff[1]], 'k-', linewidth=1.5, alpha=0.3)
        
        # Route with detour
        verts = [
            (a_pickup[0], a_pickup[1]),  # A
            (3, 3),                      # Point before detour
            (4, 5),                      # B
            (5, 3),                      # Return to route
            (a_dropoff[0], a_dropoff[1]), # Da
            (b_dropoff[0], b_dropoff[1])  # Db
        ]
        codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 1)
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='none', edgecolor='b', lw=2.5)
        ax.add_patch(patch)
        
    elif scenario == 2.1:
        # B and Db on direct route before A's dropoff
        b_pickup = (3, 3)
        b_dropoff = (6, 3)
        
        ax.plot(b_pickup[0], b_pickup[1], 'o', markersize=12, color='#4CAF50')
        ax.text(b_pickup[0], b_pickup[1]-0.4, 'B', fontsize=12, ha='center')
        
        ax.plot(b_dropoff[0], b_dropoff[1], 's', markersize=12, color='#F44336')
        ax.text(b_dropoff[0], b_dropoff[1]-0.4, 'Db', fontsize=12, ha='center')
        
        # Direct route
        ax.plot([a_pickup[0], b_pickup[0]], [a_pickup[1], b_pickup[1]], 'k-', linewidth=2.5)
        ax.plot([b_pickup[0], b_dropoff[0]], [b_pickup[1], b_dropoff[1]], 'k-', linewidth=2.5)
        ax.plot([b_dropoff[0], a_dropoff[0]], [b_dropoff[1], a_dropoff[1]], 'k-', linewidth=2.5)
        
    elif scenario == 2.2:
        # B and Db require detours before A's dropoff
        b_pickup = (2.5, 5)
        b_dropoff = (6, 1)
        
        ax.plot(b_pickup[0], b_pickup[1], 'o', markersize=12, color='#4CAF50')
        ax.text(b_pickup[0], b_pickup[1]+0.3, 'B', fontsize=12, ha='center')
        
        ax.plot(b_dropoff[0], b_dropoff[1], 's', markersize=12, color='#F44336')
        ax.text(b_dropoff[0], b_dropoff[1]-0.4, 'Db', fontsize=12, ha='center')
        
        # Direct route between A and Da (shown faded)
        ax.plot([a_pickup[0], a_dropoff[0]], [a_pickup[1], a_dropoff[1]], 'k-', linewidth=1.5, alpha=0.3)
        
        # Route with detours
        verts = [
            (a_pickup[0], a_pickup[1]),  # A
            (2, 3),                      # Point before first detour
            (2.5, 5),                    # B
            (3, 3),                      # Return to route
            (5, 3),                      # Point before second detour
            (6, 1),                      # Db
            (7, 3),                      # Return to route
            (a_dropoff[0], a_dropoff[1]) # Da
        ]
        codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 1)
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='none', edgecolor='b', lw=2.5)
        ax.add_patch(patch)
        
    elif scenario == 3.0:
        # B's pickup after A's dropoff
        b_pickup = (9.2, 4)
        b_dropoff = (9.5, 5)
        
        ax.plot(b_pickup[0], b_pickup[1], 'o', markersize=12, color='#4CAF50')
        ax.text(b_pickup[0], b_pickup[1]+0.3, 'B', fontsize=12, ha='center')
        
        ax.plot(b_dropoff[0], b_dropoff[1], 's', markersize=12, color='#F44336')
        ax.text(b_dropoff[0], b_dropoff[1]+0.3, 'Db', fontsize=12, ha='center')
        
        # Direct route A to Da
        ax.plot([a_pickup[0], a_dropoff[0]], [a_pickup[1], a_dropoff[1]], 'k-', linewidth=2.5)
        
        # Route Da to B to Db
        ax.plot([a_dropoff[0], b_pickup[0]], [a_dropoff[1], b_pickup[1]], 'k-', linewidth=2.5)
        ax.plot([b_pickup[0], b_dropoff[0]], [b_pickup[1], b_dropoff[1]], 'k-', linewidth=2.5)
    
    # Add legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#4CAF50', markersize=10, label='Pickup Point'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#F44336', markersize=10, label='Dropoff Point'),
        Line2D([0], [0], color='k', lw=2, label='Direct Route'),
    ]
    
    if scenario in [1.2, 2.2]:
        legend_elements.append(Line2D([0], [0], color='b', lw=2, label='Route with Detour'))
        
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))

# Create and display the figure
fig, ax = plt.subplots(figsize=(12, 8))
plot_scenario(scenario_code, fig, ax)
st.pyplot(fig)

# Add description of the scenario
st.header("Scenario Description")

descriptions = {
    1.1: """
    **Case 1.1: B on direct route, dropoff after A**
    
    - Customer B is picked up from a point that lies directly on the optimal route from A to Da
    - B's destination is after A's dropoff point
    - Impact on A's travel time is minimal (just the brief stop to pick up B)
    - This is one of the most efficient scenarios for ride-sharing
    - Priority Rank: 2 (Very High)
    """,
    
    1.2: """
    **Case 1.2: B requires detour, dropoff after A**
    
    - Customer B is picked up from a point that requires a detour from the direct route
    - B's destination is after A's dropoff point
    - Impact on A's travel time depends on the size of the detour
    - The cab must leave the optimal route, pick up B, then return to the route
    - Priority Rank: 4-6 (Medium to Low, depending on detour size)
    """,
    
    2.1: """
    **Case 2.1: B and Db on direct route before A's dropoff**
    
    - Both customer B and their destination lie directly on the optimal route from A to Da
    - B is dropped off before reaching A's destination
    - Impact on A's travel time comes from two stops (pickup and dropoff)
    - No detours are required, maintaining route efficiency
    - Priority Rank: 3 (High)
    """,
    
    2.2: """
    **Case 2.2: B and Db require detours before A's dropoff**
    
    - Both B's pickup and dropoff require deviations from the optimal route
    - The cab must make multiple detours before reaching A's destination
    - Highest impact on A's travel time among the valid scenarios
    - Most complex routing with potentially significant delays
    - Priority Rank: 5-7 (Low, depending on detour sizes)
    """,
    
    3.0: """
    **Case 3: B's pickup after A's dropoff**
    
    - Customer B is picked up only after A has been dropped off
    - No impact whatsoever on A's travel time
    - Essentially two separate, sequential rides
    - Most favorable scenario from A's perspective
    - Priority Rank: 1 (Highest)
    """
}

st.markdown(descriptions[scenario_code])

# Display time constraint visualization
st.header("Time Constraint Visualization")

fig2, ax2 = plt.subplots(figsize=(12, 3))

# Create a horizontal bar to visualize the time constraint
ax2.set_xlim(0, original_time * 2)
ax2.set_ylim(0, 1)
ax2.set_yticks([])

# Add colored regions
ax2.axvspan(0, original_time, facecolor='#a5d6a7', alpha=0.5)
ax2.axvspan(original_time, original_time * 1.5, facecolor='#fff9c4', alpha=0.5)
ax2.axvspan(original_time * 1.5, original_time * 2, facecolor='#ffcdd2', alpha=0.5)

# Add labels
ax2.text(original_time * 0.5, 0.5, "Optimal", ha='center', va='center', fontsize=12)
ax2.text(original_time * 1.25, 0.5, "Acceptable", ha='center', va='center', fontsize=12)
ax2.text(original_time * 1.75, 0.5, "Prohibited", ha='center', va='center', fontsize=12)

# Add vertical lines for reference
ax2.axvline(x=original_time, color='k', linestyle='-', linewidth=2)
ax2.axvline(x=original_time * 1.5, color='r', linestyle='-', linewidth=2)

# Add markers
ax2.plot(original_time, 0.3, 'ko', markersize=10)
ax2.text(original_time, 0.15, "T₀", ha='center', fontsize=12)

ax2.plot(max_allowed_time, 0.3, 'ro', markersize=10)
ax2.text(max_allowed_time, 0.15, "1.5 × T₀", ha='center', fontsize=12)

# Add current time marker
ax2.plot(new_time, 0.7, 'bo', markersize=12)
ax2.text(new_time, 0.85, f"Current: {new_time:.1f} min", ha='center', fontsize=12)

# Add x-axis
ax2.set_xlabel("Travel Time (minutes)", fontsize=12)
st.pyplot(fig2)

# Add footer with complete priority ranking
st.header("Complete Priority Ranking")
st.markdown("""
1. **Case 3:** B's pickup after A's dropoff (No impact on A)
2. **Case 1.1:** B on direct route, dropoff after A (Minimal impact)
3. **Case 2.1:** Both B and Db on direct route (Impact from two stops only)
4. **Case 1.2 (small detour):** B requires minor detour (Time increase <25%)
5. **Case 2.2 (small detours):** B/Db with minor detours (Time increase <25%)
6. **Case 1.2 (medium/large):** B requires significant detour (25-50% increase)
7. **Case 2.2 (medium/large):** Complex route with multiple significant detours (25-50%)
""")

# Implementation notes
st.header("Implementation Considerations")
st.markdown("""
- **Real-time Traffic Integration:** Adjust time estimates based on current traffic conditions
- **Dynamic Constraint Management:** Tighten constraints during peak hours (e.g., 1.3× instead of 1.5×)
- **Continuous Route Optimization:** Recalculate routes as traffic conditions change
- **Customer Communication:** Keep both customers informed of estimated arrival times
- **Incentive Structure:** Offer discounts to customers accepting shared rides with potential delays
""")
