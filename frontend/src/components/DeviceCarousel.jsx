import { useState, useRef } from 'react'
import './DeviceCarousel.css'
import DeviceDetail from './DeviceDetail'

// Constants
const MIN_SWIPE_THRESHOLD_PX = 50

function DeviceCarousel({ devices, loading, onRefresh, isDiscovering = false }) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [touchStart, setTouchStart] = useState(null)
  const [touchEnd, setTouchEnd] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState(0)
  const carouselRef = useRef(null)

  if (loading) {
    return (
      <div className="carousel-loading">
        <div className="spinner"></div>
        <p>Suche Geräte...</p>
      </div>
    )
  }

  if (devices.length === 0) {
    return (
      <div className="carousel-empty">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M9 18V5l12-2v13M9 18c0 1.657-1.343 3-3 3s-3-1.343-3-3 1.343-3 3-3 3 1.343 3 3zm12-3c0 1.657-1.343 3-3 3s-3-1.343-3-3 1.343-3 3-3 3 1.343 3 3z" />
        </svg>
        <h2>Keine Geräte gefunden</h2>
        <p>Stellen Sie sicher, dass Ihre SoundTouch-Geräte eingeschaltet und im gleichen WLAN sind.</p>
        <button className="btn-refresh" onClick={onRefresh} disabled={isDiscovering}>
          {isDiscovering ? (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="spinner" style={{marginRight: '8px'}}>
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
              Suche...
            </>
          ) : (
            'Geräte suchen'
          )}
        </button>
      </div>
    )
  }

  const isFirstCard = currentIndex === 0
  const isLastCard = currentIndex === devices.length - 1

  const handlePrevious = () => {
    if (!isFirstCard) {
      setCurrentIndex(prev => prev - 1)
    }
  }

  const handleNext = () => {
    if (!isLastCard) {
      setCurrentIndex(prev => prev + 1)
    }
  }

  const onTouchStart = (e) => {
    setTouchEnd(null)
    setTouchStart(e.targetTouches[0].clientX)
    setIsDragging(true)
  }

  const onTouchMove = (e) => {
    if (!touchStart) return
    const currentTouch = e.targetTouches[0].clientX
    setTouchEnd(currentTouch)
    const offset = currentTouch - touchStart
    setDragOffset(offset)
  }

  const onTouchEnd = () => {
    setIsDragging(false)
    if (!touchStart || !touchEnd) {
      setDragOffset(0)
      return
    }
    
    const distance = touchStart - touchEnd
    const isLeftSwipe = distance > MIN_SWIPE_THRESHOLD_PX
    const isRightSwipe = distance < -MIN_SWIPE_THRESHOLD_PX

    if (isLeftSwipe && !isLastCard) {
      handleNext()
    } else if (isRightSwipe && !isFirstCard) {
      handlePrevious()
    }
    
    setDragOffset(0)
  }

  // Mouse drag handlers (desktop)
  const onMouseDown = (e) => {
    setTouchEnd(null)
    setTouchStart(e.clientX)
    setIsDragging(true)
  }

  const onMouseMove = (e) => {
    if (!isDragging || !touchStart) return
    const offset = e.clientX - touchStart
    setDragOffset(offset)
  }

  const onMouseUp = () => {
    setIsDragging(false)
    if (!touchStart) {
      setDragOffset(0)
      return
    }
    
    const distance = touchStart - (touchStart + dragOffset)
    const isLeftSwipe = distance > MIN_SWIPE_THRESHOLD_PX
    const isRightSwipe = distance < -MIN_SWIPE_THRESHOLD_PX

    if (isLeftSwipe && !isLastCard) {
      handleNext()
    } else if (isRightSwipe && !isFirstCard) {
      handlePrevious()
    }
    
    setDragOffset(0)
  }

  const onMouseLeave = () => {
    if (isDragging) {
      setIsDragging(false)
      setDragOffset(0)
    }
  }

  return (
    <div 
      className="device-carousel"
      ref={carouselRef}
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
      onMouseDown={onMouseDown}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      onMouseLeave={onMouseLeave}
    >
      {/* Carousel Navigation */}
      {devices.length > 1 && (
        <>
          <button 
            className="carousel-nav carousel-nav--prev"
            onClick={handlePrevious}
            disabled={isFirstCard}
            aria-label="Vorheriges Gerät"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="15 18 9 12 15 6" />
            </svg>
          </button>
          
          <button 
            className="carousel-nav carousel-nav--next"
            onClick={handleNext}
            disabled={isLastCard}
            aria-label="Nächstes Gerät"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </>
      )}

      {/* Device Card */}
      <div className="carousel-container">
        <div 
          className="device-card-wrapper"
          style={{
            transform: isDragging ? `translateX(${dragOffset}px)` : 'translateX(0)',
            transition: isDragging ? 'none' : 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            opacity: isDragging && Math.abs(dragOffset) > MIN_SWIPE_THRESHOLD_PX ? 0.7 : 1
          }}
        >
          <DeviceDetail device={devices[currentIndex]} />
        </div>
      </div>

      {/* Pagination Dots */}
      {devices.length > 1 && (
        <div className="carousel-dots">
          {devices.map((_, index) => (
            <button
              key={index}
              className={`carousel-dot ${index === currentIndex ? 'carousel-dot--active' : ''}`}
              onClick={() => setCurrentIndex(index)}
              aria-label={`Gerät ${index + 1} anzeigen`}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default DeviceCarousel
