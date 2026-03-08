---
name: ui-ux-pro-max
description: UI/UX Design Intelligence — apply accessibility, interaction, performance, layout, typography, and animation guidelines to create professional, premium interfaces.
---

# UI/UX Pro Max — Design Intelligence

## When to Apply
Reference these guidelines when:
- Designing new UI components or pages
- Choosing color palettes and typography
- Reviewing code for UX issues
- Building landing pages or dashboards
- Implementing accessibility requirements

---

## Quick Reference — Rules by Priority

### 1. Accessibility (CRITICAL)
| Rule | Requirement |
|------|-------------|
| `color-contrast` | Minimum 4.5:1 ratio for normal text |
| `focus-states` | Visible focus rings on interactive elements |
| `alt-text` | Descriptive alt text for meaningful images |
| `aria-labels` | `aria-label` for icon-only buttons |
| `keyboard-nav` | Tab order matches visual order |
| `form-labels` | Use `<label>` with `for` attribute |

### 2. Touch & Interaction (CRITICAL)
| Rule | Requirement |
|------|-------------|
| `touch-target-size` | Minimum 44×44px touch targets |
| `loading-buttons` | Disable button during async operations |
| `error-feedback` | Clear error messages near problem |
| `cursor-pointer` | Add `cursor-pointer` to clickable elements |

### 3. Performance (HIGH)
| Rule | Requirement |
|------|-------------|
| `image-optimization` | Use WebP, `srcset`, lazy loading |
| `reduced-motion` | Check `prefers-reduced-motion` |
| `content-jumping` | Reserve space for async content (skeleton screens) |

### 4. Layout & Responsive (HIGH)
| Rule | Requirement |
|------|-------------|
| `viewport-meta` | `width=device-width, initial-scale=1` |
| `readable-font-size` | Minimum 16px body text on mobile |
| `horizontal-scroll` | Ensure content fits viewport width |
| `z-index-management` | Define z-index scale: 10, 20, 30, 50, 100 |

### 5. Typography & Color (MEDIUM)
| Rule | Requirement |
|------|-------------|
| `line-height` | Use 1.5–1.75 for body text |
| `line-length` | Limit to 65–75 characters per line |
| `font-pairing` | Match heading/body font personalities |

### 6. Animation (MEDIUM)
| Rule | Requirement |
|------|-------------|
| `duration-timing` | 150–300ms for micro-interactions |
| `transform-performance` | Use `transform`/`opacity`, not `width`/`height` |
| `loading-states` | Skeleton screens or spinners for async content |

### 7. Style Selection (MEDIUM)
| Rule | Requirement |
|------|-------------|
| `style-match` | Match visual style to product type |
| `consistency` | Same style across all pages |
| `no-emoji-icons` | Use SVG icons, not emoji |

### 8. Charts & Data (LOW)
| Rule | Requirement |
|------|-------------|
| `chart-type` | Match chart type to data type |
| `color-guidance` | Use accessible color palettes |
| `data-table` | Provide table alternative for accessibility |

---

## Common Rules for Professional UI

### Interaction & Cursor
```css
/* Always on interactive elements */
button, a, [role="button"], .clickable {
    cursor: pointer;
}

/* Disabled state */
button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}
```

### Light/Dark Mode Contrast
- Light mode: background `#FFFFFF`, text `#111111` (contrast ≥7:1)
- Dark mode: background `#0F0F0F`, text `#EBEBEB` (contrast ≥7:1)
- Accent colors must pass AA standard in both modes

### Layout & Spacing
- Use a spacing scale: 4, 8, 12, 16, 24, 32, 48, 64px
- Component padding: minimum 16px horizontal, 12px vertical
- Group related items closer together than unrelated items (Gestalt)

---

## Pre-Delivery Checklist

### Visual Quality
- [ ] Color contrast ≥ 4.5:1 for all text
- [ ] Consistent spacing using defined scale
- [ ] Shadows and borders consistent
- [ ] No emoji used as icons

### Interaction
- [ ] All buttons have loading/disabled states
- [ ] Error messages appear near the problem
- [ ] Touch targets ≥ 44×44px

### Light/Dark Mode
- [ ] Colors pass contrast in both modes
- [ ] Images/icons visible in both modes

### Layout
- [ ] No horizontal scroll on mobile
- [ ] Viewport meta tag present
- [ ] Z-index conflicts resolved

### Accessibility
- [ ] All images have alt text
- [ ] Icon-only buttons have aria-label
- [ ] Keyboard navigation works in correct order

## When to Use
Use this skill when designing or reviewing any UI component, page layout, or visual design decision.
