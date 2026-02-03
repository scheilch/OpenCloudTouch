# SoundTouch Device Images

## Overview
This directory contains generated SVG product images for Bose SoundTouch devices.

## Available Models

### ST10 (SoundTouch 10)
- **File**: `st10.svg`
- **Design**: Compact cube design
- **Aspect Ratio**: 1:1 (square)
- **Features**: Single speaker grill, minimal controls

### ST20 (SoundTouch 20)
- **File**: `st20.svg`
- **Design**: Horizontal rectangular design
- **Aspect Ratio**: 3:2 (landscape)
- **Features**: Full-width speaker grill, display panel

### ST30 (SoundTouch 30)
- **File**: `st30.svg`
- **Design**: Large horizontal design with dual speakers
- **Aspect Ratio**: 14:9 (landscape)
- **Features**: Dual speaker grills, center control panel, larger display

### ST300 (SoundTouch 300 Soundbar)
- **File**: `st300.svg`
- **Design**: Ultra-wide soundbar format
- **Aspect Ratio**: 4:1 (panoramic)
- **Features**: Full-width grill, minimal profile, LED indicators

### Default (Unknown Models)
- **File**: `default.svg`
- **Design**: Generic speaker with question mark
- **Usage**: Fallback for unrecognized device models

## Usage in Components

```jsx
// Import in React component
import st10 from '/images/devices/st10.svg';
import st20 from '/images/devices/st20.svg';
import st30 from '/images/devices/st30.svg';
import st300 from '/images/devices/st300.svg';
import defaultDevice from '/images/devices/default.svg';

// Or use directly in img tag
<img src="/images/devices/st10.svg" alt="SoundTouch 10" />
```

## Dynamic Model Selection

```jsx
const getDeviceImage = (deviceType) => {
  const modelMap = {
    'SoundTouch 10': '/images/devices/st10.svg',
    'SoundTouch 20': '/images/devices/st20.svg',
    'SoundTouch 30': '/images/devices/st30.svg',
    'SoundTouch 300': '/images/devices/st300.svg',
  };
  
  return modelMap[deviceType] || '/images/devices/default.svg';
};

// Usage
<img src={getDeviceImage(device.type)} alt={device.type} />
```

## Design Notes

### Style
- **Minimalist**: Clean, simple designs without excessive detail
- **Recognizable**: Silhouettes match real product proportions
- **Generated**: Clearly synthetic to avoid copyright issues
- **Scalable**: SVG format scales to any size without quality loss

### Color Palette
- **Body**: Dark grays (#0a0a0a to #1a1a1a)
- **Grill**: Mid grays (#1a1a1a to #303030)
- **Accents**: White (#fff) for Bose branding
- **LED**: Green (#0f0) for power indicators
- **Controls**: Subtle dark tones (#222 to #555)

### Effects
- Gradient fills for depth
- Subtle shadows for 3D appearance
- Semi-transparent grill patterns
- LED glow effects

## Copyright Notice
These images are **generated representations** inspired by Bose SoundTouch products but are NOT official Bose assets. They are created for the CloudTouch project to provide visual device identification without using copyrighted product photography.

**DO NOT** use these images outside the CloudTouch project or claim they represent official Bose product images.

## Maintenance

### Adding New Models
1. Create new SVG file following naming convention: `{model}.svg`
2. Use consistent viewBox dimensions
3. Match design language (gradients, shadows, colors)
4. Update this README with model details
5. Add to `modelMap` in components

### Updating Existing Images
1. Maintain aspect ratios
2. Keep color palette consistent
3. Test at multiple sizes (32px to 400px)
4. Validate SVG optimization (no unnecessary bloat)

## Technical Specs

- **Format**: SVG (Scalable Vector Graphics)
- **Optimization**: Hand-coded, minimal file size
- **Compatibility**: All modern browsers
- **Accessibility**: Include alt text when using in HTML
- **Performance**: No external dependencies, instant load

## File Sizes
- ST10: ~3.5 KB
- ST20: ~4.0 KB
- ST30: ~4.8 KB
- ST300: ~5.2 KB
- Default: ~2.8 KB

Total directory size: ~20 KB
