import { useMemo, useState } from 'react'
import { useToast } from '../../lib/useToast'
import './<Feature>Prototype.css'

export function <Feature>PrototypePage() {
  const toast = useToast()
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)

  const data = useMemo(() => ({ /* mock data */ }), [])

  function renderList() {
    const desktop = document.getElementById('<feature>-desktop-list')
    const mobile = document.getElementById('<feature>-mobile-list')
    if (desktop) desktop.innerHTML = ''
    if (mobile) mobile.innerHTML = ''
  }

  function setupAfterRender() {
    const openSheet = document.getElementById('open-mobile-sheet')
    const closeSheet = document.getElementById('close-mobile-sheet')
    const applyMobile = document.getElementById('apply-mobile-filters')
    if (openSheet) openSheet.onclick = () => setMobileFiltersOpen(true)
    if (closeSheet) closeSheet.onclick = () => setMobileFiltersOpen(false)
    if (applyMobile) {
      applyMobile.onclick = () => {
        toast.show('Mobile filters applied')
        setMobileFiltersOpen(false)
      }
    }
  }

  renderList()
  setTimeout(setupAfterRender, 0)

  return (
    <main className="<feature>-prototype-shell">
      <div className="<feature>-notice-banner" role="note">Interactive prototype · illustrative data · no production changes</div>

      <header className="<feature>-top">
        <div className="<feature>-brand"><span className="<feature>-mark">k</span>komuna</div>
        <div className="<feature>-breadcrumb">Discover › Program › All Sessions</div>
      </header>

      <section className="<feature>-desktop">
        <section className="<feature>-panel <feature>-panel--list">
          <div className="<feature>-list-wrap" id="<feature>-desktop-list" />
        </section>
        <section className="<feature>-panel <feature>-panel--calendar">
          <div className="<feature>-calendar-body">
            <section className="<feature>-month">
              <div className="<feature>-grid" id="<feature>-calendar-grid"></div>
            </section>
            <aside className="<feature>-details-panel" id="<feature>-session-details"></aside>
          </div>
        </section>
      </section>

      <section className="<feature>-mobile-review">
        <div className="<feature>-phone">
          <div className="<feature>-phone-header">
            <div className="<feature>-quick">
              <button className="active" id="quick-all">All upcoming</button>
              <button id="quick-today">Today</button>
              <button id="quick-tomorrow">Tomorrow</button>
              <button id="quick-week">This week</button>
            </div>
            <button className="<feature>-filter-trigger" id="open-mobile-sheet" aria-label="Open filters">☷</button>
          </div>
          <div className="<feature>-phone-list" id="<feature>-mobile-list"></div>
        </div>

        <div className={`<feature>-sheet-layer ${mobileFiltersOpen ? 'is-open' : ''}`} id="mobile-sheet-layer">
          <div className="<feature>-sheet" role="dialog" aria-modal="true">
            <h2>Refine results</h2>
            <div className="<feature>-sheet-filters" id="mobile-sheet-filters" />
            <div className="<feature>-sheet-actions">
              <button className="<feature>-pill" id="close-mobile-sheet" type="button">Cancel</button>
              <button className="<feature>-pill <feature>-pill--primary" id="apply-mobile-filters" type="button">Show sessions</button>
            </div>
          </div>
        </div>
      </section>

      <div className="<feature>-toast" id="<feature>-toast" role="status"></div>
    </main>
  )
}

export default <Feature>PrototypePage
