# ACT Brand Implementation Guide

This guide outlines how the ACT (Alliance for Climate Transition) brand guidelines have been implemented in the Climate Economy Ecosystem platform.

## Overview

The Massachusetts Clean Energy Ecosystem platform follows the ACT brand guidelines for a consistent, professional appearance that aligns with the organization's mission of accelerating the climate economy.

## Brand Elements

### Color Palette

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Spring Green | #B2DE26 | Primary accent color, call-to-action buttons, highlighting important elements |
| Midnight Forest | #001818 | Dark text, backgrounds for contrast areas |
| Moss Green | #394816 | Secondary color, supporting elements, secondary text |
| Seafoam Blue | #E0FFFF | Light background color, card backgrounds |
| Sand Gray | #EBE9E1 | Alternative light background, secondary panels |

The color system also includes tints of these colors at 10% increments for flexibility in design while maintaining brand consistency.

### Typography

| Font | Usage | Styling |
|------|-------|---------|
| Helvetica | Headings and titles | -0.02em tracking (letter-spacing), 1.15 line height |
| Inter | Body text | 1.25 line height for optimal readability |

### Visual Elements

1. **Cards and Borders**
   - Cards with subtle spring-green borders
   - Button styles that use the primary brand colors
   - Border treatments to highlight important content

2. **DaisyUI Integration**
   - Clean, consistent component styling
   - Customized theme with ACT brand colors

## Implementation

### Tailwind Configuration

The ACT brand colors and typography are configured in the Tailwind CSS configuration for consistent application throughout the platform:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        // ACT brand colors
        "spring-green": "#B2DE26",
        "moss-green": "#394816",
        "midnight-forest": "#001818",
        "seafoam-blue": "#E0FFFF",
        "sand-gray": "#EBE9E1",
        // Keep existing colors for compatibility
        primary: "#B2DE26", // Map to spring-green
        secondary: "#394816", // Map to moss-green
        accent: "#E0FFFF", // Map to seafoam-blue
      },
      fontFamily: {
        'helvetica': ['Helvetica', 'Arial', 'sans-serif'],
        'inter': ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          "primary": "#B2DE26", // spring-green
          "primary-content": "#001818", // midnight-forest
          "secondary": "#394816", // moss-green
          "secondary-content": "#ffffff",
          "accent": "#E0FFFF", // seafoam-blue
          "neutral": "#001818", // midnight-forest
          "base-100": "#ffffff",
          "base-200": "#f9fafb",
          "base-300": "#EBE9E1", // sand-gray
        },
      },
    ],
  },
}
```

### Component Styling

DaisyUI components are used with custom ACT styling:

```jsx
// Example button with ACT brand styling
<button className="btn btn-primary">
  Get Started
</button>

// Example card with ACT brand styling
<div className="card bg-base-100 border-2 border-spring-green">
  <div className="card-body">
    <h2 className="card-title">Clean Energy Jobs</h2>
    <p>Explore opportunities in the Massachusetts clean energy sector.</p>
  </div>
</div>
```

### Global CSS

Base styling is defined in globals.css:

```css
@layer base {
  /* ACT Brand Typography */
  h1, h2, h3, h4, h5, h6 {
    font-family: 'Helvetica', Arial, sans-serif;
    letter-spacing: -0.02em; /* -20 tracking from brand guidelines */
    line-height: 1.15; /* Approximate 32pt leading for 28pt text */
  }
  
  body {
    font-family: 'Inter', sans-serif;
    letter-spacing: -0.02em; /* -20 tracking from brand guidelines */
    line-height: 1.25; /* 15pt leading for 12pt text according to guidelines */
  }
}

/* ACT Brand Component Classes */
@layer components {
  .btn-primary {
    @apply bg-spring-green text-midnight-forest hover:bg-opacity-90 border-none;
  }
  
  .btn-secondary {
    @apply bg-moss-green text-white hover:bg-opacity-90 border-none;
  }
  
  .btn-outline {
    @apply border-2 border-spring-green text-midnight-forest hover:bg-spring-green hover:text-midnight-forest;
  }
  
  .card-title {
    @apply font-helvetica text-midnight-forest;
  }
  
  .badge-act {
    @apply bg-spring-green text-midnight-forest;
  }
}
```

## Page Examples

### Homepage

The homepage implements ACT brand guidelines with:

1. **Color Usage**
   - Spring Green (#B2DE26) for call-to-action buttons
   - Card borders with Spring Green accents
   - Seafoam Blue (#E0FFFF) for section backgrounds

2. **Typography**
   - Helvetica for headings with proper tracking and line height
   - Inter for body text with appropriate line height
   - Consistent text hierarchy

3. **Component Structure**
   - Cards with proper border styling
   - Buttons with consistent branding
   - Well-structured sections with appropriate spacing

### Counselor Page

The counselor page showcases:

1. **Professional Layout**
   - Clean card-based design with Spring Green borders
   - DaisyUI chat component for AI assistant
   - Consistent spacing and alignment

2. **Interactive Elements**
   - Appointment selection with Spring Green highlighting
   - Resource cards with hover effects
   - Clean form elements

## Best Practices

1. **Color Consistency**
   - Use DaisyUI theme colors (primary, secondary, accent) for consistency
   - Maintain proper contrast ratios for accessibility
   - Use Spring Green strategically for highlighting important elements

2. **Typography Rules**
   - Apply proper font families to headings and body text
   - Maintain consistent font sizes and weights
   - Respect line heights for optimal readability

3. **Component Usage**
   - Use DaisyUI components with ACT styling
   - Maintain consistent spacing and padding
   - Ensure proper interactive states (hover, focus)

## Additional Resources

- [ACT Brand Guidelines](../brand.md) - Complete brand guidelines document
- [ACT Website](https://joinact.org) - Official ACT website for reference
- [Tailwind Configuration](../tailwind.config.js) - Implementation of brand colors and typography 