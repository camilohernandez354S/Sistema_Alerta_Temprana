<template>
  <div class="min-h-screen bg-[#aaaaaa] flex">
    <!-- Botón de menú móvil -->
    <button 
      @click="sidebarOpen = !sidebarOpen"
      class="lg:hidden fixed top-2 left-2 sm:top-4 sm:left-4 z-50 bg-[#005187] text-white p-1.5 sm:p-2 rounded-lg shadow-lg hover:bg-[#4d82bc] transition-colors"
      aria-label="Toggle menu"
    >
      <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path v-if="!sidebarOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    </button>

    <!-- Overlay para móvil -->
    <div 
      v-if="sidebarOpen"
      @click="sidebarOpen = false"
      class="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
    ></div>

    <!-- Sidebar Lateral -->
    <aside 
      :class="[
        'w-64 bg-[#c4dafa] border-r border-[#84b6f4] flex flex-col fixed lg:static inset-y-0 left-0 z-40 transform transition-transform duration-300 ease-in-out',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      ]"
    >
      <!-- Logo y Título -->
      <div class="p-6 border-b border-[#84b6f4]">
        <div class="flex items-center space-x-3 mb-4">
          <div class="w-10 h-10 bg-[#005187] rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-semibold text-[#005187]">SAT</h1>
            <p class="text-xs text-[#4d82bc]">Sistema Alerta</p>
          </div>
        </div>
        <div v-if="saludo" class="text-xs text-[#005187] font-normal bg-[#fcffff] rounded-md px-3 py-2 border border-[#84b6f4]">
          {{ saludo }}
        </div>
      </div>

      <!-- Navegación -->
      <nav class="flex-1 p-4 space-y-1">
        <div class="text-xs font-medium text-[#4d82bc] uppercase tracking-wider mb-4 px-3">Menú Principal</div>
        
        <router-link to="/admin" class="flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-colors duration-150" :class="route.path === '/admin' ? 'bg-[#005187] text-white' : 'text-[#005187] hover:bg-[#84b6f4]'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7m-9 2v8m4-8v8m5 0h-6a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2z"></path>
          </svg>
          <span class="font-medium">Dashboard</span>
        </router-link>

        <router-link to="/admin/mediciones" class="flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-colors duration-150" :class="route.path === '/admin/mediciones' ? 'bg-[#005187] text-white' : 'text-[#005187] hover:bg-[#84b6f4]'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          <span>Mediciones</span>
        </router-link>

        <router-link to="/admin/alertas" class="flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-colors duration-150" :class="route.path === '/admin/alertas' ? 'bg-[#005187] text-white' : 'text-[#005187] hover:bg-[#84b6f4]'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
          <span>Alertas</span>
        </router-link>

        <router-link to="/admin/mapas" class="flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-colors duration-150" :class="route.path === '/admin/mapas' ? 'bg-[#005187] text-white' : 'text-[#005187] hover:bg-[#84b6f4]'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
          </svg>
          <span>Mapas</span>
        </router-link>

        <router-link to="/admin/configuracion" class="flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-colors duration-150" :class="route.path === '/admin/configuracion' ? 'bg-[#005187] text-white' : 'text-[#005187] hover:bg-[#84b6f4]'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
          <span>Configuración</span>
        </router-link>
      </nav>

      <!-- Usuario y Logout -->
      <div class="p-4 border-t border-[#84b6f4] space-y-3">
        <div class="flex items-center space-x-3 px-4 py-3 bg-[#fcffff] rounded-lg border border-[#84b6f4]">
          <div class="w-9 h-9 bg-[#005187] rounded-full flex items-center justify-center">
            <span class="text-white font-medium text-sm">A</span>
          </div>
          <div class="flex-1">
            <div class="text-sm font-medium text-[#005187]">Administrador</div>
            <div class="text-xs text-[#4d82bc]">admin@sistema.local</div>
          </div>
        </div>
        <button @click="handleLogout" class="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-[#4d82bc] text-white rounded-lg hover:bg-[#005187] transition-colors duration-150 font-medium">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
          </svg>
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </aside>

    <!-- Contenido Principal -->
    <div class="flex-1 flex flex-col overflow-hidden bg-[#fcffff] lg:ml-0">
      <!-- Header Superior -->
      <header class="bg-[#fcffff] border-b border-[#c4dafa] pl-11 sm:pl-3 md:pl-6 lg:pl-8 pr-2 sm:pr-4 md:pr-6 lg:pr-8 py-2 sm:py-3 md:py-4">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-3 md:gap-4">
          <div class="min-w-0 flex-1">
            <h1 class="text-base sm:text-lg md:text-xl lg:text-2xl font-semibold text-[#005187] truncate">Panel de Administrador</h1>
            <p class="text-xs sm:text-sm text-[#4d82bc] mt-0.5 sm:mt-1 line-clamp-1">Sistema de Alerta Temprana - Monitoreo en Tiempo Real</p>
          </div>
          <div class="flex items-center gap-2 sm:gap-3 w-full sm:w-auto">
            <div class="flex items-center space-x-1.5 sm:space-x-2 px-2 sm:px-3 py-1 sm:py-1.5 bg-[#c4dafa] rounded-full border border-[#84b6f4]">
              <div class="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-emerald-500"></div>
              <span class="text-xs sm:text-sm font-medium text-[#005187] hidden sm:inline">Sistema Activo</span>
              <span class="text-xs font-medium text-[#005187] sm:hidden">Activo</span>
            </div>
            <button @click="refreshData" class="px-2.5 sm:px-3 md:px-4 py-1.5 sm:py-2 bg-[#005187] text-white rounded-lg hover:bg-[#4d82bc] transition-colors duration-150 font-medium flex items-center space-x-1.5 sm:space-x-2 text-xs sm:text-sm md:text-base whitespace-nowrap">
              <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <span>Actualizar</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Contenido con Scroll -->
      <main class="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6">
      <!-- Mensaje de error de conexión -->
      <div v-if="connectionError" class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-6 mb-8">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <div class="w-10 h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center">
              <svg class="h-6 w-6 text-[#005187]" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-[#005187] mb-2">Error de Conexión</h3>
            <p class="text-sm text-[#4d82bc] mb-4">
              No se pueden obtener datos del sensor. Verifica que el sistema esté funcionando correctamente.
            </p>
            <button @click="refreshData" class="bg-[#005187] text-white px-4 py-2 rounded-lg hover:bg-[#4d82bc] transition-colors duration-150 text-sm font-medium">
              Reintentar Conexión
            </button>
          </div>
        </div>
      </div>
      
      <!-- Resumen de Mediciones -->
      <div class="mb-6 sm:mb-8">
        <h2 class="text-lg sm:text-xl font-semibold text-[#005187] mb-4 sm:mb-6">
          Resumen de Mediciones
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <!-- Última medición -->
          <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-3 sm:p-4 md:p-5 hover:shadow-md transition-shadow duration-150">
            <div class="flex items-center justify-between mb-2 sm:mb-3">
              <div class="w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 sm:w-5 sm:h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
              <div class="text-right min-w-0 flex-1 ml-2">
                <div class="text-xl sm:text-2xl md:text-3xl font-semibold text-[#005187] truncate" :class="ultimaMedicionColor">{{ ultimaMedicion }}</div>
                <div class="text-xs text-[#4d82bc] mt-0.5 sm:mt-1">Última medición</div>
              </div>
            </div>
            <div class="text-xs text-[#4d82bc] bg-[#c4dafa] rounded-md px-2 py-1 inline-block whitespace-nowrap">Tiempo real</div>
          </div>

          <!-- Promedio -->
          <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-3 sm:p-4 md:p-5 hover:shadow-md transition-shadow duration-150">
            <div class="flex items-center justify-between mb-2 sm:mb-3">
              <div class="w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 sm:w-5 sm:h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <div class="text-right min-w-0 flex-1 ml-2">
                <div class="text-xl sm:text-2xl md:text-3xl font-semibold text-[#005187] truncate" :class="promedioColor">{{ promedio }}</div>
                <div class="text-xs text-[#4d82bc] mt-0.5 sm:mt-1">Promedio</div>
              </div>
            </div>
            <div class="text-xs text-[#4d82bc] bg-[#c4dafa] rounded-md px-2 py-1 inline-block whitespace-nowrap">Valor promedio</div>
          </div>

          <!-- Máximo -->
          <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-3 sm:p-4 md:p-5 hover:shadow-md transition-shadow duration-150">
            <div class="flex items-center justify-between mb-2 sm:mb-3">
              <div class="w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 sm:w-5 sm:h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12"></path>
                </svg>
              </div>
              <div class="text-right min-w-0 flex-1 ml-2">
                <div class="text-xl sm:text-2xl md:text-3xl font-semibold text-[#005187] truncate" :class="maximoColor">{{ maximo }}</div>
                <div class="text-xs text-[#4d82bc] mt-0.5 sm:mt-1">Máximo</div>
              </div>
            </div>
            <div class="text-xs text-[#4d82bc] bg-[#c4dafa] rounded-md px-2 py-1 inline-block whitespace-nowrap">Valor más alto</div>
          </div>

          <!-- Mínimo -->
          <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-3 sm:p-4 md:p-5 hover:shadow-md transition-shadow duration-150">
            <div class="flex items-center justify-between mb-2 sm:mb-3">
              <div class="w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 sm:w-5 sm:h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 13l-5 5m0 0l-5-5m5 5V6"></path>
                </svg>
              </div>
              <div class="text-right min-w-0 flex-1 ml-2">
                <div class="text-xl sm:text-2xl md:text-3xl font-semibold text-[#005187] truncate" :class="minimoColor">{{ minimo }}</div>
                <div class="text-xs text-[#4d82bc] mt-0.5 sm:mt-1">Mínimo</div>
              </div>
            </div>
            <div class="text-xs text-[#4d82bc] bg-[#c4dafa] rounded-md px-2 py-1 inline-block whitespace-nowrap">Valor más bajo</div>
          </div>
        </div>
      </div>

      <!-- Layout de dos columnas -->
      <div class="space-y-4 sm:space-y-6 mt-6 sm:mt-8">
        <h2 class="text-lg sm:text-xl font-semibold text-[#005187] mb-3 sm:mb-4">
          Análisis y Monitoreo
        </h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-5 md:gap-6">
          <!-- Panel de Alertas -->
          <div class="lg:col-span-1">
            <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-6 hover:shadow-md transition-shadow duration-150">
              <div class="flex items-center mb-4">
                <div class="w-10 h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center mr-3">
                  <svg class="w-5 h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-[#005187]">Panel de Alertas</h3>
              </div>
              <div class="bg-[#c4dafa] rounded-lg p-4">
                <AlertsPanel />
              </div>
            </div>
          </div>

          <!-- Gráfico de Nivel de Agua -->
          <div class="lg:col-span-1">
            <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-6 hover:shadow-md transition-shadow duration-150">
              <div class="flex items-center mb-4">
                <div class="w-10 h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center mr-3">
                  <svg class="w-5 h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-[#005187]">Gráfico de Nivel de Agua</h3>
              </div>
              <div class="bg-[#c4dafa] rounded-lg p-4">
                <NivelAguaChart />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabla de Mediciones -->
      <div class="mt-8">
        <MedicionesTable />
      </div>

      <!-- Panel de Control y Estadísticas -->
      <div class="mt-6 sm:mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 md:gap-6">
        <!-- Panel de Control de Dispositivos -->
        <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-6 hover:shadow-md transition-shadow duration-150">
          <div class="flex items-center mb-4">
            <div class="w-10 h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center mr-3">
              <svg class="w-5 h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-[#005187]">Control de Dispositivos</h3>
          </div>
          <div class="space-y-3">
            <div class="flex items-center justify-between p-3 bg-[#c4dafa] rounded-lg border border-[#84b6f4]">
              <span class="text-sm font-medium text-[#005187]">Estado del Sistema</span>
              <span class="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium">Activo</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-[#c4dafa] rounded-lg border border-[#84b6f4]">
              <span class="text-sm font-medium text-[#005187]">Conexión Arduino</span>
              <span class="px-3 py-1 bg-[#84b6f4] text-[#005187] rounded-full text-xs font-medium">Conectado</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-[#c4dafa] rounded-lg border border-[#84b6f4]">
              <span class="text-sm font-medium text-[#005187]">Base de Datos</span>
              <span class="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium">Online</span>
            </div>
            <button class="w-full mt-4 px-4 py-2 bg-[#4d82bc] text-white rounded-lg hover:bg-[#005187] transition-colors duration-150 font-medium">
              Ver Configuración
            </button>
          </div>
        </div>

        <!-- Estadísticas Rápidas -->
        <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-6 hover:shadow-md transition-shadow duration-150">
          <div class="flex items-center mb-4">
            <div class="w-10 h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center mr-3">
              <svg class="w-5 h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-[#005187]">Estadísticas</h3>
          </div>
          <div class="space-y-3">
            <div class="p-4 bg-[#c4dafa] rounded-lg border border-[#84b6f4]">
              <div class="text-sm text-[#4d82bc] mb-1 font-medium">Mediciones Totales</div>
              <div class="text-2xl font-semibold text-[#005187]">{{ totalMediciones || '--' }}</div>
            </div>
            <div class="p-4 bg-[#c4dafa] rounded-lg border border-[#84b6f4]">
              <div class="text-sm text-[#4d82bc] mb-1 font-medium">Alertas Resueltas</div>
              <div class="text-2xl font-semibold text-[#005187]">{{ alertasResueltas || '--' }}</div>
            </div>
            <div class="p-4 bg-[#c4dafa] rounded-lg border border-[#84b6f4]">
              <div class="text-sm text-[#4d82bc] mb-1 font-medium">Tiempo Activo</div>
              <div class="text-2xl font-semibold text-[#005187]">{{ tiempoActivo || '--' }}</div>
            </div>
          </div>
        </div>

        <!-- Acciones Rápidas -->
        <div class="bg-[#fcffff] border border-[#c4dafa] rounded-lg p-6 hover:shadow-md transition-shadow duration-150">
          <div class="flex items-center mb-4">
            <div class="w-10 h-10 bg-[#c4dafa] rounded-lg flex items-center justify-center mr-3">
              <svg class="w-5 h-5 text-[#005187]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-[#005187]">Acciones Rápidas</h3>
          </div>
          <div class="space-y-2">
            <button @click="refreshData" class="w-full px-4 py-2.5 bg-[#4d82bc] text-white rounded-lg hover:bg-[#005187] transition-colors duration-150 font-medium text-left flex items-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <span>Actualizar Datos</span>
            </button>
            <button class="w-full px-4 py-2.5 bg-[#4d82bc] text-white rounded-lg hover:bg-[#005187] transition-colors duration-150 font-medium text-left flex items-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <span>Exportar Reporte</span>
            </button>
            <button class="w-full px-4 py-2.5 bg-[#4d82bc] text-white rounded-lg hover:bg-[#005187] transition-colors duration-150 font-medium text-left flex items-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              <span>Configuración</span>
            </button>
          </div>
        </div>
      </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import NivelAguaChart from '../components/NivelAguaChart.vue'
import AlertsPanel from '../components/AlertsPanel.vue'
import MedicionesTable from '../components/MedicionesTable.vue'
import { ref, onMounted } from 'vue'
import { obtenerMediciones } from '../services/medicionesService'
import { getToken, logout } from '../services/authService'
import { useRouter, useRoute } from 'vue-router'
import { API_URL } from '../config/api.js'

const ultimaMedicion = ref('--')
const promedio = ref('--')
const maximo = ref('--')
const minimo = ref('--')
const saludo = ref('')
const router = useRouter()
const route = useRoute()
const connectionError = ref(false)
const sidebarOpen = ref(false)

// Función para validar si una medición es válida
function isValidMeasurement(value) {
  return value !== null && value !== undefined && !isNaN(value) && value >= 0
}

// Función para formatear mediciones con 2 decimales consistentes
function formatMeasurement(value) {
  if (!isValidMeasurement(value)) {
    return 'Sin datos'
  }
  return value.toFixed(2) + ' cm'
}

// Función para obtener color según el rango de medición
function getMeasurementColor(value) {
  if (!isValidMeasurement(value)) {
    return 'text-[#4d82bc]'  // Texto azul medio para "Sin datos"
  }
  
  // Colores sutiles para el diseño minimalista con azules
  return 'text-[#005187]'  // Texto azul oscuro para buen contraste
}

function handleLogout() {
  logout()
  router.push('/login')
}

// Función para refrescar datos
async function refreshData() {
  try {
    connectionError.value = false
    const mediciones = await obtenerMediciones()
    
    if (mediciones.length > 0) {
      const medicionesValidas = mediciones.filter(m => isValidMeasurement(m.distancia))
      
      if (medicionesValidas.length > 0) {
        const ultimaDistancia = medicionesValidas[0].distancia
        ultimaMedicion.value = formatMeasurement(ultimaDistancia)
        ultimaMedicionColor.value = getMeasurementColor(ultimaDistancia)
        
        const distanciasValidas = medicionesValidas.map(m => m.distancia)
        const promedioValue = distanciasValidas.reduce((a, b) => a + b, 0) / distanciasValidas.length
        promedio.value = formatMeasurement(promedioValue)
        promedioColor.value = getMeasurementColor(promedioValue)
        
        const maximoValue = Math.max(...distanciasValidas)
        maximo.value = formatMeasurement(maximoValue)
        maximoColor.value = getMeasurementColor(maximoValue)
        
        const minimoValue = Math.min(...distanciasValidas)
        minimo.value = formatMeasurement(minimoValue)
        minimoColor.value = getMeasurementColor(minimoValue)
      } else {
        setNoDataState()
      }
    } else {
      setNoDataState()
    }
  } catch (e) {
    console.error('Error refrescando datos:', e)
    setConnectionErrorState()
  }
}

// Variables reactivas para colores (estilo minimalista con azules)
const ultimaMedicionColor = ref('text-[#005187]')
const promedioColor = ref('text-[#005187]')
const maximoColor = ref('text-[#005187]')
const minimoColor = ref('text-[#005187]')
const totalMediciones = ref(0)
const alertasResueltas = ref(0)
const tiempoActivo = ref('--')

onMounted(async () => {
  // Saludo personalizado
  try {
    const resp = await fetch(`${API_URL}/saludo-usuario`, {
      headers: { 'Authorization': 'Bearer ' + getToken() }
    })
    const data = await resp.json()
    if (resp.ok) {
      saludo.value = data.mensaje
    } else {
      saludo.value = data.error || 'Error de autenticación'
    }
  } catch (e) {
    saludo.value = 'Error de conexión'
  }

  // Mediciones con validación y formato mejorado
  try {
    const mediciones = await obtenerMediciones()
    
    if (mediciones.length > 0) {
      // Filtrar solo mediciones válidas
      const medicionesValidas = mediciones.filter(m => isValidMeasurement(m.distancia))
      
      if (medicionesValidas.length > 0) {
        // Última medición
        const ultimaDistancia = medicionesValidas[0].distancia
        ultimaMedicion.value = formatMeasurement(ultimaDistancia)
        ultimaMedicionColor.value = getMeasurementColor(ultimaDistancia)
        
        // Calcular estadísticas solo con datos válidos
        const distanciasValidas = medicionesValidas.map(m => m.distancia)
        
        // Promedio con precisión optimizada
        const promedioValue = distanciasValidas.reduce((a, b) => a + b, 0) / distanciasValidas.length
        promedio.value = formatMeasurement(promedioValue)
        promedioColor.value = getMeasurementColor(promedioValue)
        
        // Máximo
        const maximoValue = Math.max(...distanciasValidas)
        maximo.value = formatMeasurement(maximoValue)
        maximoColor.value = getMeasurementColor(maximoValue)
        
        // Mínimo
        const minimoValue = Math.min(...distanciasValidas)
        minimo.value = formatMeasurement(minimoValue)
        minimoColor.value = getMeasurementColor(minimoValue)
        
        // Actualizar estadísticas adicionales
        totalMediciones.value = medicionesValidas.length
        
        connectionError.value = false
      } else {
        // No hay mediciones válidas
        setNoDataState()
      }
    } else {
      // No hay mediciones
      setNoDataState()
    }
    
    // Calcular tiempo activo
    tiempoActivo.value = calcularTiempoActivo()
    
  } catch (e) {
    console.error('Error obteniendo mediciones:', e)
    setConnectionErrorState()
  }
})

// Función para establecer estado sin datos
function setNoDataState() {
  ultimaMedicion.value = 'Sin datos'
  promedio.value = 'Sin datos'
  maximo.value = 'Sin datos'
  minimo.value = 'Sin datos'
  
  ultimaMedicionColor.value = 'text-white/70'
  promedioColor.value = 'text-white/70'
  maximoColor.value = 'text-white/70'
  minimoColor.value = 'text-white/70'
  
  connectionError.value = false
}

// Función para establecer estado de error de conexión
function setConnectionErrorState() {
  ultimaMedicion.value = ''
  promedio.value = ''
  maximo.value = ''
  minimo.value = ''
  
  ultimaMedicionColor.value = 'text-white/70'
  promedioColor.value = 'text-white/70'
  maximoColor.value = 'text-white/70'
  minimoColor.value = 'text-white/70'
  
  connectionError.value = true
  saludo.value = 'Error de conexión con el servidor'
}

// Función para calcular tiempo activo (puedes mejorarla con datos reales)
function calcularTiempoActivo() {
  // Por ahora retornamos un valor simulado
  // En producción, esto debería calcularse desde la primera medición
  return '24h 15m'
}
</script>

<style scoped>
.dashboard-admin {
  padding: 2rem;
}
.cards {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}
.panel-control {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
}
</style>
