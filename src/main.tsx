import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { AppProvider } from './store/AppStore'
import App from './App'
import './styles/global.css'
import './styles/filter-scroll.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AppProvider><App /></AppProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
