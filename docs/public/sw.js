/**
 * CleanBook Docs - Service Worker
 * Provides offline caching for the documentation site
 */

const CACHE_NAME = 'cleanbook-docs-v1'
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/zh/',
  '/en/',
  '/manifest.json',
  '/logo.svg',
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing...')
  
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Caching static assets')
      return cache.addAll(STATIC_ASSETS)
    })
  )
  
  // Skip waiting to activate immediately
  self.skipWaiting()
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...')
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', cacheName)
            return caches.delete(cacheName)
          }
        })
      )
    })
  )
  
  // Take control of all clients
  self.clients.claim()
})

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return
  }
  
  // Skip external requests
  if (!url.origin.includes(self.location.origin)) {
    return
  }
  
  // Strategy: Network First, fallback to Cache for HTML pages
  // Strategy: Cache First, fallback to Network for static assets
  
  if (request.mode === 'navigate' || request.destination === 'document') {
    // HTML pages - Network First
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful response
          if (response.ok) {
            const clone = response.clone()
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, clone)
            })
          }
          return response
        })
        .catch(() => {
          // Fallback to cache
          return caches.match(request).then((cached) => {
            if (cached) {
              return cached
            }
            // Return offline page if available
            return caches.match('/offline.html')
          })
        })
    )
  } else {
    // Static assets - Cache First
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) {
          // Return cached version
          return cached
        }
        
        // Fetch from network
        return fetch(request).then((response) => {
          if (response.ok) {
            const clone = response.clone()
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, clone)
            })
          }
          return response
        })
      })
    )
  }
})

// Background sync for offline form submissions (if needed)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-data') {
    console.log('[SW] Background sync triggered')
    // Handle background sync
  }
})

// Push notifications (if needed)
self.addEventListener('push', (event) => {
  const options = {
    body: event.data?.text() || 'New content available!',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
  }
  
  event.waitUntil(
    self.registration.showNotification('CleanBook Docs', options)
  )
})

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  event.waitUntil(
    clients.openWindow('/')
  )
})
