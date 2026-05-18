/**
 * CleanBook Docs - Service Worker
 * Provides offline caching for the documentation site
 */

const CACHE_NAME = 'cleanbook-docs-v1'
const BASE_PATH = '/bookmarks-cleaner/'
const STATIC_ASSETS = [
  BASE_PATH,
  BASE_PATH + 'index.html',
  BASE_PATH + 'zh/',
  BASE_PATH + 'en/',
  BASE_PATH + 'manifest.json',
  BASE_PATH + 'logo.svg',
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
            // Fallback to root page
            return caches.match(BASE_PATH)
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

// Note: Push notifications removed - icons directory does not exist
// If push notifications are needed, create icons and uncomment:
// self.addEventListener('push', (event) => {
//   const options = {
//     body: event.data?.text() || 'New content available!',
//     icon: BASE_PATH + 'icons/icon-192x192.png',
//     badge: BASE_PATH + 'icons/icon-72x72.png',
//   }
//   event.waitUntil(
//     self.registration.showNotification('CleanBook Docs', options)
//   )
// })

// Notification click handler (for future use if push is enabled)
// self.addEventListener('notificationclick', (event) => {
//   event.notification.close()
//   event.waitUntil(
//     clients.openWindow(BASE_PATH)
//   )
// })
