import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import EmptyState from '../src/components/EmptyState'
import { ToastProvider } from '../src/contexts/ToastContext'

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      <ToastProvider>
        {component}
      </ToastProvider>
    </BrowserRouter>
  )
}

describe('EmptyState Component', () => {
  it('renders welcome message', () => {
    renderWithRouter(<EmptyState onDiscover={() => {}} />)
    expect(screen.getByText(/Willkommen bei CloudTouch/i)).toBeInTheDocument()
  })

  it('renders setup steps', () => {
    renderWithRouter(<EmptyState onDiscover={() => {}} />)
    expect(screen.getByText(/Geräte einschalten/i)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /Geräte suchen/i })).toBeInTheDocument()
    expect(screen.getByText(/Presets verwalten/i)).toBeInTheDocument()
  })

  it('renders discover button', () => {
    renderWithRouter(<EmptyState onDiscover={() => {}} />)
    const button = screen.getByRole('button', { name: /Jetzt Geräte suchen/i })
    expect(button).toBeInTheDocument()
  })

  it('renders help section', () => {
    renderWithRouter(<EmptyState onDiscover={() => {}} />)
    expect(screen.getByText(/Keine Geräte gefunden?/i)).toBeInTheDocument()
  })
})
