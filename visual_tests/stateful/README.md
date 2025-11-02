# Stateful Icons Visual Tests

This directory contains runnable examples demonstrating stateful icon features. These examples correspond to the documentation in `docs/stateful-icons.md` and can be used to capture screenshots for documentation.

## Examples

Each example is a standalone Python script that can be run independently:

### 00_state_comparison.py
**Purpose:** Side-by-side comparison of button states
**Screenshot for:** Introduction section showing normal, hover, pressed, and disabled states
**Run:** `python 00_state_comparison.py`

![State Comparison](../../docs/images/stateful/state_comparison.png)

---

### 01_automatic_color_mapping.py
**Purpose:** Basic automatic color mapping demonstration
**Screenshot for:** "Basic Usage > Automatic Color Mapping" section
**Run:** `python 01_automatic_color_mapping.py`
**Features:**
- Icon automatically inherits theme colors
- Dark theme demonstration
- Heart icon with state changes

![Automatic Color Mapping](../../docs/images/stateful/automatic_color_mapping.png)

---

### 02_custom_colors.py
**Purpose:** Custom state color specification
**Screenshot for:** "Custom State Specifications > Override Colors Per State" section
**Run:** `python 02_custom_colors.py`
**Features:**
- Star icon with custom gold/orange colors
- Color legend showing all states
- Disabled button example

![Custom Colors](../../docs/images/stateful/custom_colors.png)

---

### 03_icon_name_change.py
**Purpose:** Changing icon names per state
**Screenshot for:** "Custom State Specifications > Change Icon Name Per State" section
**Run:** `python 03_icon_name_change.py`
**Features:**
- Bookmark switching from regular to solid
- Color changes on state transitions
- State behavior documentation panel

![Icon Name Change](../../docs/images/stateful/icon_name_change.png)

---

### 04_navigation_buttons.py
**Purpose:** Navigation with active states
**Screenshot for:** "Advanced Examples > Navigation Buttons with Active State" section
**Run:** `python 04_navigation_buttons.py`
**Features:**
- Multiple navigation buttons (Home, Profile, Settings, Messages)
- Active state highlighting
- Interactive page switching
- State legend

![Navigation Buttons](../../docs/images/stateful/navigation_buttons.png)

---

### 05_toggle_button.py
**Purpose:** Toggle/checkbutton with state icons
**Screenshot for:** "Advanced Examples > Toggle Button with State Icons" section
**Run:** `python 05_toggle_button.py`
**Features:**
- Bell/bell-slash icon switching
- Green (enabled) vs Red (disabled) colors
- Status display
- Hover state color variations

![Toggle Button](../../docs/images/stateful/toggle_button.png)

---

### 06_multi_state_button.py
**Purpose:** Complex multi-state interactions
**Screenshot for:** "Advanced Examples > Multi-State Button with Complex Interactions" section
**Run:** `python 06_multi_state_button.py`
**Features:**
- Download button with 4 distinct states
- Interactive enable/disable control
- Download counter
- Comprehensive state color legend

![Multi-State Button](../../docs/images/stateful/multi_state_button.png)

---

### 07_all_states_reference.py
**Purpose:** Comprehensive TTK state flags reference
**Screenshot for:** "Common State Flags" section
**Run:** `python 07_all_states_reference.py`
**Features:**
- Visual examples of all common states
- Combined state examples
- Interactive state demonstrations
- Complete state flag reference table

![All States Reference](../../docs/images/stateful/all_states_reference.png)

---

## Requirements

All examples require:
- Python 3.10+
- ttkbootstrap
- ttkbootstrap-icons (base package)
- ttkbootstrap-icons-fa (Font Awesome provider)

Install with:
```bash
pip install ttkbootstrap ttkbootstrap-icons ttkbootstrap-icons-fa
```

## Taking Screenshots

### Recommended Screenshot Settings

1. **Window Size:** Use the default window sizes specified in each script
2. **Theme:** Examples use `cosmo` (light) or `darkly` (dark) themes as specified
3. **DPI:** Capture at 150-200 DPI for crisp documentation images
4. **Format:** PNG with transparency if possible

### Screenshot Checklist for Each Example

- [ ] Normal state (initial load)
- [ ] Hover state (move mouse over interactive elements)
- [ ] Pressed state (click and hold where applicable)
- [ ] Disabled state (if shown in example)
- [ ] Selected state (for checkbuttons/navigation)

### Recommended Screenshot Tool

- **Windows:** Windows Snipping Tool or Snip & Sketch
- **macOS:** Screenshot (Cmd+Shift+4)
- **Linux:** GNOME Screenshot or Flameshot

### Capturing Hover States

Some screenshot tools don't capture hover states. To capture hover effects:

1. **Method 1:** Use a delay/timer in your screenshot tool
   - Set a 3-5 second delay
   - Trigger the screenshot
   - Hover over the element during the delay

2. **Method 2:** Use video screen recording
   - Record interaction with the example
   - Extract frame showing hover state

3. **Method 3:** Modify the script temporarily
   - Add `btn.state(['hover'])` before `root.mainloop()`
   - Capture screenshot
   - Remove the modification

## File Naming Convention

When saving screenshots, use the format:
```
{example_number}_{description}_{state}.png
```

Examples:
- `01_automatic_color_mapping_normal.png`
- `01_automatic_color_mapping_hover.png`
- `02_custom_colors_pressed.png`
- `04_navigation_buttons_active.png`

## Adding New Examples

To add a new example:

1. Create a new numbered file (e.g., `08_new_example.py`)
2. Follow the existing structure:
   - Title and description at the top
   - ttkbootstrap Window with appropriate theme
   - Clear visual hierarchy (header, description, example, legend)
   - Instructions for user interaction
3. Update this README with the new example
4. Document which section of the docs it supports

## Troubleshooting

### Import Errors
If you get import errors, ensure all packages are installed:
```bash
pip install --upgrade ttkbootstrap ttkbootstrap-icons ttkbootstrap-icons-fa
```

### Icons Not Appearing
Make sure you have the Font Awesome provider installed:
```bash
pip install ttkbootstrap-icons-fa
```

### Theme Issues
If colors look wrong, verify the theme name in the script matches an available ttkbootstrap theme.

## Notes

- All examples are designed to be self-contained and runnable without modifications
- Examples use Font Awesome icons for consistency with the main documentation
- Window sizes are optimized for documentation screenshots
- Color choices demonstrate best practices for accessibility