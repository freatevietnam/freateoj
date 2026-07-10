# Judge Status Page Redesign - Hybrid Approach

## Date: 2026-07-10

## Overview
Redesign the Judge Status page with a hybrid approach combining table layout with interactive expand/hover features.

## Current State
- Simple table layout with basic online/offline icons
- Inline CSS styles
- Limited interactivity

## Design Goals
1. Modern, visually appealing design
2. Better color coding for status indicators
3. Interactive hover/expand features
4. Responsive layout

## Implementation Details

### 1. Table Layout Improvements

#### Status Indicators
- **Online**: Green badge (#44AD41) with check-circle icon
- **Offline**: Red badge (#DE2121) with minus-circle icon

#### Ping Display
- Color coding based on latency:
  - < 1ms: Green
  - 1-5ms: Yellow/Orange
  - > 5ms: Red

#### Load Display
- Progress bar visualization
- Color based on load level

#### Runtimes Display
- Badge-style language tags
- Compact layout for multiple languages

### 2. Hover/Click Expand Features

#### Hover Effect
- Row background change on hover
- Subtle animation for expand/collapse

#### Click to Expand
- Click on judge row to expand detailed view
- Shows:
  - Detailed uptime (days, hours, minutes)
  - Judge version
  - Language versions
  - Connection history

### 3. Responsive Design
- Mobile-friendly table layout
- Collapsible columns on small screens
- Touch-friendly expand/collapse

## Files to Modify

### Templates
- `templates/status/judge-status.html` - Main template
- `templates/status/judge-status-table.html` - Table template
- `templates/status/media-css.html` - CSS styles
- `templates/status/media-js.html` - JavaScript interactions

### Styles
- Add new SCSS file: `resources/status-judge.scss`
- Update `resources/style.scss` to include new file

## Color Scheme
- Online: #44AD41 (green)
- Offline: #DE2121 (red)
- Warning: #FAB623 (orange)
- Background: Default theme colors
- Text: Default theme colors

## Animation
- Smooth transitions for hover effects
- Expand/collapse animation
- Loading spinner for real-time updates

## Testing
- Test on different screen sizes
- Verify accessibility
- Check performance with multiple judges

## Success Criteria
- Improved visual hierarchy
- Better status indication
- Smooth interactions
- Responsive on all devices
