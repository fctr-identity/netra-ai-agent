import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { Hint } from '../directives/hint'
import '../styles/tooltips.css'

export default createVuetify({
  directives: { Hint },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#0f766e',
          'on-primary': '#ffffff',
          'surface-variant': '#edf5f2',
          background: '#f7fbfa',
          surface: '#ffffff',
          muted: '#6c817a'
        }
      }
    }
  },
  defaults: {
    VTooltip: {
      contentClass: 'app-tooltip',
      location: 'top center',
      offset: 10,
      openDelay: 350,
      closeDelay: 100,
      openOnFocus: true,
      interactive: true,
      maxWidth: 320
    },
    VCard: {
      rounded: 'lg'
    },
    VBtn: {
      variant: 'flat',
      rounded: 'pill'
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable'
    }
  }
})
