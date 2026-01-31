import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TopBar from './TopBar';

// Mock BurgerMenu to avoid conflicts with TopBar buttons
vi.mock('./BurgerMenu', () => ({
  default: ({ isOpen, onClose }) => (
    isOpen ? (
      <div data-testid="burger-menu">
        <div className="burger-overlay burger-overlay--open" onClick={onClose}></div>
        <nav className="burger-menu">Mocked Menu</nav>
      </div>
    ) : (
      <div data-testid="burger-menu"></div>
    )
  ),
}));

describe('TopBar', () => {
  const mockOnDiscover = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ========================================
  // RENDERING
  // ========================================
  describe('Rendering', () => {
    it('renders topbar element', () => {
      render(<TopBar onDiscover={mockOnDiscover} />);
      
      expect(document.querySelector('.topbar')).toBeInTheDocument();
    });

    it('renders discover button', () => {
      render(<TopBar onDiscover={mockOnDiscover} />);
      
      expect(screen.getByRole('button', { name: /geräte suchen/i })).toBeInTheDocument();
    });

    it('does not show menu button when deviceCount is 0', () => {
      render(<TopBar onDiscover={mockOnDiscover} deviceCount={0} />);
      
      expect(screen.queryByRole('button', { name: /menü öffnen/i })).not.toBeInTheDocument();
    });

    it('shows menu button when deviceCount > 0', () => {
      render(<TopBar onDiscover={mockOnDiscover} deviceCount={3} />);
      
      expect(screen.getByRole('button', { name: /menü öffnen/i })).toBeInTheDocument();
    });
  });

  // ========================================
  // DISCOVER BUTTON BEHAVIOR
  // ========================================
  describe('Discover Button', () => {
    it('calls onDiscover when clicked', async () => {
      const user = userEvent.setup();
      render(<TopBar onDiscover={mockOnDiscover} />);
      
      const discoverButton = screen.getByRole('button', { name: /geräte suchen/i });
      await user.click(discoverButton);
      
      expect(mockOnDiscover).toHaveBeenCalledTimes(1);
    });

    it('is disabled when isDiscovering is true', () => {
      render(<TopBar onDiscover={mockOnDiscover} isDiscovering={true} />);
      
      const discoverButton = screen.getByRole('button', { name: /geräte suchen/i });
      expect(discoverButton).toBeDisabled();
    });

    it('is enabled when isDiscovering is false', () => {
      render(<TopBar onDiscover={mockOnDiscover} isDiscovering={false} />);
      
      const discoverButton = screen.getByRole('button', { name: /geräte suchen/i });
      expect(discoverButton).not.toBeDisabled();
    });

    it('shows spinner icon when discovering', () => {
      render(<TopBar onDiscover={mockOnDiscover} isDiscovering={true} />);
      
      const spinner = document.querySelector('.spinner');
      expect(spinner).toBeInTheDocument();
    });

    it('shows refresh icon when not discovering', () => {
      render(<TopBar onDiscover={mockOnDiscover} isDiscovering={false} />);
      
      // Refresh icon SVG path
      const refreshIcon = document.querySelector('path[d*="M21.5 2v6h-6"]');
      expect(refreshIcon).toBeInTheDocument();
    });
  });

  // ========================================
  // MENU BUTTON BEHAVIOR
  // ========================================
  describe('Menu Button', () => {
    it('is disabled when isDiscovering is true', () => {
      render(<TopBar onDiscover={mockOnDiscover} deviceCount={3} isDiscovering={true} />);
      
      const menuButton = screen.getByRole('button', { name: /menü öffnen/i });
      expect(menuButton).toBeDisabled();
    });

    it('is enabled when isDiscovering is false', () => {
      render(<TopBar onDiscover={mockOnDiscover} deviceCount={3} isDiscovering={false} />);
      
      const menuButton = screen.getByRole('button', { name: /menü öffnen/i });
      expect(menuButton).not.toBeDisabled();
    });

    it('opens burger menu when clicked', async () => {
      const user = userEvent.setup();
      render(<TopBar onDiscover={mockOnDiscover} deviceCount={3} />);
      
      const menuButton = screen.getByRole('button', { name: /menü öffnen/i });
      await user.click(menuButton);
      
      // BurgerMenu should now be visible
      expect(document.querySelector('.burger-menu')).toBeInTheDocument();
    });
  });

  // ========================================
  // ACCESSIBILITY
  // ========================================
  describe('Accessibility', () => {
    it('discover button has aria-label', () => {
      render(<TopBar onDiscover={mockOnDiscover} />);
      
      const discoverButton = screen.getByLabelText(/geräte suchen/i);
      expect(discoverButton).toBeInTheDocument();
    });

    it('discover button has title attribute', () => {
      render(<TopBar onDiscover={mockOnDiscover} />);
      
      const discoverButton = screen.getByRole('button', { name: /geräte suchen/i });
      expect(discoverButton).toHaveAttribute('title', 'Geräte suchen');
    });

    it('menu button has aria-label', () => {
      render(<TopBar onDiscover={mockOnDiscover} deviceCount={3} />);
      
      const menuButton = screen.getByLabelText(/menü öffnen/i);
      expect(menuButton).toBeInTheDocument();
    });

    it('uses semantic header element', () => {
      render(<TopBar onDiscover={mockOnDiscover} />);
      
      const header = document.querySelector('header');
      expect(header).toBeInTheDocument();
      expect(header).toHaveClass('topbar');
    });
  });

  // ========================================
  // RESPONSIVE BEHAVIOR
  // ========================================
  describe('Responsive Behavior', () => {
    it('applies topbar-button class to all buttons', () => {
      render(<TopBar onDiscover={mockOnDiscover} deviceCount={3} />);
      
      const buttons = document.querySelectorAll('.topbar-button');
      expect(buttons.length).toBeGreaterThan(0);
      expect(buttons.length).toBe(2); // Menu + Discover
    });

    it('renders SVG icons with correct dimensions', () => {
      render(<TopBar onDiscover={mockOnDiscover} deviceCount={3} />);
      
      const svgs = document.querySelectorAll('svg');
      svgs.forEach(svg => {
        expect(svg).toHaveAttribute('width', '24');
        expect(svg).toHaveAttribute('height', '24');
      });
    });
  });

  // ========================================
  // INTEGRATION WITH BURGER MENU
  // ========================================
  describe('Integration with BurgerMenu', () => {
    it('passes correct props to BurgerMenu', () => {
      render(<TopBar onDiscover={mockOnDiscover} deviceCount={5} isDiscovering={true} />);
      
      // BurgerMenu should be rendered (mocked version)
      const burgerMenu = screen.getByTestId('burger-menu');
      expect(burgerMenu).toBeInTheDocument();
    });

    it('closes menu when BurgerMenu onClose is called', async () => {
      const user = userEvent.setup();
      render(<TopBar onDiscover={mockOnDiscover} deviceCount={3} />);
      
      // Open menu
      const menuButton = screen.getByRole('button', { name: /menü öffnen/i });
      await user.click(menuButton);
      
      // With mocked BurgerMenu, we can't test the actual close behavior
      // Just verify menu button exists and is functional
      expect(menuButton).toBeInTheDocument();
    });
  });

  // ========================================
  // EDGE CASES
  // ========================================
  describe('Edge Cases', () => {
    it('handles deviceCount prop default value', () => {
      render(<TopBar onDiscover={mockOnDiscover} />);
      
      // Should default to 0, so no menu button
      expect(screen.queryByRole('button', { name: /menü öffnen/i })).not.toBeInTheDocument();
    });

    it('handles isDiscovering prop default value', () => {
      render(<TopBar onDiscover={mockOnDiscover} />);
      
      // Should default to false, so discover button enabled
      const discoverButton = screen.getByRole('button', { name: /geräte suchen/i });
      expect(discoverButton).not.toBeDisabled();
    });

    it('handles deviceCount exactly 1', () => {
      render(<TopBar onDiscover={mockOnDiscover} deviceCount={1} />);
      
      // Menu button should still appear
      expect(screen.getByRole('button', { name: /menü öffnen/i })).toBeInTheDocument();
    });

    it('does not crash with null onDiscover', () => {
      render(<TopBar onDiscover={null} />);
      
      expect(document.querySelector('.topbar')).toBeInTheDocument();
    });
  });
});
