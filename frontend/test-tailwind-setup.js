// Script de prueba para verificar la configuración de Tailwind CSS
console.log('🧪 Probando configuración de Tailwind CSS...')

// Verificar que las clases de Tailwind estén disponibles
const testElement = document.createElement('div')
testElement.className = 'text-sm text-gray-600 bg-blue-100 p-4 rounded-lg'

// Verificar estilos aplicados
const styles = window.getComputedStyle(testElement)
console.log('Estilos aplicados:', {
  fontSize: styles.fontSize,
  color: styles.color,
  backgroundColor: styles.backgroundColor,
  padding: styles.padding,
  borderRadius: styles.borderRadius
})

// Verificar si las clases están definidas
const hasTextSm = styles.fontSize === '14px' || styles.fontSize === '0.875rem'
const hasTextGray = styles.color.includes('rgb(75, 85, 99)') || styles.color.includes('#4b5563')
const hasBgBlue = styles.backgroundColor.includes('rgb(219, 234, 254)') || styles.backgroundColor.includes('#dbeafe')

console.log('Resultados de la prueba:', {
  'text-sm funciona': hasTextSm,
  'text-gray-600 funciona': hasTextGray,
  'bg-blue-100 funciona': hasBgBlue,
  'Configuración correcta': hasTextSm && hasTextGray && hasBgBlue
})

if (hasTextSm && hasTextGray && hasBgBlue) {
  console.log('✅ Tailwind CSS está configurado correctamente')
} else {
  console.log('❌ Hay problemas con la configuración de Tailwind CSS')
  console.log('Verifica que:')
  console.log('1. @import "tailwindcss" esté en main.css')
  console.log('2. @tailwindcss/vite esté instalado')
  console.log('3. El plugin de Vite esté configurado correctamente')
}
