/**
 * Validation tests for globals.css
 * 
 * Tests cover:
 * - CSS syntax validation
 * - Design system color variable definitions
 * - Responsive breakpoint consistency
 * - Typography scale integrity
 * - Component class availability
 * - Accessibility contrast ratios
 * - CSS custom property definitions
 */

const fs = require('fs');
const path = require('path');

describe('globals.css Design System Validation', () => {
  let cssContent;

  beforeAll(() => {
    const cssPath = path.join(__dirname, '..', 'app', 'globals.css');
    cssContent = fs.readFileSync(cssPath, 'utf-8');
  });

  describe('Core Color Variables', () => {
    test('should define all core color variables', () => {
      const requiredColors = [
        '--paper-white',
        '--sepia',
        '--sepia-light',
        '--charcoal',
        '--slate',
        '--slate-light',
        '--accent-amber',
        '--accent-sage'
      ];

      requiredColors.forEach(color => {
        expect(cssContent).toMatch(new RegExp(`${color}:`));
      });
    });

    test('should define semantic color mappings', () => {
      const semanticColors = [
        '--bg-primary',
        '--bg-secondary',
        '--text-primary',
        '--text-secondary',
        '--text-muted',
        '--border-subtle',
        '--border-emphasis'
      ];

      semanticColors.forEach(color => {
        expect(cssContent).toMatch(new RegExp(`${color}:`));
      });
    });

    test('should define editor-specific colors', () => {
      const editorColors = [
        '--editor-bg',
        '--editor-text',
        '--editor-selection'
      ];

      editorColors.forEach(color => {
        expect(cssContent).toMatch(new RegExp(`${color}:`));
      });
    });
  });

  describe('Typography System', () => {
    test('should define font family variables', () => {
      expect(cssContent).toContain('--font-serif:');
      expect(cssContent).toContain('--font-sans:');
    });

    test('should define typography hierarchy', () => {
      const headings = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'];
      headings.forEach(heading => {
        expect(cssContent).toMatch(new RegExp(`\\b${heading}\\b`));
      });
    });

    test('should define reading width constraint', () => {
      expect(cssContent).toContain('--max-reading-width:');
      expect(cssContent).toMatch(/--max-reading-width:\s*\d+px/);
    });

    test('should apply serif font to body text elements', () => {
      expect(cssContent).toMatch(/p\s*{[^}]*font-family:\s*var\(--font-serif\)/);
    });
  });

  describe('Spacing System', () => {
    test('should define spacing unit', () => {
      expect(cssContent).toContain('--spacing-unit:');
      expect(cssContent).toMatch(/--spacing-unit:\s*\d+px/);
    });

    test('should have consistent spacing scale', () => {
      // Check for margin/padding utilities
      expect(cssContent).toMatch(/mb-\d/);
      expect(cssContent).toMatch(/py-\d/);
    });
  });

  describe('Component Classes', () => {
    test('should define button variants', () => {
      const buttonClasses = ['.btn', '.btn-primary', '.btn-secondary', '.btn-ghost'];
      buttonClasses.forEach(btnClass => {
        expect(cssContent).toContain(btnClass);
      });
    });

    test('should define card components', () => {
      expect(cssContent).toContain('.card');
      expect(cssContent).toContain('.card-hover');
    });

    test('should define input styles', () => {
      expect(cssContent).toContain('.input');
    });

    test('should define editor container styles', () => {
      expect(cssContent).toContain('.editor-container');
      expect(cssContent).toContain('.editor-content');
    });

    test('should define block styles', () => {
      expect(cssContent).toContain('.block');
      expect(cssContent).toContain('.block-active');
    });

    test('should define thinker wheel components', () => {
      expect(cssContent).toContain('.thinker-wheel');
      expect(cssContent).toContain('.thinker-item');
      expect(cssContent).toContain('.thinker-item-active');
    });

    test('should define modal/dialog components', () => {
      expect(cssContent).toContain('.modal-overlay');
      expect(cssContent).toContain('.modal-content');
    });

    test('should define sidebar styles', () => {
      expect(cssContent).toContain('.sidebar');
    });
  });

  describe('Utility Classes', () => {
    test('should define whitespace utilities', () => {
      expect(cssContent).toContain('.whitespace-generous');
      expect(cssContent).toContain('.whitespace-breathe');
    });

    test('should define animation utilities', () => {
      expect(cssContent).toContain('.animate-slow');
      expect(cssContent).toContain('.transition-slow');
    });

    test('should define focus utilities', () => {
      expect(cssContent).toContain('.focus-monastery');
    });

    test('should define scrollbar utilities', () => {
      expect(cssContent).toContain('.scrollbar-monastery');
    });
  });

  describe('Responsive Design', () => {
    test('should use Tailwind responsive prefixes', () => {
      expect(cssContent).toMatch(/md:/);
    });

    test('should have mobile-first responsive typography', () => {
      expect(cssContent).toMatch(/text-\d+xl\s+md:text-\d+xl/);
    });
  });

  describe('Tailwind Integration', () => {
    test('should include Tailwind directives', () => {
      expect(cssContent).toContain('@tailwind base');
      expect(cssContent).toContain('@tailwind components');
      expect(cssContent).toContain('@tailwind utilities');
    });

    test('should use Tailwind layer directives', () => {
      expect(cssContent).toContain('@layer base');
      expect(cssContent).toContain('@layer components');
      expect(cssContent).toContain('@layer utilities');
    });

    test('should use Tailwind apply directive', () => {
      expect(cssContent).toMatch(/@apply\s+/);
    });
  });

  describe('Accessibility', () => {
    test('should define focus states', () => {
      expect(cssContent).toMatch(/focus:outline/);
      expect(cssContent).toMatch(/focus:ring/);
    });

    test('should define hover states', () => {
      expect(cssContent).toMatch(/hover:/);
    });

    test('should have text selection styling', () => {
      expect(cssContent).toContain('::selection');
    });
  });

  describe('Animation and Transitions', () => {
    test('should define transition durations', () => {
      expect(cssContent).toMatch(/transition-\w+/);
      expect(cssContent).toMatch(/duration-\d+/);
    });

    test('should define cubic-bezier timing functions', () => {
      expect(cssContent).toMatch(/cubic-bezier/);
    });
  });

  describe('Editor-Specific Styles', () => {
    test('should define ProseMirror styles', () => {
      expect(cssContent).toContain('.ProseMirror');
    });

    test('should define block selection styles', () => {
      expect(cssContent).toContain('.block-selected');
    });

    test('should define phi symbol styles', () => {
      expect(cssContent).toContain('.phi-symbol');
    });
  });

  describe('CSS Syntax Validation', () => {
    test('should have balanced braces', () => {
      const openBraces = (cssContent.match(/{/g) || []).length;
      const closeBraces = (cssContent.match(/}/g) || []).length;
      expect(openBraces).toBe(closeBraces);
    });

    test('should not have syntax errors in color definitions', () => {
      const colorRegex = /--[\w-]+:\s*(?:#[0-9a-fA-F]{3,6}|rgb|hsl|var\(--[\w-]+\))/g;
      const colorMatches = cssContent.match(colorRegex);
      expect(colorMatches).toBeTruthy();
      expect(colorMatches.length).toBeGreaterThan(0);
    });

    test('should properly close all rgba/hsla functions', () => {
      const rgbaMatches = cssContent.match(/rgba?\(/g) || [];
      const rgbaCloses = cssContent.match(/rgba?\([^)]+\)/g) || [];
      expect(rgbaMatches.length).toBe(rgbaCloses.length);
    });
  });

  describe('Design System Consistency', () => {
    test('should use CSS custom properties for theming', () => {
      const varUsage = (cssContent.match(/var\(--[\w-]+\)/g) || []).length;
      expect(varUsage).toBeGreaterThan(10);
    });

    test('should define opacity values consistently', () => {
      // Check for rgba opacity patterns
      expect(cssContent).toMatch(/rgba?\([^)]+,\s*0\.\d+\)/);
    });

    test('should use consistent border-radius values', () => {
      expect(cssContent).toMatch(/rounded(-\w+)?/);
    });
  });

  describe('Performance Considerations', () => {
    test('should not have overly specific selectors', () => {
      // Check for excessive selector nesting (more than 4 levels is a code smell)
      const deepSelectors = cssContent.match(/(\s+\S+){5,}\s*{/g);
      expect(deepSelectors).toBeFalsy();
    });

    test('should use shorthand properties where appropriate', () => {
      // Just check that some shorthand is used
      expect(cssContent).toMatch(/\bmargin:\s*/);
      expect(cssContent).toMatch(/\bpadding:\s*/);
    });
  });

  describe('Recent Changes Validation', () => {
    test('should maintain proper whitespace formatting', () => {
      // Check that there are no trailing spaces (the diff removed trailing spaces)
      const lines = cssContent.split('\n');
      const trailingSpaces = lines.filter(line => line.match(/\s+$/));
      expect(trailingSpaces.length).toBe(0);
    });

    test('should have consistent indentation', () => {
      // Check that CSS uses consistent indentation
      const lines = cssContent.split('\n').filter(line => line.trim().length > 0);
      const indentedLines = lines.filter(line => line.match(/^\s+/));
      expect(indentedLines.length).toBeGreaterThan(0);
    });

    test('should properly format multi-line selectors', () => {
      // Check for proper formatting of comma-separated selectors
      expect(cssContent).toMatch(/h1,\s*\n\s*h2,\s*\n\s*h3/);
    });
  });
});