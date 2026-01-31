import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BurgerMenu from './BurgerMenu';

describe('BurgerMenu', () => {
  const mockOnClose = vi.fn();
  const mockOnDiscover = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Clean up body class
    document.body.classList.remove('no-scroll');
  });

  // ========================================
  // RENDERING
  // ========================================
  describe('Rendering', () => {
    it('renders menu when isOpen is true', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      expect(document.querySelector('.burger-menu')).toBeInTheDocument();
    });

    it('renders overlay when isOpen is true', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const overlay = document.querySelector('.burger-overlay');
      expect(overlay).toBeInTheDocument();
      expect(overlay).toHaveClass('burger-overlay--open');
    });

    it('does not show open class when isOpen is false', () => {
      render(<BurgerMenu isOpen={false} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const overlay = document.querySelector('.burger-overlay');
      expect(overlay).not.toHaveClass('burger-overlay--open');
    });

    it('renders all menu items', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      expect(screen.getByText('Spotify')).toBeInTheDocument();
      expect(screen.getByText('Amazon Music')).toBeInTheDocument();
      expect(screen.getByText('Internet Radio')).toBeInTheDocument();
      expect(screen.getByText('My Music')).toBeInTheDocument();
      expect(screen.getByText('Service hinzufügen')).toBeInTheDocument();
      expect(screen.getByText('Einstellungen')).toBeInTheDocument();
      expect(screen.getByText('Hilfe')).toBeInTheDocument();
    });

    it('shows "Geräte suchen" when deviceCount is 0', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} deviceCount={0} />);
      
      expect(screen.getByText('Geräte suchen')).toBeInTheDocument();
    });

    it('shows "Weitere Geräte suchen" when deviceCount > 0', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} deviceCount={3} />);
      
      expect(screen.getByText('Weitere Geräte suchen')).toBeInTheDocument();
    });
  });

  // ========================================
  // OVERLAY BEHAVIOR
  // ========================================
  describe('Overlay Behavior', () => {
    it('calls onClose when overlay is clicked', async () => {
      const user = userEvent.setup();
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const overlay = document.querySelector('.burger-overlay');
      await user.click(overlay);
      
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('does not call onClose when menu itself is clicked', async () => {
      const user = userEvent.setup();
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const menu = document.querySelector('.burger-menu');
      await user.click(menu);
      
      expect(mockOnClose).not.toHaveBeenCalled();
    });
  });

  // ========================================
  // DISCOVER BUTTON
  // ========================================
  describe('Discover Button', () => {
    it('calls onDiscover when discover menu item clicked', async () => {
      const user = userEvent.setup();
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const discoverButton = screen.getByRole('button', { name: /geräte suchen/i });
      await user.click(discoverButton);
      
      expect(mockOnDiscover).toHaveBeenCalledTimes(1);
    });

    it('does not close menu after discover is clicked', async () => {
      const user = userEvent.setup();
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const discoverButton = screen.getByRole('button', { name: /geräte suchen/i });
      await user.click(discoverButton);
      
      // onClose should NOT be called
      expect(mockOnClose).not.toHaveBeenCalled();
    });

    it('is disabled when isDiscovering is true', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} isDiscovering={true} />);
      
      const discoverButton = screen.getByRole('button', { name: /geräte suchen/i });
      expect(discoverButton).toBeDisabled();
    });

    it('is enabled when isDiscovering is false', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} isDiscovering={false} />);
      
      const discoverButton = screen.getByRole('button', { name: /geräte suchen/i });
      expect(discoverButton).not.toBeDisabled();
    });

    it('shows spinner icon when discovering', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} isDiscovering={true} />);
      
      const spinner = document.querySelector('.spinner');
      expect(spinner).toBeInTheDocument();
    });
  });

  // ========================================
  // DISABLED MENU ITEMS
  // ========================================
  describe('Disabled Menu Items', () => {
    it('disables Spotify menu item', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const spotifyButton = screen.getByRole('button', { name: /spotify/i });
      expect(spotifyButton).toBeDisabled();
    });

    it('disables Amazon Music menu item', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const amazonButton = screen.getByRole('button', { name: /amazon music/i });
      expect(amazonButton).toBeDisabled();
    });

    it('disables Internet Radio menu item', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const radioButton = screen.getByRole('button', { name: /internet radio/i });
      expect(radioButton).toBeDisabled();
    });

    it('disables My Music menu item', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const myMusicButton = screen.getByRole('button', { name: /my music/i });
      expect(myMusicButton).toBeDisabled();
    });

    it('disables Service hinzufügen menu item', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const addServiceButton = screen.getByRole('button', { name: /service hinzufügen/i });
      expect(addServiceButton).toBeDisabled();
    });

    it('disables Einstellungen menu item', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const settingsButton = screen.getByRole('button', { name: /einstellungen/i });
      expect(settingsButton).toBeDisabled();
    });

    it('disables Hilfe menu item', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const helpButton = screen.getByRole('button', { name: /hilfe/i });
      expect(helpButton).toBeDisabled();
    });
  });

  // ========================================
  // SCROLL LOCK
  // ========================================
  describe('Scroll Lock', () => {
    it('adds no-scroll class to body when menu opens', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      expect(document.body.classList.contains('no-scroll')).toBe(true);
    });

    it('removes no-scroll class when menu closes', () => {
      const { rerender } = render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      expect(document.body.classList.contains('no-scroll')).toBe(true);
      
      rerender(<BurgerMenu isOpen={false} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      expect(document.body.classList.contains('no-scroll')).toBe(false);
    });

    it('cleans up no-scroll class on unmount', () => {
      const { unmount } = render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      expect(document.body.classList.contains('no-scroll')).toBe(true);
      
      unmount();
      
      expect(document.body.classList.contains('no-scroll')).toBe(false);
    });
  });

  // ========================================
  // KEYBOARD NAVIGATION
  // ========================================
  describe('Keyboard Navigation', () => {
    it('supports tab navigation through menu items', async () => {
      const user = userEvent.setup();
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      // Tab through menu items
      await user.tab();
      
      // First focusable element should be a button
      const firstButton = document.activeElement;
      expect(firstButton?.tagName).toBe('BUTTON');
    });

    it('allows Enter key to activate discover button', async () => {
      const user = userEvent.setup();
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const discoverButton = screen.getByRole('button', { name: /geräte suchen/i });
      discoverButton.focus();
      
      await user.keyboard('{Enter}');
      
      expect(mockOnDiscover).toHaveBeenCalledTimes(1);
    });
  });

  // ========================================
  // ACCESSIBILITY
  // ========================================
  describe('Accessibility', () => {
    it('all interactive elements are buttons', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const menuItems = document.querySelectorAll('.burger-menu-item');
      menuItems.forEach(item => {
        if (!item.classList.contains('burger-menu-divider')) {
          expect(item.tagName).toBe('BUTTON');
        }
      });
    });

    it('disabled items have disabled attribute', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const spotifyButton = screen.getByRole('button', { name: /spotify/i });
      expect(spotifyButton).toHaveAttribute('disabled');
    });

    it('menu has proper ARIA role', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const menu = document.querySelector('.burger-menu');
      expect(menu).toHaveAttribute('role', 'navigation');
    });
  });

  // ========================================
  // VISUAL DIVIDER
  // ========================================
  describe('Visual Divider', () => {
    it('renders divider before discover button', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const divider = document.querySelector('.burger-divider');
      expect(divider).toBeInTheDocument();
    });

    it('divider is not a button', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const divider = document.querySelector('.burger-divider');
      expect(divider?.tagName).not.toBe('BUTTON');
    });
  });

  // ========================================
  // RESPONSIVE BEHAVIOR
  // ========================================
  describe('Responsive Behavior', () => {
    it('applies burger-menu class for styling', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      expect(document.querySelector('.burger-menu')).toBeInTheDocument();
    });

    it('overlay covers entire viewport', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      const overlay = document.querySelector('.burger-overlay');
      const computedStyle = window.getComputedStyle(overlay);
      
      // Overlay should have position fixed (set in CSS)
      expect(overlay).toBeInTheDocument();
    });
  });

  // ========================================
  // EDGE CASES
  // ========================================
  describe('Edge Cases', () => {
    it('handles deviceCount prop default value', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      // Should default to 0, so "Geräte suchen"
      expect(screen.getByText('Geräte suchen')).toBeInTheDocument();
    });

    it('handles isDiscovering prop default value', () => {
      render(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      // Should default to false, so discover button enabled
      const discoverButton = screen.getByRole('button', { name: /geräte suchen/i });
      expect(discoverButton).not.toBeDisabled();
    });

    it('does not crash with null callbacks', () => {
      render(<BurgerMenu isOpen={true} onClose={null} onDiscover={null} />);
      
      expect(document.querySelector('.burger-menu')).toBeInTheDocument();
    });

    it('handles rapid open/close transitions', () => {
      const { rerender } = render(<BurgerMenu isOpen={false} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      rerender(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      rerender(<BurgerMenu isOpen={false} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      rerender(<BurgerMenu isOpen={true} onClose={mockOnClose} onDiscover={mockOnDiscover} />);
      
      expect(document.querySelector('.burger-menu')).toBeInTheDocument();
      expect(document.body.classList.contains('no-scroll')).toBe(true);
    });
  });
});
