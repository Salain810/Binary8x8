# Icon Guidelines for Binary Matrix Integration

The integration should use a PNG icon with the following specifications:

1. Icon Design:
   - Size: 256x256 pixels
   - Background: Transparent
   - Primary Color: #44739e (Home Assistant Blue)
   - Design Elements:
     - 3x3 grid representing the matrix
     - HDMI connector symbol
     - Clean, minimal design
     - Recognizable at small sizes

2. Recommended Icon:
   1. Create a new 256x256 PNG with transparent background
   2. Draw a square frame in #44739e with rounded corners (8px radius)
   3. Inside the frame, draw a 3x3 grid of lines in white
   4. Add small white circles at the intersections
   5. Place a simplified HDMI symbol in the center
   6. Export as brand.png

3. File Location:
   - Save as `custom_components/binary_matrix/brand.png`
   - Ensure file size is under 100KB
   - Use PNG format with transparency

4. Home Assistant Integration:
   - The icon will appear in:
     - HACS repository listing
     - Integration setup flow
     - Device configuration
     - Dashboard cards

You can use any vector graphics editor (like Inkscape, Adobe Illustrator, or Figma) to create this icon following these guidelines.